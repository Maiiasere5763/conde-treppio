# Conde: Banco de Dados Filológico e Glotopoético do Idioma Tréppio (Era Clássica V8.4)

Este repositório centraliza a documentação normativa, o léxico canônico e o laboratório morfológico (*sandbox*) da língua artística **Tréppio** (**Trepiano Clássico V8.4**, utilizado em *Ecos de Uma Vida Perdida*).

## Estrutura do Repositório (`D:\Conde_Treppio`)

- [`SKILL.md`](./SKILL.md): Diretrizes operacionais da persona e assistente filológico **Conde**.
- [`dicionario_formas_expandidas.json`](./dicionario_formas_expandidas.json): Banco de dados lexicográfico estruturado (JSON) com **246.737 formas flexionadas e derivadas**, contendo todas as classes gramaticais (2109 substantivos, 1768 verbos da matriz quadripartida, 446 adjetivos, 1202 advérbios, pronomes, numerais, partículas e os 8 capítulos canônicos da GNLT).
- [`gramatica_normativa_base.md`](./gramatica_normativa_base.md): Gramática Normativa do Trepiano Clássico (Fonologia, Matriz Verbal Quadripartida, Sintaxe V2, Declinações e Posposições).
- [`treppio_base.md`](./treppio_base.md): Compêndio Gramatical, Filológico e **Dicionário Geral Integral** (Seções I–VIII de gramática rápida + Seção IX com todos os lemas do léxico).
- [`adendo_edicao_unificada_v8_1.md`](./adendo_edicao_unificada_v8_1.md): Edição Unificada (Chancelaria Imperial, Doutrina das Quatro Valências e Léxico Consolidado).
- [`caderno_treppio_notebook.md`](./caderno_treppio_notebook.md): Metadados e referências do Caderno Tréppio no Google Gemini Notebook.
- [`dist/`](./dist/): Pacotes compilados de distribuição multiplataforma:
  - `Codice_Treppio_Conde.apk`: Aplicativo Android nativo (100% offline com Dicionário, Pronúncia IPA, Tradutor Bilíngue `TR ↔ PT`, GNLT e Diálogos de Ecos).
  - `Codice_Treppio_Conde.exe`: Launcher executável para Windows (.NET com Pronúncia IPA, Tradutor Bilíngue e servidor embutido).
  - `Codice_Treppio_Portatil.html`: Edição web portátil autocontida em arquivo único.
