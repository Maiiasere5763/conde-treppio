# -*- coding: utf-8 -*-
"""
aplicar_evolucao_antiga_classica_pura.py
Substitui cirurgicamente o vocabulário anterior pelo novo léxico autêntico
dos 1.500 anos de desenvolvimento natural da Era Antiga para a Era Clássica (V8.1).
"""

import os

GERADOR_PY = r"D:\Conde_Treppio\sandbox\gerador_dicionario_integral_sandbox.py"

with open(GERADOR_PY, "r", encoding="utf-8") as f:
    text = f.read()

# 1. NOUNS
m_nouns_start = "NOUNS = [\n"
m_nouns_end = "    # --- Letra A ---"
idx_ns = text.find(m_nouns_start)
idx_ne = text.find(m_nouns_end, idx_ns)

if idx_ns == -1 or idx_ne == -1:
    raise ValueError(f"Marcadores de NOUNS não encontrados: {idx_ns}, {idx_ne}")

authentic_nouns = """    # ==============================================================================
    # LÉXICO PRÁTICO E COTIDIANO: 1.500 ANOS DE EVOLUÇÃO (ERA ANTIGA -> ERA CLÁSSICA V8.1)
    # Desenvolvido nas montanhas, florestas de pinheiros e castelos boreais (Ecos de Uma Vida Perdida)
    # Rigorosamente estruturado a partir das raízes canônicas e morfologia do Tréppio
    # ==============================================================================
    # --- Saudações, Casa e Abrigo na Neve ---
    ("alen", 2, "saudação matinal, bom dia, claridade benfazeja", "al- (luz) + -en"),
    ("vesen", 2, "boa noite, repouso noturno da lareira", "ves- (noite) + -en"),
    ("doobbam", 2, "por favor, com licença, favor benevolente", "raiz doob- (benevolência) + -am"),
    ("hallen", 2, "gratidão, agradecimento, bênção recebida", "hal- (sagrado/luz) + -en"),
    ("nesor", 2, "lar, morada acolhedora, habitação familiar", "raiz nes- (ser/morar) + -or"),
    ("toret", 2, "teto, telhado de ardósia, abrigo contra a neve", "raiz tor- (cobrir/proteger) + -et"),
    ("rixtor", 2, "castelo de pedra, fortaleza montanhesa, torre de guarda", "rix- (rocha) + tor- (abrigo)"),
    ("vurrex", 2, "lareira de pedra, fogão a lenha, lareira da estalagem", "raiz vur- (fogo/chama) + -ex"),
    ("vildor", 2, "brasa incandescente, carvão ardente da lareira", "vur- + dur- (operante), sandi rn->ld"),
    ("drintavl", 2, "mesa de madeira maciça, bancada rústica de carvalho", "drin- (madeira) + tavl- (prancha)"),
    ("dursit", 2, "banco de madeira, assento de espaldar alto", "dur- (operar) + sit- (assento)"),
    ("drinpost", 2, "porta espessa de carvalho, postigo fortificado", "drin- (madeira) + post- (batente)"),
    ("alfrin", 2, "janela de postigo, fresta de luz da cabana", "al- (luz) + frin- (abertura)"),
    ("kladdor", 2, "tranca de ferro, ferrolho de segurança contra o vento", "raiz klad- (fechar) + -or"),
    ("falet", 2, "leito macio, cama de palha e mantas de dormir", "raiz fal- (repousar) + -et"),
    ("kildtor", 2, "manta pesada de lã, cobertura grossa contra a geada", "kild- (frio) + tor- (cobrir)"),
    ("aldor", 2, "tocha de breu, archote de resina para iluminar o caminho", "raiz al- (luz) + -dor (instrumento)"),
    ("allin", 2, "lamparina de óleo, candeia modesta da cabeceira", "al- (luz) + -in (diminutivo)"),
    # --- Alimento, Bebida e a Mesa da Estalagem ---
    ("dakkor", 2, "alimento diário, refeição farta, sustento", "raiz dak- (consumir/alimentar) + -or"),
    ("oxedak", 2, "pão de centeio rústico, broa de pedra, cereal cozido", "oxe- (terra/cereal) + dak- (alimento)"),
    ("brenor", 2, "caldo quente, sopa nutritiva de raízes e legumes", "raiz bren- (ferver/cozer) + -or"),
    ("luttor", 2, "carne assada na brasa, provisão de caça", "raiz lut- (caça/animal silvestre) + -or"),
    ("garvlut", 2, "peixe de rio gélido, truta das montanhas", "garv- (água viva/rio) + lut- (pesca/caça)"),
    ("keldas", 2, "queijo curado de cabra das serras", "raiz keld- (coalhar/prensar) + -as"),
    ("garva", 1, "água pura potável, água fresca de degelo", "raiz garv- (fluir/nascente) + -a"),
    ("laural", 2, "cerveja encorpada escura, hidromel espesso da taberna", "laur- (dourado) + al- (cereal)"),
    ("garvok", 2, "caneca de cerâmica, taça de estanho da estalagem", "garv- (beber) + -ok (recipiente)"),
    ("drindisk", 2, "tigela de madeira torneada, prato fundo de carvalho", "drin- (madeira) + disk- (prato)"),
    ("skelkit", 2, "faca afiada de mesa, punhal utilitário de caça", "skel- (aço/ferro) + kit- (cortar)"),
    ("drinspann", 2, "colher de pau torneada, concha de sopa", "drin- (madeira) + spann- (concha)"),
    ("salet", 2, "sal de rocha, sal para conservar carnes e queijos", "raiz sal- (preservar) + -et"),
    ("dakvul", 2, "fome, apetite voraz do viajante na nevasca", "dak- (comer) + vul- (desejo/anseio)"),
    ("garvvul", 2, "sede ardente, garganta seca pelo vento da serra", "garv- (beber) + vul- (desejo/anseio)"),
    ("vesdak", 2, "ceia noturna, refeição acolhedora ao pé da lareira", "ves- (noite) + dak- (refeição)"),
    # --- Clima, Natureza e Viagem nas Terras Boreais (Ecos) ---
    ("kildar", 2, "neve fresca acumulada, manto branco de inverno", "raiz kild- (frio/gelo) + -ar"),
    ("kildrix", 2, "gelo compacto, geada cortante, carâmbanos de pedra", "kild- (gelo) + rix- (pedra)"),
    ("veksun", 2, "nevoeiro denso, bruma fria que encobre caminhos", "raiz veks- (névoa/chuva) + -un"),
    ("filox", 2, "floresta de coníferas, bosque de pinheiros nevado", "fil- (árvore) + ox- (terra)"),
    ("drinet", 2, "pinheiro silvestre, conífera alta das encostas", "drin- (madeira/resina) + -et"),
    ("halkex", 2, "estrada de pedra, trilha batida na neve, rota montanhesa", "raiz halk- (caminhar) + -ex"),
    ("rixtorr", 2, "ponte de pedra sobre o abismo ou rio torrentoso", "rix- (pedra) + torr- (passagem)"),
    ("halkvest", 2, "pegada na neve fresca, rastro de viajante ou animal", "halk- (passo) + vest- (marca)"),
    ("alves", 2, "aurora boreal, claridade mística no céu nublado de inverno", "al- (luz) + ves- (noite)"),
    ("rixmont", 2, "montanha escarpada, pico rochoso coberto de gelo", "rix- (rocha) + mont- (elevação)"),
    ("oxeval", 2, "vale abrigado entre serras, desfiladeiro protegido", "oxe- (terra) + val- (vale)"),
    # --- Companheirismo, Criaturas e Afeto (Ecos) ---
    ("hundo", 2, "o grande cão loiro de aura brilhante, guardião leal", "raiz nórdica hund- + -o"),
    ("zenor", 2, "amigo fiel de travessia, companheiro leal de jornada", "raiz zen- (lealdade) + -or"),
    ("marn", 2, "cavalo de montaria e carga, corcel resistente à neve", "raiz marn- (montaria equina)"),
    ("kindar", 2, "família da lareira, clã do abrigo doméstico", "raiz kind- (laço/pacto) + -ar"),
    ("nesmatr", 1, "mãe protetora do lar, guardiã da lareira", "nes- (lar) + matr- (mãe)"),
    ("nespatr", 2, "pai protetor do lar, chefe da morada", "nes- (lar) + patr- (pai)"),
    ("kradet", 2, "criança pequena, filho amado, rebento do lar", "raiz kradd- (nascer/gerar) + -et"),
    ("dolkord", 2, "nostalgia profunda, saudade dos ecos do passado", "dol- (pesar) + kord- (coração)"),
    ("viltor", 2, "cura revigorante, alívio de dor e cansaço", "raiz vilt- (curar) + -or"),
    ("kordal", 2, "coragem serena, calor no peito diante da tormenta", "kord- (peito/coração) + al- (luz)"),
    # --- Forja, Ferramentas, Comércio e Armas ---
    ("talor", 2, "preço justo, valor acordado de troca em mercado", "raiz tal- (pesar/medir) + -or"),
    ("rixskel", 2, "moeda de prata cunhada, metal de troca comercial", "rix- (pedra clara/prata) + skel- (metal)"),
    ("lauren", 2, "moeda imperial de ouro, metal nobre de alto valor", "raiz laur- (ouro) + -en"),
    ("tekskel", 2, "ferreiro da bigorna, mestre forjador de aço", "tek- (forjar) + skel- (ferro)"),
    ("durtek", 2, "martelo de ferreiro, marreta pesada de forja", "dur- (bater) + tek- (forja)"),
    ("skelspad", 1, "espada de aço temperado, lâmina de guarda", "skel- (aço) + spad- (lâmina)"),
    ("torskel", 2, "escudo reforçado com ferro, broquel de proteção", "tor- (proteger) + skel- (placa metálica)"),
    ("talnes", 2, "estalagem de beira de estrada, albergue de viajantes", "tal- (comércio) + nes- (pousada)"),
    ("taldur", 2, "mercador de caravana, negociante itinerante", "tal- (comerciar) + dur- (agente)"),
\n"""

