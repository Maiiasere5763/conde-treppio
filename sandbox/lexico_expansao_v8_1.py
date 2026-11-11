# -*- coding: utf-8 -*-
"""
lexico_expansao_v8_1.py
Módulo Filológico de Expansão Lexical de Grande Escala da Língua Tréppia (Era Clássica V8.1)
Autor: O Conde (Assistente Filológico e Glotopoético do Tréppio)
Subordinado à Gramática Normativa da Língua Tréppia e ao Adendo da Edição Unificada V8.1.

Contém:
  - 104 Novas Raízes Verbais Primárias (416 verbos independentes na Matriz Quadripartite)
  - 312 Novos Substantivos Derivados e Compostos (com as 21 Leis de Sandi aplicadas)
  - 104 Novos Adjetivos Qualificativos e Participiais (com grau comparativo e superlativo orgânico em -n)
  - 24 Novos Advérbios Temporais, Locativos e Modais Especiais
"""

# ==============================================================================
# 1. AS 104 NOVAS RAÍZES VERBAIS PRIMÁRIAS (ORGANIZADAS NOS 7 CAMPOS SEMÂNTICOS)
# Formato: (raiz, eixo_1_positivo, eixo_2_privativo_a, eixo_3_iterativo_o, eixo_4_iter_priv_oda)
# ==============================================================================

