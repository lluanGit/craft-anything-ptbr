# Craft Anything PT-BR (`craft-anything-ptbr`)

Plugin e pacote de localização completo em **Português do Brasil (`pt-BR`)** para o **Craft Anything v0.3.0** (`storytold/craft-anything`).

---

## O que este Plugin entrega

1. **100% da Interface Traduzida (`1.363` chaves):**
   - Todas as telas (`Estudar`, `Construir`, `Verificar`, `Pronto`, `Bancada`, `Configurações`), botões, explicações do modo Iniciante (`Simples`) e ferramentas técnicas de engenharia reversa do modo `Avançado` (`Sala limpa`, `Modo Profundo`, `Desmontagem`, `Pseudo-C`, `Grafo de chamadas`, `Registro de evidências`) traduzidas para Português do Brasil natural e preciso.
2. **Seletor Nativo nas Configurações (`Português (Brasil)`):**
   - Integra **`Português (Brasil)`** diretamente na tabela `LANGUAGES` da engine `i18n.rs` do executável e ativa `language = "pt-BR"` em `%APPDATA%\craft-anything\config.toml`.
3. **Servidor MCP Integrado (`craft_anything_ptbr`):**
   - Registrado em `config.toml` sob `[[plugins.mcp]]`, oferecendo aos agentes as ferramentas `ptbr_translate_key`, `ptbr_search_catalog` e `ptbr_plugin_status`.
4. **Instalador e Desinstalador em 1 Comando (`install.ps1` / `uninstall.ps1`):**
   - Funciona imediatamente em modo Usuário (instalando em `%LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe`, registrando no `HKCU\...\App Paths` e criando atalho no Menu Iniciar) e também atualiza `C:\Program Files\Craft Anything\craft-anything.exe` (com backup `.bak`) se executado como Administrador.

---

## Como Usar

### Instalação Rápida (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

> **Dica:** Caso queira substituir também o binário dentro de `C:\Program Files\Craft Anything\craft-anything.exe` (além da instalação automática no perfil do usuário e atalho do Menu Iniciar), basta executar o PowerShell como **Administrador** e rodar `.\install.ps1`.

### Abrir o Craft Anything em Português (Brasil)
- Pelo **Menu Iniciar**: clique em **Craft Anything (PT-BR)**.
- Ou pelo terminal / Executar (`Win + R`):
  ```powershell
  & "$env:LOCALAPPDATA\Programs\Craft Anything\craft-anything.exe"
  ```
- Ou pelo loader na raiz deste repositório:
  ```powershell
  .\CraftAnything-PTBR.exe
  ```

### Desinstalação / Restauração do Original
```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1
```

---

## Validação e Testes Automatizados

Para rodar o linter de integridade do catálogo e a suíte de testes End-to-End (`pytest`):

```powershell
python .\scripts\lint_catalog.py
python -m pytest .\tests\test_plugin_e2e.py -v
```

---

## Estrutura do Projeto

- `AGENTS.md` — Governança multi-agente e regras permanentes de localização.
- `ROADMAP.md` — Plano de ação completo (Fases 0 a 5 concluídas).
- `ESTADO.md` — Status atual e checklist de entrega.
- `locales/pt-BR.tsv` — Catálogo de tradução nativo (1.363 chaves em UTF-8 sem BOM).
- `locales/pt-BR-3col.tsv` — Catálogo tabular de referência (`key`, `en`, `pt-BR`).
- `locales/catalog_keys.json` — Inventário estruturado de chaves e placeholders.
- `src/plugin_patcher.py` — Motor de injeção binária na tabela `LANGUAGES` (`.rdata`).
- `src/mcp_server.py` — Servidor MCP (`stdio` JSON-RPC 2.0) do plugin PT-BR.
- `src/CraftAnythingPTBRLoader.cs` — Código-fonte do launcher nativo `CraftAnything-PTBR.exe`.
- `scripts/extract_strings.py` — Extrator automatizado de catálogos do binário.
- `scripts/lint_catalog.py` — Linter de paridade de chaves, placeholders e UTF-8.
- `tests/test_plugin_e2e.py` — Suíte de testes automatizados E2E.
- `docs/` — Documentação técnica de engenharia reversa (`arquitetura-i18n.md`, `mecanismo-plugin.md`, `loader-design.md`, `glossario.md` e `evidencias/`).