text = text[:idx_ns + len(m_nouns_start)] + authentic_nouns + text[idx_ne:]

# 2. ADJECTIVES
m_adjs_start = "ADJECTIVES = [\n"
m_adjs_end = '    ("aetika",'
idx_as = text.find(m_adjs_start)
idx_ae = text.find(m_adjs_end, idx_as)

if idx_as == -1 or idx_ae == -1:
    raise ValueError(f"Marcadores de ADJECTIVES não encontrados: {idx_as}, {idx_ae}")

authentic_adjs = """    # --- Adjetivos Práticos da Vida Diária (Era Antiga -> Era Clássica V8.1) ---
    ("kildan", "gélido, nevado, congelado pelo vento da serra", "maer kildan", "kildann"),
    ("vuran", "aquecido pela lareira, acolhedor, fumegante", "maer vuran", "vurann"),
    ("drinan", "de madeira maciça, entalhado em carvalho", "maer drinan", "drinann"),
    ("rixan", "pétreo, sólido como rocha, resistente", "maer rixan", "rixann"),
    ("zenan", "leal, fiel, amigo sincero de travessia", "maer zenan", "zenann"),
    ("dakkan", "nutritivo, farto, substancioso e saboroso", "maer dakkan", "dakkann"),
    ("garvan", "límpido, cristalino como água fresca de degelo", "maer garvan", "garvann"),
    ("talan", "justo no preço, correto na medida e no trato", "maer talan", "talann"),
    ("skelan", "férreo, duro como lâmina de aço temperado", "maer skelan", "skelann"),
    ("kordal", "corajoso, de peito aquecido diante do perigo", "maer kordal", "kordall"),
    ("veksan", "brumoso, encoberto pela névoa fria", "maer veksan", "veksann"),
    ("fessan", "fatigado da longa marcha, exausto na neve", "maer fessan", "fessann"),
    ("viltan", "curado, revigorado pela ceia e pelo sono", "maer viltan", "viltann"),
\n"""