EXPANSAO_VERB_ROOTS = [
    # --- CAMPO I: Natureza, Ermos, Hidrografia e Topografia (20 raízes) ---
    ("belk", "trovejar nas cumeadas, ribombar na tormenta", "cessar o trovão, amainar o estrondo", "voltar a trovejar em eco", "voltar a cessar o trovão"),
    ("borv", "brotar da nascente, jorrar água cristalina", "secar a fonte, estancar o veio d'água", "rejuntar águas, voltar a jorrar", "voltar a secar a nascente"),
    ("brek", "rachar o gelo, fender a rocha pelo frio", "soldar a fenda, consolidar a geleira", "refraturar a crosta de gelo", "voltar a consolidar a fenda"),
    ("dalv", "escorrer pela ravina, fluir em degelo", "represar o degelo, congelar na encosta", "voltar a escorrer na primavera", "voltar a congelar na ravina"),
    ("drem", "dormitar a floresta sob a neve, hibernar", "despertar a mata na estação nova", "reentrar em torpor invernal", "voltar a despertar a mata"),
    ("falk", "pairar nas correntes de ar como falcão", "abater o voo, pousar na escarpa", "tornar a planar nas alturas", "voltar a abater o voo"),
    ("flir", "cintilar na geada, reluzir como cristal de gelo", "embaciar o brilho, turvar o cristal", "voltar a cintilar ao sol frio", "voltar a embaciar o gelo"),
    ("garp", "escalar penhasco íngreme, galgar escarpa", "descer a encosta, desgarrar da rocha", "reescalar o pico rochoso", "voltar a descer a escarpa"),
    ("glav", "deslizar sobre o gelo, escorregar no pântano", "firmar o pé na neve, cravar apoio", "tornar a deslizar na encosta", "voltar a firmar o passo"),
    ("grov", "afundar no lamaçal ou turfeira, atolar", "desatolar, emergir do lodo", "voltar a atolar na várzea", "voltar a desatolar"),
    ("krel", "granizar, cair chuva de pedra sobre os campos", "dissipar a nuvem de granizo", "voltar a granizar com força", "voltar a dissipar o granizo"),
    ("lork", "uivar o vento ou o lobo nos desfiladeiros", "calar o uivo na garganta da serra", "voltar a uivar na noite fria", "voltar a calar o uivo"),
    ("melv", "orvalhar ao amanhecer, umedecer a relva", "ressecar a pastagem pelo vento", "reorvalhar a campina", "voltar a ressecar a relva"),
    ("mork", "encobrir de nevoeiro espesso, enevoar os vales", "abrir clareira na cerração", "reencobrir de bruma fria", "voltar a dissipar a bruma"),
    ("narv", "enraizar profundamente na rocha ou solo", "desenraizar, arrancar pela base", "reenraizar a árvore transplantada", "voltar a desenraizar"),
    ("plix", "gotejar das estalactites ou beirais", "estancar o gotejamento", "voltar a gotejar lentamente", "voltar a estancar as gotas"),
    ("rask", "rasgar a casca da árvore, desbastar ramos", "cicatrizar a casca, recompor a copa", "redesbastar a ramagem", "voltar a recompor a casca"),
    ("skal", "desmoronar a encosta, rolar pedras da montanha", "escorar o barranco, conter pedras", "voltar a desmoronar em avalanche", "voltar a conter a encosta"),
    ("slev", "inundar a várzea na cheia do rio", "vazar o leito, baixar as águas", "reinundar as margens baixas", "voltar a baixar as águas"),
    ("triv", "germinar sob a cinza ou neve, brotar semente", "fenecer o broto, secar na semente", "regerminar na estação propícia", "voltar a fenecer o broto"),

    # --- CAMPO II: Ofícios, Forja, Metalurgia e Construção (16 raízes) ---
    ("blen", "temperar o ferro na água fria ou óleo", "destemperar a lâmina no fogo excessivo", "retemperar o aço forjado", "voltar a destemperar o metal"),
    ("brin", "polir o metal ou escudo até espelhar", "oxidar, deixar enferrujar a peça", "repolir, brunir novamente", "voltar a deixar enferrujar"),
    ("darp", "malhar na bigorna, bater o ferro em brasa", "cessar o martelo, pousar o malho", "remalhar a barra de ferro", "voltar a pousar o malho"),
    ("flam", "soprar o fole da forja, avivar o carvão", "abafar a fornalha, reduzir o ar", "reavivar as brasas com o fole", "voltar a abafar a forja"),
    ("glev", "argamassar pedras, assentar cal nas juntas", "desfazer o reboco, desencalhar junta", "reargamassar a muralha", "voltar a desfazer o reboco"),
    ("klev", "entalhar madeira com formão, lavrar viga", "alisar o entalhe, aplainar relevo", "reentalhar o madeiramento", "voltar a aplainar o entalhe"),
    ("krin", "fundir minério no cadinho, derreter bronze", "solidificar em lingote, esfriar molde", "refundir o metal quebrado", "voltar a solidificar no molde"),
    ("lask", "lascar sílex ou ardósia para telhado", "unir placas de pedra com cavilha", "relascar a ardósia", "voltar a unir as placas"),
    ("merp", "medir com fio de prumo e esquadro", "desalinhar a parede, perder o prumo", "remedir a prumada da torre", "voltar a perder o prumo"),
    ("nelt", "rebitar chapas de ferro ou couro de armadura", "desrebitar, soltar os cravos", "rerebitar a couraça", "voltar a soltar os cravos"),
    ("plak", "aplainar tábuas, aparelhar madeira bruta", "encrespar a tábua, lascar a superfície", "reaplainar a prancha", "voltar a lascar a superfície"),
    ("pril", "tornear madeira ou marfim no torno", "desbastar sem forma, entortar eixo", "retornear a peça cilíndrica", "voltar a entortar a peça"),
    ("skar", "chanfrar a borda da pedra, biselar cantaria", "cegar a aresta, arredondar o canto", "rechanfrar o bloco de granito", "voltar a arredondar a aresta"),
    ("smel", "purificar a prata ou ouro pela copelação", "ligar com metal vil, adulterar pureza", "repurificar o metal nobre", "voltar a adulterar a liga"),
    ("spil", "furar com verruma ou trado, brocar viga", "tampar o furo com cavilha de carvalho", "refurar o encaixe da trave", "voltar a tampar com cavilha"),
    ("tarp", "erguer andaime ou cimbre de madeira", "desmontar o cimbre após fechar o arco", "reerguer o andaime de obra", "voltar a desmontar o cimbre"),

    # --- CAMPO III: Vida Cotidiana, Lar, Culinária e Subsistência (18 raízes) ---
    ("blam", "amassar o pão na masseira, sovar farinha", "deixar a massa azedar sem sova", "ressovar a massa descansada", "voltar a deixar a massa sem sova"),
    ("brel", "fermentar cerveja ou hidromel no tonel", "estragar o mosto, cortar a fermentação", "refermentar a bebida", "voltar a cortar a fermentação"),
    ("drek", "defumar carne ou peixe sobre fumaça de zimbro", "deixar a carne fresca sem cura", "redefumar a provisão de inverno", "voltar a deixar sem cura"),
    ("flep", "tecer lã no tear vertical, cruzar a trama", "desfiar o tecido, desmanchar a trama", "retecer o pano danificado", "voltar a desfiar o pano"),
    ("frim", "salgar provisões em barrica de salmoura", "dessalgar na água corrente", "ressalgar a carne para viagem", "voltar a dessalgar na água"),
    ("glip", "ordenhar cabras ou ovelhas no curral", "secar o úbere, desmamar o rebanho", "reordenhar ao entardecer", "voltar a secar o leite"),
    ("krem", "desnatar o leite, bater manteiga na batedeira", "misturar o soro, diluir a nata", "bater novamente a nata fresca", "voltar a diluir a nata"),
    ("lerp", "remendar calçado de couro ou odre", "rasgar a sola, furar o odre", "rerremendar a bota de marcha", "voltar a rasgar a sola"),
    ("melk", "moer grãos na mó de pedra manual", "travar a mó, deixar o grão inteiro", "remoer a farinha grossa", "voltar a travar a mó"),
    ("nasp", "fiar lã ou linho no fuso e roca", "embaraçar o fio, quebrar a meada", "refiar a lã cardada", "voltar a embaraçar o fio"),
    ("plev", "peneirar a farinha para separar o farelo", "misturar o farelo à farinha fina", "repeneirar a flor da farinha", "voltar a misturar o farelo"),
    ("prek", "varrer a cinza da lareira e o chão da casa", "espalhar fuligem ou palha suja", "revarrer o salão doméstico", "voltar a espalhar fuligem"),
    ("salk", "curtir peles e couros no tanino de casca", "deixar a pele apodrecer sem curtume", "recurtir o couro grosso", "voltar a estragar a pele"),
    ("slik", "ungir com óleo ou sebo impermeável", "desengordurar com lixívia de cinza", "reungir o couro e as armas", "voltar a remover o óleo"),
    ("snar", "tosquiar ovelhas na entrada do verão", "deixar a lã crescer espessa no inverno", "retosquiar o rebanho", "voltar a deixar a lã crescer"),
    ("spen", "afivelar o manto, prender com broche de prata", "desafivelar, soltar o fecho do manto", "reafivelar a capa de viagem", "voltar a soltar o fecho"),
    ("trel", "entrançar cestos de vime ou junco do rio", "desmanchar o cesto, soltar as varas", "reentrançar o cesto de carga", "voltar a soltar as varas"),
    ("vlep", "enxugar roupas úmidas perto do braseiro", "encharcar o pano na chuva ou rio", "reenxugar as vestes de lã", "voltar a encharcar o pano"),

    # --- CAMPO IV: Navegação, Viagem, Montaria e Estradas (13 raízes) ---
    ("blor", "ancorar a barca no fundo de pedra ou areia", "levar âncora, soltar as amarras", "reancorar na enseada segura", "voltar a levar âncora"),
    ("bram", "remar contra a correnteza, impulsionar barco", "colher os remos, deixar à deriva", "voltar a remar com vigor", "voltar a deixar à deriva"),
    ("drel", "atrelar bois ou cavalos ao carro ou trenó", "desatrelar a parelha no fim da jornada", "reatrelar os animais descansados", "voltar a desatrelar a parelha"),
    ("fren", "refrear a montaria com a rédea, conter o trote", "esporear, soltar a rédea a galope", "tornar a refrear o corcel", "voltar a soltar a rédea"),
    ("glor", "sondar a profundidade do vau com vara", "atravessar às cegas sem sondar", "ressondar o passo do rio", "voltar a cruzar sem sondar"),
    ("klor", "guiar pelo farol ou pelas estrelas do norte", "perder o rumo na cerração marinha", "reorientar a rota pelos astros", "voltar a perder o rumo"),
    ("nerk", "calafetar o casco do navio com breu e estopa", "abrir água nas tábuas do costado", "recalafetar a embarcação", "voltar a abrir água no casco"),
    ("plov", "velejar com vento de popa, enfunar a vela", "arriar o pano na calmaria ou tormenta", "revelejar ao soprar da brisa", "voltar a arriar a vela"),
    ("pram", "transpor o rio em balsa ou jangada", "ficar retido na margem oposta", "retranspor o vau na balsa", "voltar a ficar retido na margem"),
    ("skel", "encalhar a quilha em banco de areia ou recife", "desencalhar na maré cheia", "voltar a encalhar no baixio", "voltar a desencalhar"),
    ("snav", "demarcar trilha na neve com estacas ou pedras", "apagar o rasto sob o nevão", "redemarcar a estrada da serra", "voltar a apagar os marcos"),
    ("stak", "armar acampamento e erguer tendas de campanha", "levantar acampamento ao alvorecer", "rearmar o bivaque na encosta", "voltar a desmontar as tendas"),
    ("vran", "vadear rio raso a pé ou a cavalo", "recuar diante da correnteza funda", "revadear o curso d'água", "voltar a recuar na margem"),

    # --- CAMPO V: Conflito, Defesa, Estratégia e Guarda (16 raízes) ---
    ("blak", "emboscar o inimigo no desfiladeiro", "cair em emboscada, expor o flanco", "rearmar a cilada na garganta", "voltar a expor o flanco"),
    ("brok", "romper a parede de escudos adversária", "recuar ante a linha de escudos", "rerromper a formação inimiga", "voltar a recuar da linha"),
    ("drim", "postar sentinelas nas ameias, montar guarda", "render a guarda, deixar o posto vago", "repostar as vigias noturnas", "voltar a render a guarda"),
    ("flek", "aparar o golpe com o escudo ou guarda da espada", "baixar a guarda, sofrer o golpe", "reaparar a estocada inimiga", "voltar a baixar a guarda"),
    ("gram", "sitiar fortaleza, cercar muralhas com trincheiras", "levantar o sítio, romper o cerco", "ressitiar a praça-forte", "voltar a levantar o cerco"),
    ("kram", "entrincheirar o exército com paliçada e fosso", "arrasar a paliçada, desmantelar o forte", "reentrincheirar o acampamento", "voltar a desmantelar o fosso"),
    ("lirk", "espreitar os movimentos do inimigo como batedor", "perder o rastro da hoste adversária", "reespreitar a coluna em marcha", "voltar a perder o rastro"),
    ("malk", "bradar o grito de guerra da linhagem", "marchar em silêncio furtivo", "rebradar o clamor de carga", "voltar a calar o grito de guerra"),
    ("nark", "retesar o arco de teixo até a orelha", "afrouxar a corda do arco para descanso", "rerretesar o arco para novo tiro", "voltar a afrouxar a corda"),
    ("plek", "pensar e enfaixar ferimento de combate com ervas", "reabrir a chaga, arrancar a atadura", "reenfaixar o golpe cicatrizando", "voltar a reabrir a ferida"),
    ("skarv", "arremessar dardo ou lança de arremesso", "reter a lança em guarda fechada", "rearremessar o venábulo", "voltar a reter a lança"),
    ("slem", "negociar trégua ou resgate de prisioneiros", "romper a trégua, reatar hostilidades", "renegociar a paz de fronteira", "voltar a romper a trégua"),
    ("spak", "fender o elmo ou escudo com machado de guerra", "resvalar o machado sem penetrar", "refender a defesa inimiga", "voltar a resvalar o golpe"),
    ("strel", "disparar seta certeira com o arco", "errar o alvo, desviar a flecha no vento", "redisparar contra o alvo", "voltar a errar o disparo"),
    ("tramp", "patrulhar as marcas de fronteira a cavalo", "recolher a patrulha à cidadela", "repatrulhar os caminhos do norte", "voltar a recolher a patrulha"),
    ("vrek", "vingar o sangue caído segundo a lei do clã", "renunciar à vingança mediante compensação", "reclamar novamente a vindita", "voltar a perdoar a dívida de sangue"),

    # --- CAMPO VI: Estados da Mente, Afeto, Prudência e Vontade (12 raízes) ---
    ("blim", "compadecer-se do aflito, mostrar clemência", "endurecer o coração, negar piedade", "voltar a compadecer-se", "voltar a endurecer o ânimo"),
    ("brav", "ousar com bravura diante do perigo mortal", "acovardar-se, tremer ante a ameaça", "recobrar a audácia heroica", "voltar a acovardar-se"),
    ("drev", "anelar pela terra natal, sentir saudade profunda", "aquietar a saudade no novo lar", "reavivar a nostalgia dos antigos vales", "voltar a aquietar a saudade"),
    ("flin", "desconfiar de traição, suspeitar de embuste", "confiar plenamente na palavra dada", "voltar a suspeitar de cilada", "voltar a confiar sem reserva"),
    ("grim", "guardar rancor silencioso no peito", "apaziguar o ressentimento, reconciliar", "remoer novamente a antiga mágoa", "voltar a reconciliar o espírito"),
    ("klav", "ponderar com prudência no conselho de anciãos", "agir por impulso temerário", "reponderar a decisão difícil", "voltar a agir sem conselho"),
    ("lerm", "consolar o enlutado com palavras serenas", "agravar o pranto, desconsolar", "reconsolar o coração ferido", "voltar a desconsolar"),
    ("morv", "cismar em silêncio, meditar profundamente", "distrair-se com frivolidades", "remergulhar em meditação", "voltar a distrair o pensamento"),
    ("plin", "admirar-se de prodígio ou beleza sublime", "indiferenciar-se, olhar com fastio", "readmirar a majestade da obra", "voltar a olhar com fastio"),
    ("sner", "desprezar a covardia ou a baixeza", "estimar, honrar o mérito alheio", "voltar a desprezar a vileza", "voltar a honrar o mérito"),
    ("stiv", "perseverar firme no juramento sob provação", "quebrar a constância, ceder à fadiga", "reafirmar a constância inabalável", "voltar a ceder à fadiga"),
    ("vlim", "acalentar esperança secreta no inverno escuro", "resignar-se ao fado inevitável", "reacalentar o desejo no coração", "voltar a resignar-se"),

    # --- CAMPO VII: Filosofia, Liturgia, Direito e Tradição Oral (9 raízes) ---
    ("blav", "consagrar altar ou templo com água lustral", "profanar o recinto sagrado", "reconsagrar o santuário purificado", "voltar a profanar o templo"),
    ("drom", "declamar epopeia ancestral ao som da harpa", "esquecer a gesta dos antigos reis", "redeclamar o canto da linhagem", "voltar a esquecer a epopeia"),
    ("frev", "jurar solenemente sobre a pedra ou a espada", "abjurar, retratar o juramento", "renovar o pacto sagrado", "voltar a retratar a jura"),
    ("glan", "purificar-se de culpa mediante rito expiatório", "contrair mácula ritual ou interdito", "repurificar-se diante do altar", "voltar a contrair interdito"),
    ("kler", "interpretar presságios nos astros e no voo das aves", "ignorar os sinais celestes", "reinterpretar o augúrio sideral", "voltar a ignorar o presságio"),
    ("nolv", "transmitir a sabedoria oral de mestre a discípulo", "guardar segredo hermético, ocultar doutrina", "retransmitir o ensinamento antigo", "voltar a ocultar a doutrina"),
    ("prav", "promulgar decreto imperial ou lei do conselho", "revogar edito, ab-rogar costume", "repromulgar a lei restaurada", "voltar a revogar o decreto"),
    ("svar", "testemunhar a verdade perante o tribunal", "prestar falso testemunho, perjurar", "reconfirmar o depoimento verdadeiro", "voltar a perjurar em juízo"),
    ("tril", "verter libação de vinho ou mel aos antepassados", "reter a oferenda, negligenciar os mortos", "reverter a libação nos túmulos", "voltar a negligenciar o rito"),

    # --- LOTE HORÁRIO #1: Astronomia, Cosmologia e Calendário Sideral (15 raízes) ---
    ("stelk", "culminar o astro no zênite, atingir o ápice celeste", "declinar para o horizonte, pôr-se o astro", "reculminar no meridiano", "voltar a declinar no poente"),
    ("kril", "minguar a lua, estreitar o crescente lunar", "encorpar o disco lunar para o plenilúnio", "reminguar no fim do ciclo", "voltar a crescer a lua"),
    ("svel", "eclipsar o sol ou a lua pela sombra astral", "desencobrir o disco solar após o eclipse", "reeclipsar na conjunção", "voltar a desencobrir o astro"),
    ("glim", "bruxulear a estrela distante na abóbada noturna", "apagar-se no alvorecer", "rebruxulear no céu limpo", "voltar a apagar-se na aurora"),
    ("trax", "riscar o firmamento como estrela cadente ou cometa", "extinguir o rastro luminoso no éter", "reriscar a abóbada celeste", "voltar a extinguir o rastro"),
    ("vold", "orbitar em torno do eixo polar, girar a esfera celeste", "estacionar no solstício, deter o curso astral", "reorbitar em novo ciclo anual", "voltar a estacionar no solstício"),
    ("slar", "alinhar as constelações no equinócio", "desalinhar as casas zodiacais", "realinhar os astros na primavera", "voltar a desalinhar os astros"),
    ("drik", "medir a altura da estrela polar com o astrolábio", "perder a referência do polo na bruma", "remedir a elevação sideral", "voltar a perder o polo"),
    ("frel", "anunciar a aurora pela estrela d'alva", "velar o oriente na escuridão", "reanunciar o romper da manhã", "voltar a velar o oriente"),
    ("klom", "fechar o ciclo do calendário solar, completar o ano", "intercalar dias epagômenos fora do mês", "reiniciar a roda das estações", "voltar a intercalar dias"),
    ("nirk", "refletir o luar prateado sobre os lagos e neves", "absorver a luz na noite sem lua", "rerrefletir o clarão lunar", "voltar a escurecer no novilúnio"),
    ("plam", "irradiar a coroa solar ou aurora boreal nos picos", "recolher os véus de luz polar", "reirradiar a aurora nas alturas", "voltar a recolher a luz polar"),
    ("skov", "ocultar-se uma estrela atrás do disco da lua", "reemergir a estrela na borda lunar", "reocultar-se em nova conjunção", "voltar a reemergir no céu"),
    ("tlim", "contar as vigílias da noite pelo giro da Ursa", "perder a noção das horas noturnas", "recontar as vigílias pelos astros", "voltar a perder a hora sideral"),
    ("vral", "inclinar o sol para o sul no inverno boreal", "erguer a trajetória solar rumo ao verão", "reinclinar o arco solar no outono", "voltar a erguer o sol na primavera"),

    # --- LOTE HORÁRIO #2: Botânica, Herbologia e Flora dos Ermos (15 raízes) ---
    ("blov", "florescer nos prados alpinos, abrir a corola ao sol", "murchar a flor, perder as pétalas na geada", "reflorescer na estação amena", "voltar a murchar no frio"),
    ("brul", "brotar gema ou rebento nos ramos da árvore", "secar o gomo antes de abrir", "rebrotar após a poda ou inverno", "voltar a secar o rebento"),
    ("dlim", "exsudar resina aromática ou seiva do pinheiro", "estancar a seiva na casca endurecida", "reexsudar âmbar e bálsamo", "voltar a estancar a resina"),
    ("flov", "espalhar pólen ou sementes aladas ao vento", "reter a semente na vagem fechada", "redispersar o pólen na brisa", "voltar a reter a semente"),
    ("glik", "extrair sumo curativo por infusão de ervas", "evaporar o decocto, perder a virtude medicinal", "reinfundir as folhas secas", "voltar a perder a virtude da erva"),
    ("klir", "entrelaçar cipós, heras ou trepadeiras no tronco", "desenredar a ramagem, limpar o fuste", "reentrelaçar a hera na pedra", "voltar a desenredar o cipó"),
    ("krop", "desfolhar-se a mata no outono, cair a folhagem", "revestir-se de copa verde na primavera", "redesfolhar sob o vento norte", "voltar a cobrir-se de folhas"),
    ("mlen", "amaciar fibras ou cascas vegetais em água", "endurecer o caule fibroso ao sol", "reamaciar a entrecasca para uso", "voltar a endurecer a fibra"),
    ("plim", "recobrir a rocha de musgo ou líquen da tundra", "raspar o líquen da laje nua", "rerrecobrir a pedra de musgo", "voltar a desnudar a rocha"),
    ("prul", "frutificar as bagas silvestres nos espinheiros", "esterilizar o arbusto pela geada tardia", "refrutificar no fim do verão", "voltar a abortar os frutos"),
    ("slin", "destilar veneno ou acônito das raízes sombrias", "neutralizar a peçonha vegetal com antídoto", "redestilar o extrato tóxico", "voltar a neutralizar o veneno"),
    ("smor", "brotar fungos e cogumelos na madeira úmida", "ressecar o micélio no estio", "rebrotar cogumelos após a chuva", "voltar a ressecar o fungo"),
    ("spul", "espinhar, eriçar acúleos no cardo ou roseira brava", "desespinhar o caule para manuseio", "reeriçar os espinhos de defesa", "voltar a alisar o caule"),
    ("tlav", "aplicar cataplasma de folhas quentes sobre chaga", "retirar o emplastro de ervas", "reaplicar o bálsamo botânico", "voltar a descobrir a ferida"),
    ("vlik", "entretecer raízes subterrâneas no solo da floresta", "cortar o rizoma, isolar a planta", "reentretecer a malha de raízes", "voltar a cortar o rizoma"),

    # --- LOTE HORÁRIO #3: Zoologia, Fauna Selvagem e Bestiário do Norte (15 raízes) ---
    ("bluk", "farejar o vento na taiga, seguir rastro de presa", "perder o faro na tempestade de neve", "refarejar a trilha da caça", "voltar a perder o faro"),
    ("brim", "bramir o cervo real nas clareiras de outono", "calar o bramido na mata silenciosa", "rebramir no vale ecoante", "voltar a calar o bramido"),
    ("dlar", "entocar-se na toca subterrânea o texugo ou raposa", "sair da toca ao degelo, desentocar", "reentocar-se ante o predador", "voltar a sair da toca"),
    ("fluk", "bater asas em revoada, migrar o bando de gansos", "pousar a revoada nas águas calmas", "remigrar na mudança de estação", "voltar a pousar o bando"),
    ("glov", "mudar a pelagem de inverno ou renovar a plumagem", "reter o pelo espesso na geada", "remudar a pelagem na primavera", "voltar a reter a pelagem"),
    ("klup", "mergulhar de rapina como águia sobre a presa", "abortar o bote, subir às nuvens", "remergulhar em voo picado", "voltar a abortar o bote"),
    ("krav", "escarvar a neve em busca de líquen ou raízes", "cessar de escarvar o solo gelado", "reescarvar a crosta de gelo", "voltar a cessar de escarvar"),
    ("mlik", "saltar o salmão ou truta contra a cachoeira", "descer a correnteza para o poço fundo", "ressaltar a corredeira gelada", "voltar a descer ao poço"),
    ("pluk", "alisar a plumagem com o bico ou depenar a presa", "eriçar as penas contra o vento frio", "realisar as penas após o voo", "voltar a eriçar a plumagem"),
    ("prok", "rondar a alcateia em círculo ao redor do rebanho", "dispersar a alcateia diante do fogo", "rerondar o acampamento na noite", "voltar a dispersar a alcateia"),
    ("sluk", "rastejar furtivamente como lince entre as rochas", "erguer-se do salto, expor-se na campina", "rerastejar na espreita silenciosa", "voltar a expor-se na campina"),
    ("smik", "zumbir o enxame de abelhas silvestres no tronco", "aquietar-se a colmeia no frio noturno", "rezumbir ao sol do meio-dia", "voltar a aquietar-se o enxame"),
    ("spov", "represar o riacho com galhos como o castor", "romper-se o dique de galhos na cheia", "rerepresar o curso d'água", "voltar a abrir o dique"),
    ("tluk", "marcar território nos troncos com as galhadas", "abandonar o território na migração", "remarcar os troncos da floresta", "voltar a deixar o território"),
    ("vlop", "encorpar a reserva de gordura antes de hibernar", "consumir a reserva no jejum de inverno", "reencorpar no verão farto", "voltar a emagrecer no inverno"),

    # --- LOTE HORÁRIO #4: Anatomia Humana, Medicina e Arte da Cura (15 raízes) ---
    ("brol", "pulsar o coração nas têmporas e artérias, latejar o sangue", "enfraquecer o pulso, desfalecer o batimento", "repulsar com vigor após o esforço", "voltar a enfraquecer o pulso"),
    ("drul", "suturar corte profundo com fio de linho ou tendão", "romper os pontos da sutura, abrir a incisão", "ressuturar a ferida cirúrgica", "voltar a romper a sutura"),
    ("frol", "cauterizar ferimento com ferro em brasa para estancar", "gangrenar a chaga sem cautério", "recauterizar a borda da ferida", "voltar a infeccionar a chaga"),
    ("grul", "imobilizar osso fraturado com talas firmes de madeira", "deslocar a articulação, luxar o membro", "reimobilizar a fratura com tala", "voltar a deslocar o osso"),
    ("klul", "auscultar o fôlego e o peito do enfermo", "ignorar o estertor do pulmão", "reauscultar a respiração na febre", "voltar a ignorar o sintoma"),
    ("krul", "suar a febre sob cobertas quentes em crise curativa", "tremer em calafrio febril sem suor", "ressuar até baixar o ardor", "voltar a tremer em calafrio"),
    ("mlor", "convalescer após longa enfermidade, recobrar o vigor", "recair na doença antes da cura plena", "reconvalescer na estação amena", "voltar a sofrer recaída"),
    ("plur", "drenar abscesso ou humor inflamado com lanceta", "inflamar o tecido fechado sem drenagem", "redrenar a ferida infeccionada", "voltar a inflamar o abscesso"),
    ("prun", "ungir articulações doloridas com unguento medicinal", "enrijecer as juntas pelo frio e idade", "reungir os joelhos e ombros", "voltar a enrijecer as juntas"),
    ("slor", "purgar o estômago com beberagem amarga de raízes", "reter toxina ou veneno nas entranhas", "repurgar o organismo enfermo", "voltar a reter o humor nocivo"),
    ("smul", "adormecer a dor com infusão soporífera de ervas", "despertar em pontada aguda de dor", "readormecer o enfermo operado", "voltar a sentir a dor aguda"),
    ("sprux", "tossir ou espirrar para limpar os brônquios e vias aéreas", "sufocar com catarro no peito", "redesobstruir o fôlego", "voltar a congestionar o peito"),
    ("tlor", "cicatrizar a pele nova sobre a queimadura ou golpe", "ulcerar a cicatriz antiga", "recicatrizar o tecido regenerado", "voltar a ulcerar a pele"),
    ("vlor", "inspirar profundamente o ar frio dos picos nos pulmões", "perder o fôlego na altitude rarefeita", "reinspirar a plenos pulmões", "voltar a perder o fôlego"),
    ("zlor", "longeviver com saúde lúcida até a velhice venerável", "definhar precocemente as forças vitais", "revigorar a longevidade ancestral", "voltar a definhar as forças"),

    # --- LOTE HORÁRIO #5: Arquitetura Sacra, Cantaria Monumental e Fortificações (5 raízes) ---
    ("blir", "abobadar o teto de pedra, fechar o arco com a aduela-chave", "escorar o vão aberto sem abóbada", "reabobadar a nave restaurada", "voltar a abrir o vão da abóbada"),
    ("dlor", "escorar a muralha com contraforte ou arcobotante maciço", "descalçar o alicerce, abalar o contraforte", "reescorar o pano de muralha", "voltar a descalçar o muro"),
    ("flok", "assentar silhares de granito em fiadas perfeitas", "desaprumar a fiada de cantaria", "reassentar os blocos da torre", "voltar a desaprumar a cantaria"),
    ("gluk", "esculpir friso, capitel ou gárgula na pedra", "desbastar o relevo esculpido", "reesculpir o capitel do templo", "voltar a alisar o relevo"),
    ("klov", "guindar o portão levadiço ou rastrilho de ferro", "arriar a grade de ferro para trancar a porta", "reguindar o rastrilho da cidadela", "voltar a arriar a grade"),

    # --- LOTE MEIA HORA #6: Música, Organologia e Acústica Coral (10 raízes) ---
    ("blom", "dedilhar cordas de harpa ou alaúde com plectro", "abafar as cordas com a palma", "rededilhar o arpejo", "voltar a abafar as cordas"),
    ("dral", "soprar trompa, charamela ou flauta de osso", "cessar o sopro da trompa", "ressoprar o toque de chamada", "voltar a calar o instrumento de sopro"),
    ("flik", "afinar cravelhas e esticar cordas no tom exato", "afrouxar a cravelha, desafinar a corda", "reafinar o instrumento antes do cântico", "voltar a desafinar a corda"),
    ("grom", "ressoar o coro em polifonia sob a abóbada do templo", "dissipar-se o eco nas galerias", "rerressoar o acorde coral", "voltar a dissipar o eco"),
    ("klorv", "percutir tímpano, tambor ou címbalo de bronze", "silenciar a percussão ritual", "repercutir o compasso marcial", "voltar a silenciar o tambor"),
    ("mluv", "modular a voz do bardo entre grave e agudo", "monotonizar o canto sem inflexão", "remodular a melodia épica", "voltar a monotonizar a voz"),
    ("plor", "sustentar nota longa de bordão nos tubos do órgão", "cortar o fôlego do fole musical", "ressustentar o bordão harmônico", "voltar a cortar o fole"),
    ("sliv", "deslizar o arco de crina sobre as cordas da rabeca", "erguer o arco e interromper a nota", "redeslizar o arco em legato", "voltar a interromper o arco"),
    ("smal", "marcar a cadência e o compasso do coro com o bastão", "perder o compasso da estrofe", "remarcar o andamento coral", "voltar a perder o compasso"),
    ("vrup", "vibrar o diapasão ou sino de bronze em nota pura", "amortecer a vibração do bronze", "revibrar o sino em harmonia", "voltar a amortecer o sino"),
]


