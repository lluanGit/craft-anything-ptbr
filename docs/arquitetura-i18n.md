# Arquitetura de Internacionalização (i18n) — Craft Anything v0.3.0

> Documento técnico de engenharia reversa gerado pelo **Agent Inspector & Codebase Analyst** (`T0.2`).
> Alvo analisado: `C:\Program Files\Craft Anything\craft-anything.exe` (v0.3.0, 99.569.024 bytes, PE32+ x86_64) e `%LOCALAPPDATA%\Programs\ArtCraft\Launcher\artcraft-launcher.exe`.

---

## 1. Visão Geral da Engine `i18n.rs`

O **Craft Anything v0.3.0** utiliza um módulo interno compilado em Rust (`crates/craft-anything/src/i18n.rs`, referenciado nos símbolos de pânico em `FileOff = 42360040`, `RVA = 0x028670E8`) que embute catálogos TSV estáticos diretamente na seção `.rdata` do executável PE32+.

### 1.1 Mapa de Seções Relevantes do Binário (`craft-anything.exe`)
- **`ImageBase`**: `0x140000000`
- **`.text`**: `RVA = 0x00001000`, `VSize = 0x026CF7D0`, `RawPtr = 0x00000400`, `RawSize = 0x026CF800`
- **`.rdata`**: `RVA = 0x026D1000`, `VSize = 0x036B9294`, `RawPtr = 0x026CFC00 (40.696.832)`, `RawSize = 0x036B9400`
- **`.data`**: `RVA = 0x05D8B000`, `VSize = 0x00003BE8`, `RawPtr = 0x05D89000 (98.078.720)`, `RawSize = 0x00001A00`
- **`.pdata`**: `RVA = 0x05D8F000`, `VSize = 0x0013A928`, `RawPtr = 0x05D8AA00 (98.085.376)`, `RawSize = 0x0013AA00`

---

## 2. Tabela Estática de Idiomas (`LANGUAGES`)

Na seção `.rdata`, no endereço **`FileOff = 42359728` (`RVA = 0x02866FB0`, `VA = 0x142866FB0`)**, reside um array estático de **5 entradas de 48 bytes (`0x30` bytes) cada** (`[LanguageSpec; 5]`):

```rust
#[repr(C)]
struct LanguageSpec {
    code_ptr: *const u8,      // +0x00
    code_len: usize,          // +0x08
    name_ptr: *const u8,      // +0x10
    name_len: usize,          // +0x18
    catalog_ptr: *const u8,   // +0x20
    catalog_len: usize,       // +0x28
}
```

### Entradas Originais Mapeadas:

| Índice | File Offset | RVA | `code` (`ptr`, `len`) | `name` (`ptr`, `len`) | `catalog` (`FileOff`, `VA`, `len`) | Total de Chaves |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | `42359728` | `0x02866FB0` | `"en"` (`0x1427F1FE0`, `2`) | `"English"` (`0x14281DA2C`, `7`) | `0x1` (`len = 0`, identidade em inglês) | 1.363 (chaves diretas) |
| **1** | `42359776` | `0x02866FE0` | `"fr"` (`0x14281DA33`, `2`) | `"Français"` (`0x14281DA35`, `9`) | `FileOff = 42059326` (`0x14281DA3E`, `63.583` B) | 831 |
| **2** | `42359824` | `0x02867010` | `"ja"` (`0x14282D29D`, `2`) | `"日本語"` (`0x14282D29F`, `9`) | `FileOff = 42122920` (`0x14282D2A8`, `69.169` B) | 831 |
| **3** | `42359872` | `0x02867040` | `"zh-hans"` (`0x14281DA18`, `7`) | `"简体中文"` (`0x14283E0D9`, `12`) | `FileOff = 42192101` (`0x14283E0E5`, `83.216` B) | 1.360 |
| **4** | `42359920` | `0x02867070` | `"zh-hant"` (`0x14281DA1F`, `7`) | `"繁體中文"` (`0x1428525F5`, `12`) | `FileOff = 42275329` (`0x142852601`, `84.396` B) | 1.360 |

> **Observação Crítica:** Os catálogos `zh-hans` (1.360 chaves) e `zh-hant` (1.360 chaves) contêm praticamente a totalidade das strings da versão v0.3.0, enquanto `fr` e `ja` contêm 831 chaves (com 3 chaves adicionais específicas). A união dos 4 catálogos embutidos totaliza **1.363 chaves únicas**.

---

## 3. Funções Core de Resolução e Renderização de Idioma

A análise de referências cruzadas (`RIP-relative LEA/MOV`) e descompilação via `.pdata` identificou as **6 funções** que controlam todo o ciclo de vida de i18n no binário:

