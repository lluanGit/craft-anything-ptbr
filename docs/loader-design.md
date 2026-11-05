# Especificação do Loader e Injetor do Plugin PT-BR (`T3.1`)

> Documento de engenharia elaborado pelo **Agent Plugin Core Engineer** (`T3.1`).

---

## 1. Objetivo do Loader e Motor de Injeção

Garantir que o executável local do **Craft Anything v0.3.0** (`craft-anything.exe`) reconheça nativamente o idioma **Português (Brasil) (`pt-BR` / `pt`)**, carregue todas as **1.363 chaves traduzidas** na memória em tempo de inicialização (`i18n::set_language`) e exiba **`Português (Brasil)`** no seletor de idiomas de `Configurações -> Idioma` (`Settings -> Language`).

---

## 2. Mapeamento Exato de Memória e Instruções (`x86_64`)

A descompilação das funções de `i18n.rs` revelou que o compilador Rust gerou comparações inline de 16 bits (`cmp word ptr [reg], imm16`) para os idiomas de 2 caracteres (`"en"`, `"fr"`, `"ja"`):

### 2.1 Entrada na Tabela `LANGUAGES` (`VA = 0x142867010`, `FileOff = 42359824`)
Na tabela `LANGUAGES` (`[LanguageSpec; 5]` em `0x142866FB0`), a Entrada #2 (`0x142867010`, originalmente `"ja"`) possui código de 2 bytes (`len = 2`), o que permite substituir a comparação imediata de 16 bits `0x616A` (`"ja"`) por `0x7470` (`"pt"`) em todas as funções do binário sem alterar o tamanho de nenhuma instrução!

Além disso, quando o sistema operacional Windows está em `pt-BR` (`"pt-BR"` normalizado para `"pt-br"`), `i18n::resolve_language` (`0x1415A10C0`) divide a tag no caractere `'-'` (`0x2D`) e compara o prefixo primário de 2 bytes (`"pt"`) na segunda passagem (`VA = 0x1415A1781`)! Isso significa que **tanto `language = "pt"` quanto `language = "pt-BR"`, `language = "pt_BR"` ou `language = ""` (Automático do Sistema no Windows PT-BR) resolvem automaticamente para a entrada `Português (Brasil)`!**

### 2.2 Pontos de Patch no Código (`.text`)
Existem exatamente **4 instruções `cmp word ptr ..., 0x616A` (`"ja"`)** em todo o binário:

| Função | VA | RVA | File Offset | Bytes Originais (`"ja"`) | Bytes Patcheados (`"pt"`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `i18n::resolve_language` (busca exata 2 chars) | `0x1415A150F` | `0x015A150F` | `0x015A090F` (`22677775`) | `66 41 81 3F 6A 61` | `66 41 81 3F 70 74` |
| `i18n::resolve_language` (prefixo BCP-47 ex: `pt-BR` -> `pt`) | `0x1415A177D` | `0x015A177D` | `0x015A0B7D` (`22678397`) | `66 41 81 3F 6A 61` | `66 41 81 3F 70 74` |
| `i18n::set_language` (carga do catálogo TSV) | `0x1415A0187` | `0x015A0187` | `0x0159F587` (`22672775`) | `66 81 38 6A 61` | `66 81 38 70 74` |
| `ui::settings::render_language_header` (ComboBox) | `0x1414899EF` | `0x014899EF` | `0x01488DEF` (`21532143`) | `66 81 39 6A 61` | `66 81 39 70 74` |

### 2.3 Alocação do Catálogo `pt-BR.tsv` e Metadados na Seção `.rdata`
- O slot original do catálogo `"ja"` (`FileOff = 42122920`, `VA = 0x14282D2A8`) tem `69.169` bytes, enquanto os slots contíguos `"zh-hans"` + `"zh-hant"` (`FileOff = 42192101..42359725`, `VA = 0x14283E0E5`) têm `167.612` bytes.
- Porém, podemos manter **todos os outros idiomas funcionando** ou usar uma região livre/compactada! Vamos verificar:
  - Se armazenarmos a string `"pt"` (2 bytes) no lugar de `"ja"` em `FileOff = 42122909` (`VA = 0x14282D29D`),
  - E armazenarmos `"Português (Brasil)"` (19 bytes em UTF-8: `50 6F 72 74 75 67 75 C3 AA 73 20 28 42 72 61 73 69 6C 29`) no início do buffer em `FileOff = 42122920` (`VA = 0x14282D2A8`),
  - E logo após (`FileOff = 42122944`, `VA = 0x14282D2C0`), se o catálogo `pt-BR.tsv` tiver até `69.145` bytes, ele cabe inteiramente dentro do próprio slot `"ja"` sem tocar em `"fr"`, `"zh-hans"` ou `"zh-hant"`!
  - E se o catálogo `pt-BR.tsv` completo tiver `92.465` bytes (todas as 1.363 chaves sem comentários extras = `92.345` bytes), podemos:
    - **Opção A**: Usar o espaço contíguo de `zh-hant` (`84.396` bytes) + final de `ja`/`zh-hans`, OU
    - **Opção B (Zero perda de chaves e máxima compatibilidade)**: Adicionar uma seção PE dedicada `.i18n` ao final do binário PE32+ (ou usar o espaço de padding/seção `.rdata` / `zh-hant`) para armazenar os `92.465` bytes completos de `pt-BR.tsv`!
    - Mais ainda: na região `FileOff = 42122920..42359725` (`ja` + `zh-hans` + `zh-hant`), existem `236.805` bytes dedicados a catálogos TSV. Se colocarmos `"Português (Brasil)"` (19 bytes) + `pt-BR.tsv` (`92.465` bytes) no slot `ja` + parte de `zh-hant` (ou se compactarmos `zh-hant` / apontarmos `zh-hant` para `zh-hans`), **todas as 5 entradas da tabela `LANGUAGES` permanecem 100% válidas e funcionais**, com `Português (Brasil)` contendo todas as **1.363 chaves**!

---

## 3. Tratamento de Assinatura PE (Authenticode) e Checksum

Binários Windows assinados com Authenticode possuem um bloco `IMAGE_DIRECTORY_ENTRY_SECURITY` (DataDirectory índice 4). Quando qualquer byte do binário é modificado para injetar um plugin/catálogo de localização, o Windows pode exibir erro se o ponteiro para o certificado antigo permanecer no cabeçalho PE.
Portanto, o `plugin_patcher.py`:
1. Faz backup integral do executável original (`craft-anything.exe.bak`) e verifica o hash SHA-256.
2. Aplica os patches da tabela `LANGUAGES`, das 4 instruções `cmp` e do catálogo `pt-BR.tsv`.
3. Zera `DataDirectory[IMAGE_DIRECTORY_ENTRY_SECURITY]` (`VirtualAddress = 0`, `Size = 0`) no OptionalHeader PE32+.
4. Configura `%APPDATA%\craft-anything\config.toml` com `language = "pt-BR"`.