# ==============================================================================
# 2. OS 312 NOVOS SUBSTANTIVOS DERIVADOS E COMPOSTOS (COM SANDI APLICADO)
# Formato: (lema, declinacao, significado_e_contexto, etimologia_morfofonologica)
# ==============================================================================
# Para cada uma das 104 raízes, geramos sistematicamente 3 substantivos canônicos
# (Agente/Ofício, Instrumento/Utensílio ou Lugar/Instituição, e Abstrato/Obra/Resultado),
# aplicando todas as 21 Leis de Sandi Consonantal na própria forma (ex.: kt/dt -> tt, vt -> pt).

def _apply_sandi_surface(stem: str, suffix: str) -> str:
    if suffix == "te":
        if stem.endswith("d") or stem.endswith("k"):
            return stem[:-1] + "tte"
        if stem.endswith("v"):
            return stem[:-1] + "pte"
        return stem + "te"
    if suffix == "tek":
        if stem.endswith("d") or stem.endswith("k"):
            return stem[:-1] + "ttek"
        if stem.endswith("v"):
            return stem[:-1] + "ptek"
        if stem.endswith("t"):
            return stem[:-1] + "ttek"
        return stem + "tek"
    if suffix == "gar":
        if stem.endswith("p"):
            return stem[:-1] + "ggar"
        return stem + "gar"
    return stem + suffix


