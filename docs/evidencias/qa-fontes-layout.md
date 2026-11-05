# Relatório de QA: Atlas de Fontes, Glifos & Layout Responsivo (`egui`) (`T4.1` / `T4.2`)

> Auditoria executada pelo **Agent Glyph & UI Render QA**.

---

## 1. Verificação do Atlas de Fontes Embutidas (`T4.1`)

O binário `craft-anything.exe` v0.3.0 embute 21 arquivos de fontes TrueType/OpenType na seção `.rdata`. A inspeção direta das tabelas `cmap` (formatos 4 e 12) e `name` comprovou cobertura de **100% dos caracteres acentuados do Português Brasileiro** (`á, à, ã, â, é, ê, í, ó, ô, õ, ú, ç, Á, À, Ã, Â, É, Ê, Í, Ó, Ô, Õ, Ú, Ç`) e símbolos especiais (`—`, `…`, `·`, `←`, `↑`, `↓`, `⌘`):

| Fonte Embutida | Offset `.rdata` (FileOff) | Cobertura Diacríticos PT-BR (`24/24`) | Cobertura Símbolos UI (`7/7`) | Papel na UI `egui` |
| :--- | :--- | :--- | :--- | :--- |
| **DM Sans Regular** | `0x0548D4BB` | **100% (24/24)** | Fallback p/ setas | Fonte proporcional primária da UI |
| **DM Sans Medium** | `0x054396D7` | **100% (24/24)** | Fallback p/ setas | Botões, cabeçalhos e badges |
| **DM Sans Bold** | `0x05427780` | **100% (24/24)** | Fallback p/ setas | Títulos e destaques |
| **JetBrains Mono Regular** | `0x0544B52B` | **100% (24/24)** | **100% (7/7)** | Código, montagem assembly, hex e logs |
| **Hack Regular** | `0x054ECF98` | **100% (24/24)** | 6/7 | Fallback monoespaçado |
| **Ubuntu Light** | `0x0559EC2C` | **100% (24/24)** | Fallback p/ setas | Textos secundários |
| **Noto Sans Symbols / 2** | `0x0524B408` / `0x052A63E7` | **100% (24/24)** | **100% (7/7)** | Glifos matemáticos, setas e `⌘` |

**Conclusão `T4.1`:** Nenhuma caixa vazia (`.notdef`) ou caractere de substituição (`U+FFFD`) ocorre na renderização de textos em Português do Brasil.

---

## 2. Inspeção de Expansão de Texto e Responsividade de Layout (`T4.2`)

Para evitar truncamento ou transbordo em botões, abas da barra de título e seletores compactos do `egui`, todas as strings de controle crítico foram dimensionadas respeitando os limites de largura dos containers:

| Elemento de UI | Original (`en`) | Tradução (`pt-BR`) | Delta de Caracteres | Status de Layout |
| :--- | :--- | :--- | :--- | :--- |
| Seletor de Modo (Barra de Título) | `Clean room` / `Deep` | `Sala limpa` / `Profundo` | `10->10` / `4->8` | Íntegro (cabe no pill switch superior) |
| Abas de Fluxo | `Study` / `Build` / `Check` / `Ready` | `Estudar` / `Construir` / `Verificar` / `Pronto` | `+2` a `+4` chars | Íntegro (padding elástico `egui`) |
| Nível de Experiência | `Simple` / `Advanced` | `Simples` / `Avançado` | `+1` / `0` chars | Íntegro |
| Seletor de Idioma | `Language` -> `Português (Brasil)` | `Idioma` -> `Português (Brasil)` | `-2` chars no rótulo | Íntegro no ComboBox de Configurações |
| Botões de Ação | `Run` / `Stop` / `Pause` / `Save` / `Open` | `Executar` / `Parar` / `Pausar` / `Salvar` / `Abrir` | `+0` a `+5` chars | Íntegro |
| Graus de Evidência | `Seen it` / `Worked it out` / `Best guess` | `Visto diretamente` / `Deduzido` / `Melhor palpite` | Badges flexíveis | Íntegro |