- [`docs/`](./docs/): Portal web público e Progressive Web App (PWA) hospedado no GitHub Pages ([https://maiiasere5763.github.io/conde-treppio/](https://maiiasere5763.github.io/conde-treppio/)).
- [`sandbox/`](./sandbox/): Ambiente de experimentação filológica e expansão lexical naturalista:
  - [`sandbox/dialogos_praticos_dia_a_dia_treppio.md`](./sandbox/dialogos_praticos_dia_a_dia_treppio.md): Guia de Diálogos Práticos e Conversação Cotidiana.
  - [`sandbox/dicionario_exaustivo/`](./sandbox/dicionario_exaustivo/): Gerador filológico e compilação do léxico com todas as terminações morfológicas.
  - [`sandbox/analise_e_expansao_sandbox.py`](./sandbox/analise_e_expansao_sandbox.py): Validador fonotático e gerador morfológico da Matriz Quadripartida.
  - [`sandbox/relatorio_conde_sandbox_treppio.md`](./sandbox/relatorio_conde_sandbox_treppio.md): Relatório de Análise Filológica e Expansão Naturalista.
  - [`sandbox/launcher_exe/`](./sandbox/launcher_exe/): Código-fonte C# e rotina de compilação do executável Windows.
  - [`sandbox/android_apk/`](./sandbox/android_apk/): Projeto Android nativo em Java com Gradle e WebView de alto desempenho.
- [`sync_conde.ps1`](./sync_conde.ps1): Script de sincronização automática com OneDrive, Google Drive e GitHub.

---

## Fonética Canônica (IPA) e Lei da Haplologia Silábica (`'`)

1. **Regra Imutável do `G` e do `S`**:
   - **`G / g`** pronuncia-se **SEMPRE como `/ɡ/`** ("guitarra", "gole"), inclusive antes de *e, i, y, ë* (*gelur* `/ˈɡɛ.luɾ/`, *gizor* `/ˈɡi.zoɾ/`), **nunca** `/ʒ/`.
   - **`S / s`** pronuncia-se **SEMPRE como `/s/`** ("sapato", "massa"), inclusive entre vogais ou em final de palavra (*esu* `/ˈɛ.su/`, *rase* `/ˈɾa.se/`), **nunca** `/z/`.
   - **`X / x`** realiza-se como fricativa velar surda `/x/` (como *ch* alemão em *Bach*); **`H / h`** como aspirada `/h/`; **`Z / z`** como `/z/`; **`R / r`** como tepe `/ɾ/` e **`RR / rr`** como vibrante múltipla `/r/`.
2. **Lei Estrita da Haplologia Silábica (`'`)**:
   - O apóstrofo aplica-se **exclusivamente** quando a **primeira letra (ataque consonantal / *onset*) de uma sílaba `Sᵢ`** é idêntica à **primeira letra da sílaba imediatamente subsequente `Sᵢ₊₁`**, suprimindo a consoante inicial de `Sᵢ₊₁` (preservando geminadas legítimas de Sandi, máx. 1 apóstrofo por palavra):
     - Exemplos nominais e derivados: *vevar* → **`ve'ar`**, *vevaril* → **`ve'aril`**, *avurvé* → **`avur'é`**, *velvé* → **`vel'é`**, *Halylitror* → **`Haly'itror`**, *Treppenína* → **`Treppení'a`**.
     - Exemplos flexionais e compostos: *dooteti* → **`doote'i`**, *balkukes* → **`balku'es`**, *od-adur-* → **`oda'ur-`**, *kel-kun-* → **`kel'un-`**, *tirta* → **`Tir'a`**, *beva-vë* → **`beva'ë`**.

---

## Dicionário Resumido do Tréppio Clássico (Classes Gramaticais & Núcleo Lexicográfico)

> O catálogo integral com todos os lemas encontra-se na **Seção IX de [`treppio_base.md`](./treppio_base.md)** e em [`sandbox/dicionario_geral_treppio_sandbox.md`](./sandbox/dicionario_geral_treppio_sandbox.md).

<!-- BEGIN_README_DICT -->
### Classes Fechadas (Pronomes, Numerais, Preposições e Partículas)
- **Pronomes Pessoais (`Nom* / Gen / Acu / Dat`)**: *1ª Sg* (`eo* / ey / em / ej`), *2ª Sg* (`to* / ty / tim / tij`), *1ª Pl* (`no* / ny / nom / noj`), *2ª Pl* (`vo* / vy / vom / voj`). (*Nom.* com *pro-drop* compulsório).
- **Demonstrativos**: **San** (1ª deíxe, este), **Tan** (2ª deíxe, esse), **Kan** (3ª deíxe, aquele/ele).
- **Numerais (`1–10, 100, 1000`)**: `id / Itta` (1), `do / Dota` (2), `zel / Zelta` (3), `kat / Katta` (4; `Kat'om` 40), `vex / Vexta` (5), `tir / Tir'a` (6), `san / Santa` (7), `nyr / Nyrta` (8), `nev / Nepta` (9), `krom / Kromta` (10), `Dygum` (100), `Myga` (1000).
- **Preposições e Conjunções**: `ad` (a/para +Acu/Inf), `ex` (de/desde +Dat), `in` (em/para dentro +Acu/+Dat), `ponu` (sob), `et` (e), `u` (ou), `ke` (que/o qual), `ko` (como/quando), `so` (se), `nam` (pois/ora), `ta` (portanto/contudo), `ante ke` (antes que), `ne` (não), `yo` (sim), `zo` (assim).

### Vocabulário Essencial por Eixo Semântico
| Categoria | Verbetes Canônicos (Selecionados) |
| :--- | :--- |
| **Teologia & Cosmos** | **Gyos** (Deus), **Oratypatte** (Ilúvatar), **Haly'itror** (Ainulindalë), **Halo** (Ainur), **Halyvur** (Chama Imperecível), **Oratoxe** (Mundo/Eä), **xere** (céu), **lexe** (estrela), **fea** (sol), **lan** (luz), **vel** (sombra), **Nesu** (Vazio). |
| **Natureza & Elementos** | **Vé** (água), **oxe** (terra/chão), **rixe** (montanha), **vur** (fogo), **fer** (vento), **kor** (árvore), **ve'ar** (rio), **ve'aril** (riacho), **garvé** (oceano), **avur'é** (gelo), **veksixi** (chuva), **poke** (animal). |
| **Humanidade & Cidade** | **kron** (homem), **kran** (mulher), **mixi** (pessoa), **Patte** (pai), **mad** (mãe), **fel** (filho), **sukor** (coração), **tep** (casa), **teggar** (palácio), **var** (caminho), **falde** (pão), **sfammir** (espada). |
| **Adjetivos & Supletivos** | **moba / maer / moban** (bom / melhor / ótimo), **kura / krer / kuran** (mau-corrompido / pior / péssimo), **elfa** (sagrado), **rukra** (forte), **lota** (belo), **laura** (dourado), **vuro'a** (incandescente), **mild** (preciosíssimo), **bell** (diurníssimo). |
| **Verbos Nucleares (`-ur`)** | **esur** (ser/estar), **kazur** (viver), **kradur** (criar), **tekur** (fazer), **letur** (falar), **mirur** (ver), **gizur** (amar), **isur** (saber), **skorum / skorur** (crer), **keladur** (vir/aproximar), **ynur** (andar), **sfarur** (proteger). |
<!-- END_README_DICT -->

## Como Sincronizar Manualmente ou Automaticamente

Execute no PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File "D:\Conde_Treppio\sync_conde.ps1"
```