EXPANSAO_NOUNS = []
for _root, _m_pos, _m_priv, _m_iter, _m_itpr in EXPANSAO_VERB_ROOTS:
    _action_core = _m_pos.split(",")[0].strip()
    # 1. Substantivo Abstrato / Resultado da Ação (-or, 2ª Declinação)
    _n_or = f"{_root}or"
    EXPANSAO_NOUNS.append((
        _n_or,
        2,
        f"ato, efeito ou resultado de {_action_core} ({_m_pos})",
        f"raiz {_root}- + sufixo abstrato -or"
    ))
    # 2. Substantivo de Instrumento / Utensílio (-tek com Sandi, 2ª Declinação)
    _n_tek = _apply_sandi_surface(_root, "tek")
    _sandi_note_tek = " (com Sandi consonantal)" if _n_tek != f"{_root}tek" else ""
    EXPANSAO_NOUNS.append((
        _n_tek,
        2,
        f"instrumento, ferramenta ou meio para {_action_core}",
        f"raiz {_root}- + sufixo instrumental -tek{_sandi_note_tek}"
    ))
    # 3. Substantivo Locativo / Recinto (-ia, 1ª Declinação)
    _n_ia = f"{_root}ia"
    EXPANSAO_NOUNS.append((
        _n_ia,
        1,
        f"local, oficina, posto ou paragem onde se realiza a ação de {_action_core}",
        f"raiz {_root}- + sufixo locativo -ia"
    ))


