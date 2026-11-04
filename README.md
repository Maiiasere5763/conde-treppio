# Conde: Banco de Dados Filológico e Glotopoético do Idioma Tréppio (Era Clássica V8.1)

Este repositório centraliza a documentação normativa, o léxico canônico e o laboratório de evolução naturalista (*sandbox*) da língua artística **Tréppio** (**Trepiano Clássico**, V8.1).

## Estrutura do Repositório (`D:\Conde_Treppio`)

- [`SKILL.md`](./SKILL.md): Diretrizes operacionais da persona e assistente filológico **Conde**.
- [`gramatica_normativa_base.md`](./gramatica_normativa_base.md): Gramática Normativa do Trepiano Clássico (Fonologia, Matriz Verbal Quadripartida, Sintaxe V2, Declinações e Posposições).
- [`treppio_base.md`](./treppio_base.md): Compêndio Gramatical, Filológico e Lexicográfico Completo.
- [`adendo_edicao_unificada_v8_1.md`](./adendo_edicao_unificada_v8_1.md): Edição Unificada V8.1 (Chancelaria Imperial, Doutrina das Quatro Valências e Léxico Consolidado).
- [`caderno_treppio_notebook.md`](./caderno_treppio_notebook.md): Metadados e referências do Caderno Tréppio no Google Gemini Notebook.
- [`sandbox/`](./sandbox/): Ambiente de experimentação filológica e expansão lexical naturalista:
  - [`sandbox/analise_e_expansao_sandbox.py`](./sandbox/analise_e_expansao_sandbox.py): Validador fonotático e gerador morfológico da Matriz Quadripartida.
  - [`sandbox/relatorio_conde_sandbox_treppio.md`](./sandbox/relatorio_conde_sandbox_treppio.md): Relatório de Análise Filológica e Expansão Naturalista (~60 novos vocábulos, Lei da Haplologia Dental, Grau Superlativo em `-n/-ni` e Advérbios Modais em `-vë`).
- [`sync_conde.ps1`](./sync_conde.ps1): Script de sincronização automática com OneDrive, Google Drive e GitHub.

## Como Sincronizar Manualmente ou Automaticamente

Execute no PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File "D:\Conde_Treppio\sync_conde.ps1"
```

