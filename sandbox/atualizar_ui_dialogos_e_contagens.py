# -*- coding: utf-8 -*-
"""
atualizar_ui_dialogos_e_contagens.py
Atualiza index.html com as contagens de 44.585 formas, 
adiciona a aba XII de Diálogos Práticos da Era Antiga à Clássica e integra o reconhecimento morfológico interativo.
"""

import os

UI_INDEX_HTML = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"

with open(UI_INDEX_HTML, "r", encoding="utf-8") as f:
    src = f.read()

# 1. Atualizar placeholder e contadores
src = src.replace("37.769 formas", "44.585 formas")
src = src.replace("37.769 Formas", "44.585 Formas")
src = src.replace("46.531 formas", "44.585 formas")
src = src.replace("46.531 Formas", "44.585 Formas")

# 2. Adicionar Botão de Aba de Diálogos
tab_btn_dialogues = '''        <button class="tab-btn" data-tab="dialogues" onclick="switchTab('dialogues')">
          💬 XII. Diálogos Práticos (Era Clássica V8.1) <span class="tab-count">5 Cenas</span>
        </button>'''

if 'data-tab="dialogues"' not in src:
    target_needle = '<button class="tab-btn" data-tab="lab"'
    src = src.replace(target_needle, tab_btn_dialogues + "\n" + target_needle, 1)

# 3. Adicionar switch case na função renderActiveTab
switch_case_dial = '''        case "dialogues":
          renderDialoguesTab(container);
          break;'''

if 'case "dialogues":' not in src:
    target_switch = 'case "lab":'
    src = src.replace(target_switch, switch_case_dial + "\n        " + target_switch, 1)

