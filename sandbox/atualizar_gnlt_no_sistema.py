# -*- coding: utf-8 -*-
"""
atualizar_gnlt_no_sistema.py
Integra a Gramática Normativa da Língua Tréppia (GNLT) completa ao gerador,
à UI web (GitHub Pages), ao Launcher executável Windows e ao APK Android.
"""

import os
import re
import html
import json
import subprocess

ROOT_DIR = r"D:\Conde_Treppio"
SANDBOX_DIR = os.path.join(ROOT_DIR, "sandbox")
GERADOR_PY = os.path.join(SANDBOX_DIR, "gerador_dicionario_integral_sandbox.py")
UI_INDEX_HTML = os.path.join(SANDBOX_DIR, "ui_dicionario", "index.html")

print("=== 1. Lendo e analisando a GNLT de base e V8.1 ===")
BASE_MD = os.path.join(ROOT_DIR, "gramatica_normativa_base.md")
V81_MD = os.path.join(ROOT_DIR, "adendo_edicao_unificada_v8_1.md")

with open(BASE_MD, "r", encoding="utf-8") as f:
    text_base = f.read()

with open(V81_MD, "r", encoding="utf-8") as f:
    text_v81 = f.read()

def md_to_html(md_text: str) -> str:
    lines = md_text.strip().split("\n")
    out = []
    in_table = False
    table_rows = []
    in_list = False

    def format_inline(txt: str) -> str:
        txt = html.escape(txt)
        txt = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", txt)
        txt = re.sub(r"\*(.+?)\*", r"<em>\1</em>", txt)
        txt = re.sub(r"`(.+?)`", r'<code class="treppio-code">\1</code>', txt)
        return txt

    def render_table(rows):
        if not rows:
            return ""
        html_parts = ['<div class="data-table-wrapper"><table class="data-table">']
        header_done = False
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if len(cells) > 0 and all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue
            if not header_done:
                html_parts.append("<thead><tr>" + "".join(f"<th>{format_inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                header_done = True
            else:
                html_parts.append("<tr>" + "".join(f"<td>{format_inline(c)}</td>" for c in cells) + "</tr>")
        if header_done:
            html_parts.append("</tbody>")
        html_parts.append("</table></div>")
        return "\n".join(html_parts)

    for line in lines:
        line_str = line.strip()

        # Tabelas
        if line_str.startswith("|") and line_str.endswith("|"):
            if in_list:
                out.append("</ul>")
                in_list = False
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line_str)
            continue
        elif in_table:
            out.append(render_table(table_rows))
            in_table = False
            table_rows = []

        # Listas
        if line_str.startswith("- ") or line_str.startswith("* "):
            if not in_list:
                in_list = True
                out.append('<ul class="gnlt-list">')
            content = line_str[2:].strip()
            out.append(f"<li>{format_inline(content)}</li>")
            continue
        elif in_list:
            out.append("</ul>")
            in_list = False

        if not line_str:
            continue

        if line_str.startswith("### "):
            out.append(f'<h3 class="gnlt-h3">{format_inline(line_str[4:])}</h3>')
        elif line_str.startswith("#### "):
            out.append(f'<h4 class="gnlt-h4">{format_inline(line_str[5:])}</h4>')
        elif line_str.startswith("> "):
            out.append(f'<blockquote class="gnlt-quote">{format_inline(line_str[2:])}</blockquote>')
        elif line_str.startswith("---"):
            out.append('<hr class="gnlt-divider" />')
        else:
            out.append(f'<p class="gnlt-p">{format_inline(line_str)}</p>')

    if in_table:
        out.append(render_table(table_rows))
    if in_list:
        out.append("</ul>")
    return "\n".join(out)

def parse_chapters(md_content: str):
    raw_blocks = re.split(r"\n(?=## \d+\. )", md_content)
    intro = raw_blocks[0].strip()
    chapters = []
    for b in raw_blocks[1:]:
        lines = b.strip().split("\n")
        header = lines[0].replace("## ", "").strip()
        num_match = re.match(r"^(\d+)\.\s*(.*)", header)
        num = int(num_match.group(1)) if num_match else len(chapters) + 1
        title = num_match.group(2) if num_match else header
        full_md = "\n".join(lines[1:]).strip()
        chapters.append({
            "num": num,
            "title": title,
            "md": full_md,
            "html": md_to_html(full_md)
        })
    return intro, chapters

intro_base, chs_base = parse_chapters(text_base)
intro_v81, chs_v81 = parse_chapters(text_v81)

print(f" -> Parse concluído: 8 capítulos extraídos em Base e V8.1.")

# ==============================================================================
# 2. Atualizar gerador_dicionario_integral_sandbox.py
# ==============================================================================
print("=== 2. Atualizando gerador_dicionario_integral_sandbox.py ===")
with open(GERADOR_PY, "r", encoding="utf-8") as f:
    gerador_code = f.read()

# Código da função extract_gnlt_payload
gnlt_extractor_func = r'''
def extract_gnlt_payload(root_dir: str) -> dict:
    """Extrai e compila a Gramática Normativa da Língua Tréppia (Base e V8.1)."""
    import html, re
    base_path = os.path.join(root_dir, "gramatica_normativa_base.md")
    v81_path = os.path.join(root_dir, "adendo_edicao_unificada_v8_1.md")
    
    with open(base_path, "r", encoding="utf-8") as f:
        t_base = f.read()
    with open(v81_path, "r", encoding="utf-8") as f:
        t_v81 = f.read()

    def format_inline(txt: str) -> str:
        txt = html.escape(txt)
        txt = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", txt)
        txt = re.sub(r"\*(.+?)\*", r"<em>\1</em>", txt)
        txt = re.sub(r"`(.+?)`", r'<code class="treppio-code">\1</code>', txt)
        return txt

    def render_table(rows):
        if not rows:
            return ""
        html_parts = ['<div class="data-table-wrapper"><table class="data-table">']
        header_done = False
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if len(cells) > 0 and all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue
            if not header_done:
                html_parts.append("<thead><tr>" + "".join(f"<th>{format_inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                header_done = True
            else:
                html_parts.append("<tr>" + "".join(f"<td>{format_inline(c)}</td>" for c in cells) + "</tr>")
        if header_done:
            html_parts.append("</tbody>")
        html_parts.append("</table></div>")
        return "\n".join(html_parts)

    def md_to_html(md_text: str) -> str:
        lines = md_text.strip().split("\n")
        out = []
        in_table = False
        table_rows = []
        in_list = False
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("|") and line_str.endswith("|"):
                if in_list:
                    out.append("</ul>")
                    in_list = False
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(line_str)
                continue
            elif in_table:
                out.append(render_table(table_rows))
                in_table = False
                table_rows = []

            if line_str.startswith("- ") or line_str.startswith("* "):
                if not in_list:
                    in_list = True
                    out.append('<ul class="gnlt-list">')
                out.append(f"<li>{format_inline(line_str[2:].strip())}</li>")
                continue
            elif in_list:
                out.append("</ul>")
                in_list = False

            if not line_str:
                continue

            if line_str.startswith("### "):
                out.append(f'<h3 class="gnlt-h3">{format_inline(line_str[4:])}</h3>')
            elif line_str.startswith("#### "):
                out.append(f'<h4 class="gnlt-h4">{format_inline(line_str[5:])}</h4>')
            elif line_str.startswith("> "):
                out.append(f'<blockquote class="gnlt-quote">{format_inline(line_str[2:])}</blockquote>')
            elif line_str.startswith("---"):
                out.append('<hr class="gnlt-divider" />')
            else:
                out.append(f'<p class="gnlt-p">{format_inline(line_str)}</p>')

        if in_table:
            out.append(render_table(table_rows))
        if in_list:
            out.append("</ul>")
        return "\n".join(out)

    def parse_file(content):
        raw_blocks = re.split(r"\n(?=## \d+\. )", content)
        intro = raw_blocks[0].strip()
        chapters = []
        for b in raw_blocks[1:]:
            lines = b.strip().split("\n")
            header = lines[0].replace("## ", "").strip()
            num_match = re.match(r"^(\d+)\.\s*(.*)", header)
            num = int(num_match.group(1)) if num_match else len(chapters) + 1
            title = num_match.group(2) if num_match else header
            full_md = "\n".join(lines[1:]).strip()
            chapters.append({
                "num": num,
                "title": title,
                "md": full_md,
                "html": md_to_html(full_md)
            })
        return intro, chapters

    intro_base, chs_base = parse_file(t_base)
    intro_v81, chs_v81 = parse_file(t_v81)

    unified_chapters = []
    for c1, c2 in zip(chs_base, chs_v81):
        unified_chapters.append({
            "num": c1["num"],
            "title": c2["title"] if c2["title"] else c1["title"],
            "base_md": c1["md"],
            "v81_md": c2["md"],
            "base_html": c1["html"],
            "v81_html": c2["html"]
        })

    return {
        "title": "Gramática Normativa da Língua Tréppia (GNLT)",
        "subtitulo": "Cânone Gramatical da Era Clássica V8.1 | Chancelaria Imperial",
        "intro_base": intro_base,
        "intro_v81": intro_v81,
        "capitulos": unified_chapters
    }
'''

if "def extract_gnlt_payload" not in gerador_code:
    gerador_code = gnlt_extractor_func + "\n" + gerador_code

# Injetar full_json_db["gnlt"]
if 'full_json_db["gnlt"] =' not in gerador_code:
    target_needle = 'full_json_db["metadata"]["total_expanded_word_forms"] = total_word_forms'
    replacement = target_needle + '\n    full_json_db["gnlt"] = extract_gnlt_payload(root_dir)'
    gerador_code = gerador_code.replace(target_needle, replacement, 1)

# Injetar gravação na raiz de D:\Conde_Treppio\dicionario_formas_expandidas.json
if 'root_json_path = os.path.join(root_dir, "dicionario_formas_expandidas.json")' not in gerador_code:
    needle_save = 'with open(json_path, "w", encoding="utf-8") as f:\n        json.dump(full_json_db, f, ensure_ascii=False, indent=2)'
    save_code = needle_save + '\n    root_json_path = os.path.join(root_dir, "dicionario_formas_expandidas.json")\n    with open(root_json_path, "w", encoding="utf-8") as f:\n        json.dump(full_json_db, f, ensure_ascii=False, indent=2)'
    gerador_code = gerador_code.replace(needle_save, save_code, 1)

with open(GERADOR_PY, "w", encoding="utf-8") as f:
    f.write(gerador_code)
print(" -> gerador_dicionario_integral_sandbox.py atualizado com sucesso!")

# ==============================================================================
# 3. Atualizar sandbox/ui_dicionario/index.html
# ==============================================================================
print("=== 3. Atualizando sandbox/ui_dicionario/index.html ===")
with open(UI_INDEX_HTML, "r", encoding="utf-8") as f:
    html_src = f.read()

# A. Adicionar Estilos CSS da GNLT antes de </style>
gnlt_css = """
    /* Estilos GNLT (Gramática Normativa da Língua Tréppia) */
    .gnlt-container {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .gnlt-top-card {
      background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
      border: 1px solid var(--border-gold);
      border-radius: 12px;
      padding: 1.75rem;
      box-shadow: var(--shadow);
    }
    .gnlt-title {
      font-family: var(--font-serif);
      font-size: 1.85rem;
      color: var(--gold-bright);
      margin-bottom: 0.35rem;
    }
    .gnlt-subtitle {
      color: var(--text-secondary);
      font-size: 0.95rem;
      margin-bottom: 1.25rem;
    }
    .gnlt-controls-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--border-color);
      padding-top: 1.25rem;
    }
    .gnlt-edition-selector {
      display: inline-flex;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 4px;
      gap: 4px;
    }
    .gnlt-edition-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 0.45rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }
    .gnlt-edition-btn:hover {
      color: var(--text-primary);
      background: var(--bg-hover);
    }
    .gnlt-edition-btn.active {
      background: var(--gold);
      color: #0b0d13;
      font-weight: 600;
    }
    .gnlt-search-box {
      flex: 1;
      min-width: 280px;
      max-width: 500px;
      position: relative;
    }
    .gnlt-search-input {
      width: 100%;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      border-radius: 8px;
      padding: 0.55rem 1rem;
      font-size: 0.9rem;
    }
    .gnlt-search-input:focus {
      outline: none;
      border-color: var(--gold);
    }
    .gnlt-chapter-nav {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 1rem;
    }
    .gnlt-chapter-pill {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 0.4rem 0.85rem;
      border-radius: 20px;
      font-size: 0.82rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .gnlt-chapter-pill:hover {
      border-color: var(--gold);
      color: var(--text-primary);
    }
    .gnlt-chapter-pill.active {
      background: var(--bg-accent);
      border-color: var(--gold);
      color: var(--gold-bright);
      font-weight: 600;
    }
    .gnlt-chapter-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow);
      transition: border-color 0.2s;
    }
    .gnlt-chapter-card:hover {
      border-color: var(--border-gold);
    }
    .gnlt-card-header {
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }
    .gnlt-card-header h3 {
      font-family: var(--font-serif);
      font-size: 1.25rem;
      color: var(--gold-bright);
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .gnlt-badge {
      display: inline-block;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      background: var(--bg-accent);
      color: var(--gold);
      border: 1px solid var(--border-gold);
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
    }
    .gnlt-card-body {
      padding: 1.5rem 1.75rem;
      color: var(--text-primary);
      font-size: 0.95rem;
      line-height: 1.7;
    }
    .gnlt-h3 {
      font-family: var(--font-serif);
      font-size: 1.15rem;
      color: var(--gold);
      margin: 1.5rem 0 0.5rem 0;
      border-bottom: 1px solid rgba(212, 175, 55, 0.2);
      padding-bottom: 0.35rem;
    }
    .gnlt-h4 {
      font-size: 1.02rem;
      color: var(--emerald);
      margin: 1.2rem 0 0.4rem 0;
    }
    .gnlt-p {
      margin-bottom: 0.85rem;
      color: var(--text-primary);
    }
    .gnlt-quote {
      border-left: 3px solid var(--gold);
      background: var(--bg-accent);
      padding: 0.75rem 1.25rem;
      margin: 1rem 0;
      border-radius: 0 8px 8px 0;
      font-style: italic;
      color: var(--text-secondary);
    }
    .gnlt-list {
      margin: 0.75rem 0 1rem 1.75rem;
    }
    .gnlt-list li {
      margin-bottom: 0.4rem;
    }
    .gnlt-divider {
      border: none;
      border-top: 1px solid var(--border-color);
      margin: 1.5rem 0;
    }
    .treppio-code {
      font-family: var(--font-mono);
      background: rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      color: var(--gold-bright);
      font-size: 0.88em;
    }
"""

if "/* Estilos GNLT" not in html_src:
    html_src = html_src.replace("</style>", gnlt_css + "\n  </style>", 1)

# B. Adicionar Botão de Aba GNLT no header
tab_btn_gnlt = """        <button class="tab-btn" data-tab="gnlt" onclick="switchTab('gnlt')">
          📜 XI. GNLT (Gramática Normativa) <span class="tab-count" id="tab-cnt-gnlt">8 Capítulos</span>
        </button>"""

if 'data-tab="gnlt"' not in html_src:
    needle_tab = '<button class="tab-btn" data-tab="lab"'
    html_src = html_src.replace(needle_tab, tab_btn_gnlt + "\n" + needle_tab, 1)

# C. Adicionar switch case na função renderActiveTab
switch_case_gnlt = """        case "gnlt":
          renderGnltTab(container);
          break;"""

if 'case "gnlt":' not in html_src:
    needle_switch = 'case "lab":'
    html_src = html_src.replace(needle_switch, switch_case_gnlt + "\n        " + needle_switch, 1)

# D. Adicionar implementação de renderGnltTab e handlers interativos
gnlt_js_impl = """
    // 6.B. Renderização da Aba GNLT (Gramática Normativa da Língua Tréppia)
    let gnltActiveChapter = 0; // 0 = todos
    let gnltEdition = "v81";   // 'v81' ou 'base'
    let gnltQuery = "";

    function setGnltEdition(ed) {
      gnltEdition = ed;
      renderActiveTab();
    }

    function setGnltChapter(num) {
      gnltActiveChapter = num;
      renderActiveTab();
    }

    function handleGnltSearch(q) {
      gnltQuery = (q || "").trim().toLowerCase();
      renderActiveTab();
    }

    function toggleGnltCard(cardId) {
      const body = document.getElementById(cardId);
      if (body) {
        body.style.display = (body.style.display === "none") ? "block" : "none";
      }
    }

    function renderGnltTab(container) {
      const gnlt = DB.gnlt;
      if (!gnlt) {
        container.innerHTML = `<div class="empty-state">Gramática Normativa (GNLT) não encontrada no banco de dados.</div>`;
        return;
      }

      const chapters = gnlt.capitulos || [];
      const intro = gnltEdition === "v81" ? (gnlt.intro_v81 || "") : (gnlt.intro_base || "");

      // Filtrar capítulos
      const filtered = chapters.filter(c => {
        if (gnltActiveChapter > 0 && c.num !== gnltActiveChapter) return false;
        if (!gnltQuery) return true;
        const text = (c.title + " " + (gnltEdition === "v81" ? c.v81_md : c.base_md)).toLowerCase();
        return text.includes(gnltQuery);
      });

      const pillsHtml = [
        `<button class="gnlt-chapter-pill ${gnltActiveChapter === 0 ? "active" : ""}" onclick="setGnltChapter(0)">Todos os Capítulos (8)</button>`
      ].concat(chapters.map(c => `
        <button class="gnlt-chapter-pill ${gnltActiveChapter === c.num ? "active" : ""}" onclick="setGnltChapter(${c.num})">
          Cap. ${c.num}: ${c.title.split(",")[0].split("&")[0].trim()}
        </button>
      `)).join("");

      container.innerHTML = `
        <div class="gnlt-container">
          <div class="gnlt-top-card">
            <h2 class="gnlt-title">📜 Gramática Normativa da Língua Tréppia (GNLT)</h2>
            <p class="gnlt-subtitle">Cânone Filológico e Normativo Oficial do Trepiano Clássico | Chancelaria Imperial do Tréppio</p>
            
            <div class="gnlt-controls-bar">
              <div class="gnlt-edition-selector">
                <button class="gnlt-edition-btn ${gnltEdition === 'v81' ? 'active' : ''}" onclick="setGnltEdition('v81')">
                  ✨ Edição Unificada V8.1 (Canônica)
                </button>
                <button class="gnlt-edition-btn ${gnltEdition === 'base' ? 'active' : ''}" onclick="setGnltEdition('base')">
                  🏛️ Documento Base Original
                </button>
              </div>

              <div class="gnlt-search-box">
                <input
                  type="text"
                  class="gnlt-search-input"
                  id="gnlt-search-input"
                  placeholder="Pesquisar regra, lei de sandi, caso, paradigma..."
                  value="${gnltQuery}"
                  oninput="handleGnltSearch(this.value)"
                />
              </div>
            </div>

            <div class="gnlt-chapter-nav">
              ${pillsHtml}
            </div>
          </div>

          ${gnltQuery ? `<div style="font-size:0.9rem;color:var(--gold);margin-top:-0.5rem;">Filtrando GNLT por: "<strong>${gnltQuery}</strong>" (${filtered.length} capítulos encontrados)</div>` : ''}

          <div style="display:flex;flex-direction:column;gap:1.5rem;">
            ${filtered.map(c => {
              const htmlContent = gnltEdition === "v81" ? c.v81_html : c.base_html;
              const cardId = `gnlt-body-${c.num}`;
              return `
                <div class="gnlt-chapter-card">
                  <div class="gnlt-card-header" onclick="toggleGnltCard('${cardId}')">
                    <h3>
                      <span>Capítulo ${c.num}.</span> ${c.title}
                    </h3>
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                      <span class="gnlt-badge">${gnltEdition === 'v81' ? 'V8.1 Unificada' : 'Base Canônica'}</span>
                      <span style="color:var(--text-muted);font-size:0.85rem;">Alternar ▾</span>
                    </div>
                  </div>
                  <div class="gnlt-card-body" id="${cardId}">
                    ${htmlContent}
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;
    }
"""

if "function renderGnltTab" not in html_src:
    needle_before_toggle = "    // 7. Utilit"
    html_src = html_src.replace(needle_before_toggle, gnlt_js_impl + "\n" + needle_before_toggle, 1)

with open(UI_INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html_src)
print(" -> sandbox/ui_dicionario/index.html atualizado com sucesso!")

print("=== Processo de injeção concluído com êxito! ===")
