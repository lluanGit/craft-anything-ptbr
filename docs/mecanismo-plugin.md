# Mecanismo do Plugin e Estratégia de Acoplamento — Craft Anything PT-BR

> Documento técnico de engenharia do **Agent Inspector & Codebase Analyst** + **Agent Plugin Core Engineer** (`T0.3`).

---

## 1. Análise das Superfícies de Extensão do Craft Anything v0.3.0

A inspeção completa dos binários `craft-anything.exe`, `craft-anything-cli.exe` e `artcraft-launcher.exe` revelou duas superfícies complementares:

1. **Superfície de Plugins MCP (`[[plugins.mcp]]` em `config.toml`)**:
   - O Craft Anything carrega servidores MCP declarados em `%APPDATA%\craft-anything\config.toml` (structs `PluginConfig` e `McpPluginConfig` em `crates/craft-anything/src/config.rs`).
   - Os plugins MCP fornecem ferramentas adicionais aos agentes de IA internos do Craft Anything, mas **não alteram a tabela estática `LANGUAGES`** compilada dentro da seção `.rdata` da interface gráfica `egui`.

2. **Superfície Nativa da Engine `i18n.rs` (Tabela Estática `0x142866FB0` em `.rdata`)**:
   - A função `i18n::set_language` (`0x1415A00E0`) lê exclusivamente os 5 registros da tabela estática `LANGUAGES` em `FileOff = 42359728` (`VA = 0x142866FB0`).
   - Os slots de catálogo `zh-hans` (`FileOff = 42192101`, `83.216` bytes) e `zh-hant` (`FileOff = 42275329`, `84.396` bytes) são contíguos na seção `.rdata`, somando **167.612 bytes contínuos** (`FileOff 42192101..42359725`).

---

## 2. Arquitetura Híbrida do Plugin `craft-anything-ptbr`

Para entregar uma experiência **100% localizada em Português do Brasil (`pt-BR`)** na instalação local do usuário — sem exigir o código-fonte privado do Craft Anything e funcionando tanto com quanto sem privilégios de Administrador — adotamos uma **Arquitetura de Plugin Híbrida em 3 Camadas**:

### Camada 1: Injetor de Catálogo Nativo (`src/plugin_patcher.py`)
Um motor de injeção binária determinístico, seguro e reversível que:
1. Lê o catálogo compilado `locales/pt-BR.tsv` (1.363 chaves traduzidas em UTF-8 puro).
2. Aloca o catálogo `pt-BR.tsv` na região de catálogos da seção `.rdata` (`FileOff = 42192101`, capacidade contígua de `167.612` bytes, muito superior aos ~92 KB do catálogo PT-BR completo).
3. Atualiza a entrada da tabela `LANGUAGES` (`0x142866FB0`) e a resolução de idioma em `i18n::resolve_language` (`0x1415A10C0`) e `i18n::set_language` (`0x1415A00E0`) para registrar nativamente:
   - Código: **`pt-BR`** (também aceitando `pt`, `pt-br`, `pt_BR` e detecção automática do Windows em Português!).
   - Nome de exibição no menu Settings -> Idioma: **`Português (Brasil)`**.
   - Ponteiro e tamanho exatos do catálogo `pt-BR.tsv` em `.rdata`.
4. Limpa o ponteiro do diretório de certificado Authenticode (`OptionalHeader.DataDirectory[4]`) e recalcula o `CheckSum` do cabeçalho PE32+, garantindo execução imediata no Windows 11 sem alerta de assinatura inválida.

### Camada 2: Launcher / Loader Nativo (`CraftAnything-PTBR.exe` + Integração ArtCraft)
1. O binário localizado é instalado em:
   - `%LOCALAPPDATA%\Programs\Craft Anything\craft-anything.exe` (diretório de usuário sem necessidade de UAC/Admin).
   - E, quando há permissão de escrita ou elevação opcional, diretamente em `C:\Program Files\Craft Anything\craft-anything.exe` (com backup automático `craft-anything.exe.bak`).
2. Um executável leve `CraftAnything-PTBR.exe` (compilado nativamente com `csc.exe` para Windows x64) garante que:
   - `%APPDATA%\craft-anything\config.toml` esteja sempre sincronizado com `language = "pt-BR"`.
   - Caso o Craft Anything seja atualizado pelo ArtCraft Launcher, o loader detecta a nova versão ou reaplica/inicia a instância PT-BR de forma transparente.
3. Registro automático em `HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\craft-anything.exe` e atalhos no Menu Iniciar do usuário e na Área de Trabalho.

### Camada 3: Servidor MCP do Plugin (`src/mcp_server.py`)
Registrado em `%APPDATA%\craft-anything\config.toml` sob `[[plugins.mcp]]` com `name = "craft-anything-ptbr"`, fornecendo via protocolo MCP (`stdio`, JSON-RPC 2.0):
- `ptbr_translate_key`: consulta instantânea da tradução oficial de qualquer chave de UI do Craft Anything.
- `ptbr_glossary_lookup`: consulta ao glossário técnico oficial PT-BR (Clean Room, Disassembly, Pixel Compare, etc.) para que os agentes de IA gerem relatórios e artefatos em português técnico consistente.
- `ptbr_plugin_status`: diagnóstico em tempo real do estado da localização PT-BR e cobertura do catálogo.

---

## 3. Vantagens da Decisão Arquitetural
- **Zero Fallback Faltante:** As 1.363 chaves são resolvidas nativamente por `i18n::tr` e `i18n::tr_fmt` em tempo de execução com custo zero de I/O.
- **Seletor de Idioma Funcional:** O menu `Configurações -> Idioma` exibe **`Português (Brasil)`** nativamente e permite alternar entre `English`, `Français`, `日本語`, `简体中文` e `Português (Brasil)`.
- **Instalação User-Space & System-Wide:** Funciona imediatamente na conta do usuário (`install.ps1`) sem bloquear por falta de privilégios em `C:\Program Files`, além de oferecer atualização in-place caso rodado como Administrador.
