# ROADMAP.md — craft-anything-ptbr

> Plano de execução detalhado para o plugin/extensão de linguagem PT-BR do **Craft Anything**.
> As regras permanentes do projeto e o modelo de multi-agentes estão em `AGENTS.md` (leia primeiro).
> Marque `[x]` somente quando **todos** os critérios de aceite da tarefa estiverem comprovadamente verdes.
> `🧑 HUMANO` = requer ação ou confirmação do desenvolvedor; o agente solicita e aguarda.

---

## Como Operar este Roadmap com o Esquadrão Multi-Agente

1. **Leitura Prévia:** O agente ativo deve ler `AGENTS.md` e a faixa específica da sua tarefa neste `ROADMAP.md`.
2. **Execução Estrita:** Executar somente uma tarefa por ciclo (a primeira não marcada cujas dependências foram atendidas).
3. **Validação:** Rodar os scripts de validação de catálogo e compilação antes de assinalar `[x]`.
4. **Evidência:** Registrar 1 linha de evidência objetiva na tarefa e persistir relatórios detalhados na pasta `docs/evidencias/`.
5. **Aviso Importante:** Nenhuma linha de código do plugin deve ser implementada antes das fases preparatórias e aprovação das especificações.

---

## Mapa de Dependências

```
T0.1 ──► T0.2 ──► T0.3
                    │
                    ▼
          T1.1 ──► T1.2 ──► T1.3
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          T2.1 ──► T2.2 ──► T2.3      T3.1 ──► T3.2 ──► T3.3
                    │                   │
                    └─────────┬─────────┘
                              ▼
                    T4.1 ──► T4.2
                              │
                              ▼
                    T5.1 ──► T5.2 ──► T5.3
```

---

## Fase 0 — Descoberta & Engenharia Reversa do Craft Anything

*Agente Líder: Agent Inspector & Codebase Analyst*

### [x] T0.1 🧑 HUMANO — Definição do Ambiente e Alvo do Craft Anything
- **Responsável:** Desenvolvedor Humano.
- **Ação:** Informar se o desenvolvimento utilizará o repositório clonado localmente (`github.com/storytold/craft-anything`), o pacote binário instalado do Craft Anything ou a suite via `craft-launcher`.
- **Entregável:** Caminho do diretório base configurado em `TARGET_PATH` dentro de um arquivo `.env` local.
- **Critério de aceite:** O caminho é válido e acessível na máquina do desenvolvedor.
- **Evidência:** Configurado `.env` apontando para `C:\Program Files\Craft Anything\craft-anything.exe` (v0.3.0) e `artcraft-launcher.exe`.

### [x] T0.2 — Inspeção da Arquitetura de i18n Existente
- **Dep.:** T0.1.
- **Responsável:** *Agent Inspector & Codebase Analyst*.
- **Ação:** Auditar o código-fonte/binário do Craft Anything e dependências de `craft-i18n` para mapear:
  1. Como as strings são declaradas (`i18n::tr` em `0x1415A1BA0` e `i18n::tr_fmt` em `0x1415A1F90`).
  2. Formato esperado dos catálogos (`key<TAB>translation\n` embutidos em `.rdata` na tabela `LANGUAGES` em `0x142866FB0`).
  3. Onde o idioma padrão do sistema é detectado (`i18n::resolve_language` em `0x1415A10C0`) e persistido (`%APPDATA%\craft-anything\config.toml`).
- **Entregável:** Documento técnico `docs/arquitetura-i18n.md` contendo os pontos de injeção e ciclo de vida de localização.
- **Critério de aceite:** 100% dos mecanismos de resolução de texto mapeados com referências exatas de endereços e offsets.
- **Evidência:** Documentado em `docs/arquitetura-i18n.md` com todos os offsets PE32+ e RVAs descompilados.

### [x] T0.3 — Mapeamento do Sistema de Extensão / Plugins
- **Dep.:** T0.2.
- **Responsável:** *Agent Inspector & Codebase Analyst* + *Agent Plugin Core Engineer*.
- **Ação:** Identificar o mecanismo de extensão do Craft Anything (`[[plugins.mcp]]` em `config.toml` + injeção de catálogo na seção `.rdata` + loader nativo).
- **Entregável:** Documento `docs/mecanismo-plugin.md` definindo o ponto ótimo de acoplamento do plugin PT-BR com impacto zero no core.
- **Critério de aceite:** Decisão fechada e validada sobre a estratégia de montagem do plugin.
- **Evidência:** Documentado em `docs/mecanismo-plugin.md` definindo a arquitetura híbrida em 3 camadas.

---

## Fase 1 — Extração de Strings & Definição do Glossário

*Agente Líder: Agent Linguist & i18n Architect*

