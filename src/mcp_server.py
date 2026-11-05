#!/usr/bin/env python3
"""
Servidor MCP do Plugin Craft Anything PT-BR (`craft-anything-ptbr`).

Implementa o protocolo Model Context Protocol (MCP) via JSON-RPC 2.0 sobre stdio,
registrado em `%APPDATA%\\craft-anything\\config.toml` sob `[[plugins.mcp]]`.

Ferramentas expostas:
1. `ptbr_translate_key`: retorna a tradução oficial PT-BR para qualquer chave de UI do Craft Anything.
2. `ptbr_search_catalog`: busca termos em inglês ou português nas 1.363 chaves do catálogo.
3. `ptbr_plugin_status`: retorna o status de instalação, cobertura de chaves e configuração ativa.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "locales" / "pt-BR.tsv"
CONFIG_TOML_PATH = Path.home() / "AppData" / "Roaming" / "craft-anything" / "config.toml"


def load_catalog() -> dict[str, str]:
    entries: dict[str, str] = {}
    if not CATALOG_PATH.exists():
        return entries
    for line in CATALOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "\t" not in line:
            continue
        k, v = line.split("\t", 1)
        entries[k] = v
    return entries


TOOLS = [
    {
        "name": "ptbr_translate_key",
        "description": "Traduz uma chave original em inglês do Craft Anything para Português do Brasil (pt-BR).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Chave original em inglês (ex: 'Clean room', 'Build', 'Settings').",
                }
            },
            "required": ["key"],
        },
    },
    {
        "name": "ptbr_search_catalog",
        "description": "Pesquisa termos em inglês ou português no catálogo de 1.363 strings do Craft Anything PT-BR.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto ou termo técnico para buscar no catálogo.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Número máximo de resultados (padrão: 20).",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "ptbr_plugin_status",
        "description": "Verifica o status do plugin de localização PT-BR, total de chaves e configuração ativa.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def handle_request(req: dict) -> dict | None:
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params") or {}

    if method == "notifications/initialized":
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "craft-anything-ptbr",
                    "version": "1.0.0",
                },
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        catalog = load_catalog()

        if name == "ptbr_translate_key":
            key = str(args.get("key", ""))
            translation = catalog.get(key)
            payload = {
                "key": key,
                "found": translation is not None,
                "pt_br": translation if translation is not None else key,
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(payload, ensure_ascii=False)}
                    ]
                },
            }

        if name == "ptbr_search_catalog":
            query = str(args.get("query", "")).lower()
            limit = int(args.get("limit", 20))
            matches = []
            for k, v in catalog.items():
                if query in k.lower() or query in v.lower():
                    matches.append({"key": k, "pt_br": v})
                    if len(matches) >= limit:
                        break
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"query": query, "count": len(matches), "matches": matches},
                                ensure_ascii=False,
                            ),
                        }
                    ]
                },
            }

        if name == "ptbr_plugin_status":
            cfg_text = (
                CONFIG_TOML_PATH.read_text(encoding="utf-8")
                if CONFIG_TOML_PATH.exists()
                else ""
            )
            status = {
                "plugin": "craft-anything-ptbr",
                "version": "1.0.0",
                "target_app_version": "0.3.0",
                "catalog_keys_loaded": len(catalog),
                "config_toml_exists": CONFIG_TOML_PATH.exists(),
                "language_configured_ptbr": 'language = "pt' in cfg_text.lower(),
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(status, ensure_ascii=False)}
                    ]
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Ferramenta desconhecida: {name}"},
        }

    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }
    return None


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
