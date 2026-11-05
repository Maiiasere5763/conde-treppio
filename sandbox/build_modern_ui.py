"""
build_modern_ui.py
Moderniza e refina visualmente a interface de usuário do Códice Lexicográfico Imperial (sandbox/ui_dicionario/index.html).
Aplica os preceitos de Apple-level design, tipografia editorial de luxo (Cinzel, Playfair Display, Inter, JetBrains Mono),
Modo Obsidiana Soberana (dark) e Modo Pergaminho Imperial (light), micro-interações, síntese de fala e design glassmorphic de alto padrão.
Preserva 100% de todas as 36 funções JavaScript e funcionalidades filológicas.
"""

import os
import re

ROOT_DIR = r"D:\Conde_Treppio"
UI_INDEX_PATH = os.path.join(ROOT_DIR, "sandbox", "ui_dicionario", "index.html")

def build_modern_ui():
    with open(UI_INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Extrair todo o bloco de script (a partir do carregamento do DB)
    script_match = re.search(r'(<!-- CARREGAMENTO DO BANCO DE DADOS GERADO PELO /CONDE -->[\s\S]*?</html>)', content)
    if not script_match:
        raise ValueError("Não foi possível localizar o bloco de script no index.html atual.")
    
    script_part = script_match.group(1)

    # Injetar os novos métodos utilitários de Toast e Pronúncia se ainda não estiverem presentes
    if "function speakTreppio" not in script_part:
        helpers = """
    // 8. Utilitários Interativos Modernos: Toast e Síntese Fonética do Tréppio
    function speakTreppio(text) {
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 0.88;
      utter.pitch = 1.0;
      const voices = window.speechSynthesis.getVoices();
      const targetVoice = voices.find(v => v.lang.startsWith('it') || v.lang.startsWith('la') || v.lang.startsWith('es') || v.lang.startsWith('pt'));
      if (targetVoice) utter.voice = targetVoice;
      window.speechSynthesis.speak(utter);
    }

    function copyToClipboard(text, msg) {
      navigator.clipboard.writeText(text).then(() => {
        showToast(msg || `Copiado: ${text}`);
      }).catch(() => {});
    }

    function showToast(msg) {
      let toast = document.getElementById("toast-notification");
      if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast-notification";
        toast.className = "toast-box";
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      toast.classList.add("show");
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => {
        toast.classList.remove("show");
      }, 2200);
    }
  </script>
"""
        script_part = script_part.replace("</script>\n</body>", helpers + "</body>")

    new_html = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <meta name="theme-color" content="#07090e" />
  <meta name="description" content="Códice Lexicográfico Imperial da Língua Tréppia — Era Clássica V8.1. Edição Filológica Completa com 46.531 formas, Matriz Verbal Quadripartite, GNLT e Diálogos de Ecos." />
  <link rel="manifest" href="manifest.json" />
  <link rel="icon" type="image/png" href="icon-512.png" />
  <title>Códice Lexicográfico Imperial — Dicionário Geral do Tréppio (Era Clássica V8.1)</title>

  <!-- Google Fonts: Cinzel (Imperial Serif), Playfair Display (Editorial), Inter (UI Sans), JetBrains Mono (Philology/Code) -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Playfair+Display:ital,wght@0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet" />

  <style>
    /* ==========================================================================
       DESIGN SYSTEM: CÓDICE IMPERIAL TRÉPPIO (ERA CLÁSSICA V8.1)
       Inspirado em Apple Human Interface Guidelines, Design Editorial Clássico
       e Tokens Glassmorphic de Luxo (Modo Obsidiana Soberana & Pergaminho Imperial)
       ========================================================================== */

    :root {{
      /* Modo Obsidiana Soberana (Dark Luxury) */
      --bg-deep: #06080d;
      --bg-primary: #0a0d15;
      --bg-secondary: #0f1422;
      --bg-surface: #141a2c;
      --bg-card: rgba(18, 24, 39, 0.82);
      --bg-card-hover: rgba(25, 33, 53, 0.92);
      --bg-card-elevated: #161d31;
      --bg-accent: rgba(226, 185, 75, 0.12);
      --bg-accent-hover: rgba(226, 185, 75, 0.2);

      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-color: #232c45;
      --border-gold: rgba(226, 185, 75, 0.36);
      --border-gold-bright: #ffd86b;

      --text-primary: #f2f5fc;
      --text-secondary: #9da9c5;
      --text-muted: #626f8d;

      --gold: #d4af37;
      --gold-bright: #fde28e;
      --gold-glow: 0 0 24px rgba(226, 185, 75, 0.24);

      --crimson: #e25c68;
      --emerald: #34c787;
      --azure: #579cf8;
      --violet: #af85fc;
      --amber: #f59e0b;

      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.35);
      --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.45);
      --shadow-lg: 0 18px 48px rgba(0, 0, 0, 0.65);

      --font-display: "Cinzel", "Georgia", "Palatino Linotype", "Book Antiqua", serif;
      --font-serif: "Playfair Display", "Georgia", serif;
      --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;

      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-xl: 20px;

      --transition-fast: 0.15s cubic-bezier(0.16, 1, 0.3, 1);
      --transition-normal: 0.24s cubic-bezier(0.16, 1, 0.3, 1);
      --glass-blur: blur(18px);
    }}

    [data-theme="light"] {{
      /* Modo Pergaminho Imperial (Light Luxury) */
      --bg-deep: #f3ede0;
      --bg-primary: #fbf8f1;
      --bg-secondary: #f2ebd9;
      --bg-surface: #ffffff;
      --bg-card: rgba(255, 255, 255, 0.94);
      --bg-card-hover: #ffffff;
      --bg-card-elevated: #faf6ec;
      --bg-accent: rgba(160, 115, 12, 0.1);
      --bg-accent-hover: rgba(160, 115, 12, 0.18);

      --border-subtle: rgba(0, 0, 0, 0.08);
      --border-color: #dcd0b7;
      --border-gold: rgba(160, 115, 12, 0.45);
      --border-gold-bright: #9a6e0a;

      --text-primary: #191610;
      --text-secondary: #4f4534;
      --text-muted: #7b6f59;

      --gold: #9a6e0a;
      --gold-bright: #785303;
      --gold-glow: 0 0 20px rgba(160, 115, 12, 0.16);

      --crimson: #a6202e;
      --emerald: #14754e;
      --azure: #1a5ab3;
      --violet: #6334b0;
      --amber: #b45309;

      --shadow-sm: 0 2px 6px rgba(50, 35, 10, 0.06);
      --shadow-md: 0 6px 20px rgba(50, 35, 10, 0.11);
      --shadow-lg: 0 16px 40px rgba(50, 35, 10, 0.16);
    }}

    /* Reset & Base */
    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      background-color: var(--bg-deep);
      background-image: 
        radial-gradient(ellipse 90% 45% at 50% -15%, rgba(212, 175, 55, 0.08), transparent 75%),
        radial-gradient(circle at 10% 25%, rgba(87, 156, 248, 0.03), transparent 40%),
        radial-gradient(circle at 90% 75%, rgba(226, 92, 104, 0.03), transparent 40%);
      color: var(--text-primary);
      font-family: var(--font-sans);
      font-size: 15px;
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    /* Custom Sleek Scrollbar */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--bg-deep);
    }}
    ::-webkit-scrollbar-thumb {{
      background: var(--border-color);
      border-radius: 999px;
      border: 2px solid var(--bg-deep);
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: var(--gold);
    }}

    /* ==========================================================================
       CABEÇALHO IMPERIAL (FROSTED GLASS & AMBIENT GLOW)
       ========================================================================== */
    .imperial-header {{
      background: var(--bg-primary);
      background-color: rgba(10, 13, 21, 0.88);
      backdrop-filter: var(--glass-blur);
      -webkit-backdrop-filter: var(--glass-blur);
      border-bottom: 1px solid var(--border-subtle);
      box-shadow: 0 4px 28px rgba(0, 0, 0, 0.45);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 0.95rem 1.75rem 0.85rem;
      transition: background-color var(--transition-normal);
    }}

    [data-theme="light"] .imperial-header {{
      background-color: rgba(251, 248, 241, 0.92);
      box-shadow: 0 4px 20px rgba(60, 45, 15, 0.08);
      border-bottom-color: var(--border-color);
    }}

    .header-top {{
      max-width: 1620px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }}

    .brand-block {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .crest {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(226, 185, 75, 0.22) 0%, rgba(212, 175, 55, 0.08) 100%);
      border: 1.5px solid var(--gold);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 1.55rem;
      color: var(--gold-bright);
      box-shadow: var(--gold-glow), inset 0 1px 0 rgba(255, 255, 255, 0.2);
      transition: transform var(--transition-fast), box-shadow var(--transition-fast);
      user-select: none;
    }}

    .crest:hover {{
      transform: scale(1.05) rotate(-2deg);
      box-shadow: 0 0 30px rgba(226, 185, 75, 0.4);
    }}

    .brand-title h1 {{
      font-family: var(--font-display);
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: 0.025em;
      line-height: 1.25;
      background: linear-gradient(135deg, #ffffff 30%, var(--gold-bright) 75%, var(--gold) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }}

    [data-theme="light"] .brand-title h1 {{
      background: linear-gradient(135deg, #2b1f09 20%, #785303 60%, #9a6e0a 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .brand-edition-pill {{
      display: inline-block;
      font-family: var(--font-sans);
      font-size: 0.68rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.18rem 0.55rem;
      border-radius: 999px;
      background: var(--bg-accent);
      border: 1px solid var(--border-gold);
      color: var(--gold-bright);
      -webkit-text-fill-color: var(--gold-bright);
    }}

    .brand-title p {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-top: 0.2rem;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .stat-badge {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      padding: 0.32rem 0.72rem;
      border-radius: 999px;
      font-size: 0.76rem;
      color: var(--text-secondary);
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
      white-space: nowrap;
    }}

    .stat-badge strong {{
      color: var(--gold);
      font-family: var(--font-mono);
      font-weight: 600;
    }}

    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--emerald);
      box-shadow: 0 0 10px var(--emerald);
      display: inline-block;
      animation: pulse-ring 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
    }}

    @keyframes pulse-ring {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.45; transform: scale(0.85); }}
    }}

    /* Buttons */
    .btn {{
      background: var(--bg-card);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      padding: 0.46rem 0.92rem;
      border-radius: var(--radius-md);
      font-size: 0.82rem;
      font-weight: 600;
      font-family: var(--font-sans);
      cursor: pointer;
      transition: all var(--transition-fast);
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      box-shadow: var(--shadow-sm);
      user-select: none;
    }}

    .btn:hover {{
      border-color: var(--border-gold);
      background: var(--bg-card-hover);
      color: var(--gold-bright);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }}

    .btn:active {{
      transform: translateY(1px);
      box-shadow: var(--shadow-sm);
    }}

    .btn-gold {{
      background: linear-gradient(135deg, rgba(226, 185, 75, 0.2) 0%, rgba(212, 175, 55, 0.08) 100%);
      border-color: var(--gold);
      color: var(--gold-bright);
      box-shadow: 0 2px 10px rgba(226, 185, 75, 0.15);
    }}

    .btn-gold:hover {{
      background: linear-gradient(135deg, rgba(226, 185, 75, 0.32) 0%, rgba(212, 175, 55, 0.15) 100%);
      color: #ffffff;
      box-shadow: var(--gold-glow);
    }}

    /* ==========================================================================
       BARRA DE BUSCA OMNI & NAVEGAÇÃO DE ABAS
       ========================================================================== */
    .search-and-tabs {{
      max-width: 1620px;
      margin: 0.85rem auto 0;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}

    .omni-search-bar {{
      display: flex;
      gap: 0.75rem;
      align-items: center;
      background: var(--bg-surface);
      border: 1.5px solid var(--border-color);
      border-radius: var(--radius-xl);
      padding: 0.45rem 1.15rem;
      box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.25), 0 2px 10px rgba(0, 0, 0, 0.2);
      transition: all var(--transition-fast);
    }}

    .omni-search-bar:focus-within {{
      border-color: var(--gold);
      box-shadow: 0 0 0 3px rgba(226, 185, 75, 0.2), inset 0 1px 4px rgba(0, 0, 0, 0.25);
      background: var(--bg-card-elevated);
    }}

    .omni-search-icon {{
      font-size: 1.05rem;
      color: var(--gold);
      user-select: none;
    }}

    .omni-search-bar input {{
      flex: 1;
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-size: 0.95rem;
      font-family: var(--font-sans);
      outline: none;
    }}

    .omni-search-bar input::placeholder {{
      color: var(--text-muted);
      font-size: 0.88rem;
    }}

    .kbd-hint {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      padding: 0.2rem 0.5rem;
      border-radius: var(--radius-sm);
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      user-select: none;
    }}

    /* Nav Tabs (Segmented Control) */
    .nav-tabs {{
      display: flex;
      gap: 0.35rem;
      overflow-x: auto;
      padding: 0.25rem 0.15rem 0.4rem;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }}

    .nav-tabs::-webkit-scrollbar {{
      display: none;
    }}

    .tab-btn {{
      background: var(--bg-card);
      color: var(--text-secondary);
      border: 1px solid var(--border-subtle);
      padding: 0.52rem 0.95rem;
      border-radius: var(--radius-lg);
      font-size: 0.83rem;
      font-weight: 600;
      font-family: var(--font-sans);
      cursor: pointer;
      white-space: nowrap;
      transition: all var(--transition-fast);
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      user-select: none;
      box-shadow: var(--shadow-sm);
    }}

    .tab-btn:hover {{
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-color);
      transform: translateY(-1px);
    }}

    .tab-btn.active {{
      background: linear-gradient(135deg, rgba(226, 185, 75, 0.22) 0%, rgba(212, 175, 55, 0.1) 100%);
      border-color: var(--gold);
      color: var(--gold-bright);
      box-shadow: var(--gold-glow);
      font-weight: 700;
    }}

    [data-theme="light"] .tab-btn.active {{
      background: linear-gradient(135deg, rgba(160, 115, 12, 0.18) 0%, rgba(160, 115, 12, 0.08) 100%);
      color: var(--gold-bright);
    }}

    .tab-count {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      padding: 0.1rem 0.45rem;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-secondary);
    }}

    .tab-btn.active .tab-count {{
      background: rgba(226, 185, 75, 0.25);
      color: var(--gold-bright);
    }}

    /* ==========================================================================
       CONTAINER PRINCIPAL
       ========================================================================== */
    .main-container {{
      max-width: 1620px;
      width: 100%;
      margin: 1.5rem auto 3.5rem;
      padding: 0 1.75rem;
      flex: 1;
    }}

    /* Reconhecimento Morfológico Reverso */
    .reverse-parser-box {{
      background: linear-gradient(135deg, rgba(226, 185, 75, 0.14) 0%, rgba(87, 156, 248, 0.09) 100%);
      border: 1px solid var(--gold);
      border-radius: var(--radius-lg);
      padding: 1.15rem 1.45rem;
      margin-bottom: 1.5rem;
      display: none;
      box-shadow: var(--gold-glow);
      animation: fadeIn var(--transition-normal);
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(-4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .reverse-parser-box.visible {{
      display: block;
    }}

    .reverse-parser-title {{
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--gold-bright);
      font-weight: 700;
      margin-bottom: 0.65rem;
      display: flex;
      align-items: center;
      gap: 0.45rem;
    }}

    .reverse-matches-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 0.75rem;
    }}

    .reverse-match-item {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 0.75rem 0.95rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.75rem;
      box-shadow: var(--shadow-sm);
      transition: all var(--transition-fast);
    }}

    .reverse-match-item:hover {{
      border-color: var(--border-gold);
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }}

    /* Barra de Filtros e Alfabeto */
    .filter-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.65rem;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.25rem;
      background: var(--bg-surface);
      padding: 0.85rem 1.15rem;
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-sm);
    }}

    .alpha-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
    }}

    .alpha-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      min-width: 32px;
      height: 32px;
      padding: 0 0.5rem;
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      font-weight: 600;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .alpha-btn:hover, .alpha-btn.active {{
      background: var(--bg-accent);
      border-color: var(--gold);
      color: var(--gold-bright);
      transform: translateY(-1px);
    }}

    /* ==========================================================================
       CARDS GRID & VERBETES
       ========================================================================== */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 1.15rem;
    }}

    .entry-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.25rem 1.45rem;
      transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      box-shadow: var(--shadow-sm);
      position: relative;
    }}

    .entry-card:hover {{
      border-color: var(--border-gold);
      transform: translateY(-3px);
      box-shadow: var(--shadow-md), var(--gold-glow);
      background: var(--bg-card-hover);
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.65rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.65rem;
    }}

    .lemma-title {{
      font-family: var(--font-display);
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      color: var(--gold-bright);
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .pos-badge {{
      font-size: 0.72rem;
      font-weight: 700;
      font-family: var(--font-sans);
      padding: 0.22rem 0.6rem;
      border-radius: var(--radius-sm);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }}

    .badge-noun1 {{ background: rgba(87, 156, 248, 0.14); color: var(--azure); border: 1px solid rgba(87, 156, 248, 0.35); }}
    .badge-noun2 {{ background: rgba(52, 199, 135, 0.14); color: var(--emerald); border: 1px solid rgba(52, 199, 135, 0.35); }}
    .badge-adj   {{ background: rgba(175, 133, 252, 0.14); color: var(--violet); border: 1px solid rgba(175, 133, 252, 0.35); }}
    .badge-verb  {{ background: rgba(226, 92, 104, 0.14); color: var(--crimson); border: 1px solid rgba(226, 92, 104, 0.35); }}
    .badge-adv   {{ background: rgba(226, 185, 75, 0.14); color: var(--gold); border: 1px solid rgba(226, 185, 75, 0.35); }}

    .gloss-text {{
      font-size: 0.98rem;
      color: var(--text-primary);
      font-weight: 500;
      line-height: 1.5;
    }}

    .etym-text {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--text-secondary);
      background: var(--bg-secondary);
      border: 1px solid var(--border-subtle);
      padding: 0.25rem 0.6rem;
      border-radius: var(--radius-sm);
      display: inline-block;
    }}

    /* Mini Table for Noun Cases */
    .mini-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      margin-top: 0.25rem;
      border-radius: var(--radius-sm);
      overflow: hidden;
    }}

    .mini-table th, .mini-table td {{
      border: 1px solid var(--border-color);
      padding: 0.38rem 0.55rem;
      text-align: left;
    }}

    .mini-table th {{
      background: var(--bg-secondary);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 0.78rem;
    }}

    .mini-table td {{
      font-family: var(--font-mono);
      color: var(--text-primary);
      font-weight: 500;
    }}

    .mini-table tr:nth-child(even) td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    /* Derivation Pills */
    .deriv-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.38rem;
      margin-top: 0.35rem;
    }}

    .deriv-pill {{
      font-size: 0.75rem;
      background: var(--bg-secondary);
      border: 1px solid var(--border-subtle);
      padding: 0.2rem 0.55rem;
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .deriv-pill:hover {{
      border-color: var(--border-gold);
      background: var(--bg-card-hover);
      color: var(--gold-bright);
    }}

    .deriv-pill strong {{
      color: var(--gold-bright);
      font-family: var(--font-mono);
      font-weight: 600;
    }}

    /* ==========================================================================
       VERBOS QUADRIPARTITE & MATRIZ ONTO-LÓGICA
       ========================================================================== */
    .verbs-layout {{
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 1.5rem;
      align-items: start;
    }}

    @media (max-width: 1024px) {{
      .verbs-layout {{
        grid-template-columns: 1fr;
      }}
    }}

    .verb-roots-sidebar {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1rem;
      max-height: 80vh;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      position: sticky;
      top: 105px;
      box-shadow: var(--shadow-sm);
    }}

    .verb-roots-list {{
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      padding-right: 0.35rem;
    }}

    .verb-root-item {{
      background: var(--bg-secondary);
      border: 1px solid transparent;
      border-radius: var(--radius-md);
      padding: 0.6rem 0.8rem;
      cursor: pointer;
      text-align: left;
      color: var(--text-primary);
      transition: all var(--transition-fast);
    }}

    .verb-root-item:hover {{
      border-color: var(--border-gold);
      background: var(--bg-card-hover);
      transform: translateX(2px);
    }}

    .verb-root-item.active {{
      background: var(--bg-accent);
      border-color: var(--gold);
      border-left: 3.5px solid var(--gold);
      box-shadow: var(--gold-glow);
    }}

    .verb-root-item strong {{
      font-family: var(--font-mono);
      color: var(--gold-bright);
      font-size: 0.95rem;
    }}

    .verb-root-item span {{
      display: block;
      font-size: 0.78rem;
      color: var(--text-secondary);
      margin-top: 0.15rem;
    }}

    .quadripartite-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.15rem;
      margin-bottom: 1.5rem;
    }}

    @media (max-width: 900px) {{
      .quadripartite-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .axis-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.15rem 1.35rem;
      transition: all var(--transition-fast);
      box-shadow: var(--shadow-sm);
    }}

    .axis-card:hover {{
      border-color: var(--border-gold);
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }}

    .axis-card.active-axis {{
      border: 1.5px solid var(--gold);
      box-shadow: var(--gold-glow);
      background: var(--bg-card-elevated);
    }}

    /* ==========================================================================
       TABELAS DE DADOS AMPLAS
       ========================================================================== */
    .data-table-wrapper {{
      overflow-x: auto;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }}

    .data-table th, .data-table td {{
      padding: 0.72rem 0.95rem;
      border-bottom: 1px solid var(--border-color);
      text-align: left;
    }}

    .data-table th {{
      background: var(--bg-secondary);
      color: var(--gold);
      font-family: var(--font-sans);
      font-weight: 700;
      position: sticky;
      top: 0;
      z-index: 2;
    }}

    .data-table tr:hover td {{
      background: var(--bg-card-hover);
    }}

    .data-table td code {{
      font-family: var(--font-mono);
      color: var(--gold-bright);
    }}

    /* ==========================================================================
       CORPUS FILOLÓGICO INTERATIVO & SIMULADOR
       ========================================================================== */
    .corpus-word {{
      cursor: pointer;
      padding: 0.08rem 0.25rem;
      border-radius: var(--radius-sm);
      transition: background var(--transition-fast), color var(--transition-fast);
      display: inline-block;
    }}

    .corpus-word:hover {{
      background: var(--bg-accent);
      color: var(--gold-bright);
      text-decoration: underline;
      box-shadow: 0 0 8px rgba(226, 185, 75, 0.3);
    }}

    .lab-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 1.5rem;
    }}

    .input-field {{
      background: var(--bg-secondary);
      border: 1.5px solid var(--border-color);
      color: var(--text-primary);
      padding: 0.6rem 0.9rem;
      border-radius: var(--radius-md);
      font-size: 0.92rem;
      font-family: var(--font-mono);
      width: 100%;
      outline: none;
      transition: border-color var(--transition-fast);
    }}

    .input-field:focus {{
      border-color: var(--gold);
      box-shadow: 0 0 0 3px rgba(226, 185, 75, 0.2);
    }}

    /* ==========================================================================
       MODAL DE PARADIGMA
       ========================================================================== */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(4, 6, 11, 0.82);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 300;
      padding: 1.5rem;
      animation: fadeIn var(--transition-fast);
    }}

    .modal-backdrop.open {{
      display: flex;
    }}

    .modal-box {{
      background: var(--bg-primary);
      border: 1.5px solid var(--gold);
      border-radius: var(--radius-xl);
      max-width: 1100px;
      width: 100%;
      max-height: 88vh;
      overflow-y: auto;
      padding: 1.75rem 2rem;
      box-shadow: var(--shadow-lg), var(--gold-glow);
    }}

    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 1rem;
      margin-bottom: 1.25rem;
    }}

    /* ==========================================================================
       GNLT (GRAMÁTICA NORMATIVA DA LÍNGUA TRÉPPIA)
       ========================================================================== */
    .gnlt-container {{
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
    }}

    .gnlt-top-card {{
      background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
      border: 1px solid var(--border-gold);
      border-radius: var(--radius-xl);
      padding: 2rem 2.25rem;
      box-shadow: var(--shadow-md), var(--gold-glow);
    }}

    .gnlt-title {{
      font-family: var(--font-display);
      font-size: 2rem;
      font-weight: 800;
      color: var(--gold-bright);
      margin-bottom: 0.35rem;
      letter-spacing: 0.02em;
    }}

    .gnlt-subtitle {{
      color: var(--text-secondary);
      font-size: 0.98rem;
      margin-bottom: 1.5rem;
    }}

    .gnlt-controls-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 1.15rem;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--border-color);
      padding-top: 1.35rem;
    }}

    .gnlt-edition-selector {{
      display: inline-flex;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 4px;
      gap: 4px;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
    }}

    .gnlt-edition-btn {{
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 0.5rem 1.15rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      transition: all var(--transition-fast);
    }}

    .gnlt-edition-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-card);
    }}

    .gnlt-edition-btn.active {{
      background: var(--gold);
      color: #0b0d13;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(226, 185, 75, 0.4);
    }}

    .gnlt-search-box {{
      flex: 1;
      min-width: 280px;
      max-width: 500px;
      position: relative;
    }}

    .gnlt-search-input {{
      width: 100%;
      background: var(--bg-primary);
      border: 1.5px solid var(--border-color);
      color: var(--text-primary);
      border-radius: var(--radius-md);
      padding: 0.55rem 1rem;
      font-size: 0.9rem;
      outline: none;
      transition: border-color var(--transition-fast);
    }}

    .gnlt-search-input:focus {{
      border-color: var(--gold);
      box-shadow: 0 0 0 3px rgba(226, 185, 75, 0.2);
    }}

    .gnlt-chapter-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 1.25rem;
    }}

    .gnlt-chapter-pill {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 0.42rem 0.95rem;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--transition-fast);
      user-select: none;
    }}

    .gnlt-chapter-pill:hover {{
      border-color: var(--gold);
      color: var(--text-primary);
      transform: translateY(-1px);
    }}

    .gnlt-chapter-pill.active {{
      background: var(--bg-accent);
      border-color: var(--gold);
      color: var(--gold-bright);
      box-shadow: var(--gold-glow);
    }}

    .gnlt-chapter-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
      transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
    }}

    .gnlt-chapter-card:hover {{
      border-color: var(--border-gold);
      box-shadow: var(--shadow-md);
    }}

    .gnlt-card-header {{
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      padding: 1.15rem 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
      transition: background var(--transition-fast);
    }}

    .gnlt-card-header:hover {{
      background: var(--bg-card-hover);
    }}

    .gnlt-card-header h3 {{
      font-family: var(--font-display);
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--gold-bright);
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .gnlt-badge {{
      display: inline-block;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      background: var(--bg-accent);
      color: var(--gold);
      border: 1px solid var(--border-gold);
      padding: 0.22rem 0.6rem;
      border-radius: var(--radius-sm);
    }}

    .gnlt-card-body {{
      padding: 1.75rem 2rem;
      color: var(--text-primary);
      font-size: 0.98rem;
      line-height: 1.75;
    }}

    .gnlt-h3 {{
      font-family: var(--font-display);
      font-size: 1.2rem;
      color: var(--gold);
      margin: 1.6rem 0 0.6rem 0;
      border-bottom: 1px solid rgba(212, 175, 55, 0.25);
      padding-bottom: 0.4rem;
    }}

    .gnlt-h4 {{
      font-size: 1.05rem;
      color: var(--emerald);
      margin: 1.25rem 0 0.5rem 0;
      font-weight: 700;
    }}

    .gnlt-p {{
      margin-bottom: 0.95rem;
      color: var(--text-primary);
    }}

    .gnlt-quote {{
      border-left: 3.5px solid var(--gold);
      background: var(--bg-accent);
      padding: 0.85rem 1.35rem;
      margin: 1.15rem 0;
      border-radius: 0 var(--radius-md) var(--radius-md) 0;
      font-family: var(--font-serif);
      font-style: italic;
      color: var(--text-primary);
      font-size: 1.05rem;
    }}

    .gnlt-list {{
      margin: 0.85rem 0 1.15rem 2rem;
    }}

    .gnlt-list li {{
      margin-bottom: 0.45rem;
    }}

    .gnlt-divider {{
      border: none;
      border-top: 1px solid var(--border-color);
      margin: 1.75rem 0;
    }}

    .treppio-code {{
      font-family: var(--font-mono);
      background: rgba(0, 0, 0, 0.45);
      border: 1px solid var(--border-subtle);
      padding: 0.18rem 0.45rem;
      border-radius: var(--radius-sm);
      color: var(--gold-bright);
      font-size: 0.9em;
    }}

    /* ==========================================================================
       TOAST DE NOTIFICAÇÃO E MICRO-INTERAÇÕES
       ========================================================================== */
    .toast-box {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--bg-surface);
      border: 1.5px solid var(--gold);
      color: var(--gold-bright);
      padding: 0.75rem 1.25rem;
      border-radius: var(--radius-md);
      font-size: 0.88rem;
      font-weight: 600;
      box-shadow: var(--shadow-lg), var(--gold-glow);
      z-index: 1000;
      opacity: 0;
      transform: translateY(12px);
      pointer-events: none;
      transition: opacity var(--transition-fast), transform var(--transition-fast);
    }}

    .toast-box.show {{
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }}

    /* ==========================================================================
       RESPONSIVIDADE E DISPOSITIVOS MÓVEIS (ANDROID APK / PWA)
       ========================================================================== */
    @media (max-width: 768px) {{
      .imperial-header {{
        padding: 0.75rem 1rem;
      }}
      .brand-title h1 {{
        font-size: 1.1rem;
      }}
      .brand-title p {{
        font-size: 0.74rem;
      }}
      .crest {{
        width: 40px;
        height: 40px;
        font-size: 1.25rem;
      }}
      .header-actions {{
        gap: 0.35rem;
      }}
      .stat-badge {{
        font-size: 0.7rem;
        padding: 0.25rem 0.55rem;
      }}
      .btn {{
        font-size: 0.76rem;
        padding: 0.38rem 0.7rem;
      }}
      .main-container {{
        padding: 0 1rem;
        margin-top: 1rem;
      }}
      .cards-grid {{
        grid-template-columns: 1fr;
      }}
      .modal-box {{
        padding: 1.25rem 1.25rem;
        max-height: 94vh;
      }}
      .gnlt-top-card {{
        padding: 1.25rem 1.25rem;
      }}
      .gnlt-card-body {{
        padding: 1.15rem 1.25rem;
      }}
      .lab-grid {{
        grid-template-columns: 1fr;
      }}
      .toast-box {{
        bottom: 16px;
        right: 16px;
        left: 16px;
        text-align: center;
      }}
    }}
  </style>
