#!/usr/bin/env python3
"""
Extrator automatizado de strings de UI e MCP do Craft Anything v0.3.0 (T1.1).

Extrai todas as chaves únicas dos 4 catálogos embutidos na seção .rdata do
executável `craft-anything.exe` (fr, ja, zh-hans, zh-hant), identifica todos
os placeholders dinâmicos ({...}) e salva o inventário consolidado em:
- locales/catalog_keys.json
- locales/en_template.tsv
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXE_PATH = Path(r"C:\Program Files\Craft Anything\craft-anything.exe")

# Offsets exatos na seção .rdata do craft-anything.exe v0.3.0 (descobertos em T0.2)
CATALOG_SPECS = [
    {"code": "fr", "name": "Français", "file_offset": 42059326, "length": 63583},
    {"code": "ja", "name": "日本語", "file_offset": 42122920, "length": 69169},
    {"code": "zh-hans", "name": "简体中文", "file_offset": 42192101, "length": 83216},
    {"code": "zh-hant", "name": "繁體中文", "file_offset": 42275329, "length": 84396},
]

PLACEHOLDER_RE = re.compile(r"\{[^{}\s]*\}")


def extract_placeholders(text: str) -> list[str]:
    """Extrai placeholders do tipo {name}, {n}, {}, {c:.2} em ordem de aparição."""
    return PLACEHOLDER_RE.findall(text)


def parse_tsv_catalog(raw_text: str) -> dict[str, str]:
    """Faz o parse de um catálogo TSV embutido no formato `key\\tvalue`."""
    entries: dict[str, str] = {}
    for line in raw_text.splitlines():
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            continue
        key, val = line.split("\t", 1)
        entries[key] = val
    return entries


def extract_from_binary(exe_path: Path) -> dict[str, dict]:
    """Lê os 4 catálogos embutidos no binário PE32+ e consolida todas as chaves."""
    if not exe_path.exists():
        raise FileNotFoundError(f"Executável não encontrado: {exe_path}")

    with exe_path.open("rb") as f:
        catalogs_by_lang: dict[str, dict[str, str]] = {}
        for spec in CATALOG_SPECS:
            f.seek(spec["file_offset"])
            raw_bytes = f.read(spec["length"])
            text = raw_bytes.decode("utf-8")
            catalogs_by_lang[spec["code"]] = parse_tsv_catalog(text)

    # Preserva a ordem canônica começando pelo catálogo mais completo (zh-hans: 1360 chaves)
    # e adicionando quaisquer chaves extras presentes nos demais catálogos (fr/ja/zh-hant).
    ordered_keys: list[str] = []
    seen: set[str] = set()
    for lang_order in ("zh-hans", "zh-hant", "fr", "ja"):
        for key in catalogs_by_lang[lang_order]:
            if key not in seen:
                seen.add(key)
                ordered_keys.append(key)

    inventory: dict[str, dict] = {}
    for idx, key in enumerate(ordered_keys):
        placeholders = extract_placeholders(key)
        present_in = [
            lang for lang, cat in catalogs_by_lang.items() if key in cat
        ]
        inventory[key] = {
            "index": idx,
            "key": key,
            "placeholders": placeholders,
            "has_newline_escape": "\\n" in key,
            "present_in": present_in,
            "references": {
                lang: catalogs_by_lang[lang][key]
                for lang in ("fr", "zh-hans")
                if key in catalogs_by_lang[lang]
            },
        }
    return inventory


def main() -> int:
    exe_env = os.environ.get("CRAFT_ANYTHING_EXE")
    exe_path = Path(exe_env) if exe_env else DEFAULT_EXE_PATH

    locales_dir = PROJECT_ROOT / "locales"
    locales_dir.mkdir(parents=True, exist_ok=True)

    inventory = extract_from_binary(exe_path)

    output_json = locales_dir / "catalog_keys.json"
    output_json.write_text(
        json.dumps(
            {
                "version": "0.3.0",
                "source_binary": str(exe_path),
                "total_keys": len(inventory),
                "total_with_placeholders": sum(
                    1 for item in inventory.values() if item["placeholders"]
                ),
                "keys": list(inventory.values()),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"[OK] Extraídas {len(inventory)} chaves únicas de {exe_path}")
    print(
        f"[OK] Chaves com placeholders: "
        f"{sum(1 for item in inventory.values() if item['placeholders'])}"
    )
    print(f"[OK] Inventário salvo em: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