text = text[:idx_as + len(m_adjs_start)] + authentic_adjs + text[idx_ae:]

# 3. VERB_ROOTS
m_verbs_start = "VERB_ROOTS = [\n"
m_verbs_end = '    ("bar",'
idx_vs = text.find(m_verbs_start)
idx_ve = text.find(m_verbs_end, idx_vs)

if idx_vs == -1 or idx_ve == -1:
    raise ValueError(f"Marcadores de VERB_ROOTS não encontrados: {idx_vs}, {idx_ve}")

authentic_verbs = """    # --- Verbos de Ação Cotidiana (Era Antiga -> Era Clássica V8.1) ---
    ("dak", "comer alimento sólido, nutrir-se", "jejuar, abster-se de comida", "comer habitualmente, merendar de novo", "quebrar o jejum, voltar a comer"),
    ("garv", "beber água pura, saciar a sede", "abster-se de beber, passar sede", "bebericar repetidamente, sorver caneca a caneca", "esvaziar a última gota da caneca"),
    ("fal", "repousar no leito, dormir serenamente", "velar à noite, vigiar sem dormir", "dormir o sono habitual, tirar um cochilo", "despertar do repouso, encerrar o sono"),
    ("sfar", "enxergar na bruma, avistar os caminhos", "fechar os olhos, cegar temporariamente na neve", "vigiar atentamente, contemplar de novo", "interromper a vigília, descansar a vista"),
    ("halk", "caminhar pela trilha, marchar na neve", "deter o passo, paralisar a marcha no frio", "caminhar continuamente, peregrinar pelas serras", "dar o passo final e atingir o destino"),
    ("vur", "aquecer com fogo, avivar a lareira", "apagar as chamas, deixar o fogo extinguir-se", "reacender a lareira, soprar as brasas", "manter as brasas vivas sob as cinzas"),
    ("tek", "forjar o ferro, lavrar a pedra, construir", "deixar a obra inacabada, desconstruir", "reforjar a lâmina, martelar repetidas vezes", "concluir a forja e temperar no aço"),
    ("bren", "cozer o caldo, cozinhar no caldeirão", "deixar a comida crua, não cozinhar", "reaquecer o caldo, ferver de novo na panela", "tirar a panela do fogo no ponto exato"),
    ("klad", "trancar a porta com ferrolho contra a tempestade", "destrancar, abrir a porta para a luz", "retrancar com segurança, fechar de novo", "abrir a tranca após a tempestade passar"),
    ("lut", "caçar nas montanhas, rastrear animais silvestres", "abster-se da caça, poupar a presa", "caçar regularmente para abastecer a estalagem", "retornar da caçada com provisões"),
    ("tal", "avaliar preço, pagar moedas devidas, negociar", "recusar o pagamento, reter a moeda", "negociar no mercado, trocar mercadorias", "saldar a última moeda devida"),
    ("vilt", "curar ferimento, sarar doente com bálsamo", "adoecer, fraquejar o corpo", "recobrar gradualmente a saúde dia a dia", "cicatrizar a marca definitiva"),
\n"""

