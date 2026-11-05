# AGENTS.md — craft-anything-ptbr

> Regras permanentes do agente e especificação do esquadrão multi-agente. Leia INTEIRO antes de qualquer tarefa.
> O plano de execução está em `ROADMAP.md`. Em caso de conflito entre os dois arquivos, este documento prevalece.

---

## 1. Missão e Escopo

Desenvolver e validar uma extensão/plugin de localização para o **Craft Anything** (ferramenta open-source em Rust da Storytold / ecossistema ArtCraft), habilitando suporte nativo completo ao idioma **Português do Brasil (PT-BR)** na interface gráfica (egui/eframe), nas mensagens do CLI e nas descrições de ferramentas do protocolo MCP.

### Dentro do Escopo
1. **Mapeamento e Extração de Strings:** Identificar todas as strings de UI, mensagens de log/status, diálogos de erro e metadados de inspeção do Craft Anything.
2. **Catálogo de Tradução PT-BR:** Criação do catálogo oficial de tradução no formato compatível com o ecossistema `craft-i18n` (TSV / catálogo estruturado com fallback para inglês).
3. **Mecanismo do Plugin/Extensão:** Implementar a carga do pacote de idiomas PT-BR de forma não invasiva (diretório de plugins/localização ou patch limpo de build), respeitando o ciclo de vida do Craft Anything.
4. **Suporte Tipográfico & Glyphs:** Garantir a cobertura completa de caracteres acentuados da língua portuguesa (`á, à, ã, â, é, ê, í, ó, ô, õ, ú, ç` e maiúsculas) no atlas de fontes do `egui`.
5. **Glossário Técnico Padronizado:** Termos de clean-room, engenharia reversa, build e inspeção traduzidos com precisão para desenvolvedores brasileiros.
6. **Automação de Verificação:** Scripts de validação contra strings ausentes (missing keys), corrupção de interpolação (`{0}`, `{path}`) e testes de renderização.

### Fora do Escopo (Não implementar nem propor)
- Alterações no algoritmo de inspeção clean-room ou nas heurísticas de análise de código do Craft Anything.
- Modificações na API externa do Claude Code ou adaptadores de LLM de terceiros.
- Traduções para outros idiomas além de PT-BR neste ciclo.
- Criação prematura de código do plugin antes da validação do roadmap e aprovação do usuário.

---

## 2. Esquadrão Multi-Agente (Arquitetura e Papéis)

Para executar o projeto de forma robusta e paralelizável, utilizaremos um esquadrão de 5 agentes especializados:

```
┌──────────────────────────────────────────────────────────┐
│             AGENT ORCHESTRATOR / SUPERVISOR              │
└────────────┬─────────────┬─────────────┬─────────────────┘
             │             │             │
    ┌────────▼───────┐     │     ┌───────▼────────┐
    │ 1. INSPECTOR   │     │     │ 3. PLUGIN CORE │
    │    & CODEBASE  │     │     │    ENGINEER    │
    └────────┬───────┘     │     └───────┬────────┘
             │             │             │
    ┌────────▼───────┐     │     ┌───────▼────────┐
    │ 2. LINGUIST    │     │     │ 4. GLYPH & UI  │
    │    & i18n ARCH │     │     │    RENDER QA   │
    └────────┬───────┘     │     └───────┬────────┘
             │             │             │
             └─────────────┼─────────────┘
                           │
                  ┌────────▼────────┐
                  │ 5. E2E VERIFIER │
                  │    & AUDITOR    │
                  └─────────────────┘
```

### 1. `Agent Inspector & Codebase Analyst` (Descoberta & Engenharia Reversa)
- **Função:** Mapear a arquitetura interna do Craft Anything (`storytold/craft-anything`), localizando a integração com `craft-i18n`, as tabelas de símbolos do `egui`, o consumo de mensagens no CLI e as definições de MCP tools.
- **Entradas:** Código-fonte do Craft Anything, repositório `craft-i18n`, especificações de crates dependentes.
- **Saídas:** Lista exaustiva de pontos de texto (`catalog_keys.json`), mapa de arquivos que manipulam strings e pontos de ancoragem para plugins.
- **Ferramentas:** Leitura estática de código, regex de extração de macros (`t!()`, `tr!()`), analisador AST de Rust.

### 2. `Agent Linguist & i18n Architect` (Linguista & Arquiteto de Catálogos)
- **Função:** Construir o catálogo oficial de tradução `pt-BR.tsv` (ou JSON equivalente), mantendo consistência terminológica, tratando pluralizações e respeitando placeholders de formatação.
- **Entradas:** `catalog_keys.json`, glossário oficial de termos técnicos.
- **Saídas:** Arquivo de catálogo `locales/pt-BR.tsv`, relatório de paridade de chaves (100% de paridade com `en-US`), documentação do glossário.
- **Diretriz inviolável:** Nunca quebrar marcadores de interpolação (`{0}`, `{name}`, `%s`).

### 3. `Agent Plugin Core Engineer` (Engenheiro de Runtime & Extensibilidade)
- **Função:** Projetar e implementar o mecanismo de carregamento da tradução (plugin de runtime em `plugins/pt-br` ou injeção de catálogo via `craft-i18n`).
- **Entradas:** Arquitetura mapeada pelo Agent 1, catálogo gerado pelo Agent 2.
- **Saídas:** Módulo/crate do plugin de idioma, hook de inicialização do Craft Anything, suporte à seleção de idioma nas configurações (Settings/Preferences).
- **Ferramentas:** Rust (Cargo, crates dynamic/static linking), manipulação de arquivos de configuração (TOML/JSON).