### [x] T1.1 — Extração Automatizada das Strings de UI e MCP
- **Dep.:** T0.2.
- **Responsável:** *Agent Inspector & Codebase Analyst*.
- **Ação:** Criar script de extração (`scripts/extract_strings.py`) que extrai os 4 catálogos embutidos (`fr`, `ja`, `zh-hans`, `zh-hant`) e consolida as chaves em `locales/catalog_keys.json`.
- **Critério de aceite:**
  - [x] Inventário de chaves gerado sem duplicatas (1.363 chaves únicas).
  - [x] Todos os placeholders identificados (143 chaves com placeholders `{...}`).
  - [x] Zero strings de UI catalogadas faltando.
- **Evidência:** Gerado `locales/catalog_keys.json` com 1.363 chaves únicas e 143 chaves parametrizadas.

### [x] T1.2 — Validação e Fechamento do Glossário Técnico PT-BR
- **Dep.:** T1.1.
- **Responsável:** *Agent Linguist & i18n Architect*.
- **Ação:** Expandir o glossário da Seção 4 do `AGENTS.md`, consolidando a tradução dos termos de clean room, disassembler, pixel inspection e LLM tool orchestration para `docs/glossario.md`.
- **Critério de aceite:**
  - [x] Termos validados e documentados.
  - [x] Nenhuma tradução literal ambígua que prejudique o fluxo do desenvolvedor.
- **Evidência:** Criado `docs/glossario.md` com 32 termos técnicos padronizados.

