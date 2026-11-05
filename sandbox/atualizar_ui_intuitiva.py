# -*- coding: utf-8 -*-
"""
atualizar_ui_intuitiva.py
Reformula a UI de index.html para máxima intuitividade, simplicidade e ergonomia:
  1. 5 Hubs Principais (Dicionário, Verbos, Diálogos, Gramática, Laboratório)
  2. Mobile Bottom Navigation Bar (Android APK / PWA)
  3. Header Compacto com Stats Pill elegante
  4. Barra de Acesso Rápido com Chips de 1 clique (falde, vur, Vé, sfammir, Tette, poke xuna, etc.)
  5. Alternador de Modo de Visualização nos Cards (Resumido x Completo)
  6. Sub-hub filters fluidos e instantâneos
"""

import os
import re

UI_HTML = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"

with open(UI_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# ---------------------------------------------------------------------------
# 1. NOVOS ESTILOS CSS (HEADER COMPACTO, STATS PILL, BOTTOM BAR, QUICK CHIPS)
# ---------------------------------------------------------------------------
NEW_STYLES = """
    /* ==========================================================================
       NOVA ERGONOMIA: STATS PILL, QUICK CHIPS, SUB-HUBS E MOBILE BOTTOM NAV
       ========================================================================== */
    .stats-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.55rem;
      background: var(--bg-card);
      border: 1px solid var(--border-gold);
      padding: 0.35rem 0.85rem;
      border-radius: 999px;
      font-size: 0.82rem;
      color: var(--text-secondary);
      box-shadow: var(--shadow-sm);
      user-select: none;
    }

    .pill-sep {
      color: var(--border-gold);
      opacity: 0.6;
    }

    .stats-pill strong {
      color: var(--gold-bright);
      font-family: var(--font-mono);
    }

    .search-quick-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      align-items: center;
      margin-top: 0.25rem;
      padding: 0 0.25rem;
    }

    .quick-chip-label {
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--gold);
      letter-spacing: 0.03em;
      text-transform: uppercase;
      margin-right: 0.2rem;
    }

    .quick-chip {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 0.22rem 0.65rem;
      border-radius: 999px;
      font-size: 0.78rem;
      font-family: var(--font-sans);
      cursor: pointer;
      transition: all var(--transition-fast);
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }

    .quick-chip:hover {
      background: var(--bg-card-hover);
      border-color: var(--gold);
      color: var(--gold-bright);
      transform: translateY(-1px);
      box-shadow: var(--shadow-sm);
    }

    /* Sub-Hub Filter Bar */
    .subhub-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      align-items: center;
      background: var(--bg-secondary);
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-color);
      margin-bottom: 1.25rem;
    }

    .subhub-chip {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      padding: 0.35rem 0.75rem;
      border-radius: var(--radius-md);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--transition-fast);
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }

    .subhub-chip:hover {
      background: var(--bg-card-hover);
      color: var(--text-primary);
      border-color: var(--border-color);
    }

    .subhub-chip.active {
      background: var(--gold);
      color: #0c0e14;
      border-color: var(--gold-bright);
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(226, 185, 75, 0.35);
    }

    /* Alternador de Modo de Cards (Resumido / Detalhado) */
    .card-view-toggle {
      display: inline-flex;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 2px;
      gap: 2px;
    }

    .card-view-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 0.3rem 0.7rem;
      border-radius: var(--radius-sm);
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .card-view-btn.active {
      background: var(--bg-card-elevated);
      color: var(--gold-bright);
      font-weight: 700;
      box-shadow: var(--shadow-sm);
    }

    /* Botão de Expansão no Card Resumido */
    .btn-expand-forms {
      margin-top: 0.65rem;
      width: 100%;
      background: var(--bg-secondary);
      border: 1px dashed var(--border-color);
      color: var(--gold-bright);
      padding: 0.4rem 0.8rem;
      border-radius: var(--radius-md);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.35rem;
      transition: all var(--transition-fast);
    }

    .btn-expand-forms:hover {
      background: var(--bg-accent-hover);
      border-color: var(--gold);
      color: var(--text-primary);
    }

    /* Mobile Bottom Navigation Bar (Fixo para telas < 768px) */
    .mobile-bottom-nav {
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 60px;
      background: rgba(12, 16, 26, 0.94);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-top: 1.5px solid var(--border-gold);
      z-index: 9999;
      justify-content: space-around;
      align-items: center;
      padding: 0 0.5rem;
      box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.35);
    }

    [data-theme="light"] .mobile-bottom-nav {
      background: rgba(250, 246, 236, 0.96);
    }

    .mobile-nav-btn {
      flex: 1;
      height: 100%;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
      cursor: pointer;
      transition: all var(--transition-fast);
      user-select: none;
    }

    .mobile-nav-icon {
      font-size: 1.25rem;
      line-height: 1;
    }

    .mobile-nav-label {
      font-size: 0.68rem;
      font-weight: 600;
      font-family: var(--font-sans);
      letter-spacing: 0.02em;
    }

    .mobile-nav-btn.active {
      color: var(--gold-bright);
    }

    .mobile-nav-btn.active .mobile-nav-icon {
      transform: scale(1.15);
      filter: drop-shadow(0 0 8px rgba(226, 185, 75, 0.6));
    }

    @media (max-width: 768px) {
      .mobile-bottom-nav {
        display: flex;
      }
      body {
        padding-bottom: 72px; /* espaço para não cobrir conteúdo */
      }
      .nav-tabs {
        display: none; /* oculta tabs redundantes no topo móvel */
      }
      .stats-pill {
        display: none; /* cabeçalho super compacto */
      }
      .search-quick-chips {
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-bottom: 0.25rem;
        scrollbar-width: none;
      }
      .search-quick-chips::-webkit-scrollbar {
        display: none;
      }
    }
"""

# Injetar estilos antes de </style>
html = html.replace("  </style>", NEW_STYLES + "\n  </style>")

# ---------------------------------------------------------------------------
# 2. NOVO CABEÇALHO COMPACTO E NOVO NAV DOS 5 HUBS
# ---------------------------------------------------------------------------
OLD_HEADER_REGEX = re.compile(
    r'<div class="header-actions">.*?</div>\s*</div>\s*<div class="search-and-tabs">.*?<nav class="nav-tabs" id="main-tabs">.*?</nav>\s*</div>',
    re.DOTALL
)

NEW_HEADER_AND_HUBS = """      <div class="header-actions">
        <div class="stats-pill" title="Total de Formas e Classes Gramaticais Oficiais">
          <span class="pulse-dot"></span>
          <span><strong id="stat-forms">56.342</strong> Formas</span>
          <span class="pill-sep">•</span>
          <span><strong id="stat-nouns">453</strong> Nomes</span>
          <span class="pill-sep">•</span>
          <span><strong id="stat-verbs">408</strong> Verbos</span>
          <span class="pill-sep">•</span>
          <span><strong id="stat-adjs">102</strong> Adjs</span>
        </div>
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
          placeholder="Buscar em 56.342 formas (ex.: falde, vur, mild, pão, fogo, saittek, lareira, castelo)..."
          oninput="handleOmniSearch(this.value)"
        />
        <button class="btn" onclick="clearSearch()" id="btn-clear-search" style="display:none;">Limpar</button>
        <span class="kbd-hint">Tecla /</span>
      </div>

      <div class="search-quick-chips">
        <span class="quick-chip-label">⚡ Acesso Rápido:</span>
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

      <!-- 5 HUBS PRINCIPAIS E COESOS -->
      <nav class="nav-tabs" id="main-tabs">
        <button class="tab-btn active" data-hub="dict" onclick="switchHub('dict')">
          🔍 I. Dicionário Geral <span class="tab-count" id="hub-cnt-dict">56.342</span>
        </button>
        <button class="tab-btn" data-hub="verbs" onclick="switchHub('verbs')">
          ⚔️ II. Conjugador Verbal <span class="tab-count">408 Verbos</span>
        </button>
        <button class="tab-btn" data-hub="dialogues" onclick="switchHub('dialogues')">
          💬 III. Diálogos Práticos <span class="tab-count">5 Cenas</span>
        </button>
        <button class="tab-btn" data-hub="grammar" onclick="switchHub('grammar')">
          📜 IV. Gramática & Corpus <span class="tab-count">GNLT + Ainulindalë</span>
        </button>
        <button class="tab-btn" data-hub="lab" onclick="switchHub('lab')">
          ⚗️ V. Laboratório Sandi V8.1
        </button>
      </nav>
    </div>"""

html = OLD_HEADER_REGEX.sub(NEW_HEADER_AND_HUBS, html)

# ---------------------------------------------------------------------------
# 3. ADICIONAR MOBILE BOTTOM NAV ANTES DE </body>
# ---------------------------------------------------------------------------
BOTTOM_NAV_HTML = """
  <!-- BARRA DE NAVEGAÇÃO INFERIOR PARA DISPOSITIVOS MÓVEIS (ANDROID APK / PWA) -->
  <nav class="mobile-bottom-nav">
    <button class="mobile-nav-btn active" data-mobile-hub="dict" onclick="switchHub('dict')">
      <span class="mobile-nav-icon">🔍</span>
      <span class="mobile-nav-label">Dicionário</span>
    </button>
    <button class="mobile-nav-btn" data-mobile-hub="verbs" onclick="switchHub('verbs')">
      <span class="mobile-nav-icon">⚔️</span>
      <span class="mobile-nav-label">Conjugador</span>
    </button>
    <button class="mobile-nav-btn" data-mobile-hub="dialogues" onclick="switchHub('dialogues')">
      <span class="mobile-nav-icon">💬</span>
      <span class="mobile-nav-label">Diálogos</span>
    </button>
    <button class="mobile-nav-btn" data-mobile-hub="grammar" onclick="switchHub('grammar')">
      <span class="mobile-nav-icon">📜</span>
      <span class="mobile-nav-label">Gramática</span>
    </button>
    <button class="mobile-nav-btn" data-mobile-hub="lab" onclick="switchHub('lab')">
      <span class="mobile-nav-icon">⚗️</span>
      <span class="mobile-nav-label">Lab Sandi</span>
    </button>
  </nav>
"""

html = html.replace("</body>", BOTTOM_NAV_HTML + "\n</body>")

# ---------------------------------------------------------------------------
# 4. ATUALIZAR O ESTADO JS E A FUNÇÃO SWITCHHUB & RENDERACTIVETAB
# ---------------------------------------------------------------------------
JS_STATE_TARGET = "let currentTab = \"nouns\";"
NEW_JS_STATE = """let currentHub = "dict";
    let dictSubtab = "nouns";
    let grammarSubtab = "gnlt";
    let cardViewMode = "compact"; // "compact" ou "full"
"""

html = html.replace(JS_STATE_TARGET, NEW_JS_STATE)

# Funções switchHub, setDictSubtab, setGrammarSubtab, quickSearch, toggleCardForms
NEW_HUB_LOGIC = """
    function quickSearch(term) {
      const inp = document.getElementById("omni-input");
      if (!inp) return;
      inp.value = term;
      handleOmniSearch(term);
      switchHub("dict");
      inp.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function switchHub(hubId, optionalSubtab) {
      currentHub = hubId;
      if (optionalSubtab) {
        if (hubId === "dict") dictSubtab = optionalSubtab;
        if (hubId === "grammar") grammarSubtab = optionalSubtab;
      }
      // Atualizar botões desktop
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.hub === hubId);
      });
      // Atualizar botões mobile
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
        if (btn) btn.innerHTML = "▲ Ocultar 18 Formas";
      } else {
        el.style.display = "none";
        if (btn) btn.innerHTML = "📋 Ver 18 Formas & Derivações";
      }
    }
"""

html = html.replace("function switchTab(tabId) {", NEW_HUB_LOGIC + "\n    function switchTab(tabId) { switchHub(tabId); }\n    function old_switchTab(tabId) {")

# Atualizar renderActiveTab para despachar pelos 5 Hubs
OLD_RENDER_ACTIVE_REGEX = re.compile(r'function renderActiveTab\(\) \{.*?switch \(currentTab\) \{.*?\}\s*\}', re.DOTALL)

NEW_RENDER_ACTIVE = """function renderActiveTab() {
      const container = document.getElementById("tab-content");
      if (!DB || !container) return;

      switch (currentHub) {
        case "dict":
          renderDictHub(container);
          break;
        case "verbs":
          renderVerbsTab(container);
          break;
        case "dialogues":
          renderDialoguesTab(container);
          break;
        case "grammar":
          renderGrammarHub(container);
          break;
        case "lab":
          renderLabTab(container);
          break;
        default:
          renderDictHub(container);
      }
    }

    function renderDictHub(container) {
      const nCount = Object.keys(DB.substantivos || {}).length;
      const aCount = Object.keys(DB.adjetivos || {}).length;
      const advCount = Object.keys(DB.adverbios || {}).length;
      const pCount = Object.keys(DB.particulas_e_afixos || {}).length;
      const dCount = Object.keys(DB.registro_diacronico_e_variantes || {}).length;

      const subhubBar = `
        <div class="subhub-bar">
          <button class="subhub-chip ${dictSubtab==='nouns'?'active':''}" onclick="setDictSubtab('nouns')">
            🏛️ Substantivos (${nCount})
          </button>
          <button class="subhub-chip ${dictSubtab==='adjectives'?'active':''}" onclick="setDictSubtab('adjectives')">
            ✨ Adjetivos (${aCount})
          </button>
          <button class="subhub-chip ${dictSubtab==='adverbs'?'active':''}" onclick="setDictSubtab('adverbs')">
            🧭 Advérbios (${advCount})
          </button>
          <button class="subhub-chip ${dictSubtab==='pronouns'?'active':''}" onclick="setDictSubtab('pronouns')">
            👑 Pronomes (7)
          </button>
          <button class="subhub-chip ${dictSubtab==='numerals'?'active':''}" onclick="setDictSubtab('numerals')">
            🔢 Numerais (12)
          </button>
          <button class="subhub-chip ${dictSubtab==='particles'?'active':''}" onclick="setDictSubtab('particles')">
            🔗 Partículas (${pCount})
          </button>
          <button class="subhub-chip ${dictSubtab==='diachronic'?'active':''}" onclick="setDictSubtab('diachronic')">
            📜 Diacrônico (${dCount})
          </button>
        </div>
      `;

      container.innerHTML = subhubBar + '<div id="dict-subcontent"></div>';
      const subContainer = document.getElementById("dict-subcontent");

      switch (dictSubtab) {
        case "nouns":
          renderNounsTab(subContainer);
          break;
        case "adjectives":
          renderAdjectivesTab(subContainer);
          break;
        case "adverbs":
          renderAdverbsTab(subContainer);
          break;
        case "pronouns":
          renderPronounsTab(subContainer);
          break;
        case "numerals":
          renderNumeralsTab(subContainer);
          break;
        case "particles":
          renderParticlesTab(subContainer);
          break;
        case "diachronic":
          renderDiachronicTab(subContainer);
          break;
        default:
          renderNounsTab(subContainer);
      }
    }

    function renderGrammarHub(container) {
      const subhubBar = `
        <div class="subhub-bar">
          <button class="subhub-chip ${grammarSubtab==='gnlt'?'active':''}" onclick="setGrammarSubtab('gnlt')">
            📜 GNLT — Gramática Normativa (8 Capítulos)
          </button>
          <button class="subhub-chip ${grammarSubtab==='corpus'?'active':''}" onclick="setGrammarSubtab('corpus')">
            📖 Halylitror (Ainulindalë) & Corpus Litúrgico
          </button>
        </div>
      `;

      container.innerHTML = subhubBar + '<div id="grammar-subcontent"></div>';
      const subContainer = document.getElementById("grammar-subcontent");

      if (grammarSubtab === "gnlt") {
        renderGnltTab(subContainer);
      } else {
        renderCorpusTab(subContainer);
      }
    }"""

html = OLD_RENDER_ACTIVE_REGEX.sub(NEW_RENDER_ACTIVE, html)

# ---------------------------------------------------------------------------
# 5. ATUALIZAR CARDS DE SUBSTANTIVOS COM MODO RESUMIDO E EXPANSÃO INTUITIVA
# ---------------------------------------------------------------------------
OLD_CARD_TABLE_REGEX = re.compile(
    r'<table class="mini-table">.*?</div>\s*</article>',
    re.DOTALL
)

# Substituir dentro de renderNounsTab para ter alternador e expansão suave
OLD_NOUNS_FILTER_BAR = """      container.innerHTML = `
        <div class="filter-bar">"""

NEW_NOUNS_FILTER_BAR = """      container.innerHTML = `
        <div class="filter-bar">
          <div class="card-view-toggle" title="Modo de exibição dos cartões">
            <button class="card-view-btn ${cardViewMode==='compact'?'active':''}" onclick="setCardViewMode('compact')">📱 Resumido</button>
            <button class="card-view-btn ${cardViewMode==='full'?'active':''}" onclick="setCardViewMode('full')">📋 Detalhado</button>
          </div>"""

html = html.replace(OLD_NOUNS_FILTER_BAR, NEW_NOUNS_FILTER_BAR)

# Atualizar renderização do card de substantivo
OLD_NOUN_CARD_SNIPPET = """            return `
              <article class="entry-card">
                <div class="card-header">
                  <div>
                    <span class="lemma-title">${lemma}</span>
                    <span class="etym-text" style="margin-left:0.4rem;">${obj.etimologia}</span>
                  </div>
                  <span class="pos-badge ${badgeClass}">${obj.declinacao}ª Decl.</span>
                </div>
                <div class="gloss-text">${obj.significado}</div>
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
                </div>
              </article>
            `;"""

NEW_NOUN_CARD_SNIPPET = """            const cardId = "card-forms-" + lemma.replace(/[^a-zA-Z0-9]/g, "_");
            const isFull = (cardViewMode === "full");
            return `
              <article class="entry-card">
                <div class="card-header">
                  <div>
                    <span class="lemma-title">${lemma}</span>
                    <span class="etym-text" style="margin-left:0.4rem;">${obj.etimologia}</span>
                  </div>
                  <span class="pos-badge ${badgeClass}">${obj.declinacao}ª Decl.</span>
                </div>
                <div class="gloss-text">${obj.significado}</div>
                
                <div id="${cardId}" style="display:${isFull ? 'block' : 'none'};">
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
                  </div>
                </div>

                ${!isFull ? `
                  <button class="btn-expand-forms" id="btn-toggle-${cardId}" onclick="toggleCardForms('${cardId}')">
                    📋 Ver 18 Formas & Derivações
                  </button>
                ` : ''}
              </article>
            `;"""

html = html.replace(OLD_NOUN_CARD_SNIPPET, NEW_NOUN_CARD_SNIPPET)

# Atualizar jumpToEntry
OLD_JUMP = """      if (type === "noun") {
        selectedLetter = key[0].toUpperCase();
        switchTab("nouns");
        setTimeout(() => openNounModal(key), 120);
      } else if (type === "verb") {
        selectedVerbRoot = key;
        switchTab("verbs");
      } else if (type === "adj") {
        switchTab("adjectives");
      }"""

NEW_JUMP = """      if (type === "noun") {
        selectedLetter = key[0].toUpperCase();
        switchHub("dict", "nouns");
        setTimeout(() => openNounModal(key), 120);
      } else if (type === "verb") {
        selectedVerbRoot = key;
        switchHub("verbs");
      } else if (type === "adj") {
        switchHub("dict", "adjectives");
      }"""

html = html.replace(OLD_JUMP, NEW_JUMP)

with open(UI_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("sandbox/ui_dicionario/index.html atualizado com sucesso!")