### 4. `Agent Glyph & UI Render QA` (Especialista em Fontes & Layout egui)
- **Função:** Garantir a fidelidade visual da interface egui em português.
- **Entradas:** Binário/interface executada com o catálogo PT-BR ativo.
- **Saídas:** Relatório de inspeção de layout (detecção de quebras de linha indesejadas, truncamento de botões) e configuração de atlas de fontes (`egui::FontDefinitions`) garantindo suporte aos diacríticos PT-BR sem glifos ausentes (`` ou retângulos vazios).

### 5. `Agent E2E Verifier & Release Auditor` (Auditor de Qualidade e Entrega)
- **Função:** Validação holística de ponta a ponta, testes de regressão, persistência de preferências de idioma e empacotamento final.
- **Entradas:** Produto integrado (Craft Anything + Plugin PT-BR).
- **Saídas:** Relatório de testes automatizados, checklist de release, pacote de distribuição (zip/installer) e manual de instalação do usuário.

---

## 3. Decisões Arquiteturais Fechadas

| Tema | Decisão | Justificativa |
|---|---|---|
| **Alvo Principal** | Craft Anything (`storytold/craft-anything`) | Motor de engenharia reversa clean-room open-source em Rust |
| **Framework de UI** | `egui` / `eframe` (Rust) | Interface nativa utilizada pela Storytold nos apps da suíte Craft |
| **Padrão de i18n** | Padrão `craft-i18n` (TSV / UTF-8) | Mantém total interoperabilidade com os demais apps do ecossistema Craft |
| **Encoding** | **UTF-8 estrito sem BOM** | Imprescindível para acentuação correta no compilador Rust e atlas de texto do egui |
| **Formato do Catálogo** | Tab-Separated Values (`.tsv`) com colunas `key`, `en`, `pt-BR` | Compatibilidade nativa com os scripts de CI e build do `craft-i18n` |
| **Estratégia de Fallback** | `pt-BR` ➔ `en` (Inglês padrão) | Chaves não traduzidas ou novas em updates futuros nunca causarão crash ou texto vazio |
| **Persistência de Idioma** | Configuração do usuário (`settings.toml` / `craft-anything.json`) | Manter o idioma selecionado após reiniciar o aplicativo |
| **Terminologia Técnica** | Híbrida / Contextual | Termos amplamente adotados na comunidade dev (como *Clean Room*, *Build*, *Diff*, *CLI*, *MCP*) são mantidos ou elucidados, evitando traduções forçadas |

---

## 4. Glossário Terminológico Oficial (PT-BR)

Para manter coesão entre todos os agentes e telas do software:

| Termo Original (EN) | Tradução Adotada (PT-BR) | Contexto / Nota |
|---|---|---|
| **Study** | Estudar / Analisar | Etapa de análise do software original |
| **Build** | Construir / Gerar | Etapa onde o agente de IA gera o novo código |
| **Check** | Verificar / Comparar | Comparação e self-tests contra o original |
| **Ready** | Concluído / Pronto | Validação final do projeto |
| **Clean Room** | Sala Limpa (Clean Room) | Preservar termo técnico com elucidação contextual |
| **Deep Mode** | Modo Aprofundado (Deep Mode) | Modo com permissão de inspeção interna |
| **Inspection Tool** | Ferramenta de Inspeção | Ferramentas CLI/MCP que extraem evidências |
| **Discrepancy / Diff** | Divergência / Diferença | Pixel diff ou divergência de comportamento |
| **Settings / Preferences** | Configurações | Painel de ajustes do Craft Anything |
| **Tool Calling / MCP** | Chamada de Ferramenta / MCP | Protocolo de contexto e ferramentas para IA |

---

## 5. Regras Invioláveis do Projeto

1. **R1. Não inventar chaves nem modificar identificadores:** As chaves de localização (`key`) são sagradas e referenciadas no código Rust. Apenas o valor da coluna `pt-BR` pode ser editado.
2. **R2. Preservação de Placeholders:** Placeholders como `{path}`, `{count}`, `{0}`, `%d`, etc., devem ser mantidos idênticos na string traduzida, sob pena de erro em tempo de formatação (`format!()`).
3. **R3. UTF-8 Obrigatório:** Qualquer arquivo de localização, script ou código Rust deve ser salvo em UTF-8 puro. Ocorrência de caracteres corrompidos (`Ã§`, ``) reprova a tarefa imediatamente.
4. **R4. Zero Impacto no Core:** O plugin não deve desestabilizar ou causar panic em builds padrão do Craft Anything. Se o arquivo do plugin estiver corrompido ou ausente, a aplicação deve subir em inglês normalmente com um aviso no log.
5. **R5. Separação de Fases:** Nenhuma linha de código do plugin deve ser produzida antes que o catálogo e o protocolo de carregamento estejam detalhados e aprovados.
6. **R6. Economia de Contexto:** Agentes trabalham com escopo estrito por tarefa (T0.x, T1.x, etc.), registrando evidências concisas e commitando alterações atômicas.

---

## 6. Protocolo de Comunicação e Handoff entre Agentes

1. Cada agente atua apenas nas tarefas onde está designado como `Líder`.
2. Ao concluir uma etapa, o agente gera um **Artefato de Handoff** padronizado (ex: `specs/discovery.json`, `locales/pt-BR.tsv`, `tests/report.md`).
3. O próximo agente na cadeia de dependências só inicia após validar o checklist de entrada.
4. Qualquer ambiguidade ou inconsistência estrutural deve ser escalada ao desenvolvedor humano antes de qualquer suposição.