### [x] T1.3 — Scaffold do Repositório do Plugin
- **Dep.:** T1.1.
- **Responsável:** *Agent Plugin Core Engineer*.
- **Ação:** Inicializar o layout estrutural do projeto do plugin (`craft-anything-ptbr`), incluindo `locales/`, `src/`, `scripts/`, `tests/`, `.gitignore`, `README.md` e `LICENSE`.
- **Critério de aceite:** Estrutura criada e scripts de validação inicial rodando limpos.
- **Evidência:** Estrutura completa criada em `.\`.

---

## Fase 2 — Criação e Validação do Catálogo de Tradução

*Agente Líder: Agent Linguist & i18n Architect*

### [x] T2.1 — Geração do Catálogo Base PT-BR (`pt-BR.tsv`)
- **Dep.:** T1.2, T1.3.
- **Responsável:** *Agent Linguist & i18n Architect*.
- **Ação:** Produzir o catálogo `locales/pt-BR.tsv` (formato nativo 2 colunas `key\tpt-BR`) e `locales/pt-BR-3col.tsv` (formato 3 colunas `key\ten\tpt-BR`).
- **Critério de aceite:**
  - [x] Arquivo codificado em UTF-8 puro (sem BOM).
  - [x] 100% das chaves do inventário T1.1 presentes e traduzidas (1.363/1.363).
  - [x] Todas as interpolações (`{name}`, `{n}`, `{}`, etc.) rigorosamente preservadas.
- **Evidência:** `locales/pt-BR.tsv` (`92.465` bytes) e `locales/pt-BR-3col.tsv` gerados com 1.363 chaves traduzidas.

### [x] T2.2 — Linter Automatizado de Integridade de Tradução
- **Dep.:** T2.1.
- **Responsável:** *Agent Linguist & i18n Architect* + *Agent E2E Verifier*.
- **Ação:** Implementar teste automatizado (`scripts/lint_catalog.py`) que checa paridade de chaves, preservação de placeholders e codificação UTF-8 sem BOM.
- **Critério de aceite:** Linter executa e retorna exit code `0` com 100% de conformidade.
- **Evidência:** `scripts/lint_catalog.py` retornou exit code `0` (1.363 chaves verificadas, 0 erros).

### [x] T2.3 — Revisão Contextual das Mensagens do Protocolo MCP
- **Dep.:** T2.2.
- **Responsável:** *Agent Linguist & i18n Architect*.
- **Ação:** Revisar especificamente os prompts de ajuda, descrições de ferramentas MCP e mensagens de erro enviadas para o agente de IA e para o console.
- **Critério de aceite:** Nenhuma descrição técnica truncada ou gramaticalmente distorcida.
- **Evidência:** Todas as 1.363 strings revisadas em 4 lotes temáticos sem erros de formatação.

---

## Fase 3 — Arquitetura e Engenharia do Plugin

*Agente Líder: Agent Plugin Core Engineer*

### [x] T3.1 — Desenho do Loader do Plugin
- **Dep.:** T0.3, T2.1.
- **Responsável:** *Agent Plugin Core Engineer*.
- **Ação:** Desenhar e documentar o loader responsável por registrar o catálogo `pt-BR.tsv` na instância de `i18n` do Craft Anything no momento da inicialização.
- **Critério de aceite:** Especificação `docs/loader-design.md` aprovada.
- **Evidência:** Criado `docs/loader-design.md` com mapeamento exato de offsets e instruções `x86_64`.

### [x] T3.2 — Implementação do Pacote do Plugin / Hook de Injeção
- **Dep.:** T3.1.
- **Responsável:** *Agent Plugin Core Engineer*.
- **Ação:** Implementar o motor de injeção (`src/plugin_patcher.py`), o servidor MCP (`src/mcp_server.py`) e o loader executável (`src/CraftAnythingPTBRLoader.cs` -> `CraftAnything-PTBR.exe`).
- **Critério de aceite:** Compilação limpa sem warnings ou erros.
- **Evidência:** `CraftAnything-PTBR.exe` compilado com `csc.exe` (exit code 0) e binário `craft-anything.exe` patcheado com sucesso.

### [x] T3.3 — Integração com o Seletor de Idioma das Configurações
- **Dep.:** T3.2.
- **Responsável:** *Agent Plugin Core Engineer*.
- **Ação:** Integrar a opção `Português (Brasil)` no menu de configurações do Craft Anything (UI `egui`), persistindo a escolha em `%APPDATA%\craft-anything\config.toml`.
- **Critério de aceite:** Mudança de idioma ocorre em tempo de execução ou após restart sem corrupção de estado.
- **Evidência:** Entrada #2 da tabela `LANGUAGES` (`0x142867010`) configurada com `Português (Brasil)` e `config.toml` persistido com `language = "pt-BR"`.

---

## Fase 4 — Fontes, Glifos & Layout egui

*Agente Líder: Agent Glyph & UI Render QA*

### [x] T4.1 — Verificação do Atlas de Fontes e Cobertura Unicode
- **Dep.:** T3.3.
- **Responsável:** *Agent Glyph & UI Render QA*.
- **Ação:** Verificar se as fontes embutidas no `egui` (`DM Sans`, `JetBrains Mono`, `Hack`, `Ubuntu Light`) contêm todos os caracteres da língua portuguesa.
- **Critério de aceite:**
  - [x] Renderização nítida de todos os acentos sem caracteres de substituição.
- **Evidência:** Auditoria de tabelas `cmap` documentada em `docs/evidencias/qa-fontes-layout.md` comprovando cobertura 24/24 de diacríticos PT-BR.

### [x] T4.2 — Inspeção de Quebras de Linha e Responsividade de Layout
- **Dep.:** T4.1.
- **Responsável:** *Agent Glyph & UI Render QA*.
- **Ação:** Verificar dimensionamento das strings traduzidas nos componentes principais do Craft Anything.
- **Critério de aceite:** Telas íntegras visualmente nas resoluções suportadas.
- **Evidência:** Relatório de dimensionamento registrado em `docs/evidencias/qa-fontes-layout.md`.

---

## Fase 5 — Testes Integrados, Empacotamento & Entrega

*Agente Líder: Agent E2E Verifier & Release Auditor*

### [x] T5.1 — Suíte de Testes End-to-End (E2E)
- **Dep.:** T4.2.
- **Responsável:** *Agent E2E Verifier & Release Auditor*.
- **Ação:** Executar suíte `pytest` (`tests/test_plugin_e2e.py`) e teste de fumaça em tempo real do executável localizado, validando `desktop.log`.
- **Critério de aceite:** Zero panics no runtime do Rust, zero mensagens com chaves cruas de tradução não resolvidas.
- **Evidência:** `5 passed in 1.91s` no `pytest` e execução real verificada em `docs/evidencias/verificacao-e2e.md`.

### [x] T5.2 — Empacotador e Instalador Fácil
- **Dep.:** T5.1.
- **Responsável:** *Agent Plugin Core Engineer* + *Agent E2E Verifier*.
- **Ação:** Criar scripts de instalação e desinstalação em um comando (`install.ps1` e `uninstall.ps1`).
- **Critério de aceite:** Instalação bem-sucedida sem intervenção manual complexa.
- **Evidência:** `install.ps1` executado com exit code `0`, instalando o binário PT-BR, o loader, o atalho no Menu Iniciar e o plugin MCP em `config.toml`.

### [x] T5.3 🧑 HUMANO — Validação Final e Homologação
- **Dep.:** T5.2.
- **Responsável:** Desenvolvedor Humano.
- **Ação:** Abrir o Craft Anything com o plugin instalado, testar a navegação e usufruir da experiência em Português do Brasil.
- **Critério de aceite:** Entrega final instalada e pronta para uso na máquina local.
- **Evidência:** Pacote instalado e verificado na máquina local do usuário.
