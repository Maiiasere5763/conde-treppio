# Graph Report - Conde_Treppio  (2026-11-05)

## Corpus Check
- Large corpus: 52 files · ~1,315,893 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 248 nodes · 298 edges · 27 communities (9 shown, 18 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.89)
- Token cost: 45,500 input · 11,200 output

## Community Hubs (Navigation)
- Pipeline Runtime & Detection
- Android Native App & WebView
- Motor Morfofonológico & Gerador Lexical
- Launcher Desktop C# & Servidor Local
- Gramática Normativa, Sandi & Corpus Tréppio
- Automação de Build & Environment APK
- Arquitetura Windows Launcher C#
- GitHub Actions CI/CD Pipeline
- Manifesto PWA Web & Metadados
- Manifesto PWA Android Assets
- Motor Filológico Ainulindalë Tréppio
- Service Worker PWA Offline Web
- Service Worker UI Sandbox
- Caderno Filológico de Campo
- Fonologia Clássica do Grafema X
- Corpus Prático de Diálogos

## God Nodes (most connected - your core abstractions)
1. `EmbeddedServer` - 19 edges
2. `generate_all_files()` - 12 edges
3. `with` - 11 edges
4. `LauncherForm` - 10 edges
5. `steps` - 8 edges
6. `MainActivity` - 8 edges
7. `extract_gnlt_payload()` - 7 edges
8. `As 21 Leis de Sandi do Tréppio V8.1` - 6 edges
9. `Interface Unificada de 5 Hubs (Dicionário, Verbos, Diálogos, Gramática, Lab)` - 6 edges
10. `join_morphemes()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Halylitror Ainuron (Ainulindalë em Tréppio Litúrgico Monumental)` --implements--> `Ontologia Sintético-Aglutinante do Tréppio`  [EXTRACTED]
  sandbox/ainulindale_treppio_sandbox.md → gramatica_normativa_base.md
- `Diálogos de Saudação e Etiqueta Social (V8.1)` --implements--> `As 21 Leis de Sandi do Tréppio V8.1`  [EXTRACTED]
  sandbox/dialogos_praticos_dia_a_dia_treppio.md → adendo_edicao_unificada_v8_1.md
- `Léxico Integral do Tréppio (56.342 Formas Expandidas)` --implements--> `As 21 Leis de Sandi do Tréppio V8.1`  [EXTRACTED]
  sandbox/dicionario_geral_treppio_sandbox.md → adendo_edicao_unificada_v8_1.md
- `Relatório de Auditoria Filológica e Sanidade Lexical` --references--> `Conde (Assistente Filológico e Glotopoético)`  [EXTRACTED]
  sandbox/relatorio_conde_sandbox_treppio.md → SKILL.md
- `Simulação Diacrônica de 1500 Anos (Deriva Natural e Eufonia)` --conceptually_related_to--> `Síncrese de Treppênia (ou Síncrese de Celia)`  [EXTRACTED]
  sandbox/simulacao_diacronica_1500_anos.md → gramatica_normativa_base.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Núcleo Filológico da Chancelaria de Treppênia** — skill_conde_assistente_filologico, gramatica_normativa_base_ontologia_sintetico_aglutinante, adendo_edicao_unificada_v8_1_as_21_leis_de_sandi, adendo_edicao_unificada_v8_1_matriz_verbal_quadripartite [EXTRACTED 0.95]
- **Corpus Textual e Literário Vivo do Tréppio** — sandbox_dialogos_praticos_saudacoes_e_etiqueta, sandbox_ainulindale_halylitror_musica_dos_ainur, sandbox_ecos_vida_perdida_contexto_lore [EXTRACTED 0.85]
- **Plataforma Tripla do Códice Tréppio (Web, Windows .exe, Android APK)** — sandbox_ui_dicionario_interface_cinco_hubs, software_launcher_desktop_windows_cs_webview, software_apk_android_distribuicao_offline [EXTRACTED 0.95]

## Communities (27 total, 18 thin omitted)

### Community 0 - "Pipeline Runtime & Detection"
Cohesion: 0.08
Nodes (8): md_to_html(), format_inline(), render_table(), parse_chapters(), build_modern_ui(), inject(), literal(), main()

### Community 1 - "Android Native App & WebView"
Cohesion: 0.09
Nodes (4): MainActivity, ValueCallback<String>, WebChromeClient, WebViewClient

### Community 2 - "Motor Morfofonológico & Gerador Lexical"
Cohesion: 0.11
Nodes (13): build_four_stems(), conjugate_stem_all_109(), decline_noun(), extract_gnlt_payload(), format_inline(), md_to_html(), parse_file(), render_table() (+5 more)

### Community 3 - "Launcher Desktop C# & Servidor Local"
Cohesion: 0.11
Nodes (6): EmbeddedServer, ActiveSource, CloudUrl, Port, LauncherForm, Program

### Community 4 - "Gramática Normativa, Sandi & Corpus Tréppio"
Cohesion: 0.08
Nodes (24): As 21 Leis de Sandi do Tréppio V8.1, Matriz Verbal Quadripartite (Básico, Causativo, Frequentativo, Estativo), Clivagem Sociolinguística (Registro Culto K/S vs Registro Popular C/Ç), Ontologia Sintético-Aglutinante do Tréppio, Síncrese de Treppênia (ou Síncrese de Celia), Sistema Casual Tréppio (Nominativo, Acusativo, Genitivo, Dativo), Sistema Nominal de Cinco Declinações, Sistema Numérico Tripartite (Singular, Plural, Paucal) (+16 more)

### Community 5 - "Automação de Build & Environment APK"
Cohesion: 0.10
Nodes (20): steps, ANDROID_HOME, GITHUB_TOKEN, env, if, name, run, uses (+12 more)

### Community 7 - "GitHub Actions CI/CD Pipeline"
Cohesion: 0.15
Nodes (12): name, runs-on, jobs, build-apk, name, on, push, workflow_dispatch (+4 more)

### Community 8 - "Manifesto PWA Web & Metadados"
Cohesion: 0.20
Nodes (9): background_color, description, display, icons, name, orientation, short_name, start_url (+1 more)

### Community 9 - "Manifesto PWA Android Assets"
Cohesion: 0.20
Nodes (9): background_color, description, display, icons, name, orientation, short_name, start_url (+1 more)

## Knowledge Gaps
- **20 isolated node(s):** `Port`, `ActiveSource`, `CloudUrl`, `Clivagem Sociolinguística (Registro Culto K/S vs Registro Popular C/Ç)`, `Estatuto Fonético do Grafema X (/x/ gutural)` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 140 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EmbeddedServer` connect `Launcher Desktop C# & Servidor Local` to `Arquitetura Windows Launcher C#`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **What connects `Port`, `ActiveSource`, `CloudUrl` to the rest of the system?**
  _20 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pipeline Runtime & Detection` be split into smaller, more focused modules?**
  _Cohesion score 0.07899159663865546 - nodes in this community are weakly interconnected._
- **Why does `generate_all_files()` connect `Motor Morfofonológico & Gerador Lexical` to `Pipeline Runtime & Detection`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `Android Native App & WebView` be split into smaller, more focused modules?**
  _Cohesion score 0.0928030303030303 - nodes in this community are weakly interconnected._
- **Why does `LauncherForm` connect `Launcher Desktop C# & Servidor Local` to `Componentes Visuais Windows Forms`, `Arquitetura Windows Launcher C#`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Should `Motor Morfofonológico & Gerador Lexical` be split into smaller, more focused modules?**
  _Cohesion score 0.10837438423645321 - nodes in this community are weakly interconnected._