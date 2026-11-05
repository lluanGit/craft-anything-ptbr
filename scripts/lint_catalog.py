#!/usr/bin/env python3
"""
Linter automatizado de integridade do catálogo PT-BR (T2.2).

Verifica:
1. Codificação UTF-8 pura (sem BOM).
2. Paridade exata de 100% das chaves com o inventário `catalog_keys.json` (1.363 chaves).
3. Preservação idêntica de todos os placeholders dinâmicos (`{name}`, `{n}`, `{}`, `${c:.2}`).
4. Ausência de caracteres de substituição Unicode (U+FFFD), tabulações extras ou quebras de linha corrompidas.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PLACEHOLDER_RE = re.compile(r"\{[^{}\s]*\}")


def lint_catalog(tsv_path: Path, keys_json_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not tsv_path.exists():
        return False, [f"Catálogo TSV não encontrado: {tsv_path}"]
    if not keys_json_path.exists():
        return False, [f"Inventário JSON não encontrado: {keys_json_path}"]

    raw_bytes = tsv_path.read_bytes()
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        errors.append("O arquivo TSV contém UTF-8 BOM (esperado UTF-8 puro sem BOM).")

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return False, [f"Erro de codificação UTF-8: {exc}"]

    if "\ufffd" in text:
        errors.append("Caractere de substituição Unicode (U+FFFD) detectado no catálogo.")

    inventory_data = json.loads(keys_json_path.read_text(encoding="utf-8"))
    expected_keys = {item["key"]: item for item in inventory_data["keys"]}

    catalog_entries: dict[str, str] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) not in (2, 3):
            errors.append(
                f"Linha {line_no}: esperado 2 (ou 3) colunas separadas por TAB, encontrado {len(parts)}."
            )
            continue
        key = parts[0]
        translation = parts[-1]
        if key in catalog_entries:
            errors.append(f"Linha {line_no}: chave duplicada '{key}'.")
        if not translation:
            errors.append(f"Linha {line_no}: tradução vazia para a chave '{key}'.")
        catalog_entries[key] = translation

    missing_keys = set(expected_keys) - set(catalog_entries)
    extra_keys = set(catalog_entries) - set(expected_keys)

    if missing_keys:
        errors.append(f"Chaves ausentes no catálogo ({len(missing_keys)}): {sorted(missing_keys)[:5]}")
    if extra_keys:
        errors.append(f"Chaves desconhecidas no catálogo ({len(extra_keys)}): {sorted(extra_keys)[:5]}")

    for key, translation in catalog_entries.items():
        expected_ph = PLACEHOLDER_RE.findall(key)
        actual_ph = PLACEHOLDER_RE.findall(translation)
        if sorted(expected_ph) != sorted(actual_ph):
            errors.append(
                f"Divergência de placeholders na chave '{key}': esperado {expected_ph}, encontrado {actual_ph} em '{translation}'."
            )
        if key.count("\\n") != translation.count("\\n"):
            errors.append(
                f"Divergência de quebras de linha escapadas (\\n) na chave '{key}'."
            )

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a integridade do catálogo PT-BR.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--tsv",
        type=Path,
        default=default_root / "locales" / "pt-BR.tsv",
        help="Caminho para o arquivo pt-BR.tsv",
    )
    parser.add_argument(
        "--keys",
        type=Path,
        default=default_root / "locales" / "catalog_keys.json",
        help="Caminho para o arquivo catalog_keys.json",
    )
    args = parser.parse_args()

    ok, errors = lint_catalog(args.tsv, args.keys)
    if not ok:
        print(f"[ERRO] Falha na validação de {args.tsv}:")
        for err in errors:
            print(f"  - {err}")
        return 1

    raw_size = args.tsv.stat().st_size
    inv = json.loads(args.keys.read_text(encoding="utf-8"))
    print(f"[OK] Catálogo '{args.tsv.name}' validado com sucesso!")
    print(f"     - Total de chaves verificadas: {inv['total_keys']} (100% de cobertura)")
    print(f"     - Chaves com placeholders verificadas: {inv['total_with_placeholders']} (100% íntegros)")
    print(f"     - Codificação: UTF-8 puro sem BOM ({raw_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
