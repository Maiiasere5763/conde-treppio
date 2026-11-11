# Conde: Banco de Dados Filológico e Glotopoético do Idioma Tréppio (Era Clássica V8.1 ao Neo-Trepiano)

Este repositório centraliza a documentação normativa, o léxico canônico, o laboratório de evolução naturalista (*sandbox*) e a simulação diacrônica de 1.500 anos da língua artística **Tréppio** (**Trepiano Clássico V8.1** e **Evolução da Era Antiga para a Clássica no cenário de *Ecos de Uma Vida Perdida***).

## Estrutura do Repositório (`D:\Conde_Treppio`)

- [`SKILL.md`](./SKILL.md): Diretrizes operacionais da persona e assistente filológico **Conde**.
- [`dicionario_formas_expandidas.json`](./dicionario_formas_expandidas.json): Banco de dados lexicográfico estruturado (JSON) com **178.879 formas flexionadas e derivadas**, contendo todas as classes gramaticais (1511 substantivos, 1288 verbos da matriz quadripartida, 326 adjetivos, 388 advérbios, pronomes, numerais, partículas e os 8 capítulos canônicos da GNLT).
- [`gramatica_normativa_base.md`](./gramatica_normativa_base.md): Gramática Normativa do Trepiano Clássico (Fonologia, Matriz Verbal Quadripartida, Sintaxe V2, Declinações e Posposições).
- [`treppio_base.md`](./treppio_base.md): Compêndio Gramatical, Filológico e Lexicográfico Completo.
- [`adendo_edicao_unificada_v8_1.md`](./adendo_edicao_unificada_v8_1.md): Edição Unificada V8.1 (Chancelaria Imperial, Doutrina das Quatro Valências e Léxico Consolidado).
- [`caderno_treppio_notebook.md`](./caderno_treppio_notebook.md): Metadados e referências do Caderno Tréppio no Google Gemini Notebook.
- [`dist/`](./dist/): Pacotes compilados de distribuição multiplataforma:
  - `Codice_Treppio_Conde.apk`: Aplicativo Android nativo (100% offline com GNLT e Diálogos de Ecos).
  - `Codice_Treppio_Conde.exe`: Launcher executável para Windows (.NET com recursos e servidor embutidos).
  - `Codice_Treppio_Portatil.html`: Edição web portátil autocontida em arquivo único.
- [`docs/`](./docs/): Portal web público e Progressive Web App (PWA) hospedado no GitHub Pages ([https://maiiasere5763.github.io/conde-treppio/](https://maiiasere5763.github.io/conde-treppio/)).
- [`sandbox/`](./sandbox/): Ambiente de experimentação filológica, simulação diacrônica e expansão lexical naturalista:
  - [`sandbox/simulacao_diacronica_1500_anos.md`](./sandbox/simulacao_diacronica_1500_anos.md): Tratado Filológico da Evolução de 1.500 Anos (Do Tréppio Imperial ao Neo-Trepiano de *Ecos de Uma Vida Perdida*, com as 5 Leis Fonéticas Diacrônicas e a secularização da cópula).
  - [`sandbox/dialogos_praticos_dia_a_dia_treppio.md`](./sandbox/dialogos_praticos_dia_a_dia_treppio.md): Guia de Diálogos Práticos e Conversação Cotidiana (O cão dourado na neve, a estalagem acolhedora, o ferreiro e a noite de inverno).
  - [`sandbox/dicionario_exaustivo/`](./sandbox/dicionario_exaustivo/): Gerador filológico e compilação do léxico com todas as terminações morfológicas.
  - [`sandbox/analise_e_expansao_sandbox.py`](./sandbox/analise_e_expansao_sandbox.py): Validador fonotático e gerador morfológico da Matriz Quadripartida.
  - [`sandbox/relatorio_conde_sandbox_treppio.md`](./sandbox/relatorio_conde_sandbox_treppio.md): Relatório de Análise Filológica e Expansão Naturalista.
  - [`sandbox/launcher_exe/`](./sandbox/launcher_exe/): Código-fonte C# e rotina de compilação do executável Windows.
  - [`sandbox/android_apk/`](./sandbox/android_apk/): Projeto Android nativo em Java com Gradle e WebView de alto desempenho.
- [`sync_conde.ps1`](./sync_conde.ps1): Script de sincronização automática com OneDrive, Google Drive e GitHub.

## Como Sincronizar Manualmente ou Automaticamente

Execute no PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File "D:\Conde_Treppio\sync_conde.ps1"
```