text = text[:idx_vs + len(m_verbs_start)] + authentic_verbs + text[idx_ve:]

# 4. ADVERBS
m_advs_start = "ADVERBS = [\n"
m_advs_end = "    # Temporais, Locativos"
idx_advs = text.find(m_advs_start)
idx_adve = text.find(m_advs_end, idx_advs)

if idx_advs == -1 or idx_adve == -1:
    raise ValueError(f"Marcadores de ADVERBS não encontrados: {idx_advs}, {idx_adve}")

authentic_adverbs = """    # --- Advérbios e Partículas da Vida Diária (Era Antiga -> Era Clássica V8.1) ---
    ("yo", "Afirmação Prática", "partícula afirmativa arcaica", "sim, certamente, com certeza"),
    ("ne", "Negação Prática Pré-Verbal", "raiz primária ne", "não (negação factual antes do verbo)"),
    ("kildanvë", "Modal de Frio", "kildan + -vë", "gélidamente, sob frio cortante"),
    ("vuranvë", "Modal de Aconchego", "vuran + -vë", "calorosamente, ao calor da lareira"),
    ("zenanvë", "Modal de Fidelidade", "zenan + -vë", "lealmente, de coração amigo sincero"),
    ("halkanvë", "Modal de Marcha", "halkan + -vë", "a passo firme, marchando resolutamente"),
    ("dakkanvë", "Modal de Fartura", "dakkan + -vë", "com fartura, regaladamente"),
    ("talanvë", "Modal de Justiça", "talan + -vë", "honestamente, por preço justo"),
    ("alenvë", "Temporal Matinal", "alen + -vë", "ao raiar da manhã, com o nascer do sol"),
    ("vesenvë", "Temporal Noturno", "vesen + -vë", "à noite fechada, na hora do repouso"),
\n"""

text = text[:idx_advs + len(m_advs_start)] + authentic_adverbs + text[idx_adve:]

with open(GERADOR_PY, "w", encoding="utf-8") as f:
    f.write(text)

print("=== SUCESSO: Todas as 4 seções foram substituídas com precisão cirúrgica! ===")