1. **`i18n::resolve_language` (`VA = 0x1415A10C0`, `RVA = 0x015A10C0..0x015A1A5F`)**
   - Recebe uma tag de idioma (vinda de `config.toml` ou da API do Windows/variáveis de ambiente quando `language = ""`).
   - Normaliza para minúsculas, converte `_` em `-` e resolve tags BCP-47 para um dos códigos suportados.
   - Se a string for vazia (`""`), consulta o locale do sistema operacional.

2. **`i18n::set_language` (`VA = 0x1415A00E0`, `RVA = 0x015A00E0..0x015A0CC5`)**
   - Normaliza a tag chamando `i18n::resolve_language`.
   - Compara o código resolvido com as entradas da tabela `0x142866FB0`.
   - Lê o slice `(catalog_ptr, catalog_len)` em `entry + 0x20` e `entry + 0x28`.
   - Faz o parse linha a linha (`\n`), ignorando linhas vazias ou iniciadas por `#`, separa no primeiro `\t` (`key\tvalue`), converte sequências literais `\n` (2 bytes: `0x5C 0x6E`) em quebras de linha reais (`0x0A`) e popula o `RwLock<HashMap<&'static str, String>>` global situado em **`RVA = 0x05D8B210`** (`VA = 0x145D8B210`).

3. **`i18n::tr` (`VA = 0x1415A1BA0`, `RVA = 0x015A1BA0..0x015A1E85`)**
   - **532 pontos de chamada** diretos na seção `.text`.
   - Adquire lock de leitura no `RwLock` em `0x145D8B210`.
   - Busca a chave `key: &str` no `HashMap` (usando SipHash-1-3 com chave inicializada).
   - Se encontrar a chave traduzida, retorna `String` com a tradução; caso contrário (ou se o idioma ativo for `"en"` com mapa vazio), retorna a própria chave original em inglês como fallback seguro!

4. **`i18n::tr_fmt` (`VA = 0x1415A1F90`, `RVA = 0x015A1F90..0x015A25CA`)**
   - **96 pontos de chamada** diretos na seção `.text`.
   - Resolve a tradução base via `i18n::tr(key)` e substitui todos os placeholders nomeados `{(arg_name)}` pelos valores passados no slice `&[(&str, &str)]`.

5. **`ui::settings::render_language_header` (`VA = 0x141489690`, `RVA = 0x01489690..0x01489C5D`)**
   - Renderiza o seletor `ComboBox` de idioma na aba de Configurações (`Settings -> Language`), exibindo `"System ({name})"` quando `config.language` está vazio ou o `name` do idioma selecionado na tabela `0x142866FB0`.

6. **`ui::settings::render_language_popup` (`VA = 0x1414BD070`, `RVA = 0x014BD070..0x014BD999`)**
   - Itera sobre as 5 entradas da tabela `0x142866FB0` (offset `0x00` até `0xF0` com passo `0x30`), renderizando cada opção selecionável no menu dropdown e persistindo a escolha.

---

## 4. Persistência de Configuração e Ecossistema

1. **Craft Anything (`config.toml`)**:
   - Caminho: `%APPDATA%\craft-anything\config.toml`
   - Chave de idioma na raiz do arquivo:
     ```toml
     language = "pt-BR"
     ```
   - Chave de plugins MCP:
     ```toml
     [[plugins.mcp]]
     name = "craft-anything-ptbr"
     transport = "stdio"
     command = "..."
     args = [...]
     enabled = true
     ```
2. **Estado da Janela (`app.ron`)**:
   - `%APPDATA%\ai.storyteller.craft-anything\data\app.ron`
3. **ArtCraft Launcher (`app.ron`)**:
   - `%APPDATA%\ai.storyteller.artcraft-launcher\data\app.ron`
   - Já possui suporte nativo e está configurado com `language:"pt-BR"`.

---

## 5. Formato Exato dos Catálogos Embutidos (`.tsv`)

Os catálogos embutidos na seção `.rdata` seguem estritamente o formato de **2 colunas separadas por TAB (`\t`)**:
- Comentários iniciam com `#` no começo da linha.
- Formato de linha: `<key in English>\t<translated string in UTF-8>\n`
- Quebras de linha dentro de um texto de UI são representadas pela sequência literal de 2 caracteres `\n` (`0x5C 0x6E`) tanto na chave quanto na tradução.
- Placeholders dinâmicos usam chaves `{...}`, como `{name}`, `{n}`, `{count}`, `{path}`, `{}`, `${c:.2}`, etc., e são substituídos em tempo de execução por `i18n::tr_fmt` ou formatadores de string.
