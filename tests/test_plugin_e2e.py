from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from lint_catalog import lint_catalog
from mcp_server import handle_request, load_catalog
from plugin_patcher import (
    CAT_PT_FILE_OFFSET,
    CODE_PT_FILE_OFFSET,
    ENTRY_PT_FILE_OFFSET,
    NAME_PT_FILE_OFFSET,
    TEXT_PATCH_SITES,
    apply_ptbr_patch,
    file_offset_to_va,
)


def test_catalog_lint_passes_100_percent() -> None:
    tsv_path = PROJECT_ROOT / "locales" / "pt-BR.tsv"
    keys_path = PROJECT_ROOT / "locales" / "catalog_keys.json"
    ok, errors = lint_catalog(tsv_path, keys_path)
    assert ok, f"Erros no linter: {errors}"


def test_catalog_3col_lint_passes() -> None:
    tsv_path = PROJECT_ROOT / "locales" / "pt-BR-3col.tsv"
    keys_path = PROJECT_ROOT / "locales" / "catalog_keys.json"
    ok, errors = lint_catalog(tsv_path, keys_path)
    assert ok, f"Erros no linter 3col: {errors}"


def test_catalog_has_all_1363_keys_and_key_terms() -> None:
    cat = load_catalog()
    assert len(cat) == 1363
    assert cat["Language"] == "Idioma"
    assert cat["Settings"] == "Configurações"
    assert cat["Clean room"] == "Sala limpa"
    assert cat["Deep"] == "Profundo"
    assert cat["Study"] == "Estudar"
    assert cat["Build"] == "Construir"
    assert cat["Check"] == "Verificar"
    assert cat["Ready"] == "Pronto"
    assert cat["Workbench"] == "Bancada"


def test_mcp_server_initialize_and_tools() -> None:
    init_resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert init_resp is not None
    assert init_resp["result"]["serverInfo"]["name"] == "craft-anything-ptbr"

    list_resp = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert list_resp is not None
    tool_names = [t["name"] for t in list_resp["result"]["tools"]]
    assert "ptbr_translate_key" in tool_names
    assert "ptbr_search_catalog" in tool_names
    assert "ptbr_plugin_status" in tool_names

    call_resp = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "ptbr_translate_key", "arguments": {"key": "Clean room"}},
        }
    )
    assert call_resp is not None
    payload = json.loads(call_resp["result"]["content"][0]["text"])
    assert payload["found"] is True
    assert payload["pt_br"] == "Sala limpa"


def test_binary_patcher_verification(tmp_path: Path) -> None:
    source_exe = Path(r"C:\Program Files\Craft Anything\craft-anything.exe")
    target_exe = tmp_path / "craft-anything.exe"
    catalog_tsv = PROJECT_ROOT / "locales" / "pt-BR.tsv"

    res = apply_ptbr_patch(source_exe, target_exe, catalog_tsv)
    assert target_exe.exists()
    assert res["catalog_bytes"] == catalog_tsv.stat().st_size

    with target_exe.open("rb") as f:
        for site in TEXT_PATCH_SITES:
            f.seek(site["file_offset"])
            actual = f.read(len(site["patched"]))
            assert actual == site["patched"], f"Patch falhou em {site['name']}"

        f.seek(ENTRY_PT_FILE_OFFSET)
        c_va, c_len, n_va, n_len, cat_va, cat_len = struct.unpack("<QQQQQQ", f.read(48))
        assert c_va == file_offset_to_va(CODE_PT_FILE_OFFSET)
        assert c_len == 2
        assert n_va == file_offset_to_va(NAME_PT_FILE_OFFSET)
        assert n_len == len("Português (Brasil)".encode("utf-8"))
        assert cat_va == file_offset_to_va(CAT_PT_FILE_OFFSET)
        assert cat_len == catalog_tsv.stat().st_size

        f.seek(CODE_PT_FILE_OFFSET)
        assert f.read(2) == b"pt"
        f.seek(NAME_PT_FILE_OFFSET)
        assert f.read(n_len).decode("utf-8") == "Português (Brasil)"
        f.seek(CAT_PT_FILE_OFFSET)
        embedded_cat = f.read(cat_len).decode("utf-8")
        assert "Language\tIdioma" in embedded_cat
        assert "Settings\tConfigurações" in embedded_cat
