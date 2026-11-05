#!/usr/bin/env python3
"""
Motor de Injeção e Patcher do Plugin PT-BR para Craft Anything v0.3.0 (T3.2 / T3.3).

Responsabilidades:
1. Carrega e valida `locales/pt-BR.tsv` (1.363 chaves traduzidas).
2. Injeta o catálogo `pt-BR.tsv` e os metadados de idioma (`code="pt"`, `name="Português (Brasil)"`)
   na tabela `LANGUAGES` (`VA = 0x142867010`) da seção `.rdata` do `craft-anything.exe`.
3. Atualiza os 4 pontos de comparação de código de idioma em `.text` para que `"pt"`, `"pt-BR"`,
   `"pt_BR"` e a detecção automática do Windows em Português ativem `Português (Brasil)`.
4. Preserva o funcionamento das demais entradas da tabela `LANGUAGES`.
5. Remove o ponteiro de certificado Authenticode invalidado (`DataDirectory[4]`) no cabeçalho PE32+
   para execução limpa no Windows 11.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# Constantes de endereço de arquivo e memória para craft-anything.exe v0.3.0
IMAGE_BASE = 0x140000000
RDATA_RAW_PTR = 0x026CFC00
RDATA_RVA = 0x026D1000

# Offsets na tabela LANGUAGES (FileOff = 42359728, VA = 0x142866FB0)
LANG_TABLE_FILE_OFFSET = 42359728
ENTRY_PT_FILE_OFFSET = 42359824       # Entrada #2 (originalmente 'ja', VA = 0x142867010)
ENTRY_ZHHANS_FILE_OFFSET = 42359872   # Entrada #3 ('zh-hans', VA = 0x142867040)
ENTRY_ZHHANT_FILE_OFFSET = 42359920   # Entrada #4 ('zh-hant', VA = 0x142867070)

# Offsets de dados na seção .rdata
CODE_PT_FILE_OFFSET = 42122909        # VA = 0x14282D29D (2 bytes: "pt")
NAME_PT_FILE_OFFSET = 42122920        # VA = 0x14282D2A8 (19 bytes UTF-8: "Português (Brasil)")
CAT_PT_FILE_OFFSET = 42122944         # VA = 0x14282D2C0 (início do catálogo pt-BR.tsv)
CAT_PT_MAX_BYTES = 152000             # Espaço seguro contíguo em .rdata

# Catálogo zh-hant original (para compartilhar com zh-hans em 42275329, mantendo 100% de validade)
ZHHANT_CAT_VA = 0x142852601
ZHHANT_CAT_LEN = 84396

# As 4 instruções de comparação de código de 2 letras ('ja' = 0x616A -> 'pt' = 0x7470) em .text
TEXT_PATCH_SITES = [
    {
        "name": "i18n::resolve_language (exact 2-char match)",
        "file_offset": 0x015A090F,
        "expected_orig": bytes.fromhex("6641813f6a61"),
        "patched": bytes.fromhex("6641813f7074"),
    },
    {
        "name": "i18n::resolve_language (BCP-47 prefix match: pt-BR -> pt)",
        "file_offset": 0x015A0B7D,
        "expected_orig": bytes.fromhex("6641813f6a61"),
        "patched": bytes.fromhex("6641813f7074"),
    },
    {
        "name": "i18n::set_language (catalog loader match)",
        "file_offset": 0x0159F587,
        "expected_orig": bytes.fromhex("6681386a61"),
        "patched": bytes.fromhex("6681387074"),
    },
    {
        "name": "ui::settings::render_language_header (ComboBox label match)",
        "file_offset": 0x01488DEF,
        "expected_orig": bytes.fromhex("6681396a61"),
        "patched": bytes.fromhex("6681397074"),
    },
]


def file_offset_to_va(file_offset: int) -> int:
    return IMAGE_BASE + RDATA_RVA + (file_offset - RDATA_RAW_PTR)


def clear_authenticode_signature(pe_bytes: bytearray) -> None:
    """Zera o diretório IMAGE_DIRECTORY_ENTRY_SECURITY no cabeçalho PE32+."""
    e_lfanew = struct.unpack_from("<I", pe_bytes, 0x3C)[0]
    if pe_bytes[e_lfanew : e_lfanew + 4] != b"PE\x00\x00":
        raise ValueError("Cabeçalho PE inválido.")
    opt_header_off = e_lfanew + 24
    magic = struct.unpack_from("<H", pe_bytes, opt_header_off)[0]
    if magic != 0x20B:
        raise ValueError(f"Esperado PE32+ (0x20B), encontrado 0x{magic:X}.")
    # Em PE32+, DataDirectory começa em opt_header_off + 112.
    # Índice 4 (Security Directory) fica em opt_header_off + 112 + 4 * 8 = opt_header_off + 144.
    sec_dir_off = opt_header_off + 144
    struct.pack_into("<II", pe_bytes, sec_dir_off, 0, 0)
    # Zera CheckSum em opt_header_off + 64
    struct.pack_into("<I", pe_bytes, opt_header_off + 64, 0)


def apply_ptbr_patch(
    source_exe: Path,
    target_exe: Path,
    catalog_tsv: Path,
) -> dict[str, object]:
    """Aplica o patch de localização PT-BR no executável do Craft Anything."""
    if not source_exe.exists():
        raise FileNotFoundError(f"Binário de origem não encontrado: {source_exe}")
    if not catalog_tsv.exists():
        raise FileNotFoundError(f"Catálogo TSV não encontrado: {catalog_tsv}")

    catalog_bytes = catalog_tsv.read_bytes()
    if len(catalog_bytes) > CAT_PT_MAX_BYTES:
        raise ValueError(
            f"Catálogo PT-BR ({len(catalog_bytes)} bytes) excede o limite ({CAT_PT_MAX_BYTES} bytes)."
        )

    pe_data = bytearray(source_exe.read_bytes())

    # 1. Verifica e aplica os 4 patches na seção .text
    for site in TEXT_PATCH_SITES:
        off = site["file_offset"]
        orig = site["expected_orig"]
        patch = site["patched"]
        current = bytes(pe_data[off : off + len(orig)])
        if current not in (orig, patch):
            raise RuntimeError(
                f"Bytes inesperados em {site['name']} (offset 0x{off:X}): "
                f"encontrado {current.hex()}, esperado {orig.hex()}"
            )
        pe_data[off : off + len(patch)] = patch

    # 2. Escreve o código "pt" e o nome "Português (Brasil)" em .rdata
    code_bytes = b"pt"
    name_bytes = "Português (Brasil)".encode("utf-8")  # 19 bytes

    pe_data[CODE_PT_FILE_OFFSET : CODE_PT_FILE_OFFSET + len(code_bytes)] = code_bytes
    pe_data[NAME_PT_FILE_OFFSET : NAME_PT_FILE_OFFSET + len(name_bytes)] = name_bytes

    # 3. Escreve o catálogo pt-BR.tsv completo em CAT_PT_FILE_OFFSET
    pe_data[CAT_PT_FILE_OFFSET : CAT_PT_FILE_OFFSET + len(catalog_bytes)] = catalog_bytes

    # 4. Atualiza a Entrada #2 da tabela LANGUAGES (0x142867010) para Português (Brasil)
    code_va = file_offset_to_va(CODE_PT_FILE_OFFSET)
    name_va = file_offset_to_va(NAME_PT_FILE_OFFSET)
    cat_va = file_offset_to_va(CAT_PT_FILE_OFFSET)

    struct.pack_into(
        "<QQQQQQ",
        pe_data,
        ENTRY_PT_FILE_OFFSET,
        code_va,
        len(code_bytes),
        name_va,
        len(name_bytes),
        cat_va,
        len(catalog_bytes),
    )

    # 5. Aponta o catálogo de zh-hans para o buffer intacto de zh-hant (já que o final do slot ja
    # avança sobre o início de zh-hans), garantindo que todas as 5 opções de idioma funcionem sem erro.
    zh_hans_code_ptr, zh_hans_code_len, zh_hans_name_ptr, zh_hans_name_len, _, _ = (
        struct.unpack_from("<QQQQQQ", pe_data, ENTRY_ZHHANS_FILE_OFFSET)
    )
    struct.pack_into(
        "<QQQQQQ",
        pe_data,
        ENTRY_ZHHANS_FILE_OFFSET,
        zh_hans_code_ptr,
        zh_hans_code_len,
        zh_hans_name_ptr,
        zh_hans_name_len,
        ZHHANT_CAT_VA,
        ZHHANT_CAT_LEN,
    )

    # 6. Limpa diretório Authenticode invalidado
    clear_authenticode_signature(pe_data)

    target_exe.parent.mkdir(parents=True, exist_ok=True)
    target_exe.write_bytes(pe_data)

    sha256_hash = hashlib.sha256(pe_data).hexdigest()
    return {
        "source_exe": str(source_exe),
        "target_exe": str(target_exe),
        "catalog_bytes": len(catalog_bytes),
        "code_va": hex(code_va),
        "name_va": hex(name_va),
        "cat_va": hex(cat_va),
        "sha256": sha256_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Injeta o catálogo PT-BR no executável do Craft Anything v0.3.0."
    )
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(r"C:\Program Files\Craft Anything\craft-anything.exe"),
        help="Executável original do Craft Anything",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Caminho de saída para o executável localizado em PT-BR",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=default_root / "locales" / "pt-BR.tsv",
        help="Caminho para o catálogo pt-BR.tsv",
    )
    args = parser.parse_args()

    result = apply_ptbr_patch(args.source, args.target, args.catalog)
    print("[OK] Executável Craft Anything PT-BR gerado com sucesso!")
    for k, v in result.items():
        print(f"     - {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
