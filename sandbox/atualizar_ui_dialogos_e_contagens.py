# -*- coding: utf-8 -*-
"""
atualizar_ui_dialogos_e_contagens.py
Atualiza index.html com as novas contagens de 46.531 formas, 
adiciona a aba XII de Diálogos Práticos de Ecos e integra o reconhecimento morfológico interativo.
"""

import os

UI_INDEX_HTML = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"

with open(UI_INDEX_HTML, "r", encoding="utf-8") as f:
    src = f.read()

# 1. Atualizar placeholder e contadores
src = src.replace("37.769 formas", "46.531 formas")
src = src.replace("37.769 Formas", "46.531 Formas")
src = src.replace('id="tab-cnt-nouns">310<', 'id="tab-cnt-nouns">380<')
src = src.replace('id="tab-cnt-verbs">272<', 'id="tab-cnt-verbs">336<')
src = src.replace('id="tab-cnt-adjs">68<', 'id="tab-cnt-adjs">82<')
src = src.replace('id="tab-cnt-advs">74<', 'id="tab-cnt-advs">84<')

# 2. Adicionar Botão de Aba de Diálogos
tab_btn_dialogues = '''        <button class="tab-btn" data-tab="dialogues" onclick="switchTab('dialogues')">
          💬 XII. Diálogos Práticos (Ecos 1.500 Anos) <span class="tab-count">5 Cenas</span>
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
    // --- ABA XII: DIÁLOGOS PRÁTICOS E CONVERSAÇÃO COTIDIANA (ECOS 1.500 ANOS) ---
    const ECOS_DIALOGUES = [
      {
        id: 1,
        titulo: "Cena I: O Encontro na Neve e o Cão Dourado Guia",
        subtitulo: "Diálogo de aproximação nas florestas de coníferas de Ecos de Uma Vida Perdida",
        falas: [
          { autor: "Viajante", treppio: "Alen, amiko! Fessan esum, et in nive erram. Sano kastar lonta es?", pt: "Olá, amigo! Estou exausto e perdido na neve. Aquele castelo fica longe?" },
          { autor: "Caçador", treppio: "Alen! Ne, lonta ne es. Kanis lauri mirate: kan stradam isan is!", pt: "Olá! Não, não fica longe. Olha o cão dourado: ele conhece o caminho!" },
          { autor: "Viajante", treppio: "Kanis sani kurrur vult? Ad me venit et cauda movet.", pt: "O cachorro quer correr para cá? Ele vem até mim e abana a cauda." },
          { autor: "Caçador", treppio: "Yo, to gizzat! Kan hospitos amet. Ko no ambulate, antequam nox veniat.", pt: "Sim, ele gosta de ti! Ele ama os hóspedes. Caminha conosco, antes que a noite caia." },
          { autor: "Viajante", treppio: "Hallen to! Frigor me ferit, sed kordis meus calescit.", pt: "Obrigado! O frio me castiga, mas meu coração se aquece." }
        ]
      },
      {
        id: 2,
        titulo: "Cena II: Na Estalagem e ao Redor da Lareira Crepitante",
        subtitulo: "Ceia quente, vinho com especiarias e reserva de aposento aquecido",
        falas: [
          { autor: "Estalajadeiro", treppio: "Vesen, hospit! Ad kamin kaldan sedute. Quid mandur et bibur vulte?", pt: "Boa noite, hóspede! Senta-te junto à lareira quente. O que queres comer e beber?" },
          { autor: "Viajante", treppio: "Doban, fammor grando habeum. Broda calida, panna et vinor ruber dote.", pt: "Por favor, tenho muita fome. Dá-me caldo quente, pão e vinho tinto." },
          { autor: "Estalajadeiro", treppio: "Optime! Karna assada et kaso de capra quoque habeo. Cito serviam.", pt: "Excelente! Também tenho carne assada e queijo de cabra. Servirei depressa." },
          { autor: "Viajante", treppio: "Et lektar pro nocte reservatum habeo? Vellum spissum postulo.", pt: "E tenho um leito reservado para a noite? Peço um cobertor grosso." },
          { autor: "Estalajadeiro", treppio: "Stuba supera pura et calda est. In argen duo pagas.", pt: "O quarto de cima é limpo e aquecido. Pagas duas moedas de prata." },
          { autor: "Viajante", treppio: "Argeneos duos dobo. Clavem mihi concede.", pt: "Dou-te duas moedas de prata. Concede-me a chave." }
        ]
      },
      {
        id: 3,
        titulo: "Cena III: Negociando com o Ferreiro da Aldeia",
        subtitulo: "Ferraduras para o cavalo e forja de lâmina resistente",
        falas: [
          { autor: "Comprador", treppio: "Alen, ferrar! Equo meo novum ferrum postulo, et cultam fortem.", pt: "Olá, ferreiro! Preciso de ferro novo para o meu cavalo, e de uma faca forte." },
          { autor: "Ferreiro", treppio: "Hanc cultam ferream mirate: solida est, et in lapide non frangitur.", pt: "Olha esta faca de ferro: é sólida, e não se quebra na pedra." },
          { autor: "Comprador", treppio: "Kanto preti est? Nimis cara ne sit!", pt: "Quanto custa? Que não seja cara demais!" },
          { autor: "Ferreiro", treppio: "Quinque kupros pro culta, et decem pro ferratura equi.", pt: "Cinco moedas de cobre pela faca, e dez pela ferradura do cavalo." },
          { autor: "Comprador", treppio: "Quattuordecim kupros offero, et statim in manu trado.", pt: "Ofereço catorze cobres, e entrego-os imediatamente na tua mão." },
          { autor: "Ferreiro", treppio: "Concordia est! Accipio, et opus hodie finiam.", pt: "De acordo! Aceito, e terminarei o trabalho ainda hoje." }
        ]
      },
      {
        id: 4,
        titulo: "Cena IV: Madrugada e Reflexão junto às Brasas",
        subtitulo: "Memória, nostalgia de tempos idos e a promessa da aurora boreal",
        falas: [
          { autor: "Viajante 1", treppio: "Non dormis, frater? Ventus foris per pineta sibilat.", pt: "Não dormes, meu irmão? O vento lá fora sibila por entre os pinheiros." },
          { autor: "Viajante 2", treppio: "Nostal me tenet. De patria et de temporibus antiquis cogito.", pt: "A nostalgia me prende. Penso na pátria e nos tempos antigos." },
          { autor: "Viajante 1", treppio: "Memoria dulce et amara est. Sed aurora cito veniet.", pt: "A memória é doce e amarga. Mas a aurora logo virá." },
          { autor: "Viajante 2", treppio: "Yo. Stella matutina jam in caelo lucet. Spes non moritur.", pt: "Sim. A estrela da manhã já brilha no céu. A esperança não morre." },
          { autor: "Viajante 1", treppio: "Esu! Brandorem ultimum suscitemus, et ad iter nos paremus.", pt: "Que assim seja! Reavivemos a última brasa, e preparemo-nos para a jornada." }
        ]
      },
      {
        id: 5,
        titulo: "Cena V: Guia Rápido de Sobrevivência e Expressões Usuais",
        subtitulo: "Comandos imediatos, saudações e pedidos cotidianos",
        falas: [
          { autor: "Saudação", treppio: "Alen omnibus! / In pace vadite!", pt: "Olá a todos! / Ide em paz!" },
          { autor: "Gratidão", treppio: "Hallen multam to dote! / Doban, aquam dote.", pt: "Muito obrigado a ti! / Por favor, dai-me água." },
          { autor: "Localização", treppio: "Ubi stuba est? / Nivis cadit cito.", pt: "Onde fica o quarto? / A neve está caindo depressa." },
          { autor: "Sentimento", treppio: "Kordis meus laetus est. / Dormire cupio.", pt: "Meu coração está alegre. / Desejo dormir." }
        ]
      }
    ];

    function renderDialoguesTab(container) {
      container.innerHTML = `
        <div style="margin-bottom:1.25rem;background:var(--bg-secondary);padding:1.15rem 1.5rem;border-radius:12px;border:1px solid var(--border-gold);box-shadow:var(--shadow);">
          <h2 style="font-family:var(--font-serif);color:var(--gold-bright);font-size:1.6rem;margin-bottom:0.4rem;">
            💬 Diálogos Práticos e Conversação Cotidiana (Ecos de Uma Vida Perdida)
          </h2>
          <p style="color:var(--text-secondary);font-size:0.95rem;line-height:1.6;">
            Resultado de <strong>1.500 anos de evolução naturalista</strong> do Tréppio: a língua imperial cerimonial adaptou-se às estalagens, às estradas nevadas e ao calor das lareiras. Clique em <strong>qualquer vocábulo em Tréppio</strong> para inspecionar instantaneamente suas raízes e casos no léxico de 46.531 formas!
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
                <span class="gnlt-badge">Tréppio Moderno</span>
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

