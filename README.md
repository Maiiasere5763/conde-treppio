# Conde: Banco de Dados Filológico e Glotopoético do Idioma Tréppio (Era Clássica V8.1)

Este repositório centraliza a documentação normativa, o léxico canônico e o laboratório de evolução naturalista (*sandbox*) da língua artística **Tréppio** (**Trepiano Clássico**, V8.1).

## Estrutura do Repositório (`D:\Conde_Treppio`)

- [`SKILL.md`](./SKILL.md): Diretrizes operacionais da persona e assistente filológico **Conde**.
- [`dicionario_formas_expandidas.json`](./dicionario_formas_expandidas.json): Banco de dados lexicográfico estruturado (JSON) com 37.769 formas flexionadas da língua tréppia, contendo todas as classes gramaticais (substantivos, adjetivos, advérbios, pronomes, numerais, partículas e a matriz verbal quadripartida) e variantes canônicas.
- [`gramatica_normativa_base.md`](./gramatica_normativa_base.md): Gramática Normativa do Trepiano Clássico (Fonologia, Matriz Verbal Quadripartida, Sintaxe V2, Declinações e Posposições).
- [`treppio_base.md`](./treppio_base.md): Compêndio Gramatical, Filológico e Lexicográfico Completo.
- [`adendo_edicao_unificada_v8_1.md`](./adendo_edicao_unificada_v8_1.md): Edição Unificada V8.1 (Chancelaria Imperial, Doutrina das Quatro Valências e Léxico Consolidado).
- [`caderno_treppio_notebook.md`](./caderno_treppio_notebook.md): Metadados e referências do Caderno Tréppio no Google Gemini Notebook.
- [`dist/`](./dist/): Pacotes compilados de distribuição multiplataforma:
  - `Codice_Treppio_Conde.apk`: Aplicativo Android nativo (100% offline).
  - `Codice_Treppio_Conde.exe`: Launcher executável para Windows (.NET).
  - `Codice_Treppio_Portatil.html`: Edição web portátil autocontida em arquivo único.
- [`docs/`](./docs/): Portal web público e Progressive Web App (PWA) hospedado no GitHub Pages ([https://maiiasere5763.github.io/conde-treppio/](https://maiiasere5763.github.io/conde-treppio/)).
- [`sandbox/`](./sandbox/): Ambiente de experimentação filológica e expansão lexical naturalista:
  - [`sandbox/dicionario_exaustivo/`](./sandbox/dicionario_exaustivo/): Gerador filológico e compilação do léxico com todas as terminações morfológicas.
  - [`sandbox/analise_e_expansao_sandbox.py`](./sandbox/analise_e_expansao_sandbox.py): Validador fonotático e gerador morfológico da Matriz Quadripartida.
  - [`sandbox/relatorio_conde_sandbox_treppio.md`](./sandbox/relatorio_conde_sandbox_treppio.md): Relatório de Análise Filológica e Expansão Naturalista (~60 novos vocábulos, Lei da Haplologia Dental, Grau Superlativo em `-n/-ni` e Advérbios Modais em `-vë`).
  - [`sandbox/launcher_exe/`](./sandbox/launcher_exe/): Código-fonte C# e rotina de compilação do executável Windows.
  - [`sandbox/android_apk/`](./sandbox/android_apk/): Projeto Android nativo em Java com Gradle e WebView de alto desempenho.
- [`sync_conde.ps1`](./sync_conde.ps1): Script de sincronização automática com OneDrive, Google Drive e GitHub.

## Como Sincronizar Manualmente ou Automaticamente

Execute no PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File "D:\Conde_Treppio\sync_conde.ps1"
```