# 4. Código da função renderDialoguesTab
dialogues_js = r'''
    // --- ABA XII: DIÁLOGOS PRÁTICOS E CONVERSAÇÃO COTIDIANA (ECOS DA ERA ANTIGA À CLÁSSICA) ---
    const ECOS_DIALOGUES = [
      {
        id: 1,
        titulo: "Cena I: Chegada à Estalagem sob a Nevasca (Talnes in Rixi)",
        subtitulo: "Diálogo de acolhida no calor da lareira de pedra após travessia na nevasca",
        falas: [
          { autor: "Tepatte (Estalajadeiro)", treppio: "Moba'el ad ti, trakte! Avurvé et fer in rixi vurba. Tep ny vuran esu!", pt: "Bom dia a ti, viajante! Gelo e vento rugiam na montanha. Nossa casa está aquecida!" },
          { autor: "Trakte (Viajante)", treppio: "Moba'el, Tepatte! Faldem et luttorom vurom pasum. Avur in vari em fassa.", pt: "Bom dia, senhor da estalagem! Preciso de pão e carne assada quente. O frio na estrada castigou-me." },
          { autor: "Tepatte (Estalajadeiro)", treppio: "In takej faldem et garvokom mobum! In vurrexi karem tor!", pt: "À mesa sirvo pão fresco e uma caneca de cerveja escura! Toma um assento junto à lareira!" },
          { autor: "Trakte (Viajante)", treppio: "Mobavë letum: faletom in tepi toruska? Post vesdakom falur pasum.", pt: "Peço-te com cortesia: tens um leito vago na casa? Após a ceia, repousar preciso." },
          { autor: "Tepatte (Estalajadeiro)", treppio: "Torum! Falet vuran in kardi esu. Zelta verreoi paror parru.", pt: "Tenho-o! Um leito aquecido aguarda no aposento superior. Por três moedas de bronze acertaremos o valor." }
        ]
      },
      {
        id: 2,
        titulo: "Cena II: Na Forja do Mestre Artífice (In Tekiai Tettey)",
        subtitulo: "Reparo da ferradura da montaria e encomenda de lâmina afiada",
        falas: [
          { autor: "Trakte (Viajante)", treppio: "Mobor ad ti, Tette! Poke ey in vari poketekom kossa. Tettek ty tekba ne?", pt: "Graça e paz a ti, mestre forjador! Minha montaria perdeu a ferradura no caminho pedregoso. Teu martelo está ativo?" },
          { autor: "Tette (Ferreiro)", treppio: "Vurrex tekba et verre vurran esu! Pokem in tepi tekur rukrum.", pt: "A forja trabalhava e o metal está incandescente! Posso ferrar o animal aqui na oficina." },
          { autor: "Trakte (Viajante)", treppio: "Sfammirom saidet et sfartekom pasum, nam rixer vela esu. Paror kanto esu?", pt: "Preciso também de uma espada afiada e um escudo, pois as serras são perigosas e sombrias. Quanto custará?" },
          { autor: "Tette (Ferreiro)", treppio: "Vexta verreoi sfammirom saidrum. Mobavë tekorom tekum!", pt: "Por cinco moedas de bronze afiarei a lâmina. Trabalho com lealdade e precisão!" }
        ]
      },
      {
        id: 3,
        titulo: "Cena III: A Travessia da Floresta com o Cão Loiro (Poke Xuna in Ecos)",
        subtitulo: "O encontro místico com o animal-guia luminoso através da bruma e do gelo",
        falas: [
          { autor: "Trakte (Viajante)", treppio: "Poke xuna! Alim ynus? In fervei lanom ty mirum.", pt: "Cão loiro e sagrado! Para onde andas? Através da névoa contemplo a tua aura luminosa." },
          { autor: "Interação", treppio: "Poke in filoxi keladba, et halkvestos ty in avurvéi ynnan.", pt: "O animal avançava pelo vale profundo, e nós seguimos tuas pegadas no chão gelado." },
          { autor: "Trakte (Viajante)", treppio: "Teggarom rixa mirum! In kadi kan durba, kora et avura. Litror kanye sukori ey keladu!", pt: "Avisto a fortaleza da montanha! No alto da colina ela resplandecia, antiga e coroada de gelo. A ressonância de seus ecos toca o meu coração!" }
        ]
      },
      {
        id: 4,
        titulo: "Cena IV: À Beira das Brasas na Vigília da Noite (In Vildori)",
        subtitulo: "Diálogo meditativo entre dois companheiros de jornada no silêncio invernal",
        falas: [
          { autor: "Fratror (Companheiro 1)", treppio: "Mobanir ad ti, fratr. Avura fer in filoxi vurba, ta vurrex kan vildorom mobu.", pt: "Boa noite a ti, companheiro. O vento gélido rugia no vale, mas esta lareira nos concede brasas acolhedoras." },
          { autor: "Zenor (Companheiro 2)", treppio: "Zo es! Sambel falur pasum, ad ke beloroi in varom trakan. Mobor ad tepi san!", pt: "Assim é! Esta noite preciso repousar, para que na alvorada marchemos pela estrada. Que a paz permaneça nesta casa!" }
        ]
      },
      {
        id: 5,
        titulo: "Cena V: Repertório e Fórmulas de Sobrevivência (Lete Pratika)",
        subtitulo: "Expressões usuais imediatas, comandos de estrada e pedidos na estalagem",
        falas: [
          { autor: "Saudação Canônica", treppio: "Moba'el ad ti! / Mobanir! / Lamir!", pt: "Bom dia a ti! / Boa noite! / Noite clara de luar!" },
          { autor: "Bênção e Voto", treppio: "Mobor ad ti! / Zo es!", pt: "Paz e graça a ti! / Assim seja! (De acordo)" },
          { autor: "Alimento e Fogo", treppio: "Faldem et Véom pasum. / Vurem in vurrexi mob!", pt: "Preciso de pão e água pura. / Dá-nos o calor da lareira!" },
          { autor: "Orientação e Direção", treppio: "Alim var ad teggarom ynnu? / In vari trakan.", pt: "Onde o caminho conduz à fortaleza? / Marchemos pela estrada." }
        ]
      }
    ];

    function renderDialoguesTab(container) {
      container.innerHTML = `
        <div style="margin-bottom:1.25rem;background:var(--bg-secondary);padding:1.15rem 1.5rem;border-radius:12px;border:1px solid var(--border-gold);box-shadow:var(--shadow);">
          <h2 style="font-family:var(--font-serif);color:var(--gold-bright);font-size:1.6rem;margin-bottom:0.4rem;">
            💬 Diálogos Práticos e Conversação Cotidiana (Era Clássica V8.1)
          </h2>
          <p style="color:var(--text-secondary);font-size:0.95rem;line-height:1.6;">
            Resultado de <strong>1.500 anos de evolução da Era Antiga para a Clássica V8.1</strong>: a linguagem prática do dia a dia no cenário de <em>Ecos de Uma Vida Perdida</em> com sintaxe V2, dativo vocalizado e rigor eufônico canônico. Clique em <strong>qualquer vocábulo em Tréppio</strong> para inspecionar instantaneamente suas raízes e casos no léxico de 44.585 formas!
          </p>
        </div>

        <div style="display:flex;flex-direction:column;gap:1.5rem;">
          ${ECOS_DIALOGUES.map(d => `
            <div class="gnlt-chapter-card">
              <div class="gnlt-card-header">
                <div>
                  <h3 style="font-size:1.2rem;color:var(--gold-bright);">${d.titulo}</h3>
                  <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.2rem;">${d.subtitulo}</div>
                </div>
                <span class="gnlt-badge">Trepiano Clássico V8.1</span>
              </div>
              <div class="gnlt-card-body" style="display:flex;flex-direction:column;gap:1rem;">
                ${d.falas.map(f => {
                  const tokenized = f.treppio.split(/(\s+)/).map(tok => {
                    if (/^\s+$/.test(tok)) return tok;
                    const clean = tok.replace(/[.,;:!?]/g, "");
                    return `<span class="corpus-word" onclick="inspectCorpusWord('${clean.replace(/'/g, "\\'")}')">${tok}</span>`;
                  }).join("");
                  return `
                    <div style="background:var(--bg-primary);border:1px solid var(--border-color);border-radius:8px;padding:0.9rem 1.15rem;">
                      <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--gold);font-weight:600;margin-bottom:0.35rem;">
                        👤 ${f.autor}
                      </div>
                      <div style="font-family:var(--font-serif);font-size:1.15rem;color:var(--gold-bright);line-height:1.6;">
                        ${tokenized}
                      </div>
                      <div style="font-size:0.92rem;color:var(--text-secondary);margin-top:0.4rem;border-top:1px dashed var(--border-color);padding-top:0.4rem;">
                        <strong>PT:</strong> ${f.pt}
                      </div>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>
          `).join("")}
        </div>
      `;
    }
'''

if "function renderDialoguesTab" not in src:
    target_pos = "// 7. Utilit"
    src = src.replace(target_pos, dialogues_js + "\n" + target_pos, 1)

with open(UI_INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(src)

print("sandbox/ui_dicionario/index.html atualizado com sucesso com os Diálogos e Novas Contagens!")
