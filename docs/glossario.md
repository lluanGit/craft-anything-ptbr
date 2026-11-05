# Glossário Técnico Oficial PT-BR — Craft Anything v0.3.0

> Documento consolidado pelo **Agent Linguist & i18n Architect** (`T1.2`).
> Define a padronização terminológica para as 1.363 chaves de interface gráfica (`egui`), descrições de ferramentas MCP, prompts de agentes e logs de auditoria.

---

## 1. Princípios de Tradução
1. **Clareza e Naturalidade:** O Craft Anything possui dois modos de linguagem na UI (`Simple` — linguagem cotidiana para iniciantes; e `Advanced` — bancada técnica). As traduções preservam o tom acolhedor e claro nas explicações simples e o rigor técnico da engenharia de software nas ferramentas avançadas.
2. **Integridade de Placeholders:** Todos os marcadores dinâmicos (`{name}`, `{n}`, `{what}`, `{}`, `{c:.2}`, `{spent:.2}`, `{budget:.2}`) são intocáveis.
3. **Concisão Visual (`egui`):** Botões e abas usam termos curtos para evitar truncamento ou quebra de layout.

---

## 2. Tabela de Terminologia Padronizada

| Termo Original (EN) | Tradução Oficial (PT-BR) | Contexto / Regra de Uso |
| :--- | :--- | :--- |
| **Study / Studying** | **Estudar / Estudando** | Etapa de análise e inspeção de um alvo. |
| **Build / Building** | **Construir / Construindo** | Ação de construir/reconstruir; como substantivo (`a build`, `pinned builds`), **compilação / versão construída** ou **construção**. |
| **Builder** | **Construtor** | O agente de código responsável por construir o projeto. |
| **Brain / AI brain** | **Cérebro de IA / IA** | Modelo de linguagem configurado para responder perguntas. |
| **Check / Checking** | **Verificar / Verificando** | Etapa de verificação visual e funcional contra o original. |
| **Ready** | **Pronto** | Estado de conclusão de projeto ou ferramenta. |
| **Clean room (mode)** | **Sala limpa (modo Sala limpa)** | Análise caixa-preta sem leitura de código-fonte interno. |
| **Deep (mode)** | **Modo Profundo / Profundo** | Análise estática/dinâmica completa com descompiladores e Ghidra. |
| **Workbench** | **Bancada** | Ambiente técnico avançado (`Advanced` / `Workbench`). |
| **Evidence / Evidence ledger** | **Evidências / Registro de evidências** | Fatos verificados e salvos durante o estudo. |
| **Finding / Findings** | **Descoberta / Descobertas** | Item individual registrado no painel de evidências. |
| **Seen it** | **Visto diretamente** | Grau máximo de certeza (lido diretamente do arquivo, página ou captura). |
| **Worked it out** | **Deduzido** | Grau médio-alto de certeza (calculado passo a passo a partir do que foi visto). |
| **Best guess** | **Melhor palpite** | Grau heurístico de certeza (leitura razoável, mas não provada). |
| **Target / Targets** | **Alvo / Alvos** | Programa, jogo, app ou site sendo analisado. |
| **Pinned build / Pin** | **Construção fixada / Fixar** | Versão salva na barra lateral para abrir a qualquer momento. |
| **Frozen copy** | **Cópia congelada** | Cópia independente completa da construção. |
| **Light copy** | **Cópia leve** | Cópia que compartilha arquivos grandes e mídia com o projeto. |
| **Stand-in backend** | **Backend substituto** | Servidor simulado localmente para substituir APIs externas. |
| **Call graph** | **Grafo de chamadas** | Mapa de quais funções chamam quais outras funções. |
| **Control-flow graph** | **Grafo de fluxo de controle** | Mapa de caminhos de execução dentro de uma função. |
| **Cross-references** | **Referências cruzadas** | Locais do programa que referenciam ou chamam um item. |
| **Disassembly / Disassemble** | **Desmontagem / Desmontar** | Código de máquina em instruções assembly linha a linha. |
| **Decompile / Pseudo-C** | **Descompilar / Pseudo-C** | Código reconstruído próximo à linguagem C. |
| **Entry point** | **Ponto de entrada** | Primeira instrução executada quando o programa inicia. |
| **Sections / Segments** | **Seções / Segmentos** | Regiões do binário em disco ou na memória. |
| **Strings** | **Strings (Textos)** | Sequências de texto armazenadas dentro de um binário. |
| **Imports / Exports** | **Importações / Exportações** | Símbolos e funções importados ou exportados por um binário. |
| **Likeness** | **Semelhança** | Percentual de fidelidade visual entre o original e a reconstrução. |
| **Asset budget** | **Orçamento de recursos (assets)** | Limite de gasto com modelos 3D e imagens geradas via `fal.ai`. |
| **Command palette** | **Paleta de comandos** | Atalho `Ctrl/⌘ K` para executar ferramentas. |
| **Settings** | **Configurações** | Painel de preferências do aplicativo. |
| **Plugins** | **Plugins** | Extensões MCP ou componentes WebAssembly. |
