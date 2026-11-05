# ESTADO.md — craft-anything-ptbr

> Estado atual do projeto, próxima tarefa e entregas concluídas.

## 1. Onde Estamos
- **Fase Atual:** Fase 5 — Concluída (100% das tarefas `T0.1` a `T5.3` finalizadas e verificadas).
- **Status Geral:** Plugin de localização **Português (Brasil) (`pt-BR`)** construído, validado por suíte `pytest` E2E e instalado na máquina local do usuário.

## 2. Entregáveis Construídos e Instalados
- **Catálogo Completo PT-BR (`1.363` chaves, 100% de cobertura):**
  - `locales/pt-BR.tsv` (`92.465` bytes, UTF-8 sem BOM, formato 2 colunas nativo `i18n.rs`).
  - `locales/pt-BR-3col.tsv` (formato 3 colunas `key\ten\tpt-BR`).
  - `locales/catalog_keys.json` (inventário completo extraído do binário v0.3.0).
- **Motor do Plugin & Integração MCP:**
  - `src/plugin_patcher.py`: injetor binário determinístico para o `craft-anything.exe` v0.3.0.
  - `src/mcp_server.py`: servidor MCP (`craft_anything_ptbr`) registrado em `%APPDATA%\craft-anything\config.toml`.
  - `src/CraftAnythingPTBRLoader.cs` & `CraftAnything-PTBR.exe`: loader nativo Windows x64.
- **Instalador e Desinstalador Automatizados:**
  - `install.ps1` e `uninstall.ps1`.
- **Binário Localizado Instalado e Ativo:**
  - `%LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe`
  - Atalho no Menu Iniciar: `Craft Anything (PT-BR).lnk`
  - Configuração ativa: `%APPDATA%\craft-anything\config.toml` (`language = "pt-BR"`).

## 3. Verificação de Qualidade
- **Linter de Catálogo (`scripts/lint_catalog.py`):** `0` erros, 1.363 chaves traduzidas, 143 chaves com placeholders `{...}` 100% preservados.
- **Suíte E2E (`tests/test_plugin_e2e.py`):** `5 passed` (100% verde).
- **Smoke Test Runtime (`desktop.log`):** Inicialização DirectX 12 limpa, zero panics, zero avisos de configuração.