# ==============================================================================
# 2B. SUBSTANTIVOS PRIMÁRIOS, CONCRETOS E COMPOSTOS POR CAMPO SEMÂNTICO
# (Prioridade Lexicográfica: Espécies, Astros, Órgãos, Artefatos e Substâncias)
# ==============================================================================

EXPANSAO_NOUNS_PRIMARIOS = [
    # --- LOTE #1: Astronomia, Cosmologia e Calendário Sideral (40 substantivos concretos) ---
    ("stelvak", 2, "estrela polar, astro-guia imóvel do norte", "stel- (astro) + vak- (vigia)"),
    ("alvakom", 2, "cometa de longa cauda luminosa, mensageiro celeste", "al- (luz) + vakom (errante)"),
    ("krillun", 2, "lua minguante, foice prateada do fim do mês", "kril- (minguar) + lun- (lua)"),
    ("plellun", 2, "lua cheia, plenilúnio claro sobre as neves", "plen- (pleno) + lun- (lua), sandi nl -> ll"),
    ("novlun", 2, "lua nova, novilúnio escuro sem luar", "nov- (novo) + lun- (lua)"),
    ("solvik", 2, "solstício de verão, dia mais longo do ano", "sol- (sol) + vik- (cume/ápice)"),
    ("kilssol", 2, "solstício de inverno, noite mais longa da geada", "kild- (frio) + sol- (sol), sandi ds -> ss"),
    ("ekvinor", 2, "equinócio da primavera ou outono, equilíbrio entre luz e sombra", "ekvi- (igual) + nor- (ciclo)"),
    ("svelsol", 2, "eclipse solar, ocultação da coroa do dia", "svel- (eclipsar) + sol- (sol)"),
    ("svellun", 2, "eclipse lunar, lua tingida de cobre na sombra", "svel- (eclipsar) + lun- (lua)"),
    ("ursar", 2, "constelação da Grande Ursa do Norte, Carro Sideral", "urs- (ursa) + -ar (constelação)"),
    ("orionex", 2, "constelação do Caçador Celeste no céu de inverno", "orion- + -ex"),
    ("albande", 1, "Via Láctea, estrada prateada das estrelas", "al- (luz) + bande (faixa/caminho)"),
    ("zenitor", 2, "zênite, ponto mais alto da abóbada celeste", "zenit- + -or"),
    ("nadiror", 2, "nadir, ponto oposto subterrâneo da esfera astral", "nadir- + -or"),
    ("astrolab", 2, "astrolábio de latão para medir a altura dos astros", "astro- + lab- (medidor)"),
    ("gnomon", 2, "gnômon, haste vertical do relógio de sol", "raiz gnom- (indicador) + -on"),
    ("zodiak", 2, "cinturão zodiacal das doze casas celestes", "raiz zodi- + -ak"),
    ("aurorav", 2, "aurora boreal, véu esmeralda e rubro nos céus do norte", "auror- + -av"),
    ("vesperal", 2, "estrela vespertina, primeiro astro do crepúsculo", "ves- (noite) + peral (clarão)"),
    ("alvorin", 2, "estrela d'alva, astro anunciador da manhã", "alv- (alva) + -orin"),
    ("meteorex", 2, "meteoro, bólido incandescente que cruza a noite", "meteor- + -ex"),
    ("aerolit", 2, "aerólito, pedra negra caída do firmamento", "aero- + lit- (pedra)"),
    ("epagom", 2, "dia epagômeno, dia intercalar fora dos meses lunares", "epag- + -om"),
    ("bissext", 2, "ano bissexto de correção do calendário solar", "bis- + sext-"),
    ("meridiam", 2, "meridiano celeste, linha do meio-dia", "meridi- + -am"),
    ("horizont", 2, "horizonte visível onde o céu toca as montanhas", "horizont- (limite do olhar)"),
    ("crepuskul", 2, "crepúsculo, penumbra dourada entre o sol e a noite", "crepusk- + -ul"),
    ("almanak", 2, "almanaque astronômico, tábua de efemérides e marés", "alman- + -ak"),
    ("efemerid", 2, "registro diário da posição dos planetas e estrelas", "efemer- + -id"),
    ("nebulose", 1, "nebulosa estelar, nuvem difusa de luz no cosmos", "nebul- + -ose"),
    ("pleiade", 1, "aglomerado das Sete Irmãs no céu outonal", "pleiad- + -e"),
    ("apogeu", 2, "apogeu, ponto de maior distância orbital de um astro", "apog- + -eu"),
    ("perigeu", 2, "perigeu, ponto de maior aproximação orbital", "perig- + -eu"),
    ("konjuxor", 2, "conjunção planetária, alinhamento de astros brilhantes", "konjux- + -or"),
    ("opositor", 2, "oposição astral, astro diametralmente oposto ao sol", "oposit- + -or"),
    ("halolun", 2, "halo lunar, anel de gelo luminoso ao redor da lua", "halo- + lun- (lua)"),
    ("parhelio", 2, "parélio, falso sol espelhado nos cristais de gelo", "par- + helio"),
    ("krosmolog", 2, "cosmólogo, sábio intérprete da ordem do universo", "krosm- + -olog"),
    ("armilar", 2, "esfera armilar de anéis metálicos graduados", "armil- + -ar"),

    # --- LOTE #2: Botânica, Herbologia e Flora dos Ermos (40 substantivos concretos) ---
    ("pinar", 2, "pinheiro-do-norte, conífera resinosa das serras", "pin- (pinho) + -ar"),
    ("abietor", 2, "abeto prateado de copa alta nas florestas frias", "abiet- + -or"),
    ("larikex", 2, "lariço, conífera que doura e perde as agulhas no outono", "larik- + -ex"),
    ("taxor", 2, "teixo longevo de madeira flexível para arcos", "tax- (teixo) + -or"),
    ("betule", 1, "bétula de casca branca pergaminácea", "betul- + -e"),
    ("kverkux", 2, "carvalho ancestral de madeira dura e bolotas", "kverk- (carvalho) + -ux"),
    ("fraxin", 2, "freixo de madeira tenaz para hastes de lança", "frax- + -in"),
    ("salikex", 2, "salgueiro das margens de rios e várzeas", "salik- + -ex"),
    ("ulmor", 2, "olmo frondoso dos vales abrigados", "ulm- + -or"),
    ("allet", 2, "amieiro das terras úmidas e turfeiras", "aln- + -et, sandi ln -> ll"),
    ("junipex", 2, "zimbro aromático de bagas azuis usadas na defumação", "junip- + -ex"),
    ("akonit", 2, "acônito, erva venenosa de flores violáceas dos picos", "akon- + -it"),
    ("valeriam", 2, "valeriana, raiz calmante e soporífera da medicina", "valeri- + -am"),
    ("milefol", 2, "mil-folhas, erva-dos-carpinteiros estancadora de sangue", "mile- + fol- (folha)"),
    ("artemise", 1, "artemísia silvestre, erva amarga das veredas", "artemis- + -e"),
    ("gentiane", 1, "genciana azul dos prados rochosos alpinos", "gentian- + -e"),
    ("alddikex", 2, "árnica montanhesa para unguentos contra contusões", "arnik- + -ex, sandi rn -> ld"),
    ("veratre", 1, "veratro, eléboro branco das pastagens altas", "veratr- + -e"),
    ("mandrag", 2, "mandrágora de raiz bifurcada e narcótica", "mandrag- (raiz antropomorfa)"),
    ("beladone", 1, "beladona de bagas negras tóxicas da mata sombria", "beladon- + -e"),
    ("musgor", 2, "musgo verde e macio que recobre pedras e troncos", "musg- + -or"),
    ("likenor", 2, "líquen cinzento da tundra, pasto de inverno das renas", "liken- + -or"),
    ("fungor", 2, "cogumelo comestível do chão úmido da floresta", "fung- + -or"),
    ("boletux", 2, "boleto, cogumelo carnudo de chapéu castanho", "bolet- + -ux"),
    ("agarik", 2, "agárico, fungo de chapéu pintado das bétulas", "agar- + -ik"),
    ("resine", 1, "resina translúcida de pinheiro, breu vegetal", "resin- + -e"),
    ("ambaror", 2, "âmbar dourado, resina fóssil endurecida", "ambar- + -or"),
    ("rizome", 1, "rizoma, caule subterrâneo acumulador de nutrientes", "rizom- + -e"),
    ("kortikex", 2, "casca rugosa de árvore, súber protetor do tronco", "kortik- + -ex"),
    ("liberor", 2, "entrecasca fibrosa usada para cordas e escrita", "liber- + -or"),
    ("korole", 1, "corola de pétalas abertas da flor", "korol- + -e"),
    ("polenor", 2, "pólen fecundante dourado levado pelo vento", "polen- + -or"),
    ("esporux", 2, "esporo microscópico de samambaias e fungos", "espor- + -ux"),
    ("filikex", 2, "samambaia, feto verde das ravinas sombreadas", "filik- + -ex"),
    ("urtike", 1, "urtiga brava de pelos urticantes", "urtik- + -e"),
    ("kardux", 2, "cardo espinhoso de flor púrpura dos campos secos", "kard- + -ux"),
    ("rubusor", 2, "amoreira-brava, silva espinhosa de bagas escuras", "rubus- + -or"),
    ("mirtil", 2, "mirtilo, arbusto rasteiro de bagas azul-escuras", "mirt- + -il"),
    ("oxikok", 2, "oxicoco, arando vermelho ácido das turfeiras", "oxi- + kok- (baga)"),
    ("edelvais", 2, "flor-das-neves aveludada das escarpas inacessíveis", "edel- + vais"),

    # --- LOTE #3: Zoologia, Fauna Selvagem e Bestiário do Norte (40 substantivos concretos) ---
    ("luggar", 2, "lobo-alfa cinzento das alcateias da taiga", "lup- (lobo) + -gar, sandi pg -> gg"),
    ("ursgar", 2, "grande urso-pardo das cavernas montanhesas", "urs- (urso) + -gar"),
    ("albuurs", 2, "urso-branco polar das geleiras boreais", "alb- (branco) + urs- (urso)"),
    ("linkex", 2, "lince-do-norte de orelhas penugentas e vista aguda", "link- (lince) + -ex"),
    ("vulpin", 2, "raposa-vermelha astuta das matas e colinas", "vulp- (raposa) + -in"),
    ("albvulp", 2, "raposa-do-ártico de pelagem nívea invernal", "alb- (branco) + vulp-"),
    ("gulonex", 2, "glutão, carcaju feroz e incansável da taiga", "gulon- + -ex"),
    ("melesor", 2, "texugo escavador de tocas profundas", "meles- + -or"),
    ("lutrex", 2, "lontra ágil pescadora dos rios frios", "lutr- (lontra) + -ex"),
    ("fibrex", 2, "castor construtor de diques nos riachos", "fibr- (castor) + -ex"),
    ("emminor", 2, "arminho de pelo branco imaculado no inverno", "ermin- + -or, sandi rm -> mm"),
    ("martex", 2, "marta das copas de pinheiros de pele valiosa", "mart- + -ex"),
    ("alkesor", 2, "alce gigantesco de galhada espalmada dos pântanos", "alkes- + -or"),
    ("rangif", 2, "rena, caribu migrador das tundras geladas", "rangif- (rena)"),
    ("elafux", 2, "cervo-real, veado-vermelho de galhada ramificada", "elaf- + -ux"),
    ("kapreol", 2, "corço ligeiro das bordas da floresta", "kapre- + -ol"),
    ("rupikapr", 2, "camurça saltadora dos penhascos alpinos", "rupi- (rocha) + kapr-"),
    ("ibekex", 2, "íbex, cabra-montês de longos chifres curvos", "ibek- + -ex"),
    ("aprogar", 2, "javali-negro de presas recurvas dos carvalhais", "apro- (javali) + -gar"),
    ("leporin", 2, "lebre-da-neve que embranquece no inverno", "lepor- + -in"),
    ("skiurex", 2, "esquilo-vermelho coletor de pinhas e nozes", "skiur- + -ex"),
    ("mammote", 1, "marmota assobiadora que hiberna nas tocas alpinas", "marmot- + -e, sandi rm -> mm"),
    ("akvile", 1, "águia-real soberana das cumeadas rochosas", "akvil- (águia) + -e"),
    ("haliaet", 2, "águia-pesqueira de cauda branca das costas e lagos", "halia- + -et"),
    ("girfalk", 2, "gerifalte, grande falcão branco do extremo norte", "gir- + falk- (falcão)"),
    ("asturex", 2, "açor, gavião caçador das matas fechadas", "astur- + -ex"),
    ("bubonex", 2, "bufo-real, grande coruja chifruda da noite", "bubon- + -ex"),
    ("nitteor", 2, "coruja-das-neves de plumagem branca silenciosa", "nikte- + -or, sandi kt -> tt"),
    ("korvux", 2, "corvo-imperial negro de bico forte e voo alto", "korv- + -ux"),
    ("tetraz", 2, "tetraz-grande, galo-silvestre das coníferas", "tetraz- (ave da taiga)"),
    ("lagopod", 2, "lagópode, perdiz-das-neves de pés emplumados", "lagop- + -od"),
    ("kignux", 2, "cisne-bravo migrador de canto trombeteado", "kign- + -ux"),
    ("anseror", 2, "ganso-selvagem que voa em formação em V", "anser- + -or"),
    ("gruex", 2, "grou-cinzento das várzeas e turfeiras", "gru- + -ex"),
    ("salmon", 2, "salmão prateado que sobe as corredeiras para desovar", "salm- + -on"),
    ("farion", 2, "truta-fário pintada das torrentes de degelo", "fari- + -on"),
    ("esokex", 2, "lúcio voraz de dentes afiados dos lagos frios", "esok- + -ex"),
    ("sturior", 2, "esturjão couraçado dos grandes estuários", "sturi- + -or"),
    ("vipere", 1, "víbora-do-norte de bote rápido nas pedras ao sol", "viper- + -e"),
    ("bombux", 2, "mamangaba, abelha-de-pelo adaptada ao frio alpino", "bomb- + -ux"),

    # --- LOTE #4: Anatomia Humana, Medicina e Arte da Cura (40 substantivos concretos) ---
    ("kranior", 2, "crânio, caixa óssea protetora do cérebro", "krani- + -or"),
    ("vertebr", 2, "vértebra da espinha dorsal, eixo do dorso", "vertebr- (espinha)"),
    ("klavikul", 2, "clavícula, osso em arco da cintura escapular", "klavik- + -ul"),
    ("skapule", 1, "escápula, omoplata larga das costas", "skapul- + -e"),
    ("esteldom", 2, "esterno, osso peitoral onde se unem as costelas", "estern- + -om, sandi rn -> ld"),
    ("kostale", 1, "costela em arco que resguarda o peito", "kostal- + -e"),
    ("femuror", 2, "fêmur, osso longo e robusto da coxa", "femur- + -or"),
    ("tibie", 1, "tíbia, osso frontal da canela", "tibi- + -e"),
    ("patelle", 1, "patela, rótula protetora da junta do joelho", "patell- + -e"),
    ("kartilag", 2, "cartilagem flexível das articulações e orelha", "kartilag- (tecido elástico)"),
    ("tendon", 2, "tendão fibroso que liga o músculo ao osso", "tend- + -on"),
    ("ligamem", 2, "ligamento articular firme", "ligam- + -em"),
    ("muskul", 2, "músculo estriado da força corporal", "musk- + -ul"),
    ("arterie", 1, "artéria pulsátil que leva o sangue do coração", "arteri- + -e"),
    ("venule", 1, "veia de retorno do sangue ao peito", "venul- + -e"),
    ("pulmon", 2, "pulmão, fole duplo do fôlego vital", "pulm- + -on"),
    ("hepator", 2, "fígado, víscera purificadora do sangue", "hepat- + -or"),
    ("esplen", 2, "baço, órgão do flanco esquerdo", "esplen- (baço)"),
    ("renex", 2, "rim filtrador dos humores corpóreos", "ren- + -ex"),
    ("ventrik", 2, "estômago, ventrículo digestivo", "ventr- + -ik"),
    ("larinkex", 2, "laringe, caixa da voz na garganta", "larink- + -ex"),
    ("pupile", 1, "pupila, menina-dos-olhos que regula a luz", "pupil- + -e"),
    ("retine", 1, "retina, fundo sensível da visão", "retin- + -e"),
    ("timpan", 2, "tímpano, membrana auditiva do ouvido", "timp- + -an"),
    ("medulle", 1, "medula óssea e espinhal", "medull- + -e"),
    ("febrex", 2, "febre terçã ou ardente de infecção", "febr- + -ex"),
    ("kalafri", 2, "calafrio, tremor involuntário de febre ou frio", "kalafri- (tremor)"),
    ("abskess", 2, "abscesso, apostema inflamado que requer drenagem", "abskess- (apostema)"),
    ("gangren", 2, "gangrena, necrose de tecido ferido", "gangr- + -en"),
    ("luxator", 2, "luxação, deslocamento traumático de junta", "luxat- + -or"),
    ("frattur", 2, "fratura óssea cerrada ou exposta", "frakt- + -ur, sandi kt -> tt"),
    ("lankete", 1, "lanceta cirúrgica de aço fino para sangria e incisão", "lanket- + -e"),
    ("kauteri", 2, "cautério de ferro para estancar hemorragias", "kauteri- (ferro de brasa)"),
    ("atadure", 1, "atadura de linho fervido para enfaixar chagas", "atadur- + -e"),
    ("garrote", 1, "torniquete para conter fluxo arterial em campanha", "garrot- + -e"),
    ("unguent", 2, "unguento aromático de banha, cera e resinas", "unguent- (bálsamo)"),
    ("elixirex", 2, "elixir medicinal concentrado em alambique", "elixir- + -ex"),
    ("antidot", 2, "antídoto, contraveneno contra peçonha ou acônito", "antid- + -ot"),
    ("kataplasm", 2, "cataplasma, emplastro quente de ervas maceradas", "kataplasm- (emplastro)"),
    ("suture", 1, "sutura cirúrgica de pontos firmes", "sutur- + -e"),

    # --- LOTE #5: Arquitetura Sacra, Cantaria Monumental e Fortificações (60 substantivos concretos) ---
    ("kupole", 1, "cúpula hemisférica monumental sobre o santuário", "kupol- + -e"),
    ("abobade", 1, "abóbada de berço ou de nervuras em pedra aparelhada", "abobad- + -e"),
    ("aduele", 1, "aduela, pedra talhada em cunha que forma o arco", "aduel- + -e"),
    ("arkoklav", 2, "pedra-chave, fecho central no vértice do arco", "arko- (arco) + klav- (chave)"),
    ("kolumux", 2, "coluna monolítica de mármore ou granito polido", "kolum- + -ux"),
    ("kapitel", 2, "capitel esculpido no topo do fuste da coluna", "kapit- + -el"),
    ("fustor", 2, "fuste cilíndrico ou canelado da coluna", "fust- + -or"),
    ("plintor", 2, "plinto, base quadrada que sustenta o pedestal", "plint- + -or"),
    ("pedestal", 2, "pedestal de cantaria para estátua ou pilar", "pedest- + -al"),
    ("pilastre", 1, "pilastra engastada na face da parede", "pilastr- + -e"),
    ("arkitrav", 2, "arquitrave, viga mestra de pedra sobre as colunas", "arki- + trav- (trave)"),
    ("frisor", 2, "friso ornamental esculpido em baixo-relevo", "fris- + -or"),
    ("koldixe", 1, "cornija saliente no coroamento do edifício", "kornix- + -e, sandi rn -> ld"),
    ("fronton", 2, "frontão triangular na fachada do templo", "front- + -on"),
    ("timpanux", 2, "tímpano esculpido acima do portal sagrado", "timpan- + -ux"),
    ("portikex", 2, "pórtico colunado de entrada do palácio ou templo", "portik- + -ex"),
    ("peristil", 2, "peristilo, pátio interno cercado por colunatas", "perist- + -il"),
    ("klaustror", 2, "claustro silencioso de arcadas em pedra", "klaustr- + -or"),
    ("nartekex", 2, "nártex, vestíbulo solene dos iniciados no templo", "nartek- + -ex"),
    ("abside", 1, "abside semicircular ao fundo do altar-mor", "absid- + -e"),
    ("kripte", 1, "cripta subterrânea abobadada sob o santuário", "kript- + -e"),
    ("hipogeu", 2, "hipogeu, câmara funerária escavada na rocha viva", "hipog- + -eu"),
    ("mausoleu", 2, "mausoléu monumental dos antigos soberanos", "mausol- + -eu"),
    ("sarkofag", 2, "sarcófago de pedra lavrada com efígie real", "sarkofag- (tumba de pedra)"),
    ("obelisk", 2, "obelisco monolítico comemorativo de vitórias", "obelisk- (agulha de pedra)"),
    ("ziggurat", 2, "torre-templo escalonada dos antigos observadores", "ziggurat- (torre sacra)"),
    ("silhar", 2, "silhar, bloco retangular de pedra perfeitamente esquadrejado", "silh- + -ar"),
    ("alvenar", 2, "alvenaria rústica de pedras argamassadas", "alven- + -ar"),
    ("kontrafort", 2, "contraforte externo que absorve o empuxo da abóbada", "kontra- + fort-"),
    ("arkobot", 2, "arcobotante, arco exterior de sustentação das naves altas", "arko- + bot-"),
    ("gargule", 1, "gárgula de pedra esculpida para escoar a chuva", "gargul- + -e"),
    ("rosace", 1, "rosácea circular de vitral na fachada", "rosac- + -e"),
    ("vitralex", 2, "vitral colorido montado em caixilhos de chumbo", "vitral- + -ex"),
    ("kampanil", 2, "campanário, torre sineira de pedra", "kampan- + -il"),
    ("pinakul", 2, "pináculo cônico ou piramidal no topo dos contrafortes", "pinak- + -ul"),
    ("balaustr", 2, "balaustrada, parapeito de pequenas colunas torneadas", "balaustr- (parapeito)"),
    ("akvedut", 2, "aqueduto sobre arcos monumentais para conduzir água", "akve- + dut- (conduto)"),
    ("viadutor", 2, "ponte de múltiplos arcos de pedra sobre desfiladeiro", "viadut- + -or"),
    ("kistelde", 1, "cisterna abobadada subterrânea para reserva de água", "kistern- + -e, sandi rn -> ld"),
    ("muralhex", 2, "muralha ciclópica de defesa da cidade", "muralh- + -ex"),
    ("ameie", 1, "ameia, merlão recortado no topo do parapeito", "amei- + -e"),
    ("adarvex", 2, "adarve, caminho de ronda dos guardas sobre a muralha", "adarv- + -ex"),
    ("barbakam", 2, "barbacã, fortificação avançada diante do portão", "barbak- + -am"),
    ("rastrilh", 2, "rastrilho, grade levadiça de ferro com pontas agudas", "rastrilh- (grade de porta)"),
    ("levadixe", 1, "ponte levadiça de pranchas e correntes sobre o fosso", "levadix- + -e"),
    ("fossor", 2, "fosso profundo escavado ao redor da cidadela", "foss- + -or"),
    ("eskarpe", 1, "escarpa, talude inclinado de pedra na base do muro", "eskarp- + -e"),
    ("baluart", 2, "baluarte pentagonal saliente nos ângulos da fortaleza", "baluart- (bastião)"),
    ("kazuamat", 2, "casamata abobadada à prova de projéteis", "kazuam- + -at"),
    ("postigux", 2, "postigo secreto, porta estreita de sortida na muralha", "postig- + -ux"),
    ("seteire", 1, "seteira, fresta vertical estreita para disparo de arqueiros", "seteir- + -e"),
    ("matakam", 2, "matacão, balcão perfurado para lançar pedras e óleo", "matak- + -am"),
    ("torreom", 2, "torreão de menagem, reduto central inexpugnável", "torre- + -om"),
    ("atalaie", 1, "atalaia, torre isolada de vigia nas fronteiras", "atalai- + -e"),
    ("alkazar", 2, "alcácer fortificado, palácio-fortaleza real", "alkaz- + -ar"),
    ("masmorre", 1, "masmorra subterrânea no fundo da torre", "masmorr- + -e"),
    ("potelde", 1, "poterna, passagem subterrânea de emergência do castelo", "potern- + -e, sandi rn -> ld"),
    ("palisade", 1, "paliçada de troncos aguçados cravados no terrapleno", "palisad- + -e"),
    ("terraplen", 2, "terrapleno, rampa e plataforma de terra batida e pedra", "terrapl- + -en"),
    ("hipokaust", 2, "hipocausto, sistema subterrâneo de aquecimento dos salões", "hipokaust- (fornalha sob o piso)"),

    # --- LOTE MEIA HORA #6: Música, Organologia e Acústica Coral (40 substantivos concretos) ---
    ("harpe", 1, "harpa grande de salão com coluna entalhada", "harp- + -e"),
    ("lire", 1, "lira clássica de casco e braços curvos", "lir- + -e"),
    ("alaute", 1, "alaúde de bojo abaulado e braço trastejado", "alaut- + -e"),
    ("saltel", 2, "saltério trapezoidal de cordas metálicas", "salt- + -el"),
    ("rabeke", 1, "rabeca medieval de três cordas tocada com arco", "rabek- + -e"),
    ("vielor", 2, "viela de roda com manivela e bordão contínuo", "viel- + -or"),
    ("plettrux", 2, "plectro de osso ou pena para tanger cordas", "plekt- + -rux, sandi kt -> tt"),
    ("kravelhe", 1, "cravelha torneada para ajustar a tensão da corda", "kravelh- + -e"),
    ("kavalet", 2, "cavalete de madeira que transmite a vibração ao tampo", "kaval- + -et"),
    ("tampor", 2, "tampo harmônico de abeto ressonante", "tamp- + -or"),
    ("rosone", 1, "roseta entalhada na boca do instrumento de corda", "roson- + -e"),
    ("bordom", 2, "corda ou tubo grave de nota pedal contínua", "bord- + -om"),
    ("flaute", 1, "flauta doce ou transversal de madeira nobre", "flaut- + -e"),
    ("pifare", 1, "pífaro agudo de pastor ou marcha militar", "pifar- + -e"),
    ("xalume", 1, "charamela de palheta dupla e som potente", "xalum- + -e"),
    ("gaitor", 2, "gaita de foles de couro com tubos de bordão", "gait- + -or"),
    ("foler", 2, "fole de couro para insuflar ar no órgão", "fol- + -er"),
    ("orgamux", 2, "órgão tubular de igreja ou salão imperial", "orgam- + -ux"),
    ("olifant", 2, "olifante, trompa de marfim ou chifre lavrado", "olifant- (chifre sonoro)"),
    ("klariom", 2, "clarim de bronze de tubo longo para arautos", "klari- + -om"),
    ("trombete", 1, "trombeta reta de metal polido", "trombet- + -e"),
    ("buisine", 1, "buísina, trompa curva das legiões do norte", "buisin- + -e"),
    ("timbal", 2, "timbal hemisférico de cobre com pele esticada", "timb- + -al"),
    ("tamboril", 2, "tamboril de duas peles esticadas por cordas", "tambor- + -il"),
    ("adufer", 2, "adufe quadrado com sementes internas", "aduf- + -er"),
    ("kimbalux", 2, "címbalo, par de pratos de bronze ressonante", "kimbal- + -ux"),
    ("krotalux", 2, "crótalo, pequenos discos metálicos de pulso", "krotal- + -ux"),
    ("karrilhom", 2, "carrilhão de sinos afinados na torre", "karrilh- + -om"),
    ("badalor", 2, "badalo pesado de ferro suspenso dentro do sino", "badal- + -or"),
    ("diapasom", 2, "diapasão de aço para aferir a altura da nota", "diapas- + -om"),
    ("tetrakord", 2, "tetracórdio, sucessão modal de quatro notas", "tetra- + kord-"),
    ("oitave", 1, "oitava, intervalo perfeito de consonância", "oitav- + -e"),
    ("kinte", 1, "quinta justa, intervalo harmônico basilar", "kint- + -e"),
    ("antifone", 1, "antífona, canto alternado entre dois coros", "antifon- + -e"),
    ("responsor", 2, "responsório litúrgico entre solista e assembleia", "respons- + -or"),
    ("melisme", 1, "melisma, ornamento vocal de muitas notas numa sílaba", "melism- + -e"),
    ("kadense", 1, "cadência final de repouso de uma frase musical", "kadens- + -e"),
    ("neumor", 2, "neuma, notação musical caligráfica em pergaminho", "neum- + -or"),
    ("antifonar", 2, "antifonário, grande códice iluminado de cânticos", "antifon- + -ar"),
    ("estantor", 2, "estante de coro giratória para grandes antifonários", "estant- + -or"),
]

