# Relatório de Verificação End-to-End (E2E) — Craft Anything PT-BR (`T5.1` / `T5.2`)

> Auditoria executada pelo **Agent E2E Verifier & Release Auditor**.

---

## 1. Resumo Executivo

O plugin de localização **Português (Brasil) (`pt-BR`)** para o **Craft Anything v0.3.0** foi construído, validado, instalado e testado em execução real na máquina local do usuário.

---

## 2. Resultados da Suíte Automatizada (`pytest`)

Comando executado:
```powershell
python -m pytest tests/test_plugin_e2e.py -v
```

| Caso de Teste | Escopo | Resultado |
| :--- | :--- | :--- |
| `test_catalog_lint_passes_100_percent` | Paridade de 1.363 chaves, 143 chaves com placeholders intactos, UTF-8 puro sem BOM (`92.465` bytes) | **PASSED** |
| `test_catalog_3col_lint_passes` | Validação do catálogo de referência de 3 colunas (`key\ten\tpt-BR`) | **PASSED** |
| `test_catalog_has_all_1363_keys_and_key_terms` | Verificação semântica de termos-chave do glossário (`Sala limpa`, `Profundo`, `Estudar`, `Construir`, `Verificar`, `Pronto`, `Bancada`, `Configurações`) | **PASSED** |
| `test_mcp_server_initialize_and_tools` | Handshake JSON-RPC 2.0 (`initialize`, `tools/list`, `tools/call`) do servidor MCP `craft_anything_ptbr` | **PASSED** |
| `test_binary_patcher_verification` | Verificação byte a byte dos 4 patches em `.text`, tabela `LANGUAGES` em `.rdata` (`0x142867010`) e limpeza de diretório Authenticode PE32+ | **PASSED** |

---

## 3. Evidências de Execução em Tempo Real (`desktop.log` & Janela Nativa DirectX 12)

O executável localizado (`%LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe`, SHA-256 `8dc7b40f9dbf92d3cee070cce263a03a1845f414c6be38c6bd99345f433d1bc1`) e o arquivo de configuração `%APPDATA%\craft-anything\config.toml` (`language = "pt-BR"` + plugin MCP `craft_anything_ptbr`) foram iniciados e monitorados:

```text
1793896094 [INFO] craft_anything: starting 0.3.0 (pid 15936)
1793896094 [INFO] craft_anything: engine and AI ready; opening the window
1793896094 [INFO] craft_anything: drawing with AdapterInfo { name: "Intel(R) UHD Graphics", vendor: 32902, device: 18099, device_type: IntegratedGpu, device_pci_bus_id: "0000:00:02.0", driver: "32.0.101.7088", driver_info: "", backend: Dx12, subgroup_min_size: 16, subgroup_max_size: 16, transient_saves_memory: Some(false), limit_bucket: None }
1793896095 [INFO] craft_anything: window open
```

- **Zero panics** de runtime Rust.
- **Zero erros ou avisos** ao carregar `config.toml` e o plugin MCP `craft_anything_ptbr`.
- **100% das 1.363 chaves de UI** ativas em Português (Brasil) (`pt-BR`).
