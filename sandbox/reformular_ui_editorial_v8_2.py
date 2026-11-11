# -*- coding: utf-8 -*-
"""
reformular_ui_editorial_v8_2.py
Corrige os bugs críticos de JavaScript identificados na auditoria do index.html,
remove duplicações de CSS/JS/DOM e aplica o redesign estético 'Códice Imperial de Obsidiana e Ouro Brilhante (V8.2)'.
"""
import os
import re

HTML_PATH = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"


def upgrade_index_html():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    orig_len = len(html)

    # 1. Atualizar título e versão para V8.2
    html = html.replace("Era Clássica V8.1", "Era Clássica V8.2")
    html = html.replace("treppio-v8-1-cache-v2-intuitivo", "treppio-v8-2-cache-editorial")
    html = html.replace("sw.js?v=8.1.1", "sw.js?v=8.2.0")
    html = html.replace("dados_dicionario_conde.js?v=8.1.1", "dados_dicionario_conde.js?v=8.2.0")

    # 2. Remover bloco CSS duplicado (segunda ocorrência de NOVA ERGONOMIA)
    dup_css_marker = "/* ==========================================================================\n       NOVA ERGONOMIA: STATS PILL, QUICK CHIPS, SUB-HUBS E MOBILE BOTTOM NAV\n       ========================================================================== */"
    first_idx = html.find(dup_css_marker)
    if first_idx != -1:
        second_idx = html.find(dup_css_marker, first_idx + len(dup_css_marker))
        if second_idx != -1:
            end_style_idx = html.find("</style>", second_idx)
            if end_style_idx != -1:
                html = html[:second_idx] + html[end_style_idx:]
                print("[OK] Bloco CSS duplicado removido.")

    # 3. Adicionar novos estilos editoriais V8.2 antes de </style>
    editorial_v82_css = """
    /* ==========================================================================
       REDESIGN EDITORIAL V8.2: TOP COMMAND BAR, HERO COLAPSÁVEL, BENTO TELEMETRIA
       & MICRO-INTERAÇÕES (OUVIR / COPIAR / PAGINAÇÃO PROGRESSIVA)
       ========================================================================== */
    .imperial-header {
      padding: 0.65rem 1.5rem 0.6rem !important;
      background-color: rgba(8, 11, 18, 0.90) !important;
      border-bottom: 1px solid var(--border-gold) !important;
    }
    [data-theme="light"] .imperial-header {
      background-color: rgba(251, 248, 241, 0.94) !important;
    }
    .header-top {
      gap: 0.75rem !important;
    }
    .crest {
      width: 40px !important;
      height: 40px !important;
      font-size: 1.3rem !important;
      border-radius: 10px !important;
    }
    .brand-title h1 {
      font-size: 1.18rem !important;
    }
    .brand-title p {
      display: none;
    }
    .search-and-tabs {
      margin-top: 0.55rem !important;
      gap: 0.5rem !important;
    }
    .omni-search-bar {
      padding: 0.35rem 0.65rem !important;
      border-radius: 12px !important;
      background: rgba(15, 20, 34, 0.92) !important;
      border: 1px solid var(--border-gold) !important;
      box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.45), 0 0 18px rgba(212, 175, 55, 0.08) !important;
    }
    [data-theme="light"] .omni-search-bar {
      background: #ffffff !important;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    }
    .omni-search-bar input {
      font-size: 0.92rem !important;
      padding: 0.28rem 0.4rem !important;
    }
    .btn-voice-search {
      background: linear-gradient(135deg, rgba(212, 175, 55, 0.22), rgba(212, 175, 55, 0.08));
      border: 1px solid var(--border-gold);
      color: var(--gold-bright);
      padding: 0.28rem 0.68rem;
      border-radius: 8px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      transition: all var(--transition-fast);
      white-space: nowrap;
    }
    .btn-voice-search:hover {
      background: var(--gold);
      color: #090c14;
      box-shadow: var(--gold-glow);
    }
    .btn-voice-search.listening {
      background: var(--crimson);
      border-color: #ff8a93;
      color: #fff;
      animation: pulseListening 1.2s infinite;
    }
    @keyframes pulseListening {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(226, 92, 104, 0.6); }
      50% { transform: scale(1.04); box-shadow: 0 0 14px 4px rgba(226, 92, 104, 0.4); }
    }

    /* Hero Editorial Colapsável no Main */
    .imperial-hero-banner {
      background: linear-gradient(145deg, rgba(18, 24, 39, 0.92) 0%, rgba(11, 15, 25, 0.96) 100%);
      border: 1px solid var(--border-gold);
      border-radius: var(--radius-lg);
      padding: 1.15rem 1.4rem;
      margin-bottom: 1.25rem;
      box-shadow: var(--shadow-md), 0 0 32px rgba(212, 175, 55, 0.07);
      position: relative;
      overflow: hidden;
      transition: all var(--transition-normal);
    }
    [data-theme="light"] .imperial-hero-banner {
      background: linear-gradient(145deg, #ffffff 0%, #f5efe0 100%);
    }
    .imperial-hero-banner.collapsed .hero-collapsible-body {
      display: none;
    }
    .imperial-hero-banner.collapsed {
      padding: 0.65rem 1.15rem;
    }
    .hero-top-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }
    .hero-headline {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }
    .hero-headline h2 {
      font-family: var(--font-display);
      font-size: 1.08rem;
      color: var(--gold-bright);
      letter-spacing: 0.03em;
    }
    .hero-subtitle-inline {
      font-size: 0.82rem;
      color: var(--text-secondary);
    }
    .hero-bento-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.75rem;
      margin-top: 0.9rem;
    }
    .hero-bento-card {
      background: rgba(10, 14, 23, 0.68);
      border: 1px solid var(--border-subtle);
      border-left: 3px solid var(--gold);
      border-radius: var(--radius-md);
      padding: 0.65rem 0.9rem;
      transition: transform var(--transition-fast), border-color var(--transition-fast);
    }
    [data-theme="light"] .hero-bento-card {
      background: rgba(255, 255, 255, 0.85);
    }
    .hero-bento-card:hover {
      transform: translateY(-2px);
      border-color: var(--border-gold);
    }
    .hero-bento-label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
      font-weight: 600;
    }
    .hero-bento-value {
      font-family: var(--font-mono);
      font-size: 1.32rem;
      font-weight: 800;
      color: var(--gold-bright);
      line-height: 1.25;
      margin: 0.15rem 0;
    }
    .hero-bento-meta {
      font-size: 0.72rem;
      color: var(--text-muted);
    }
    .hero-bottom-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: 0.85rem;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border-subtle);
    }
    .ecosystem-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      align-items: center;
    }
    .eco-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.26rem 0.7rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-decoration: none;
      background: var(--bg-accent);
      border: 1px solid var(--border-gold);
      color: var(--gold-bright);
      transition: all var(--transition-fast);
      cursor: pointer;
    }
    .eco-pill:hover {
      background: var(--gold);
      color: #090c14;
      transform: translateY(-1px);
    }

    /* Micro-botões nos cards (Ouvir / Copiar / Detalhes) */
    .card-micro-actions {
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }
    .micro-btn {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      padding: 0.2rem 0.48rem;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.22rem;
      transition: all var(--transition-fast);
    }
    .micro-btn:hover {
      background: var(--bg-accent-hover);
      border-color: var(--gold);
      color: var(--gold-bright);
      transform: translateY(-1px);
    }
    .compact-cases-strip {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.4rem;
      margin-top: 0.45rem;
      padding: 0.45rem 0.6rem;
      background: rgba(10, 14, 23, 0.55);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.78rem;
    }
    [data-theme="light"] .compact-cases-strip {
      background: rgba(242, 235, 217, 0.65);
    }
    .compact-case-item span {
      color: var(--text-muted);
      font-size: 0.68rem;
      display: block;
      font-family: var(--font-sans);
      text-transform: uppercase;
    }
    .compact-case-item strong {
      color: var(--gold-bright);
    }
    .load-more-container {
      margin: 1.5rem 0 0.75rem;
      text-align: center;
    }
    .btn-load-more {
      background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.08));
      border: 1.5px solid var(--gold);
      color: var(--gold-bright);
      padding: 0.65rem 1.6rem;
      border-radius: 999px;
      font-size: 0.88rem;
      font-weight: 700;
      cursor: pointer;
      transition: all var(--transition-fast);
      box-shadow: var(--shadow-sm);
    }
    .btn-load-more:hover {
      background: var(--gold);
      color: #080b12;
      box-shadow: var(--gold-glow);
      transform: translateY(-2px);
    }

    @media (max-width: 960px) {
      .hero-bento-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    @media (max-width: 560px) {
      .hero-bento-grid {
        grid-template-columns: 1fr;
      }
    }
"""
    html = html.replace("</style>", editorial_v82_css + "\n  </style>", 1)

    # 4. Reformular o Header e adicionar o Hero Banner Colapsável no topo do <main>
    old_header_main = re.search(
        r'<!-- CABEÇALHO IMPERIAL -->[\s\S]*?<div id="tab-content"></div>\s*</main>',
        html,
    )
    if not old_header_main:
        raise RuntimeError("Não foi possível localizar o bloco CABEÇALHO IMPERIAL + main no index.html")

    new_header_main = """<!-- CABEÇALHO IMPERIAL COMPACTO (TOP COMMAND BAR V8.2) -->
  <header class="imperial-header">
    <div class="header-top">
      <div class="brand-block">
        <div class="crest" title="Chancelaria Imperial de Treppênia">𝓣</div>
        <div class="brand-title">
          <h1>
            Códice Imperial Tréppio
            <span class="brand-edition-pill">Era Clássica V8.2</span>
          </h1>
        </div>
      </div>

      <div class="header-actions">
        <div class="stats-pill" title="Total de Formas e Classes Gramaticais Oficiais">
          <span class="pulse-dot"></span>
          <span><strong id="stat-forms">143.353</strong> Formas</span>
          <span class="pill-sep">•</span>
          <span><strong id="stat-nouns">1104</strong> Nomes</span>
          <span class="pill-sep">•</span>
          <span><strong id="stat-verbs">1048</strong> Verbos</span>
          <span class="pill-sep">•</span>
          <span><strong id="stat-adjs">266</strong> Adjs</span>
        </div>
        <button class="btn" id="btn-toggle-hero" onclick="toggleHeroBanner()" title="Mostrar ou recolher o Painel Filológico Imperial">
          📊 Painel
        </button>
        <button class="btn btn-gold" id="btn-sync" onclick="syncWithCondeBackend()" title="Sincronizar base local ou da nuvem">
          ⟳ Sincronizar
        </button>
        <button class="btn" onclick="openCloudConfigModal()" title="Configurar URL Online (Git/Drive)">
          ☁️ Nuvem
        </button>
        <button class="btn" onclick="toggleTheme()" id="btn-theme" title="Alternar entre modo noturno obsidiana e modo pergaminho">☀ Pergaminho</button>
      </div>
    </div>

    <div class="search-and-tabs">
      <div class="omni-search-bar">
        <span class="omni-search-icon">🔍</span>
        <input
          type="text"
          id="omni-input"
          placeholder="Buscar em 143.353 formas (ex.: falde, vur, mild, pão, fogo, saittek, lareira, castelo)..."
          oninput="handleOmniSearch(this.value)"
        />
        <button class="btn-voice-search" id="btn-voice-omni" onclick="startVoiceSearch()" title="Pesquisar falando pelo microfone">
          🎙️ Voz
        </button>
        <button class="btn" onclick="clearSearch()" id="btn-clear-search" style="display:none;">Limpar</button>
        <span class="kbd-hint">Tecla /</span>
      </div>

      <!-- 5 HUBS PRINCIPAIS E COESOS -->
      <nav class="nav-tabs" id="main-tabs">
        <button class="tab-btn active" data-hub="dict" onclick="switchHub('dict')">
          🔍 I. Dicionário Geral <span class="tab-count" id="hub-cnt-dict">143.353</span>
        </button>
        <button class="tab-btn" data-hub="verbs" onclick="switchHub('verbs')">
          ⚔️ II. Conjugador Verbal <span class="tab-count" id="hub-cnt-verbs">1048 Verbos</span>
        </button>
        <button class="tab-btn" data-hub="dialogues" onclick="switchHub('dialogues')">
          💬 III. Diálogos Práticos <span class="tab-count">5 Cenas</span>
        </button>
        <button class="tab-btn" data-hub="grammar" onclick="switchHub('grammar')">
          📜 IV. Gramática & Corpus <span class="tab-count">GNLT + Ainulindalë</span>
        </button>
        <button class="tab-btn" data-hub="lab" onclick="switchHub('lab')">
          ⚗️ V. Laboratório Sandi V8.2
        </button>
      </nav>
    </div>
  </header>

  <!-- CONTEÚDO PRINCIPAL -->
  <main class="main-container">
    <!-- HERO BANNER EDITORIAL COLAPSÁVEL (TELEMETRIA BENTO + ACESSO RÁPIDO + ECOSSISTEMA) -->
    <section class="imperial-hero-banner" id="imperial-hero">
      <div class="hero-top-row">
        <div class="hero-headline">
          <h2>🏛️ Chancelaria Imperial de Treppênia — Códice Morfológico Exaustivo</h2>
          <span class="hero-subtitle-inline">Fonte: <strong id="conn-status" style="color:var(--emerald);">Embutido Offline</strong> • Ciclo Autônomo de 200 Temas (30 min)</span>
        </div>
        <button class="micro-btn" id="btn-hero-collapse-label" onclick="toggleHeroBanner()">▲ Recolher Painel</button>
      </div>

      <div class="hero-collapsible-body">
        <div class="hero-bento-grid">
          <div class="hero-bento-card">
            <div class="hero-bento-label">Formas Flexionadas e Derivadas</div>
            <div class="hero-bento-value" id="hero-stat-forms">143.353</div>
            <div class="hero-bento-meta">0 Colisões Homonímicas • 21 Leis de Sândi</div>
          </div>
          <div class="hero-bento-card">
            <div class="hero-bento-label">Substantivos Canônicos</div>
            <div class="hero-bento-value" id="hero-stat-nouns">1.104</div>
            <div class="hero-bento-meta">8 Casos (Sg/Pl) + 10 Sufixos Derivacionais</div>
          </div>
          <div class="hero-bento-card">
            <div class="hero-bento-label">Matriz Verbal Quadripartite</div>
            <div class="hero-bento-value" id="hero-stat-verbs">1.048</div>
            <div class="hero-bento-meta">4 Eixos Ontológicos × 114 Formas Finitas</div>
          </div>
          <div class="hero-bento-card">
            <div class="hero-bento-label">Adjetivos & Advérbios</div>
            <div class="hero-bento-value"><span id="hero-stat-adjs">266</span> <span style="font-size:0.9rem;color:var(--text-secondary);">/</span> <span id="hero-stat-advs">583</span></div>
            <div class="hero-bento-meta">Comparativo, Superlativo (-n/-ni) e Modal (-vë)</div>
          </div>
        </div>

        <div class="hero-bottom-bar">
          <div class="search-quick-chips" style="margin-top:0;">
            <span class="quick-chip-label">⚡ Ecos Rápidos:</span>
            <button class="quick-chip" onclick="quickSearch('falde')">🍞 Pão (falde)</button>
            <button class="quick-chip" onclick="quickSearch('vur')">🔥 Fogo (vur)</button>
            <button class="quick-chip" onclick="quickSearch('Vé')">💧 Água (Vé)</button>
            <button class="quick-chip" onclick="quickSearch('sfammir')">⚔️ Espada (sfammir)</button>
            <button class="quick-chip" onclick="quickSearch('Tette')">⚒️ Ferreiro (Tette)</button>
            <button class="quick-chip" onclick="quickSearch('poke xuna')">🐕 Cão Loiro</button>
            <button class="quick-chip" onclick="quickSearch('teggar')">🏰 Castelo (teggar)</button>
            <button class="quick-chip" onclick="quickSearch('Patte ny')">📜 Pai Nosso</button>
            <button class="quick-chip" onclick="quickSearch('Halylitror')">🎶 Ainulindalë</button>
          </div>

          <div class="ecosystem-pills">
            <a class="eco-pill" href="../Codice_Treppio_Conde.exe" download title="Baixar Launcher Desktop Windows (.EXE)">💻 Desktop .EXE</a>
            <a class="eco-pill" href="../Codice_Treppio_Conde.apk" download title="Baixar Aplicativo Android (.APK)">📱 Android .APK</a>
            <a class="eco-pill" href="../dist/Codice_Treppio_Portatil.html" download title="Baixar Códice Portátil 100% Autocontido (.HTML)">📄 Portátil .HTML</a>
          </div>
        </div>
      </div>
    </section>

    <!-- PAINEL DE RECONHECIMENTO MORFOLÓGICO REVERSO -->
    <section class="reverse-parser-box" id="reverse-box">
      <div class="reverse-parser-title">⚡ Reconhecimento Morfológico Reverso Instantâneo</div>
      <div class="reverse-matches-grid" id="reverse-grid"></div>
    </section>

    <!-- CONTEÚDO DA ABA ATIVA -->
    <div id="tab-content"></div>
  </main>"""

    html = html[:old_header_main.start()] + new_header_main + html[old_header_main.end():]
    print("[OK] Header Compacto V8.2 e Hero Banner Colapsável inseridos.")

    # 5. Adicionar variáveis de paginação e timer de debounce no estado global
    html = html.replace(
        'let selectedVerbAxisIdx = 0;',
        'let selectedVerbAxisIdx = 0;\n    let nounDisplayLimit = 60;\n    let omniDebounceTimer = null;',
    )

    # 6. Corrigir Bug #2: updateHeaderCounters() com null-checks seguros e novos IDs do Hero
    old_counters_fn = re.search(
        r'function updateHeaderCounters\(\) \{[\s\S]*?\n    \}',
        html,
    )
    if not old_counters_fn:
        raise RuntimeError("Não encontrou updateHeaderCounters()")

    new_counters_fn = """function updateHeaderCounters() {
      const m = DB.metadata || {};
      const nCount = Object.keys(DB.substantivos || {}).length;
      const vRoots = Object.keys(DB.verbos_quadripartite || {}).length;
      const aCount = Object.keys(DB.adjetivos || {}).length;
      const advCount = Object.keys(DB.adverbios || {}).length;
      const pCount = Object.keys(DB.particulas_e_afixos || {}).length;
      const dCount = Object.keys(DB.registro_diacronico_e_variantes || {}).length;
      const totalForms = (m.total_expanded_word_forms || 143353).toLocaleString("pt-BR");

      const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };

      setTxt("stat-nouns", nCount.toLocaleString("pt-BR"));
      setTxt("stat-verbs", (vRoots * 4).toLocaleString("pt-BR"));
      setTxt("stat-adjs", aCount.toLocaleString("pt-BR"));
      setTxt("stat-advs", advCount.toLocaleString("pt-BR"));
      setTxt("stat-forms", totalForms);

      setTxt("hero-stat-forms", totalForms);
      setTxt("hero-stat-nouns", nCount.toLocaleString("pt-BR"));
      setTxt("hero-stat-verbs", (vRoots * 4).toLocaleString("pt-BR"));
      setTxt("hero-stat-adjs", aCount.toLocaleString("pt-BR"));
      setTxt("hero-stat-advs", advCount.toLocaleString("pt-BR"));

      setTxt("hub-cnt-dict", totalForms);
      setTxt("hub-cnt-verbs", (vRoots * 4) + " Verbos");

      setTxt("tab-cnt-nouns", nCount);
      setTxt("tab-cnt-verbs", vRoots * 4);
      setTxt("tab-cnt-adjs", aCount);
      setTxt("tab-cnt-advs", advCount);
      setTxt("tab-cnt-part", pCount);
      setTxt("tab-cnt-diac", dCount);

      const omniInp = document.getElementById("omni-input");
      if (omniInp) {
        omniInp.placeholder = `Buscar em ${totalForms} formas (ex.: falde, vur, mild, pão, fogo, saittek, lareira, castelo)...`;
      }
      if (localStorage.getItem("CONDE_HERO_COLLAPSED") === "1") {
        const hero = document.getElementById("imperial-hero");
        const lbl = document.getElementById("btn-hero-collapse-label");
        if (hero) hero.classList.add("collapsed");
        if (lbl) lbl.textContent = "▼ Expandir Painel";
      }
    }"""

    html = html[:old_counters_fn.start()] + new_counters_fn + html[old_counters_fn.end():]
    print("[OK] updateHeaderCounters() corrigida com null-checks seguros.")

    # 7. Substituir handleOmniSearch, jumpToEntry e blocos duplicados de switchHub/quickSearch
    old_search_nav_block = re.search(
        r'// 5\. Busca Omni e Reconhecimento Morfológico Reverso[\s\S]*?// 6\. Renderização das Abas',
        html,
    )
    if not old_search_nav_block:
        raise RuntimeError("Não encontrou bloco 5 (Busca Omni e Navegação)")

    new_search_nav_block = """// 5. Busca Omni (Com Debounce de 100ms), Busca por Voz e Reconhecimento Morfológico Reverso
    function handleOmniSearch(val) {
      const cleanVal = (val || "").trim();
      const clearBtn = document.getElementById("btn-clear-search");
      if (clearBtn) clearBtn.style.display = cleanVal ? "inline-flex" : "none";
      clearTimeout(omniDebounceTimer);
      omniDebounceTimer = setTimeout(() => {
        searchQuery = cleanVal;
        nounDisplayLimit = 60;
        renderReverseMatches(searchQuery);
        renderActiveTab();
      }, 100);
    }

    function clearSearch() {
      const inp = document.getElementById("omni-input");
      if (!inp) return;
      inp.value = "";
      clearTimeout(omniDebounceTimer);
      searchQuery = "";
      nounDisplayLimit = 60;
      const clearBtn = document.getElementById("btn-clear-search");
      if (clearBtn) clearBtn.style.display = "none";
      renderReverseMatches("");
      renderActiveTab();
      inp.focus();
    }

    function startVoiceSearch() {
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      const btn = document.getElementById("btn-voice-omni");
      if (!SpeechRec) {
        showToast("🎙️ Dica: Use o botão 'Conversar por Voz (Whisper)' no Launcher Desktop!");
        return;
      }
      try {
        const rec = new SpeechRec();
        rec.lang = "pt-BR";
        rec.interimResults = false;
        rec.maxAlternatives = 1;
        if (btn) {
          btn.classList.add("listening");
          btn.innerHTML = "🔴 Ouvindo...";
        }
        rec.onresult = (event) => {
          const transcript = (event.results[0][0].transcript || "").replace(/[.,!?]/g, "").trim();
          const inp = document.getElementById("omni-input");
          if (inp && transcript) {
            inp.value = transcript;
            searchQuery = transcript;
            nounDisplayLimit = 60;
            const clearBtn = document.getElementById("btn-clear-search");
            if (clearBtn) clearBtn.style.display = "inline-flex";
            renderReverseMatches(searchQuery);
            renderActiveTab();
            showToast(`🎙️ Buscando por voz: "${transcript}"`);
          }
        };
        rec.onerror = () => {
          showToast("⚠️ Não foi possível capturar o áudio do microfone.");
        };
        rec.onend = () => {
          if (btn) {
            btn.classList.remove("listening");
            btn.innerHTML = "🎙️ Voz";
          }
        };
        rec.start();
      } catch (e) {
        showToast("⚠️ Microfone indisponível neste navegador.");
      }
    }

    function toggleHeroBanner() {
      const hero = document.getElementById("imperial-hero");
      const lbl = document.getElementById("btn-hero-collapse-label");
      if (!hero) return;
      const isCollapsed = hero.classList.toggle("collapsed");
      localStorage.setItem("CONDE_HERO_COLLAPSED", isCollapsed ? "1" : "0");
      if (lbl) lbl.textContent = isCollapsed ? "▼ Expandir Painel" : "▲ Recolher Painel";
    }

    function renderReverseMatches(q) {
      const box = document.getElementById("reverse-box");
      const grid = document.getElementById("reverse-grid");
      if (!box || !grid) return;
      if (!q || q.length < 2) {
        box.classList.remove("visible");
        grid.innerHTML = "";
        return;
      }

      const cleanQ = q.replace(/[!?]/g, "").toLowerCase();
      let matches = reverseIndex.get(cleanQ) || [];

      if (matches.length === 0) {
        box.classList.remove("visible");
        return;
      }

      box.classList.add("visible");
      grid.innerHTML = matches.map(m => `
        <div class="reverse-match-item">
          <div>
            <div style="font-family:var(--font-mono);font-weight:700;color:var(--gold-bright);font-size:0.95rem;">
              ${m.form} <span style="color:var(--text-secondary);font-weight:400;">←</span> <span style="color:var(--azure);">${m.lemma}</span>
            </div>
            <div style="font-size:0.78rem;color:var(--text-secondary);">
              <strong>${m.category}</strong> • ${m.tag}
            </div>
            <div style="font-size:0.78rem;color:var(--text-primary);">${m.meaning}</div>
          </div>
          <div class="card-micro-actions">
            <button class="micro-btn" onclick="speakTreppio('${m.form.replace(/'/g, "\\'")}')" title="Ouvir pronúncia">🔊</button>
            <button class="micro-btn" onclick="copyToClipboard('${m.form.replace(/'/g, "\\'")}')">📋</button>
            <button class="btn" onclick="jumpToEntry('${m.actionType}', '${m.actionKey.replace(/'/g, "\\'")}')">
              Ver Paradigma →
            </button>
          </div>
        </div>
      `).join("");
    }

    function jumpToEntry(type, key) {
      if (type === "noun") {
        openNounModal(key);
      } else if (type === "verb") {
        selectedVerbRoot = key;
        switchHub("verbs");
      } else if (type === "adj") {
        switchHub("dict", "adjectives");
      }
    }

    function quickSearch(term) {
      const inp = document.getElementById("omni-input");
      if (!inp) return;
      inp.value = term;
      clearTimeout(omniDebounceTimer);
      searchQuery = term.trim();
      nounDisplayLimit = 60;
      const clearBtn = document.getElementById("btn-clear-search");
      if (clearBtn) clearBtn.style.display = searchQuery ? "inline-flex" : "none";
      renderReverseMatches(searchQuery);
      switchHub("dict");
      inp.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function switchHub(hubId, optionalSubtab) {
      currentHub = hubId;
      if (optionalSubtab) {
        if (hubId === "dict") dictSubtab = optionalSubtab;
        if (hubId === "grammar") grammarSubtab = optionalSubtab;
      }
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.hub === hubId);
      });
      document.querySelectorAll(".mobile-nav-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.mobileHub === hubId);
      });
      renderActiveTab();
    }

    function setDictSubtab(sub) {
      dictSubtab = sub;
      renderActiveTab();
    }

    function setGrammarSubtab(sub) {
      grammarSubtab = sub;
      renderActiveTab();
    }

    function setCardViewMode(mode) {
      cardViewMode = mode;
      renderActiveTab();
    }

    function toggleCardForms(cardId) {
      const el = document.getElementById(cardId);
      const btn = document.getElementById('btn-toggle-' + cardId);
      if (!el) return;
      if (el.style.display === "none" || !el.style.display) {
        el.style.display = "block";
        if (btn) btn.innerHTML = "▲ Ocultar 18 Formas & Derivações";
      } else {
        el.style.display = "none";
        if (btn) btn.innerHTML = "📋 Ver 18 Formas & Derivações";
      }
    }

    function loadMoreNouns() {
      nounDisplayLimit += 60;
      renderActiveTab();
    }

    function switchTab(tabId) { switchHub(tabId); }

    // 6. Renderização das Abas"""

    html = html[:old_search_nav_block.start()] + new_search_nav_block + html[old_search_nav_block.end():]
    print("[OK] Funções de busca, voz, jumpToEntry e switchHub deduplicadas e atualizadas.")

    # 8. Substituir renderNounsTab e openNounModal com suporte real a Resumido/Detalhado, Ouvir/Copiar e Paginação de 60 itens
    old_nouns_block = re.search(
        r'// --- ABA I: SUBSTANTIVOS[\s\S]*?// --- ABA II: VERBOS',
        html,
    )
    if not old_nouns_block:
        raise RuntimeError("Não encontrou bloco ABA I: SUBSTANTIVOS")

    new_nouns_block = """// --- ABA I: SUBSTANTIVOS (COM PAGINAÇÃO PROGRESSIVA, MODO RESUMIDO/DETALHADO E ÁUDIO/CÓPIA) ---
    function renderNounsTab(container) {
      const entries = Object.entries(DB.substantivos || {});
      const letters = ["ALL", ..."ABCDEFGHIKLMNOPRSTVXY".split("")];
      const q = searchQuery.toLowerCase();

      const filtered = entries.filter(([lemma, obj]) => {
        if (selectedLetter !== "ALL" && lemma[0].toUpperCase() !== selectedLetter) return false;
        if (selectedDeclFilter !== "ALL" && String(obj.declinacao) !== selectedDeclFilter) return false;
        if (!q) return true;
        const inLemma = lemma.toLowerCase().includes(q);
        const inMean = obj.significado.toLowerCase().includes(q);
        const inEtym = obj.etimologia.toLowerCase().includes(q);
        const inForms = Object.values(obj.formas || {}).some(v => v.toLowerCase().includes(q));
        return inLemma || inMean || inEtym || inForms;
      });

      const visibleSlice = filtered.slice(0, nounDisplayLimit);
      const remaining = Math.max(0, filtered.length - visibleSlice.length);

      container.innerHTML = `
        <div class="filter-bar">
          <div class="card-view-toggle" title="Modo de exibição dos cartões">
            <button class="card-view-btn ${cardViewMode==='compact'?'active':''}" onclick="setCardViewMode('compact')">📱 Resumido</button>
            <button class="card-view-btn ${cardViewMode==='full'?'active':''}" onclick="setCardViewMode('full')">📋 Detalhado</button>
          </div>
          <div class="alpha-bar">
            ${letters.map(l => `
              <button class="alpha-btn ${selectedLetter === l ? 'active' : ''}" onclick="selectedLetter='${l}';nounDisplayLimit=60;renderActiveTab()">
                ${l === 'ALL' ? 'Todos' : l}
              </button>
            `).join("")}
          </div>
          <div style="display:flex;gap:0.4rem;align-items:center;">
            <button class="btn ${selectedDeclFilter==='ALL'?'btn-gold':''}" onclick="selectedDeclFilter='ALL';nounDisplayLimit=60;renderActiveTab()">Todas (${entries.length})</button>
            <button class="btn ${selectedDeclFilter==='1'?'btn-gold':''}" onclick="selectedDeclFilter='1';nounDisplayLimit=60;renderActiveTab()">1ª Decl. (-e/-a)</button>
            <button class="btn ${selectedDeclFilter==='2'?'btn-gold':''}" onclick="selectedDeclFilter='2';nounDisplayLimit=60;renderActiveTab()">2ª Decl. (Consonantal)</button>
          </div>
        </div>

        <div style="margin-bottom:0.75rem;font-size:0.84rem;color:var(--text-secondary);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
          <span>Exibindo <strong>${visibleSlice.length}</strong> de <strong>${filtered.length}</strong> substantivos filtrados (cada verbete com 8 casos declinados + 10 derivações sufixais).</span>
          <span style="font-size:0.78rem;color:var(--gold);">💡 Clique em 🔊 para ouvir a pronúncia ou em 📋 para copiar.</span>
        </div>

        <div class="cards-grid">
          ${visibleSlice.map(([lemma, obj], idx) => {
            const f = obj.formas;
            const badgeClass = obj.declinacao === 1 ? "badge-noun1" : "badge-noun2";
            const safeLemma = lemma.replace(/'/g, "\\'");
            const cardId = "noun-forms-" + idx;
            const isFull = cardViewMode === "full";
            return `
              <article class="entry-card">
                <div class="card-header">
                  <div>
                    <span class="lemma-title" style="cursor:pointer;" onclick="openNounModal('${safeLemma}')">${lemma}</span>
                    <span class="etym-text" style="margin-left:0.4rem;">${obj.etimologia}</span>
                  </div>
                  <div class="card-micro-actions">
                    <button class="micro-btn" onclick="speakTreppio('${safeLemma}')" title="Ouvir pronúncia Tréppia">🔊</button>
                    <button class="micro-btn" onclick="copyToClipboard('${safeLemma}', 'Copiado: ${safeLemma}')" title="Copiar lema">📋</button>
                    <button class="micro-btn" onclick="openNounModal('${safeLemma}')" title="Inspecionar paradigma completo">🔍</button>
                    <span class="pos-badge ${badgeClass}">${obj.declinacao}ª Decl.</span>
                  </div>
                </div>
                <div class="gloss-text">${obj.significado}</div>

                ${!isFull ? `
                  <div class="compact-cases-strip">
                    <div class="compact-case-item"><span>Nom. Sg</span><strong>${f["Nom.Sg"]}</strong></div>
                    <div class="compact-case-item"><span>Gen. Sg</span><strong>${f["Gen.Sg"]}</strong></div>
                    <div class="compact-case-item"><span>Nom. Pl</span><strong>${f["Nom.Pl"]}</strong></div>
                  </div>
                  <button class="btn-expand-forms" id="btn-toggle-${cardId}" onclick="toggleCardForms('${cardId}')">
                    📋 Ver 18 Formas & Derivações
                  </button>
                ` : ""}

                <div id="${cardId}" style="display:${isFull ? 'block' : 'none'};margin-top:0.55rem;">
                  <table class="mini-table">
                    <thead>
                      <tr><th>Número</th><th>Nom.</th><th>Gen.</th><th>Dat.</th><th>Acu.</th></tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th>Singular</th>
                        <td>${f["Nom.Sg"]}</td>
                        <td>${f["Gen.Sg"]}</td>
                        <td>${f["Dat.Sg"]}</td>
                        <td>${f["Acu.Sg"]}</td>
                      </tr>
                      <tr>
                        <th>Plural</th>
                        <td>${f["Nom.Pl"]}</td>
                        <td>${f["Gen.Pl"]}</td>
                        <td>${f["Dat.Pl"]}</td>
                        <td>${f["Acu.Pl"]}</td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="deriv-pills">
                    <span class="deriv-pill">Adj: <strong>${f["Adj(-a)"]}</strong></span>
                    <span class="deriv-pill">Adv: <strong>${f["Adv(-vë)"]}</strong></span>
                    <span class="deriv-pill">Sup: <strong>${f["Superl.Sg(-n)"]}/${f["Superl.Pl(-ni)"]}</strong></span>
                    <span class="deriv-pill">Lug: <strong>${f["Lugar(-ia)"]}</strong></span>
                    <span class="deriv-pill">Ag: <strong>${f["Agente(-te)"]}</strong></span>
                    <span class="deriv-pill">Abst: <strong>${f["Abstrato(-or)"]}</strong></span>
                    <span class="deriv-pill">Inst: <strong>${f["Instrum(-tek)"]}</strong></span>
                    <span class="deriv-pill">Dim: <strong>${f["Dimin(-il)"]}</strong></span>
                    <span class="deriv-pill">Aum: <strong>${f["Aument(-gar)"]}</strong></span>
                  </div>
                </div>
              </article>
            `;
          }).join("")}
        </div>

        ${remaining > 0 ? `
          <div class="load-more-container">
            <button class="btn-load-more" onclick="loadMoreNouns()">
              ⬇ Carregar mais substantivos (+${Math.min(60, remaining)} de ${remaining} restantes)
            </button>
          </div>
        ` : ""}
      `;
    }

    function openNounModal(lemma) {
      const obj = (DB.substantivos || {})[lemma];
      if (!obj) return;
      const f = obj.formas;
      const safeLemma = lemma.replace(/'/g, "\\'");
      document.getElementById("modal-title").innerHTML = `
        <span>${lemma} — Substantivo (${obj.declinacao}ª Declinação)</span>
        <button class="micro-btn" style="margin-left:0.6rem;" onclick="speakTreppio('${safeLemma}')">🔊 Ouvir</button>
        <button class="micro-btn" onclick="copyToClipboard('${safeLemma}')">📋 Copiar</button>
      `;
      document.getElementById("modal-body").innerHTML = `
        <p style="font-size:1.05rem;margin-bottom:0.5rem;"><strong>Significado:</strong> ${obj.significado}</p>
        <p style="margin-bottom:1rem;"><span class="etym-text">Etimologia: ${obj.etimologia}</span></p>
        <h4 style="color:var(--gold);margin-bottom:0.5rem;">1. Paradigma Casual Completo (Reforma Vocalizada V8.2)</h4>
        <table class="data-table" style="margin-bottom:1.25rem;">
          <thead><tr><th>Caso</th><th>Singular</th><th>Plural</th></tr></thead>
          <tbody>
            <tr><td><strong>Nominativo (Sujeito)</strong></td><td style="font-family:var(--font-mono);">${f["Nom.Sg"]}</td><td style="font-family:var(--font-mono);">${f["Nom.Pl"]}</td></tr>
            <tr><td><strong>Genitivo (Posse / Origem)</strong></td><td style="font-family:var(--font-mono);">${f["Gen.Sg"]}</td><td style="font-family:var(--font-mono);">${f["Gen.Pl"]}</td></tr>
            <tr><td><strong>Dativo (Obj. Indireto / ex, in)</strong></td><td style="font-family:var(--font-mono);">${f["Dat.Sg"]}</td><td style="font-family:var(--font-mono);">${f["Dat.Pl"]}</td></tr>
            <tr><td><strong>Acusativo (Obj. Direto / ad, in)</strong></td><td style="font-family:var(--font-mono);">${f["Acu.Sg"]}</td><td style="font-family:var(--font-mono);">${f["Acu.Pl"]}</td></tr>
          </tbody>
        </table>
        <h4 style="color:var(--gold);margin-bottom:0.5rem;">2. Matriz Derivacional Endógena (10 Sufixos Produtivos)</h4>
        <div class="deriv-pills">
          <span class="deriv-pill">Adjetivo (-a): <strong>${f["Adj(-a)"]}</strong></span>
          <span class="deriv-pill">Advérbio Modal (-vë): <strong>${f["Adv(-vë)"]}</strong></span>
          <span class="deriv-pill">Superlativo Sg (-n): <strong>${f["Superl.Sg(-n)"]}</strong></span>
          <span class="deriv-pill">Superlativo Pl (-ni): <strong>${f["Superl.Pl(-ni)"]}</strong></span>
          <span class="deriv-pill">Lugar (-ia): <strong>${f["Lugar(-ia)"]}</strong></span>
          <span class="deriv-pill">Agente (-te): <strong>${f["Agente(-te)"]}</strong></span>
          <span class="deriv-pill">Abstrato (-or): <strong>${f["Abstrato(-or)"]}</strong></span>
          <span class="deriv-pill">Instrumento (-tek): <strong>${f["Instrum(-tek)"]}</strong></span>
          <span class="deriv-pill">Diminutivo (-il): <strong>${f["Dimin(-il)"]}</strong></span>
          <span class="deriv-pill">Aumentativo (-gar): <strong>${f["Aument(-gar)"]}</strong></span>
        </div>
      `;
      document.getElementById("detail-modal").classList.add("open");
    }

    // --- ABA II: VERBOS"""

    html = html[:old_nouns_block.start()] + new_nouns_block + html[old_nouns_block.end():]
    print("[OK] renderNounsTab atualizada com paginação 60 cards, modo Resumido/Detalhado e botões Ouvir/Copiar.")

    # 9. Adicionar micro-botões Ouvir/Copiar nas falas de Diálogos Práticos
    old_dlg_fala = """                      <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--gold);font-weight:600;margin-bottom:0.35rem;">
                        👤 ${f.autor}
                      </div>"""
    new_dlg_fala = """                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;gap:0.5rem;flex-wrap:wrap;">
                        <span style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--gold);font-weight:600;">👤 ${f.autor}</span>
                        <div class="card-micro-actions">
                          <button class="micro-btn" onclick="speakTreppio('${f.treppio.replace(/'/g, "\\'")}')" title="Ouvir frase completa em Tréppio">🔊 Ouvir Fala</button>
                          <button class="micro-btn" onclick="copyToClipboard('${f.treppio.replace(/'/g, "\\'")}', 'Fala copiada!')" title="Copiar frase em Tréppio">📋 Copiar</button>
                        </div>
                      </div>"""
    if old_dlg_fala in html:
        html = html.replace(old_dlg_fala, new_dlg_fala, 1)
        print("[OK] Micro-botões Ouvir/Copiar adicionados aos Diálogos Práticos.")

    # 10. Corrigir Bug Crítico #1 (linha 3488: SyntaxError no registro do Service Worker) + atualizar speakTreppio/copyToClipboard com ponte Android
    old_sw_and_utils = re.search(
        r"if \('serviceWorker' in navigator[\s\S]*?</script>",
        html,
    )
    if not old_sw_and_utils:
        raise RuntimeError("Não encontrou o bloco final do Service Worker e utilitários antes de </script>")

    new_sw_and_utils = """if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
      navigator.serviceWorker.register('sw.js?v=8.2.0', { updateViaCache: 'none' })
        .then(function(reg) {
          reg.update();
          reg.addEventListener('updatefound', function() {
            var newWorker = reg.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', function() {
                if (newWorker.state === 'activated') {
                  console.log('[SW] Novo Service Worker V8.2 ativado.');
                }
              });
            }
          });
        })
        .catch(function() {});
    }

    // 8. Utilitários Interativos Modernos: Toast, Cópia e Síntese Fonética do Tréppio (Web Speech + Ponte Nativa Android APK)
    function speakTreppio(text) {
      if (!text) return;
      showToast(`🔊 Pronunciando: ${text}`);
      // 1º: Ponte Nativa Android WebView (TextToSpeech nativo do sistema Android)
      if (window.AndroidCondeBridge && typeof window.AndroidCondeBridge.speak === "function") {
        try {
          window.AndroidCondeBridge.speak(text);
          return;
        } catch (_) {}
      }
      // 2º: Web Speech API (Desktop / Mobile Browser)
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
      if (!text) return;
      if (window.AndroidCondeBridge && typeof window.AndroidCondeBridge.copy === "function") {
        try {
          window.AndroidCondeBridge.copy(text);
          showToast(msg || `Copiado: ${text}`);
          return;
        } catch (_) {}
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          showToast(msg || `Copiado: ${text}`);
        }).catch(() => {
          showToast(msg || `Copiado: ${text}`);
        });
      } else {
        showToast(msg || `Copiado: ${text}`);
      }
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
  </script>"""

    html = html[:old_sw_and_utils.start()] + new_sw_and_utils + html[old_sw_and_utils.end():]
    print("[OK] Bug crítico SyntaxError na linha 3488 corrigido e ponte AndroidCondeBridge integrada.")

    # 11. Remover a segunda barra mobile-bottom-nav duplicada no final do body
    nav_marker = "<!-- BARRA DE NAVEGAÇÃO INFERIOR PARA DISPOSITIVOS MÓVEIS (ANDROID APK / PWA) -->"
    first_nav = html.find(nav_marker)
    if first_nav != -1:
        second_nav = html.find(nav_marker, first_nav + len(nav_marker))
        if second_nav != -1:
            end_body = html.find("</body>", second_nav)
            if end_body != -1:
                html = html[:second_nav] + "\n</body>" + html[end_body + 7:]
                print("[OK] Barra mobile-bottom-nav duplicada removida.")

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[CONCLUÍDO] index.html atualizado ({orig_len:,} -> {len(html):,} bytes).")


if __name__ == "__main__":
    upgrade_index_html()