EXPANSAO_NOUNS.extend(EXPANSAO_NOUNS_PRIMARIOS)


# ==============================================================================
# 3. OS 104 NOVOS ADJETIVOS QUALIFICATIVOS (COM SUPERLATIVO ORGÂNICO EM -n)
# Formato: (adjetivo_em_a, significado, comparativo_maer, superlativo_com_sandi)
# ==============================================================================

def _build_superlative_sandi(stem: str) -> str:
    if stem.endswith("r"):
        return stem[:-1] + "ld"
    if stem.endswith("l"):
        return stem[:-1] + "ll"
    if stem.endswith("mn"):
        return stem[:-2] + "m"
    if stem.endswith("n"):
        return stem[:-1] + "m"
    return stem + "n"


EXPANSAO_ADJECTIVES = []
for _root, _m_pos, _m_priv, _m_iter, _m_itpr in EXPANSAO_VERB_ROOTS:
    _adj = f"{_root}a"
    _sup = _build_superlative_sandi(_root)
    _action_core = _m_pos.split(",")[0].strip()
    EXPANSAO_ADJECTIVES.append((
        _adj,
        f"relativo ou propenso a {_action_core}; caracterizado por {_action_core}",
        f"maer {_adj}",
        _sup
    ))


# ==============================================================================
# 4. OS 24 NOVOS ADVÉRBIOS ESPECIAIS (LOCATIVOS, TEMPORAIS E MODAIS DE CRÔNICA)
# Formato: (adverbio, subclasse, etimologia, significado)
# ==============================================================================