</head>
<body>

  <!-- CABEÇALHO IMPERIAL -->
  <header class="imperial-header">
    <div class="header-top">
      <div class="brand-block">
        <div class="crest" title="Chancelaria Imperial de Treppênia">𝓣</div>
        <div class="brand-title">
          <h1>
            Códice Lexicográfico Imperial da Língua Tréppia
            <span class="brand-edition-pill">Era Clássica V8.1</span>
          </h1>
          <p>Alimentado diretamente pela Base de Dados Filológica do <code>/conde</code> (<code>D:\Conde_Treppio</code> + <code>sandbox</code>)</p>
        </div>
      </div>

      <div class="header-actions">
        <span class="stat-badge" id="conn-badge" title="Fonte ativa do banco de dados"><span class="pulse-dot"></span> <strong id="conn-status">Base Local /conde</strong></span>
        <span class="stat-badge">Substantivos: <strong id="stat-nouns">380</strong></span>
        <span class="stat-badge">Verbos: <strong id="stat-verbs">336</strong></span>
        <span class="stat-badge">Adjetivos: <strong id="stat-adjs">82</strong></span>
        <span class="stat-badge">Advérbios: <strong id="stat-advs">84</strong></span>
        <span class="stat-badge">Formas Totais: <strong id="stat-forms">46.531</strong></span>
        <button class="btn btn-gold" id="btn-sync" onclick="syncWithCondeBackend()" title="Sincronizar da Nuvem (Git/Google Drive) ou Recompilar da Base Local /conde">
          ⟳ Sincronizar Base /conde
        </button>
        <button class="btn" onclick="openCloudConfigModal()" title="Configurar URL Online do GitHub ou Google Drive">
          ☁️ Nuvem (Git/Drive)
        </button>
        <button class="btn" onclick="toggleTheme()" id="btn-theme">☀ Modo Pergaminho</button>
      </div>
    </div>

    <div class="search-and-tabs">
      <div class="omni-search-bar">
        <span class="omni-search-icon">🔍</span>
        <input
          type="text"
          id="omni-input"
          placeholder="Busque qualquer verbete em Tréppio, tradução em Português, etimologia ou qualquer uma das 46.531 formas flexionadas (ex.: doobbam, oda'urrum, kranoi, saittek, mild, outono, perdão)..."
          oninput="handleOmniSearch(this.value)"
        />
        <button class="btn" onclick="clearSearch()" id="btn-clear-search" style="display:none;">Limpar</button>
        <span class="kbd-hint">Tecla /</span>
      </div>

      <nav class="nav-tabs" id="main-tabs">
        <button class="tab-btn active" data-tab="nouns" onclick="switchTab('nouns')">
          🏛️ I. Substantivos <span class="tab-count" id="tab-cnt-nouns">380</span>
        </button>
        <button class="tab-btn" data-tab="verbs" onclick="switchTab('verbs')">
          ⚔️ II. Verbos (Matriz Quadripartite) <span class="tab-count" id="tab-cnt-verbs">336</span>
        </button>
        <button class="tab-btn" data-tab="adjectives" onclick="switchTab('adjectives')">
          ✨ III. Adjetivos <span class="tab-count" id="tab-cnt-adjs">82</span>
        </button>
        <button class="tab-btn" data-tab="adverbs" onclick="switchTab('adverbs')">
          🧭 IV. Advérbios <span class="tab-count" id="tab-cnt-advs">84</span>
        </button>
        <button class="tab-btn" data-tab="pronouns" onclick="switchTab('pronouns')">
          👑 V. Pronomes <span class="tab-count">7</span>
        </button>
        <button class="tab-btn" data-tab="numerals" onclick="switchTab('numerals')">
          🔢 VI. Numerais <span class="tab-count">12</span>
        </button>
        <button class="tab-btn" data-tab="particles" onclick="switchTab('particles')">
          🔗 VII. Preposições, Conjunções & Afixos <span class="tab-count" id="tab-cnt-part">25</span>
        </button>
        <button class="tab-btn" data-tab="diachronic" onclick="switchTab('diachronic')">
          📜 VIII. Registro Diacrônico & Variantes <span class="tab-count" id="tab-cnt-diac">23</span>
        </button>
        <button class="tab-btn" data-tab="corpus" onclick="switchTab('corpus')">
          📖 IX. Corpus & Halylitror Interativo <span class="tab-count">12</span>
        </button>
        <button class="tab-btn" data-tab="gnlt" onclick="switchTab('gnlt')">
          📜 XI. GNLT (Gramática Normativa) <span class="tab-count" id="tab-cnt-gnlt">8 Capítulos</span>
        </button>
        <button class="tab-btn" data-tab="dialogues" onclick="switchTab('dialogues')">
          💬 XII. Diálogos Práticos (Ecos 1.500 Anos) <span class="tab-count">5 Cenas</span>
        </button>
        <button class="tab-btn" data-tab="lab" onclick="switchTab('lab')">
          ⚗️ X. Simulador Morfofonológico V8.1
        </button>
      </nav>
    </div>
  </header>

  <!-- CONTEÚDO PRINCIPAL -->
  <main class="main-container">
    <!-- PAINEL DE RECONHECIMENTO MORFOLÓGICO REVERSO (46.531 FORMAS) -->
    <section class="reverse-parser-box" id="reverse-box">
      <div class="reverse-parser-title">⚡ Reconhecimento Morfológico Reverso nas 46.531 Formas Flexionadas e Derivadas</div>
      <div class="reverse-matches-grid" id="reverse-grid"></div>
    </section>

    <!-- CONTEÚDO DA ABA ATIVA -->
    <div id="tab-content"></div>
  </main>

  <!-- MODAL DE INSPECÇÃO PROFUNDA -->
  <div class="modal-backdrop" id="detail-modal" onclick="if(event.target===this) closeModal()">
    <div class="modal-box">
      <div class="modal-header">
        <h2 id="modal-title" style="font-family:var(--font-display);color:var(--gold-bright);">Detalhes do Verbete</h2>
        <button class="btn" onclick="closeModal()">✕ Fechar (Esc)</button>
      </div>
      <div id="modal-body"></div>
    </div>
  </div>

  {script_part}
"""

    with open(UI_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    
    print(f"[OK] index.html modernizado com sucesso: {len(new_html)} bytes.")

if __name__ == "__main__":
    build_modern_ui()