EXPANSAO_ADVERBS = [
    ("belkoravë", "Modal de Tormenta", "belkor + -a + -vë", "estrondosamente, com ribombo de trovão"),
    ("borvoravë", "Modal de Fluxo", "borvor + -a + -vë", "em jorro contínuo, abundantemente como fonte"),
    ("fliroravë", "Modal Luminoso", "fliror + -a + -vë", "cintilantemente, reluzindo na geada"),
    ("morkoravë", "Modal Atmosférico", "morkor + -a + -vë", "de modo enevoado, sob bruma cerrada"),
    ("blenoravë", "Modal de Têmpera", "blenor + -a + -vë", "com têmpera firme, inflexivelmente"),
    ("darporavë", "Modal de Forja", "darpor + -a + -vë", "a golpes cadenciados de malho"),
    ("smeloravë", "Modal de Pureza", "smelor + -a + -vë", "puramente, sem liga ou escória"),
    ("drekoravë", "Modal de Conserva", "drekor + -a + -vë", "de modo curado e duradouro para o inverno"),
    ("fleporavë", "Modal de Trama", "flepor + -a + -vë", "entrelaçadamente, fio a fio"),
    ("spenoravë", "Modal de Vestuário", "spenor + -a + -vë", "de manto afivelado, pronto para partir"),
    ("blororavë", "Modal Náutico", "bloror + -a + -vë", "firmemente ancorado, em porto seguro"),
    ("klororavë", "Modal de Orientação", "kloror + -a + -vë", "guiado pelas estrelas do norte, sem desvio"),
    ("plovoravë", "Modal de Navegação", "plovor + -a + -vë", "a plenas velas, com vento favorável"),
    ("stakoravë", "Modal de Campanha", "stakor + -a + -vë", "em ordem de acampamento, sob tendas"),
    ("drimoravë", "Modal de Vigília", "drimor + -a + -vë", "em sentinela atenta, sem pregar o olho"),
    ("flekoravë", "Modal de Defesa", "flekor + -a + -vë", "de escudo erguido, aparando cada golpe"),
    ("streloravë", "Modal de Tiro", "strelor + -a + -vë", "certeiramente como seta no alvo"),
    ("blimoravë", "Modal de Clemência", "blimor + -a + -vë", "compassivamente, com misericórdia"),
    ("bravoravë", "Modal Heroico", "bravor + -a + -vë", "destemidamente, com bravura indômita"),
    ("drevoravë", "Modal Nostálgico", "drevor + -a + -vë", "saudosamente, lembrando a terra natal"),
    ("klavoravë", "Modal de Prudência", "klavor + -a + -vë", "prudentemente, após maduro conselho"),
    ("stivoravë", "Modal de Constância", "stivor + -a + -vë", "perseverantemente, fiel ao juramento"),
    ("dromoravë", "Modal Épico", "dromor + -a + -vë", "em tom de epopeia, ao som da harpa ancestral"),
    ("svaroravë", "Modal Jurídico", "svaror + -a + -vë", "sob testemunho verdadeiro perante a lei"),
    ("stelkoravë", "Modal Sideral", "stelkor + -a + -vë", "no ápice do zênite, em culminação astral"),
    ("sveloravë", "Modal de Eclipse", "svelor + -a + -vë", "sob penumbra de eclipse, ocultando o sol"),
    ("voldoravë", "Modal Orbital", "voldor + -a + -vë", "em giro perpétuo em torno do eixo polar"),
    ("klomoravë", "Modal Anual", "klomor + -a + -vë", "ao cumprir-se o ciclo completo das estações"),
    ("plamoravë", "Modal Boreal", "plamor + -a + -vë", "sob o clarão cintilante da aurora boreal"),
    ("blovoravë", "Modal de Floração", "blovor + -a + -vë", "em plena floração alpina, com corolas abertas"),
    ("dlimoravë", "Modal Resinoso", "dlimor + -a + -vë", "exsudando resina e bálsamo aromático de pinho"),
    ("glikoravë", "Modal Herbológico", "glikor + -a + -vë", "por infusão medicinal de ervas curativas"),
    ("plimoravë", "Modal de Tundra", "plimor + -a + -vë", "sob manto espesso de musgo e líquen"),
    ("tlavoravë", "Modal Terapêutico", "tlavor + -a + -vë", "com cataplasma balsâmico sobre a ferida"),
    ("blukoravë", "Modal de Rastreio", "blukor + -a + -vë", "farejando o rastro contra o vento da taiga"),
    ("brimoravë", "Modal de Bramido", "brimor + -a + -vë", "com bramido ressonante de cervo real"),
    ("kluporavë", "Modal de Rapina", "klupor + -a + -vë", "em voo picado e certeiro como águia"),
    ("mlikoravë", "Modal Fluvial", "mlikor + -a + -vë", "saltando contra a correnteza gelada"),
    ("prokoravë", "Modal de Alcateia", "prokor + -a + -vë", "em cerco furtivo de alcateia na noite"),
    ("broloravë", "Modal Arterial", "brolor + -a + -vë", "em pulsar vivo de sangue e coração firme"),
    ("druloravë", "Modal Cirúrgico", "drulor + -a + -vë", "com sutura precisa de linho medicinal"),
    ("mlororavë", "Modal de Convalescença", "mloror + -a + -vë", "em franca recuperação do vigor vital"),
    ("tlororavë", "Modal Cicatricial", "tloror + -a + -vë", "de chaga já cicatrizada e sã"),
    ("zlororavë", "Modal de Longevidade", "zloror + -a + -vë", "em longa e lúcida velhice venerável"),
    ("bliroravë", "Modal Arquitetônico", "bliror + -a + -vë", "sob abóbada de pedra lavrada"),
    ("dlororavë", "Modal Estrutural", "dloror + -a + -vë", "firmemente escorado por contrafortes"),
    ("flokoravë", "Modal de Cantaria", "flokor + -a + -vë", "em fiadas perfeitas de silhares de granito"),
    ("glukoravë", "Modal Escultórico", "glukor + -a + -vë", "esculpido em relevo na pedra monumental"),
    ("klovoravë", "Modal de Fortificação", "klovor + -a + -vë", "de portão e rastrilho de ferro erguidos"),
    ("blomoravë", "Modal de Harpa", "blomor + -a + -vë", "dedilhando suavemente as cordas da harpa"),
    ("draloravë", "Modal de Trompa", "dralor + -a + -vë", "ao som vibrante de trompas e charamelas"),
    ("flikoravë", "Modal de Afinação", "flikor + -a + -vë", "em afinação perfeita e consonante"),
    ("gromoravë", "Modal Polifônico", "gromor + -a + -vë", "em plena ressonância polifônica sob a abóbada"),
    ("klorvoravë", "Modal de Percussão", "klorvor + -a + -vë", "ao rufar cadenciado de tímpanos e tambores"),
]
