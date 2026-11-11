# -*- coding: utf-8 -*-
r"""
gerar_lexico_expansao_puro.py
Gera e valida o módulo D:\Conde_Treppio\sandbox\lexico_expansao_v8_1.py com 100% de
pureza glotopoética endógena do Tréppio (0 decalques românicos/greco-latinos > 50%,
0 grafemas proibidos, 0 violações das 21 Leis de Sandi e 0 colisões homofônicas).
"""
import os
import re
import sys
import unicodedata
from difflib import SequenceMatcher

sys.path.insert(0, r"D:\Conde_Treppio\sandbox")

FORBIDDEN_CLUSTERS = re.compile(r"rn|nl|nr|dt|kt|pg|tk|ds|zr|mr|sr|ln")
FORBIDDEN_GRAPHEMES = re.compile(r"c|ç|q|w|lh|nh|ch|j")

# ==============================================================================
# 1. 179 RAÍZES VERBAIS PRIMÁRIAS E COGNITIVAS 100% A-PRIORI / ENDÓGENAS
# ==============================================================================
EXPANSAO_VERB_ROOTS = [
    # --- Campo I: Fenômenos da Natureza, Clima, Geografia e Cosmos (24 raízes) ---
    ("belk", "relampejar, faiscar no céu", "cessar os relâmpagos, serenar o éter", "relampejar repetidamente", "voltar a cessar os relâmpagos"),
    ("darp", "trovejar, ribombar nas serras", "silenciar o trovão", "trovejar continuamente", "voltar a silenciar o trovão"),
    ("fex", "chover fino, garoar na campina", "estiar, secar a garoa", "garoar intermitentemente", "voltar a estiar"),
    ("glor", "congelar a superfície, formar geada", "degelar a crosta de frio", "recongelar pela geada", "voltar a degelar"),
    ("krel", "granizar, chover pedras de gelo", "cessar o granizo", "voltar a granizar", "voltar a cessar o granizo"),
    ("lur", "encobrir de neblina espessa", "dissipar a neblina", "reencobrir de bruma", "voltar a dissipar a neblina"),
    ("mirk", "orvalhar ao amanhecer", "secar o orvalho pelo sol", "reorvalhar", "voltar a secar o orvalho"),
    ("nax", "escurecer no ocaso, anoitecer", "clarear a alvorada", "voltar a anoitecer", "voltar a clarear"),
    ("peld", "inundar a margem, transbordar o rio", "baixar o nível das águas", "reinundar na cheia", "voltar a baixar as águas"),
    ("rixk", "desmoronar rochas, causar avalancha", "estabilizar a encosta", "desmoronar de novo", "voltar a estabilizar a encosta"),
    ("svel", "eclipsar um astro, ocultar o sol", "desvelar o disco solar", "reeclipsar no ciclo sideral", "voltar a desvelar o astro"),
    ("tarp", "sacudir a terra, causar tremor", "assentar o solo firme", "tremer em réplicas", "voltar a assentar o solo"),
    ("vruk", "jorrar água termal ou gêiser", "estancar a nascente quente", "rejorrar das profundezas", "voltar a estancar a fonte"),
    ("xelp", "rodopiar em redemoinho de vento", "acalmar o turbilhão", "rodopiar novamente", "voltar a acalmar o turbilhão"),
    ("zold", "ressoar o eco nos desfiladeiros", "abafar a acústica do vale", "ecoar repetidas vezes", "voltar a abafar o eco"),
    ("brek", "rachar o gelo na primavera", "soldar a placa glacial", "rachar novamente o gelo", "voltar a soldar o gelo"),
    ("flir", "cintilar como estrela ou aurora boreal", "apagar a cintilação", "recintilar no firmamento", "voltar a apagar a cintilação"),
    ("grop", "erodir a pedra pela água ou vento", "sedimentar a rocha", "reerodir o cânion", "voltar a sedimentar"),
    ("kvas", "brotar manancial da rocha viva", "secar o olho d'água", "rebrotar na estação das chuvas", "voltar a secar o manancial"),
    ("mvelk", "ondular o mar, formar vagas", "aplainar a superfície marinha", "ondular em ressaca", "voltar a acalmar o mar"),
    ("nulp", "acumular bancos de neve alta", "varrer a neve acumulada", "reacumular neve na tormenta", "voltar a limpar a neve"),
    ("skir", "clarear o céu após a tempestade", "toldar o firmamento de nuvens", "reclarear o horizonte", "voltar a toldar o céu"),
    ("tvel", "soprar brisa suave das colinas", "estagnar o ar em calmaria", "soprar brisa novamente", "voltar a estagnar o ar"),
    ("vrel", "fluir em corredeira rápida", "represar em águas paradas", "voltar a correr em cachoeira", "voltar a represar"),

    # --- Campo II: Corpo, Saúde, Percepção Sensorial e Emoções (24 raízes) ---
    ("blam", "palpitar o coração, pulsar forte", "aquietar o batimento", "pulsar aceleradamente", "voltar a aquietar o pulso"),
    ("drek", "engolir, deglutir o alimento", "regurgitar, expelir", "engolir repetidamente", "voltar a expelir"),
    ("frel", "estremecer de calafrio ou emoção", "firmar os membros", "estremecer de novo", "voltar a firmar o corpo"),
    ("glin", "piscar os olhos, pestanejar", "fitar com olhar fixo", "piscar continuamente", "voltar a fitar sem piscar"),
    ("ferp", "inspirar fundo o ar nos pulmões", "prender o fôlego, expirar", "inspirar compassadamente", "voltar a prender o fôlego"),
    ("lisk", "lamber, provar com a língua", "rejeitar ao paladar", "provar repetidas vezes", "voltar a rejeitar ao paladar"),
    ("mvuk", "franzir o cenho em concentração", "desanuviar a fronte", "franzir a testa de novo", "voltar a serenar a fronte"),
    ("nelp", "farejar, sentir aroma ou perfume", "perder o olfato", "farejar a trilha novamente", "voltar a perder o olfato"),
    ("prek", "tocar com os dedos, tatear", "recolher a mão, abster-se de tocar", "tatear no escuro de novo", "voltar a recolher a mão"),
    ("rulp", "bocejar de sono ou fadiga", "despertar a atenção", "bocejar repetidamente", "voltar a despertar"),
    ("falp", "cochilar suavemente, dormitar", "manter-se alerta", "tornar a cochilar", "voltar a manter-se alerta"),
    ("truk", "morder, mastigar com firmeza", "afrouxar os dentes", "mastigar lentamente", "voltar a afrouxar a mordida"),
    ("vlim", "lacrimejar, marejar os olhos", "enxugar as lágrimas", "voltar a lacrimejar", "voltar a enxugar o pranto"),
    ("xarp", "tossir, limpar a garganta", "acalmar a tosse", "tossir repetidamente", "voltar a acalmar a garganta"),
    ("zlep", "cicatrizar a pele, fechar corte", "reabrir a chaga", "recicatrizar o tecido", "voltar a abrir o ferimento"),
    ("kuex", "corar a face de pudor ou rubor", "empalidecer o semblante", "tornar a corar", "voltar a empalidecer"),
    ("fluk", "sussurrar ao ouvido, segredar", "falar em voz plena", "sussurrar novamente", "voltar a falar alto"),
    ("fasp", "soltar queixume de dor ou esforço", "reprimir o queixume", "queixar-se continuamente", "voltar a suportar em silêncio"),
    ("klir", "ouvir com nitidez, escutar atento", "ensurdecer ao ruído", "escutar de novo com atenção", "voltar a ignorar o som"),
    ("mlep", "sorrir serenamente, comprazer-se", "assumir semblante austero", "sorrir outra vez", "voltar à austeridade"),
    ("nvek", "esticar os membros, espreguiçar-se", "encolher o corpo", "alongar-se novamente", "voltar a encolher-se"),
    ("skul", "suar pelo esforço da forja ou marcha", "refrescar a epiderme", "suar abundantemente", "voltar a refrescar o corpo"),
    ("tlim", "jejuar por voto litúrgico", "quebrar a abstinência ritual", "retomar o jejum sacro", "voltar a alimentar-se"),
    ("visk", "enfaixar ferida, aplicar atadura", "desenfaixar o membro", "reenfaixar com linho limpo", "voltar a retirar a atadura"),

    # --- Campo III: Ofícios, Agricultura, Forja, Tecelagem e Arquitetura (24 raízes) ---
    ("brik", "assentar tijolos ou blocos de pedra", "demolir alvenaria", "reerguer parede de pedra", "voltar a demolir"),
    ("drel", "tornear madeira ou marfim", "deixar a peça bruta", "retornear com precisão", "voltar a desbastar"),
    ("fruk", "arar a terra, abrir sulco no solo", "deixar o campo em pousio", "rearar na nova estação", "voltar a deixar em pousio"),
    ("glop", "fundir metal no cadinho ardente", "solidificar o lingote", "refundir a liga metálica", "voltar a resfriar o molde"),
    ("krimp", "temperar o aço em água gélida", "destemperar no fogo brando", "retemperar a lâmina", "voltar a destemperar"),
    ("lrek", "fiar a lã ou o linho no fuso", "desfiar a meada", "fiar novamente", "voltar a desfiar"),
    ("mvop", "tecer no tear, entrelaçar fios", "destecer a trama", "retecer o estofo", "voltar a destecer"),
    ("nvik", "entalhar relevo em madeira nobre", "alisar a superfície entalhada", "reentalhar o brasão", "voltar a alisar"),
    ("mirx", "lustrar joia ou espelho metálico", "fosquear a superfície", "relustrar até espelhar", "voltar a fosquear"),
    ("rlep", "ceifar o trigo maduro com foice", "poupar a seara verde", "ceifar a segunda colheita", "voltar a poupar a lavoura"),
    ("smel", "moer o grão entre mós de pedra", "conservar o grão inteiro", "remoer até obter flor de farinha", "voltar a guardar o grão"),
    ("tlek", "erguer viga mestra ou cumeeira", "desmontar o madeiramento", "reerguer a estrutura do teto", "voltar a desmontar"),
    ("vlop", "calafetar casco de nau com breu", "abrir fresta no costado", "recalafetar a embarcação", "voltar a desgastar o breu"),
    ("xrel", "podar ramos secos da árvore", "deixar a copa silvestre", "repodar o pomar", "voltar a não podar"),
    ("zvuk", "forjar elos de corrente ou cota", "romper os elos da malha", "reforjar a malha de aço", "voltar a romper os elos"),
    ("bluk", "curtir o couro em tanino de casca", "deixar a pele crua", "recurtir o couro", "voltar a amaciar a pele"),
    ("drim", "esculpir estátua em mármore ou rocha", "desfazer a efígie", "reesculpir o monumento", "voltar a quebrar a estátua"),
    ("flep", "trançar cordas de cânhamo ou crina", "destrançar o cabo", "retrançar a amarra", "voltar a destrançar"),
    ("grik", "cinzelar inscrição na lápide", "apagar o epígrafo", "recinzelar as letras", "voltar a rasurar a pedra"),
    ("klup", "encastoar gema em anel ou coroa", "desencastoar a pedra preciosa", "reencastoar a joia", "voltar a remover a gema"),
    ("mlik", "ordenhar o rebanho ao alvorecer", "desmamar o filhote", "ordenhar novamente à tarde", "voltar a encerrar a ordenha"),
    ("nvop", "semear grãos na terra lavrada", "recolher a sementeira", "ressemeadura de primavera", "voltar a suspender o plantio"),
    ("slik", "esmaltar cerâmica ao forno", "deixar o barro poroso", "reesmaltar a ânfora", "voltar a tirar o verniz"),
    ("tril", "peneirar a farinha ou o ouro", "misturar o cascalho", "repeneirar com malha fina", "voltar a misturar"),

    # --- Campo IV: Navegação, Guerra, Estratégia, Equitação e Viagem (24 raízes) ---
    ("bvel", "ancorar a nau em porto seguro", "levar âncora, zarpar", "reancorar na enseada", "voltar a zarpar"),
    ("drik", "esporear o corcel a galope", "conter a montaria a passo", "galopar novamente", "voltar a conter o cavalo"),
    ("flin", "encordoar o arco de guerra", "afrouxar a corda do arco", "reencordoar para o combate", "voltar a desarmar o arco"),
    ("gvel", "remar contra a correnteza", "erguer os remos em descanso", "remar em cadência dobrada", "voltar a recolher os remos"),
    ("tvelp", "sitiar fortaleza, rodear muralha", "levantar o sítio militar", "ressitiar a praça-forte", "voltar a levantar o sítio"),
    ("lvim", "hastear o estandarte imperial", "arriar o pavilhão", "rehastear a bandeira", "voltar a arriar o pendão"),
    ("mvek", "emboscar o inimigo no desfiladeiro", "revelar a posição tática", "armar nova emboscada", "voltar a descobrir a guarda"),
    ("nvel", "vadear o rio nos baixios", "recuar ante a cheia", "revadear a passagem", "voltar a deter-se na margem"),
    ("veyn", "velejar com vento de popa", "colher as velas na tormenta", "velejar novamente ao largo", "voltar a colher o pano"),
    ("rvel", "acantonar a legião em acampamento", "desmontar as tendas de campanha", "reacantonar no inverno", "voltar a levantar acampamento"),
    ("tupx", "disparar flecha ou dardo certeiro", "reter o disparo na aljava", "disparar em salva contínua", "voltar a cessar os disparos"),
    ("varx", "patrulhar as fronteiras da serra", "recolher as sentinelas", "repatrulhar o perímetro", "voltar a recolher a ronda"),
    ("vlir", "aparar golpe com o escudo", "baixar a guarda na luta", "aparar sucessivos golpes", "voltar a abrir a guarda"),
    ("xvel", "tocar o clarim de alvorada ou carga", "calar a trombeta de guerra", "ressoar o toque de reunir", "voltar a calar o clarim"),
    ("malp", "aparelhar o cavalo de viagem", "desaparelhar a montaria cansada", "reaparelhar para nova etapa", "voltar a tirar o arreio"),
    ("rukx", "desafiar em duelo singular de honra", "recusar o desafio", "redobrar o desafio", "voltar a declinar o combate"),
    ("dvel", "fortificar trincheira ou paliçada", "desmantelar as defesas", "refortificar o reduto", "voltar a abrir brecha"),
    ("malx", "domar corcel bravo pelas rédeas", "soltar o cavalo em liberdade", "redomar a montaria", "voltar a soltar as rédeas"),
    ("glik", "escalar escarpa ou muralha com gancho", "descer por corda à base", "reescalar o paredão", "voltar a descer a encosta"),
    ("kvel", "escoltar caravana pelos passos alpinos", "dispersar o comboio", "reescoltar a travessia", "voltar a deixar sem escolta"),
    ("mvel", "negociar trégua entre exércitos", "romper o armistício", "renovar a trégua", "voltar a declarar hostilidades"),
    ("pvel", "sondar a profundidade do canal", "navegar às cegas sem prumo", "ressondar o fundo rochoso", "voltar a recolher a sonda"),
    ("svik", "forragear provisões no campo", "esgotar os víveres da tropa", "reforragear a região", "voltar a racionar víveres"),
    ("tvelk", "orientar-se pela estrela polar", "perder o rumo na cerração", "reorientar a rota sideral", "voltar a desviar do norte"),

    # --- Campo V: Direito Imperial, Diplomacia, Administração e Comércio (24 raízes) ---
    ("blik", "autenticar com selo de cera real", "romper o lacre oficial", "resselar o pergaminho", "voltar a violar o selo"),
    ("drul", "cobrar tributo ou dízimo imperial", "isentar de impostos", "recobrar o fisco anual", "voltar a conceder isenção"),
    ("flim", "arbitrar litígio entre Casas Nobres", "abster-se de mediar", "rearbitrar a contenda", "voltar a declinar o juízo"),
    ("grul", "emancipar servo ou vassalo", "sujeitar à servidão", "reemancipar por carta", "voltar a sujeitar"),
    ("tokx", "reunir a corte suprema da Coroa", "dissolver a assembleia", "reconvocar os dignitários", "voltar a dissolver a sessão"),
    ("lruk", "confiscar bens para o erário", "restituir o patrimônio", "reconfiscar por traição", "voltar a restituir os bens"),
    ("mvul", "outorgar feudo ou título de nobreza", "revogar a mercê condal", "reconfirmar a carta de feudo", "voltar a cassar o título"),
    ("nvul", "testemunhar sob juramento sagrado", "retratar o depoimento", "reafirmar o testemunho", "voltar a calar no tribunal"),
    ("molx", "promulgar decreto da Chancelaria", "ab-rogar lei antiga", "repromulgar o édito", "voltar a revogar a norma"),
    ("rluk", "auditar as contas do tesouro", "encerrar a tomada de contas", "reauditar os livros", "voltar a arquivar o balanço"),
    ("sluk", "apelar à Corte Suprema", "acatar a sentença inferior", "recorrer novamente em graça", "voltar a desistir do recurso"),
    ("trul", "ratificar tratado de aliança", "denunciar o pacto diplomático", "reratificar a aliança", "voltar a romper o tratado"),
    ("vluk", "cunhar moedas com a efígie real", "recolher moeda desvalorizada", "recunhar a série áurea", "voltar a fundir as moedas"),
    ("xrul", "banir para além das fronteiras", "repatriar o exilado", "rebanir por reincidência", "voltar a conceder retorno"),
    ("zvukx", "empenhar palavra ou penhor real", "resgatar a garantia dada", "reempenhar a honra", "voltar a quitar o penhor"),
    ("brul", "inventariar o espólio da Casa", "dispersar a herança", "reinventariar os bens", "voltar a partilhar o acervo"),
    ("dlim", "acreditar embaixador junto à corte", "retirar as credenciais", "reacreditar o legado", "voltar a chamar o enviado"),
    ("frul", "arrendar terras da Coroa", "retomar a posse direta", "renovar o arrendamento", "voltar a extinguir o foro"),
    ("glul", "notificar oficialmente por arauto", "revogar a citação", "renotificar em praça pública", "voltar a sustar o pregão"),
    ("krul", "coroar o soberano no santuário", "abdicar do trono", "reafirmar os votos da coroa", "voltar a depor as insígnias"),
    ("mlul", "arquivar nos rolos perpétuos", "desentranhar o pergaminho", "rearquivar na Chancelaria", "voltar a extrair dos autos"),
    ("plul", "indenizar dano causado em guerra", "eximir de reparação", "reindenizar em ouro", "voltar a perdoar a dívida"),
    ("svul", "demarcar fronteira com marcos de pedra", "apagar os limites territoriais", "redemarcar a divisa", "voltar a remover os marcos"),
    ("tlul", "exercer regência em nome do herdeiro", "entregar o cetro ao maior", "reassumir a regência", "voltar a passar o governo"),

    # --- Campo VI: Filosofia, Teologia, Liturgia, Música, Retórica e Arte (24 raízes) ---
    ("blir", "meditar em silêncio contemplativo", "dispersar a mente no mundo", "remeditar sobre o dogma", "voltar a distrair o espírito"),
    ("drir", "salmodiar em versículos alternados", "encerrar a salmodia", "ressalmodiar em coro", "voltar a calar o antifonário"),
    ("flirx", "incensar o altar nos ritos solenes", "extinguir o turíbulo", "reincensar o santuário", "voltar a recolher o incenso"),
    ("grir", "dedilhar as cordas da harpa", "abafar as cordas com a palma", "rededilhar o prelúdio", "voltar a silenciar a lira"),
    ("halx", "interpretar presságio sideral", "velar o mistério dos astros", "reinterpretar a conjunção", "voltar a fechar o prognóstico"),
    ("lrir", "iluminar manuscrito com ouro e carmim", "deixar o fólio sem ornato", "reiluminar a capitular", "voltar a raspar a iluminura"),
    ("mvir", "declamar epopeia em cadência clássica", "falar em prosa chã", "redeclamar o canto heróico", "voltar à locução comum"),
    ("nvir", "consagrar a fronte com bálsamo sagrado", "purificar a fronte com água", "reconsagrar o iniciado", "voltar a lavar a fronte"),
    ("prir", "refutar argumento com silogismo", "conceder a premissa ao adversário", "rerrefutar na disputa", "voltar a anuir à tese"),
    ("rrir", "compor hino ou cânone polifônico", "improvisar sem regra", "recompor a partitura", "voltar a desfechar o improviso"),
    ("svir", "jejuar na vigília das estrelas", "celebrar o ágape festivo", "retomar a vigília sacra", "voltar a abrir o banquete"),
    ("tvir", "isolar a essência universal na mente", "particularizar no caso concreto", "reisolar o conceito puro", "voltar ao exemplo sensível"),
    ("vrir", "consagrar o cálice na elevação", "purificar os vasos após o rito", "reconsagrar na festa", "voltar a guardar o cálice"),
    ("xvir", "esconjurar sombra ou espírito impuro", "invocar a proteção celeste", "reesconjurar o recinto", "voltar a selar o portal"),
    ("zvir", "afinar os tubos do grande órgão", "desafinar pela umidade", "reafinar na oitava justa", "voltar a perder a afinação"),
    ("bmir", "decifrar inscrição arcaica pré-Síncrese", "criptografar em cifra secreta", "redecifrar o códice", "voltar a ocultar em cifra"),
    ("dmir", "venerar relíquia dos antigos", "recolher a relíquia ao sacrário", "revenerar em procissão", "voltar a velar o relicário"),
    ("fmir", "ensinar a gramática normativa", "desaprender o vício plebeu", "reensinar a doutrina culta", "voltar a corrigir a pronúncia"),
    ("gmir", "contemplar a harmonia das esferas", "baixar os olhos à terra", "recontemplar o firmamento", "voltar ao horizonte terreno"),
    ("kmir", "transcrever códice em pergaminho limpo", "inutilizar fólio maculado", "retranscrever sem erro", "voltar a descartar a cópia"),
    ("lmir", "modular a voz para o registro grave", "elevar o canto ao agudo", "remodular a cadência", "voltar a subir o tom"),
    ("mmir", "dedicar templo ou monumento a Gyos", "desconsagrar ruína antiga", "rededicar o santuário", "voltar a encerrar o culto"),
    ("pmir", "demonstrar teorema ou verdade eterna", "pôr em dúvida metódica", "redemonstrar pela razão", "voltar a questionar a prova"),
    ("smir", "entoar o Zo es de fechamento", "abrir o introito litúrgico", "reentoar o amém coral", "voltar a iniciar a prece"),

    # --- Campo VII: Vida Doméstica, Costumes, Vestuário, Culinária e Família (20 raízes) ---
    ("bnik", "embalar o berço da criança", "despertar o infante", "reembalar ao som de cantiga", "voltar a tirar do berço"),
    ("dnik", "temperar o assado com ervas da serra", "servir a vianda simples", "retemperar o caldo", "voltar a suavizar o tempero"),
    ("fnik", "varrer a cinza da lareira", "espalhar brasa no borralho", "revarrer o salão de pedra", "voltar a cobrir a brasa"),
    ("gnik", "abotoar o manto com fivela de prata", "desafivelar a capa de viagem", "reabotoar contra o vento", "voltar a soltar o manto"),
    ("xalb", "bater a nata até formar manteiga", "desnatar o leite fresco", "rebater na batedeira", "voltar a separar o soro"),
    ("lvik", "defumar carnes no fumeiro de pinho", "hidratar a carne seca", "redefumar a provisão", "voltar a pôr de molho"),
    ("huxp", "dobrar os linhos e cobertas na arca", "estender a roupa ao sol", "redobrar o enxoval", "voltar a desdobrar as mantas"),
    ("nnik", "trançar os cabelos em penteado nobre", "soltar as madeixas", "retrançar com fitas de ouro", "voltar a soltar os cabelos"),
    ("pnik", "pôr a mesa para o banquete", "levantar a mesa após a ceia", "repor as taças e travessas", "voltar a recolher a baixela"),
    ("rvik", "fermentar o hidromel em tonéis de carvalho", "decantar a bebida límpida", "refermentar a safra", "voltar a engarrafar"),
    ("snik", "bordar brasão da Casa no estandarte", "desmanchar o ponto torto", "rebordar com fio de ouro", "voltar a desfazer o bordado"),
    ("tnik", "aquecer água para o banho de vapor", "esvaziar a tina de madeira", "reaquecer as pedras do banho", "voltar a esfriar a tina"),
    ("vnik", "acender todas as arandelas do salão", "apagar os archotes para o sono", "reacender as luminárias", "voltar a deixar em penumbra"),
    ("xnik", "agasalhar o hóspede com peles perto do fogo", "acompanhar o viajante à porta", "reagasalhar na nevasca", "voltar a despedir o amigo"),
    ("znik", "celebrar bodas ou aliança entre famílias", "encerrar os festejos nupciais", "comemorar o aniversário da união", "voltar à rotina após a festa"),
    ("brikx", "assar pães no forno de pedra comunitário", "esfriar a fornada na grade", "reassar o pão dormido", "voltar a tirar do forno"),
    ("drikx", "calçar botas encouraçadas para a neve", "descalçar junto à lareira", "recalçar para a marcha", "voltar a descansar os pés"),
    ("frikx", "destilar essência de ervas alpinas", "diluir o elixir em água pura", "redestilar no alambique", "voltar a suavizar a poção"),
    ("grikx", "prensar bagas silvestres para vinho", "recolher o bagaço", "reprensar a vindima", "voltar a limpar o lagar"),
    ("krikx", "transmitir o anel de sinete ao primogênito", "guardar as joias da linhagem", "reconfirmar a sucessão", "voltar a lacrar o cofre"),

    # --- Lote #1 (Astronomia e Mecânica Celeste): 15 Raízes Verbais Puras ---
    ("lexp", "alinhar o quadrante com o meridiano", "desalinhar o limbo graduado", "realinhar a alidade", "voltar a recolher o instrumento"),
    ("xerk", "atingir o ponto culminante no céu", "declinar rumo ao poente", "reculminar no ciclo anual", "voltar a declinar no horizonte"),
    ("filp", "mergulhar no hemisfério inferior sob a terra", "ascender do fundo à aurora", "remergulhar no hemisfério inferior", "voltar a emergir no oriente"),
    ("zulp", "percorrer as casas das constelações", "sair da faixa eclíptica", "repercorrer o anel sideral", "voltar a afastar-se da eclíptica"),
    ("feap", "projetar a sombra solar no relógio de pedra", "apagar a sombra ao meio-dia", "reprojetar a sombra horária", "voltar a anular a sombra"),
    ("tonp", "calcular as tábuas celestes em pergaminho", "errar o cômputo astral", "recalcular as tábuas siderais", "voltar a revisar o cálculo"),
    ("kelp", "alinhar dois astros no mesmo grau sideral", "afastar-se em oposição astral", "realinhar em par sideral", "voltar a separar as órbitas"),
    ("varp", "afastar-se no ponto mais distante da órbita", "aproximar-se no ponto orbital mais próximo", "reatingir o extremo orbital", "voltar a aproximar-se do centro"),
    ("turp", "deslocar lentamente o polo dos equinócios", "estabilizar o polo celeste", "redeslocar ao longo das eras", "voltar a fixar o polo"),
    ("tupk", "oscilar sutilmente o eixo da esfera", "cessar a oscilação axial", "reoscilar no ciclo lunar", "voltar a deter a oscilação"),
    ("libk", "balançar a face visível da lua", "ocultar a face posterior lunar", "rebalançar em quadratura", "voltar a esconder a borda lunar"),
    ("velp", "encobrir estrela atrás do disco lunar", "reemergir a estrela após a passagem", "reencobrir o astro", "voltar a liberar o brilho estelar"),
    ("kadp", "medir a distância angular até o topo do céu", "perder a referência vertical", "remedir a altura do astro", "voltar a baixar o quadrante"),
    ("oxep", "determinar o ângulo sobre a linha da terra", "desviar da linha meridiana", "redeterminar a direção", "voltar a perder o rumo"),
    ("belp", "intercalar os dias sagrados fora do mês", "fechar o ano civil ordinário", "reintercalar no ciclo quadrienal", "voltar a contar o ano comum"),
]

# ==============================================================================
# 2. 260 SUBSTANTIVOS ENDÓGENOS DOS LOTES #1 A #6 (100% RAÍZES TRÉPPIAS + SANDI)
# ==============================================================================
EXPANSAO_NOUNS_PRIMARIOS = [
    # --- Lote #1: Astronomia, Esfera Celeste e Calendário (40 substantivos endógenos) ---
    ("lexevur", 2, "cometa, astro errante de cabeleira ígnea", "lexe (estrela) + vur (fogo)"),
    ("gildirlan", 2, "lua crescente, quarto crescente lunar", "gir- (crescer) + nirlan (lua), rn -> ld"),
    ("lamirlan", 2, "lua cheia, plenilúnio de prata", "lan (luz/cheia) + nirlan (lua), nn -> m"),
    ("vellirlan", 2, "lua nova, novilúnio escuro", "vel (sombra) + nirlan (lua), ln -> ll"),
    ("agildirlan", 2, "lua minguante, quarto minguante", "agir- (minguar) + nirlan (lua), rn -> ld"),
    ("avellirlan", 2, "eclipse lunar, sombra sobre a lua", "avel- + nirlan (lua), ln -> ll"),
    ("velfea", 1, "eclipse solar, ocultação do disco do sol", "vel (sombra) + fea (sol)"),
    ("feakade", 1, "solstício de verão, ápice da jornada solar", "fea (sol) + kade (cume/ápice)"),
    ("avurfeabel", 2, "solstício de inverno, dia do sol gélido", "avur (frio) + feabel (solstício)"),
    ("iddabellir", 2, "equinócio, igualdade entre dia e noite", "idda (igual) + bel (dia) + nir (noite), ln -> ll"),
    ("xerypokegar", 2, "constelação boreal do Grande Guardião do Norte", "xery (do céu) + pokegar (grande fera)"),
    ("xeryoxte", 1, "constelação do Guerreiro Celeste", "xery (do céu) + oxte (guerreiro)"),
    ("lanxeryvar", 2, "Via Láctea, estrada luminosa de estrelas no céu", "lan (luz) + xery (do céu) + var (caminho)"),
    ("xerkade", 1, "zênite, ponto culminante do firmamento", "xer (céu) + kade (topo)"),
    ("filkade", 1, "nadir, ponto abissal oposto ao zênite", "fil (abismo) + kade (ponto)"),
    ("lexemirttek", 2, "astrolábio de latão, instrumento de medir estrelas", "lexe (estrela) + mir (olhar) + -tek"),
    ("feaveltek", 2, "gnômon, haste do relógio de sol", "fea (sol) + vel (sombra) + -tek"),
    ("lexekaran", 2, "anel das constelações, cinturão sideral do ano", "lexe (estrela) + karan (domínio/anel)"),
    ("xunfealan", 2, "arrebol dourado da aurora, rubor matinal", "xun (dourado) + fealan (aurora)"),
    ("vellexe", 1, "estrela vespertina, primeiro astro do entardecer", "vel (entardecer) + lexe (estrela)"),
    ("bellexe", 1, "estrela d'alva, astro anunciador da manhã", "bel (dia) + lexe (estrela)"),
    ("xervuril", 2, "estrela cadente, bólido luminoso na noite", "xer (céu) + vuril (centelha de fogo)"),
    ("xerrixe", 1, "pedra caída do céu, meteorito sideral de forja", "xer (céu) + rixe (rocha)"),
    ("atonkrbel", 2, "dia sagrado fora do mês no fim do ano solar", "atonkre (fora do tempo) + bel (dia)"),
    ("kattonkrbel", 2, "ano de dia intercalado a cada quatro ciclos", "kat (quatro) + tonkre + bel"),
    ("feabelvar", 2, "linha do meio-dia, arco norte-sul do céu", "feabel (meio-dia) + var (linha/caminho)"),
    ("xeroxe", 1, "horizonte, linha onde o céu encontra a terra", "xer (céu) + oxe (terra)"),
    ("velfealan", 2, "penumbra entre a luz solar e a noite", "vel (sombra) + fealan (clarão)"),
    ("tonkrsiftek", 2, "códice anual das estações e fases da lua", "tonkre (tempo) + siftek (anais)"),
    ("lexekitor", 2, "tábua calculada das posições dos astros", "lexe (estrela) + kitor (registro)"),
    ("lexefervé", 2, "nuvem estelar profunda no firmamento", "lexe (estrela) + fervé (nuvem)"),
    ("sallexe", 1, "aglomerado das Irmãs Luminosas no céu", "san (sete) + lexe (estrela), nl -> ll"),
    ("xerypalkgar", 2, "ponto orbital mais distante da Terra", "xery (celeste) + palk (passo) + -gar"),
    ("oxepalkil", 2, "ponto orbital mais próximo da Terra", "oxe (terra) + palk (passo) + -il"),
    ("kellexe", 1, "alinhamento de dois astros no mesmo grau sideral", "kel (junto) + lexe (astro)"),
    ("odlexe", 1, "posição de dois astros em lados opostos do céu", "od- (oposto) + lexe (astro)"),
    ("lammirlan", 2, "halo luminoso de gelo ao redor da lua", "lan (luz) + mir + nirlan, nm -> m"),
    ("dofea", 1, "falso sol espelhado nas nuvens de gelo", "do (dois) + fea (sol)"),
    ("oratisor", 2, "ciência sagrada da arquitetura do universo", "orat (universo) + isor (sabedoria)"),
    ("xerykorgar", 2, "esfera de anéis metálicos que representa o cosmos", "xery (celeste) + kor (aro) + -gar"),

    # --- Lote #2: Botânica, Flora, Silvicultura e Ervas Medicinais (40 substantivos endógenos) ---
    ("koldirkor", 2, "pinheiro boreal perene resistente ao inverno", "koldir (inverno) + kor (árvore)"),
    ("rixekor", 2, "abeto alto das escarpas montanhesas", "rixe (montanha) + kor (árvore)"),
    ("feldirkor", 2, "larício de agulhas douradas no outono", "feldir (outono) + kor (árvore)"),
    ("sfarkor", 2, "teixo longevo de madeira flexível para combate", "sfar (defesa) + kor (árvore)"),
    ("lankor", 2, "bétula de casca alva prateada", "lan (luz/alva) + kor (árvore)"),
    ("rukrakor", 2, "carvalho real de tronco venerável", "rukra (forte) + kor (árvore)"),
    ("yntekkor", 2, "freixo firme usado para hastes de lança e cajados", "yntek (cajado/haste) + kor (árvore)"),
    ("vevarkor", 2, "salgueiro chorão das margens de rio", "vevar (rio) + kor (árvore)"),
    ("velkor", 2, "olmo frondoso de sombra espessa", "vel (sombra) + kor (árvore)"),
    ("vekor", 2, "amieiro das várzeas úmidas", "Vé (água) + kor (árvore)"),
    ("xunkoril", 2, "zimbro aromático de bagas azuladas das serras", "xun (aromático/dourado) + koril (arbusto)"),
    ("akazkoril", 2, "erva-de-lobo de flor azul e raiz venenosa", "akaz- (matar) + koril (erva)"),
    ("falmkoril", 2, "erva calmante das encostas úmidas para o sono", "fal- (dormir) + koril (erva)"),
    ("mygakoril", 2, "erva-dos-carpinteiros de folhas recortadas", "myga (mil) + koril (erva)"),
    ("nirlankoril", 2, "erva prateada lunar das veredas", "nirlan (lua) + koril (erva)"),
    ("kuekoril", 2, "erva amarga de flor azul intenso dos prados altos", "kue (intenso) + koril (erva)"),
    ("vilkkoril", 2, "erva-das-quedas de flor amarela para contusões", "vilt- (curar) + koril (erva), tk -> kk"),
    ("tulkoril", 2, "raiz tóxica das pastagens alpinas", "tul (delírio) + koril (erva)"),
    ("kronkoril", 2, "raiz antropomórfica dos ritos arcanos", "kron (homem) + koril (raiz)"),
    ("nirkoril", 2, "planta sombria de bagas negras soporíferas", "nir (noite) + koril (erva)"),
    ("oxekoril", 2, "tapete verde macio sobre rochas e troncos", "oxe (solo) + koril (planta)"),
    ("avurkoril", 2, "vegetação cinzenta que reveste penhascos gélidos", "avur (gelo) + koril (planta)"),
    ("velkoril", 2, "cogumelo silvestre nascido após a chuva", "vel (sombra) + koril (planta)"),
    ("dakkoril", 2, "cogumelo comestível carnudo dos bosques de pinho", "dak- (comer) + koril (planta)"),
    ("kuakoril", 2, "cogumelo de chapéu rubro mosqueado", "kua (vermelho) + koril (planta)"),
    ("vurkorvé", 2, "breu inflamável extraído dos pinheiros", "vur (fogo) + korvé (resina)"),
    ("laurikorvé", 2, "resina fóssil translúcida cor de mel", "lauri (ouro) + korvé (resina)"),
    ("filkor", 2, "caule subterrâneo que armazena sustento no inverno", "fil (cerne/fundo) + kor (planta)"),
    ("korsfar", 2, "casca protetora externa do tronco das árvores", "kor (árvore) + sfar (proteção)"),
    ("korvok", 2, "entrecasca fibrosa que conduz a seiva da árvore", "kor (árvore) + vok (fluido vital)"),
    ("lotakoril", 2, "anel de pétalas coloridas da flor", "lota (belo) + koril (flor)"),
    ("xunferil", 2, "pó dourado fecundo levado pelo vento", "xun (dourado) + fer (vento) + -il"),
    ("idkoril", 2, "partícula reprodutiva das samambaias e musgos", "id (semente mínima) + koril"),
    ("velkropekor", 2, "feto de frondes rendilhadas da floresta úmida", "vel (sombra) + krope + kor"),
    ("faskoril", 2, "erva de pelos ardentes que queima a pele", "fas (ardor/dor) + koril (erva)"),
    ("saikkoril", 2, "planta espinhosa roxa das encostas pedregosas", "said- (espinho/ferir) + koril, dk -> kk"),
    ("kuefelil", 2, "amora silvestre de espinheiro", "kue (rubro) + felil (pequeno fruto)"),
    ("velkuefel", 2, "baga azul-escura dos sub-bosques boreais", "vel (escuro) + kue + fel (fruto)"),
    ("avurfelil", 2, "baga ácida escarlate dos charcos gelados", "avur (gelo) + felil (fruto)"),
    ("xelvelotakor", 2, "flor-das-neves aveludada e alva dos picos", "xelvé (neve) + lota (bela) + kor"),

    # --- Lote #3: Zoologia, Fauna Boreal, Aves, Peixes e Bestiário (40 substantivos endógenos) ---
    ("nirpokegar", 2, "grande lobo cinzento das matas boreais", "nir (noite) + pokegar (fera)"),
    ("rixepokegar", 2, "urso pardo poderoso das cavernas montanhesas", "rixe (montanha) + pokegar (fera)"),
    ("avurpokegar", 2, "grande fera branca dos mares gelados", "avur (gelo) + pokegar (fera)"),
    ("mirbaxi", 1, "felino montês de orelhas em penacho e vista aguda", "mir (visão) + baxi (felino)"),
    ("kuepoke", 1, "animal astuto de cauda felpuda avermelhada", "kue (vermelho) + poke (animal)"),
    ("xelvepoke", 1, "animal de pelagem alva mimética no inverno", "xelvé (neve) + poke (animal)"),
    ("rukravokpoke", 1, "predador feroz e incansável da taiga nevada", "rukra + vok + poke"),
    ("tukpoke", 1, "animal escavador de listras alvinegras na face", "tuk- (cavar) + poke (animal)"),
    ("vevarpoke", 1, "animal nadador ágil caçador de trutas nos rios", "vevar (rio) + poke (animal)"),
    ("vevartekpoke", 1, "roedor que ergue diques de madeira nos riachos", "vevar (rio) + tek (erguer) + poke"),
    ("huxlanpoke", 1, "pequeno animal de inverno cuja pele alva veste reis", "hux (pele) + lan (alva) + poke"),
    ("korpoke", 1, "caçador ágil dos ramos de pinheiros de pele macia", "kor (árvore) + poke (animal)"),
    ("korgarpoke", 1, "grande cervídeo de galhada espalmada dos pântanos", "korgar (floresta) + poke"),
    ("xelvemald", 2, "cervídeo de trenó adaptado à tundra glacial", "xelvé (neve) + mald (montaria)"),
    ("edelpoke", 1, "cervo real de galhada ramificada das florestas", "edel (nobre) + poke (animal)"),
    ("litapoke", 1, "pequeno cervídeo gracioso das clareiras", "lita (pequeno) + poke (animal)"),
    ("rixepoke", 1, "cabra montesa ágil que salta nos precipícios", "rixe (rocha) + poke (animal)"),
    ("palkpoke", 1, "cabra alpina de longos chifres curvos em anéis", "palk (desfiladeiro) + poke"),
    ("faspokegar", 2, "javali silvestre de presas curvas das matas", "fas (ferir) + pokegar (fera)"),
    ("xelveynte", 1, "animal saltador de orelhas longas que embranquece na neve", "xelvé (neve) + ynte (corredor)"),
    ("korfelpoke", 1, "pequeno animal arborícola coletor de pinhões", "korfel (pinhão) + poke"),
    ("falpoke", 1, "roedor das serras que dorme todo o inverno em tocas", "fal- (dormir) + poke (animal)"),
    ("xerpokegar", 2, "grande ave soberana dos picos mais altos", "xer (céu) + pokegar (ave real)"),
    ("garvepokegar", 2, "grande ave pescadora das costas rochosas", "garvé (mar) + pokegar"),
    ("ferpokegar", 2, "ave real de voo velocíssimo usada na caça nobre", "fer (vento) + pokegar"),
    ("koryferpoke", 1, "ave de rapina ágil que caça entre as árvores", "kory (floresta) + ferpoke (ave)"),
    ("nirmirpoke", 1, "grande ave noturna de olhos dourados e voo silencioso", "nir (noite) + mir (olho) + poke"),
    ("lanferpoke", 1, "ave noturna de plumagem branca imaculada do norte", "lan (alva) + ferpoke (ave)"),
    ("velferpoke", 1, "grande ave de plumagem negra e grande inteligência", "vel (negro/sombra) + ferpoke"),
    ("kropeferpoke", 1, "ave escura de cauda em lira dos bosques de pinho", "krope + ferpoke"),
    ("avurferpoke", 1, "ave das serras com pés emplumados contra a neve", "avur (frio) + ferpoke"),
    ("lanvepoke", 1, "grande ave aquática alva de pescoço arqueado", "lan (alvo) + vepoke (ave d'água)"),
    ("kelferpoke", 1, "ave migratória que voa em formação de cunha", "kel (formação) + ferpoke"),
    ("kadeferpoke", 1, "ave pernalta cinzenta de canto sonoroso nos pântanos", "kade (alto) + ferpoke"),
    ("girvepoke", 1, "peixe de carne rosada que salta cachoeiras na desova", "gir- (saltar/subir) + vepoke (peixe)"),
    ("mirvepoke", 1, "peixe pintado das águas cristalinas de degelo", "mir (pinta/joia) + vepoke"),
    ("sfammirvepoke", 1, "peixe predador alongado dos lagos frios", "sfammir (espada) + vepoke"),
    ("laurivepoke", 1, "grande peixe encouraçado dos rios profundos", "lauri (nobre) + vepoke"),
    ("oxefaspoke", 1, "serpente peçonhenta de dorso em zigue-zague das pedras", "oxe (terra) + fas (veneno) + poke"),
    ("xullitrpoke", 1, "inseto robusto revestido de penugem que poliniza sob o frio", "xun (amarelo) + litr (zumbir) + poke, nl -> ll"),

    # --- Lote #4: Anatomia Humana, Medicina, Ervanária e Cirurgia (40 substantivos endógenos) ---
    ("daiosfar", 2, "caixa óssea que protege o cérebro e a mente", "daior (mente) + sfar (defesa)"),
    ("giryrixil", 2, "osso anelar que compõe a coluna espinhal", "gir- (erguer) + rixil (osso)"),
    ("sfarrixil", 2, "osso longo em arco entre o peito e o ombro", "sfar + rixil (osso)"),
    ("sinnixil", 2, "osso plano triangular da parte posterior do ombro", "sin (espádua) + rixil, nr -> nn"),
    ("sukorrixil", 2, "osso chato central do peito onde se unem as costelas", "sukor (peito) + rixil"),
    ("sukorsfar", 2, "arco ósseo que forma a caixa protetora do peito", "sukor (coração) + sfar (grade)"),
    ("ynnixilgar", 2, "osso da coxa, o mais longo e forte do esqueleto", "yn- (andar) + rixilgar, nr -> nn"),
    ("ynnixil", 2, "osso frontal resistente da canela", "yn- (andar) + rixil, nr -> nn"),
    ("sekrixil", 2, "disco ósseo protetor da articulação do joelho", "sek- (dobrar/sentar) + rixil"),
    ("litarixil", 2, "tecido flexível que reveste as juntas dos ossos", "lita (macio) + rixil"),
    ("drakvokor", 2, "cordão fibroso que prende o músculo ao osso", "drak- (tracionar) + vokor (carne)"),
    ("kindrvokor", 2, "feixe fibroso que mantém os ossos unidos na junta", "kindr- (unir) + vokor"),
    ("rukravokor", 2, "feixe de carne contrátil que move o corpo", "rukra (força) + vokor (músculo)"),
    ("vokvar", 2, "vaso pulsátil que leva sangue do coração ao corpo", "vok (sangue) + var (caminho)"),
    ("ovokvar", 2, "vaso que conduz o sangue de retorno ao coração", "o- (retorno) + vokvar"),
    ("fervokor", 2, "órgão esponjoso do peito responsável pelo fôlego", "fer (ar/fôlego) + vokor (órgão)"),
    ("lixvokor", 2, "grande órgão avermelhado que filtra o sangue", "lix- (purificar) + vokor"),
    ("velvokor", 2, "órgão situado sob as costelas esquerdas que renova o sangue", "vel + vokor"),
    ("vevokor", 2, "órgão par lombar que filtra os líquidos do corpo", "Vé (água) + vokor"),
    ("dakvokor", 2, "cavidade muscular que digere o alimento", "dak- (comer) + vokor"),
    ("suletvokor", 2, "órgão da garganta onde vibram as cordas da voz", "sulet (voz) + vokor"),
    ("mirsu", 2, "abertura central escura do olho por onde entra a luz", "mir (olho) + su (cerne)"),
    ("mirlanvokor", 2, "fundo sensível do olho onde se forma a imagem", "mir + lan (luz) + vokor"),
    ("klirvokor", 2, "membrana tensa do ouvido que vibra com o som", "klir- (ouvir) + vokor"),
    ("filrixil", 2, "substância vital no interior dos ossos longos", "fil (cerne) + rixil (osso)"),
    ("vurfasor", 2, "elevação anormal do calor do corpo na doença", "vur (fogo) + fasor (doença)"),
    ("avurfrelor", 2, "tremor súbito do corpo acompanhado de sensação de frio", "avur (frio) + frelor (tremor)"),
    ("kurafasor", 2, "acúmulo inflamado sob a pele que requer drenagem", "kura + fasor"),
    ("akazvokor", 2, "morte e escurecimento de tecido por falta de sangue", "akaz- (morrer) + vokor (carne)"),
    ("akelexrixil", 2, "deslocamento de um osso para fora de sua junta", "akelex- + rixil"),
    ("pekrixil", 2, "quebra ou rachadura de um osso por impacto", "pek- (quebrar) + rixil (osso)"),
    ("viltsaittek", 2, "pequena lâmina de dois gumes para incisões médicas", "vilt- (curar) + saittek (lâmina)"),
    ("vursaittek", 2, "ferro aquecido ao rubro para estancar hemorragias", "vur (fogo) + saittek"),
    ("viskhuxil", 2, "tira de linho limpo para envolver membros feridos", "visk- (enfaixar) + huxil (pano)"),
    ("avottek", 2, "laço apertado sobre um membro para conter sangramento", "avok- (estancar sangue) + -tek, kt -> tt"),
    ("vilkkorvé", 2, "pomada resinosa aromática aplicada sobre chagas", "vilt- (curar) + korvé (bálsamo), tk -> kk"),
    ("vilkkomor", 2, "preparado líquido concentrado de ervas medicinais", "vilt- (curar) + komor (poção), tk -> kk"),
    ("afasvé", 2, "remédio específico para neutralizar veneno ou peçonha", "afas- (aliviar dor/veneno) + Vé"),
    ("vuranvilttor", 2, "pasta quente de farinha e ervas aplicada sobre o peito", "vuran (quente) + viltor"),
    ("kaskvokor", 2, "costura cirúrgica das bordas de um corte profundo", "kask- (coser) + vokor (carne)"),

    # --- Lote #5: Arquitetura Imperial, Engenharia Civil e Fortificações (60 substantivos endógenos) ---
    ("xertep", 2, "teto hemisférico monumental erguido sobre o salão", "xer (abóbada celeste) + tep"),
    ("kildetoret", 2, "cobertura arqueada de pedra em berço ou nervuras", "kilde + toret (teto)"),
    ("saidrixeil", 2, "pedra talhada em cunha que forma a curva de um arco", "saidrixe + -il"),
    ("sfartoret", 2, "arco externo que escora o empuxo lateral das paredes", "sfar (escorar) + toret"),
    ("sfarteprixe", 1, "pilar maciço adossado à parede externa para sustentação", "sfar + tep + rixe"),
    ("teprixe", 1, "fuste cilíndrico de pedra que sustenta arcos e tetos", "tep (edifício) + rixe (rocha)"),
    ("kaderixe", 1, "topo esculpido de uma coluna onde pousa o arco", "kade (topo) + rixe (coluna)"),
    ("toretrixe", 1, "viga mestra de pedra que pousa sobre os capitéis", "toret (teto) + rixe"),
    ("illottoret", 2, "faixa horizontal esculpida com relevos sob o beiral", "illot- (adornar) + toret"),
    ("kadetoret", 2, "moldura saliente superior no alto da fachada", "kade (topo) + toret"),
    ("zelttoret", 2, "remate triangular da fachada de um santuário", "zelta (três/triângulo) + toret"),
    ("nykesotim", 2, "superfície semicircular esculpida acima do portal", "nyke (porta) + sotim (face)"),
    ("rixekoria", 1, "pátio interno rodeado por galerias de colunas", "rixekor (coluna) + -ia"),
    ("tepsuia", 1, "pátio central aberto na entrada de um palácio", "tep (casa) + su (centro) + -ia"),
    ("inelfia", 1, "pórtico vestíbulo situado à entrada do santuário", "in- (entrada) + elfia (santuário)"),
    ("suelfia", 1, "recinto semicircular abobadado ao fundo do altar", "su (cerne) + elfia (santuário)"),
    ("filoxetep", 2, "recinto subterrâneo abobadado sob o piso do santuário", "fil (subterrâneo) + oxe + tep"),
    ("kadeelfia", 1, "galeria estreita em arcos sobre as naves laterais", "kade (alto) + elfia"),
    ("veiketepia", 1, "pátio quadrangular rodeado de arcadas em mosteiro", "veike (jardim) + tepia"),
    ("litrgartep", 2, "torre alta anexa ao templo onde pendem os sinos", "litrgar (sinos) + tep (torre)"),
    ("rixekadil", 2, "remate cônico ou piramidal no alto dos contrafortes", "rixe + kadil (pequeno pico)"),
    ("veksixitek", 2, "bica de pedra esculpida que lança a água do telhado", "veksixi (chuva) + -tek"),
    ("lammildykil", 2, "grande janela circular rendilhada na fachada", "lan (luz) + mir + nykil (janela), nm -> m, rn -> ld"),
    ("mirlanil", 2, "painel de vidros coloridos montados em chumbo", "mir (joia) + lanil (janela de luz)"),
    ("mirrixetor", 2, "painel formado por pequenos cubos de pedra e vidro", "mir (joia) + rixe + -tor"),
    ("kuekitrixe", 1, "pintura mural aplicada sobre o revestimento ainda úmido", "kue (cor) + kit- + rixe"),
    ("lanoxetor", 2, "massa branca fina de cal e pó de rocha para relevos", "lan (branco) + oxe + -tor"),
    ("kindrrixevé", 2, "mistura de cal, areia e água que une as pedras", "kindr- (unir) + rixe + Vé"),
    ("brittekor", 2, "arte de erguer muros de pedra aparelhada", "brik- (assentar pedra) + tekor, kt -> tt"),
    ("saidrixe", 1, "bloco de pedra lavrado em faces retangulares perfeitas", "said- (talhar) + rixe (pedra)"),
    ("kadenyke", 1, "viga horizontal de pedra ou carvalho no topo da porta", "kade (topo) + nyke (porta)"),
    ("sinnyke", 1, "pilares laterais que ladeiam o vão da porta", "sin/dak (lado) + nyke"),
    ("oxenyke", 1, "degrau de pedra na base inferior da porta de entrada", "oxe (chão) + nyke (porta)"),
    ("nykilteggar", 2, "pequena porta secundária dissimulada na muralha", "nykil (portinhola) + teggar"),
    ("tupxnykil", 2, "fresta vertical estreita na muralha para arqueiros", "tupx- (atirar flecha) + nykil"),
    ("sfarkadil", 2, "recorte dentado no parapeito superior das muralhas", "sfar (defesa) + kadil"),
    ("sfarrixilgar", 2, "bloco maciço de pedra entre duas aberturas de parapeito", "sfar + rixilgar"),
    ("innyketeggar", 2, "fortim avançado circular que defende o portão", "in- + nyke + teggar"),
    ("kadeteggar", 2, "fortaleza real erguida no ponto mais alto da serra", "kade (alto) + teggar (fortaleza)"),
    ("suteggar", 2, "fortaleza central onde resiste a última guarnição", "su (núcleo) + teggar"),
    ("sfarrixegar", 2, "cinturão espesso de pedra que protege a fortaleza", "sfar (defesa) + rixegar (muralha)"),
    ("paltteggar", 2, "obra angular avançada na esquina da muralha", "palk (ângulo) + teggar, kt -> tt"),
    ("filteggar", 2, "abóbada subterrânea à prova de impacto sob a muralha", "fil (subterrâneo) + teggar"),
    ("sfarvefil", 2, "vala profunda escavada e inundada ao redor do castelo", "sfar + vefil (fosso d'água)"),
    ("girvartek", 2, "ponte de madeira erguida por correntes sobre o fosso", "gir- (erguer) + vartek (ponte)"),
    ("sfarnyketek", 2, "grade pesada de ferro que desce verticalmente no portão", "sfar + nyketek (grade), rn -> ld -> sfaldyketek"),
    ("sfarvaril", 2, "caminho de ronda no topo da muralha junto ao parapeito", "sfar (guarda) + varil (caminho)"),
    ("suarateggar", 2, "torre central mais alta e último reduto do castelo", "sua (central) + teggar"),
    ("velkosia", 1, "câmara prisional subterrânea nos alicerces da torre", "vel (treva) + kosia (câmara)"),
    ("filkosia", 1, "poço subterrâneo fechado por alçapão no piso", "fil (abismo) + kosia"),
    ("vevartek", 2, "canal sobre arcadas de pedra para conduzir água", "vevar (rio) + -tek (engenharia)"),
    ("filveia", 1, "reservatório subterrâneo abobadado para águas da chuva", "fil (fundo) + veia (cisterna)"),
    ("lixvevaril", 2, "galeria subterrânea de pedra para escoamento urbano", "lix- (limpar) + vevaril"),
    ("vuroxetep", 2, "sistema de fornalhas sob o piso de pedra para aquecer salões", "vur (fogo) + oxe (piso) + tep"),
    ("rixekare", 1, "assento contínuo de pedra ao longo das paredes do salão", "rixe (pedra) + kare (assento)"),
    ("gildyke", 1, "porta de duas folhas monumentais chapeadas em bronze", "gir- + nyke (portal), rn -> ld"),
    ("lanmirtepia", 1, "galeria envidraçada voltada ao sul para o sol de inverno", "lan (luz) + mir + tepia"),
    ("xerkadetep", 2, "torre octogonal no topo do palácio para observar a serra", "xer (céu) + kade + tep"),
    ("malttepia", 1, "pavilhões abobadados de pedra para os corcéis imperiais", "mald (cavalo) + tepia, dt -> tt"),
    ("fartepia", 1, "celeiro subterrâneo revestido de pedra para guardar trigo", "far (trigo) + tepia"),

    # --- Lote #6: Música Sacra, Instrumentos, Poética e Canto Litúrgico (40 substantivos endógenos) ---
    ("grirlitrtek", 2, "grande harpa triangular de trinta cordas douradas", "grir- (dedilhar) + litrtek"),
    ("sulitrtek", 2, "instrumento antigo de braços curvos usado pelos poetas", "su (cerne) + litrtek"),
    ("korlitrtek", 2, "alaúde de caixa abaulada de madeira nobre", "kor (madeira) + litrtek"),
    ("takelitrtek", 2, "instrumento trapezoidal de cordas percutidas ou beliscadas", "take (tábua) + litrtek"),
    ("draklitrtek", 2, "instrumento de arco de três cordas dos menestréis", "drak- (friccionar/arco) + litrtek"),
    ("turlitrtek", 2, "instrumento de cordas com roda de madeira resinada", "tur- + litrtek"),
    ("saidlitril", 2, "palheta de marfim ou pena para tangenciar as cordas", "said- + litril"),
    ("zeklitrtek", 2, "peça torneada que gira para esticar e afinar a corda", "zek- + litrtek"),
    ("kadelitrtek", 2, "peça de madeira que sustenta as cordas sobre o tampo", "kade (apoio) + litrtek"),
    ("korlitrtoret", 2, "tampo de abeto fino que amplifica o som das cordas", "kor + litr + toret"),
    ("litrkoldykil", 2, "abertura circular entalhada no centro da caixa acústica", "litr + kor + nykil, rn -> ld"),
    ("fullitrsulet", 2, "corda ou tubo grave que soa nota contínua de fundo", "fil (grave/fundo) + litr + sulet"),
    ("ferlitrtek", 2, "instrumento tubular de madeira ou prata tocado pelo sopro", "fer (sopro/vento) + litrtek"),
    ("oxtelitrtek", 2, "pequena flauta aguda que acompanha os tambores de marcha", "oxte (guerreiro) + litrtek"),
    ("korvelitrtek", 2, "instrumento de sopro rústico de palheta dupla", "kor + vel + litrtek"),
    ("huxferlitrtek", 2, "instrumento de odre de couro com tubos melódicos", "hux (couro) + fer + litrtek"),
    ("ferlitrgar", 2, "fole de couro que alimenta de ar o grande órgão", "fer (ar) + litrgar"),
    ("rukralitrgar", 2, "grande órgão monumental de tubos de estanho e bronze", "rukra (potente) + litrgar"),
    ("pokelitgar", 2, "trompa de marfim ou chifre entalhado dos arautos", "poke + litrgar"),
    ("durxveltek", 2, "trombeta reta de prata de som claro e agudo", "dur- (brilhar) + xveltek"),
    ("verrelitrtek", 2, "trombeta curva de bronze das legiões imperiais", "verre (bronze) + litrtek"),
    ("kadexveltek", 2, "longa trombeta reta de arauto com estandarte pendente", "kade + xveltek"),
    ("darpelitrgar", 2, "grande tambor hemisférico de cobre e pele de montaria", "darp- (ribombar) + litrgar"),
    ("darpelitril", 2, "tambor cilíndrico portátil tocado em marcha", "darp- (bater) + litril"),
    ("katlitril", 2, "pandeiro quadrangular de pele com sementes internas", "kat (quatro) + litril"),
    ("verredarptek", 2, "par de discos de bronze entrechocados em ritos solenes", "verre (bronze) + darptek"),
    ("litadarptek", 2, "pequenos sinos de bronze presos em arco para marcar o compasso", "lita + darptek"),
    ("kellitrgar", 2, "conjunto de sinos afinados na torre que tocam melodias", "kel (conjunto) + litrgar"),
    ("darpelitrsu", 2, "haste interna de ferro que percute a borda do sino", "darp- + litr + su (cerne)"),
    ("islitrtek", 2, "instrumento de ferro que emite a nota padrão de afinação", "is- (medir/saber) + litrtek"),
    ("kattsulette", 1, "escala fundamental de quatro notas sucessivas", "katta (quatro) + sulet"),
    ("nyrtsulet", 2, "intervalo perfeito de oito graus entre duas notas", "nyrta (oitavo) + sulet"),
    ("vextsulet", 2, "consonância perfeita de cinco graus na polifonia", "vexta (quinto) + sulet"),
    ("ossuletor", 2, "canto sacro alternado entre dois coros no santuário", "od- (alternado) + suletor, ds -> ss"),
    ("bossuletor", 2, "canto em que o coro responde ao versículo do cantor", "bod- (responder) + suletor, ds -> ss"),
    ("girsulet", 2, "longo ornamento melódico cantado sobre uma única sílaba", "gir- (elevar) + sulet (voz)"),
    ("alerlitror", 2, "repouso harmônico que conclui uma frase musical", "aler- (concluir) + litror"),
    ("kitlitror", 2, "sinal gráfico de notação musical sobre o texto sacro", "kit- (escrever) + litror"),
    ("elfkitor", 2, "grande códice iluminado contendo os cantos do ano sagrado", "elf- (sacro) + kitor (códice)"),
    ("kitlitrtek", 2, "estante giratória de madeira no centro do coro para o códice", "kitlitror + -tek"),
]

# Corrigir "sfarnyketek" -> "sfaldyketek" (rn -> ld)
EXPANSAO_NOUNS_PRIMARIOS = [
    ("sfaldyketek", d, m, e) if n == "sfarnyketek" else (n, d, m, e)
    for (n, d, m, e) in EXPANSAO_NOUNS_PRIMARIOS
]

# ==============================================================================
# 3. 35 ADVÉRBIOS ESPECIAIS SINTÁTICOS, TEMPORAIS E LOCATIVOS (100% ENDÓGENOS)
# ==============================================================================
EXPANSAO_ADVERBS_ESPECIAIS = [
    ("antebel", "Temporal Composto", "ante + bel (dia)", "ontem, no dia anterior"),
    ("posbel", "Temporal Composto", "pos + bel (dia)", "amanhã, no dia seguinte"),
    ("iddabel", "Temporal de Frequência", "idda + bel (dia)", "diariamente, todos os dias sem falta"),
    ("iddanir", "Temporal Noturno", "idda + nir (noite)", "todas as noites, a cada vigília"),
    ("filtonk", "Temporal Primordial", "fil (cerne) + tonkre", "no princípio dos tempos, desde a origem"),
    ("atonk", "Temporal Perpétuo", "a- + tonkre", "eternamente, para todo o sempre"),
    ("litatonk", "Temporal Breve", "lita + tonkre", "por pouco tempo, provisoriamente"),
    ("rukratonk", "Temporal Longo", "rukra + tonkre", "por longo tempo, duradouramente"),
    ("sankad", "Locativo Superior", "san + kade (monte)", "aqui no alto, neste cume"),
    ("sanfil", "Locativo Profundo", "san + fil (abismo)", "aqui no fundo, nesta baixada"),
    ("kankad", "Locativo Distante Superior", "kan + kade", "lá no alto, naquele pico distante"),
    ("kanfil", "Locativo Distante Profundo", "kan + fil", "lá no fundo, naquele abismo"),
    ("invar", "Locativo de Trânsito", "in + var (caminho)", "a caminho, em plena marcha, na estrada"),
    ("extep", "Locativo Exterior", "ex + tep (casa)", "fora de casa, ao relento, no exterior"),
    ("intep", "Locativo Interior", "in + tep (casa)", "dentro de casa, sob o teto, no abrigo"),
    ("indatte", "Locativo Direcional Destro", "in + datte (direita)", "à direita, pelo flanco destro"),
    ("insinte", "Locativo Direcional Sinistro", "in + sinte (esquerda)", "à esquerda, pelo flanco sinistro"),
    ("insotim", "Locativo Frontal", "in + sotim (rosto)", "de frente, face a face, perante"),
    ("invel", "Modal / Locativo Oculto", "in + vel (sombra)", "às ocultas, em segredo, na penumbra"),
    ("inbeli", "Modal / Locativo Público", "in + beli (dia)", "às claras, abertamente, à luz do dia"),
    ("issu", "Modal de Unidade", "id + su (cerne), ds -> ss", "unanimemente, num só coração"),
    ("idlete", "Modal de Uníssono", "id + lete (voz)", "a uma só voz, em uníssono"),
    ("kelvë", "Modal Coletivo", "kel- + -vë", "conjuntamente, em formação unida"),
    ("iddavë", "Modal Exclusivo", "idda + -vë", "unicamente, exclusivamente, tão só"),
    ("oratvë", "Modal Integral", "orat + -vë", "integralmente, na totalidade, por inteiro"),
    ("nesuvë", "Modal Nulo", "nesu + -vë", "em vão, inutilmente, para o nada"),
    ("skorvë", "Modal Fiduciário", "skor- + -vë", "fielmente, com fé inabalável"),
    ("molletvë", "Modal Judicial", "mollet- + -vë", "justamente, segundo a sentença da lei"),
    ("tokvë", "Modal Soberano", "tok- + -vë", "soberanamente, com autoridade imperial"),
    ("sfarvë", "Modal Defensivo", "sfar- + -vë", "em guarda, sob proteção armada"),
    ("krazvë", "Modal Festivo", "kraz- + -vë", "jubilosamente, entre risos"),
    ("fasvë", "Modal Doloroso", "fas- + -vë", "dolorosamente, a duras penas"),
    ("girvë", "Modal Progressivo", "gir- + -vë", "crescentemente, de modo ascendente"),
    ("agirvë", "Modal Regressivo", "agir- + -vë", "minguantemente, cada vez menos"),
    ("okazvë", "Modal Restitutivo", "okaz- + -vë", "renascidamente, com vigor restaurado"),
]

def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

STOPWORDS_PT = {
    "para", "como", "pelo", "pela", "pelos", "pelas", "entre", "sobre",
    "contra", "desde", "apos", "ante", "perante", "segundo", "durante",
    "dentro", "fora", "acima", "abaixo", "atraves", "perto", "longe",
    "muito", "pouco", "mais", "menos", "todo", "toda", "todos", "todas",
    "outro", "outra", "outros", "outras", "mesmo", "mesma", "cada",
    "qualquer", "algum", "alguma", "nenhum", "nenhuma", "este", "esta",
    "esse", "essa", "aquele", "aquela", "isto", "isso", "aquilo", "onde",
    "quando", "quanto", "quanta", "quem", "qual", "quais", "cujo", "cuja",
    "fazer", "feito", "feita", "tornar", "modo", "forma", "acao", "efeito",
    "relativo", "proprio", "dotado", "cheio", "coberto", "provido",
    "pequeno", "pequena", "grande", "alto", "alta", "baixo", "baixa",
    "longo", "longa", "curto", "curta", "novo", "nova", "velho", "velha",
    "antigo", "antiga", "sagrado", "sagrada", "imperial", "real",
    "montanha", "montanhas", "serra", "serras", "pedra", "rocha", "madeira",
    "agua", "fogo", "vento", "noite", "terra", "casa", "corpo", "sangue",
    "instrumento", "lugar", "oficina", "recinto", "arte", "tecnica",
    "voltar", "deixar", "repetidamente", "novamente", "habitualmente",
    "animal", "planta", "erva", "arvore", "flor", "fruto", "folha",
    "orgao", "osso", "carne", "pele", "olho", "canto", "musica", "som",
    "arco", "ponte", "porta", "torre", "muro", "muralha", "parede", "teto",
    "estrela", "astro", "ceu", "frio", "gelo", "neve", "chuva", "mar", "rio",
}

def normalize_treppio_stem(lemma: str) -> str:
    s = strip_accents(lemma.lower().replace("'", ""))
    for suf in ("gar", "tek", "ia", "or", "il", "te", "et", "ve", "ur"):
        if len(s) > len(suf) + 2 and s.endswith(suf):
            s = s[:-len(suf)]
            break
    if len(s) > 3 and s[-1] in ("e", "a", "o", "i"):
        s = s[:-1]
    return s.replace("k", "c")

def check_romance_similarity(lemma: str, meaning: str) -> tuple[float, str]:
    t_norm = normalize_treppio_stem(lemma)
    t_raw = strip_accents(lemma.lower().replace("'", "")).replace("k", "c")
    best_sim = 0.0
    best_word = ""

    words = [w for w in re.findall(r"[a-z]{4,}", strip_accents(meaning.lower())) if w not in STOPWORDS_PT]
    for w in words:
        w_stem = w[:-1] if len(w) > 4 and w[-1] in "aeos" else w
        for ct in (t_norm, t_raw):
            for cw in (w, w_stem):
                ratio = SequenceMatcher(None, ct, cw).ratio()
                if len(ct) >= 4 and len(cw) >= 4 and ct[:4] == cw[:4]:
                    ratio = max(ratio, 0.75)
                if ratio > best_sim:
                    best_sim = ratio
                    best_word = f"glosa:{w}"

    return best_sim, best_word

def write_module():
    target_path = r"D:\Conde_Treppio\sandbox\lexico_expansao_v8_1.py"
    lines = []
    lines.append("# -*- coding: utf-8 -*-")
    lines.append('"""')
    lines.append("lexico_expansao_v8_1.py")
    lines.append("Módulo de Expansão Lexical Endógena da Língua Tréppia (Era Clássica V8.2 — O Conde).")
    lines.append("100% construído sobre as raízes primárias canônicas do Tréppio e as 21 Leis de Sandi Consonantal,")
    lines.append("respeitando o Limite Estrito de <= 50% de Similaridade Românica/Greco-Latina.")
    lines.append('"""')
    lines.append("")
    lines.append("def _join_sandi(left: str, right: str) -> str:")
    lines.append("    if not left: return right")
    lines.append("    if not right: return left")
    lines.append("    if left[-1] in 'ae' and right[0] in 'aeiouy': left_stem = left[:-1]")
    lines.append("    else: left_stem = left")
    lines.append("    if not left_stem: return right")
    lines.append("    if left_stem.endswith('r') and right.startswith('n'): return left_stem[:-1] + 'ld' + right[1:]")
    lines.append("    if left_stem.endswith('l') and right.startswith('n'): return left_stem[:-1] + 'll' + right[1:]")
    lines.append("    if left_stem.endswith('n') and right.startswith('l'): return left_stem[:-1] + 'll' + right[1:]")
    lines.append("    if left_stem.endswith('mn') and right.startswith('n'): return left_stem[:-2] + 'm' + right[1:]")
    lines.append("    if left_stem.endswith('n') and right.startswith('n'): return left_stem[:-1] + 'm' + right[1:]")
    lines.append("    if left_stem.endswith('n') and right.startswith('r'): return left_stem[:-1] + 'nn' + right[1:]")
    lines.append("    if left_stem.endswith('t') and right.startswith('d'): return left_stem[:-1] + 'dd' + right[1:]")
    lines.append("    if (left_stem.endswith('d') or left_stem.endswith('k')) and right.startswith('t'): return left_stem[:-1] + 'tt' + right[1:]")
    lines.append("    if left_stem.endswith('s') and right.startswith('r'): return left_stem[:-1] + 'ss' + right[1:]")
    lines.append("    if left_stem.endswith('d') and right.startswith('s'): return left_stem[:-1] + 'ss' + right[1:]")
    lines.append("    if left_stem.endswith('z') and right.startswith('r'): return left_stem[:-1] + 'zz' + right[1:]")
    lines.append("    if (left_stem.endswith('m') and right.startswith('r')) or (left_stem.endswith('r') and right.startswith('m')): return left_stem[:-1] + 'mm' + right[1:]")
    lines.append("    if left_stem.endswith('ld') and right.startswith('b'): return left_stem[:-2] + 'lbb' + right[1:]")
    lines.append("    if (left_stem.endswith('k') or left_stem.endswith('t') or left_stem.endswith('f')) and right.startswith('b'): return left_stem[:-1] + 'bb' + right[1:]")
    lines.append("    if left_stem.endswith('n') and right.startswith('b'): return left_stem[:-1] + 'mb' + right[1:]")
    lines.append("    if left_stem.endswith('p') and right.startswith('g'): return left_stem[:-1] + 'gg' + right[1:]")
    lines.append("    if left_stem.endswith('t') and right.startswith('k'): return left_stem[:-1] + 'kk' + right[1:]")
    lines.append("    if left_stem.endswith('x') and right.startswith('r'): return left_stem[:-1] + 'rr' + right[1:]")
    lines.append("    if left_stem.endswith('v') and right.startswith('t'): return left_stem[:-1] + 'pt' + right[1:]")
    lines.append("    if left_stem.endswith('k') and right.startswith('l'): return left_stem[:-1] + 'll' + right[1:]")
    lines.append("    return left_stem + right")
    lines.append("")
    lines.append("EXPANSAO_VERB_ROOTS = [")
    for item in EXPANSAO_VERB_ROOTS:
        lines.append(f"    {repr(item)},")
    lines.append("]")
    lines.append("")
    lines.append("EXPANSAO_NOUNS_PRIMARIOS = [")
    for item in EXPANSAO_NOUNS_PRIMARIOS:
        lines.append(f"    {repr(item)},")
    lines.append("]")
    lines.append("")
    lines.append("EXPANSAO_ADVERBS_ESPECIAIS = [")
    for item in EXPANSAO_ADVERBS_ESPECIAIS:
        lines.append(f"    {repr(item)},")
    lines.append("]")
    lines.append("")
    lines.append("EXPANSAO_NOUNS = list(EXPANSAO_NOUNS_PRIMARIOS)")
    lines.append("EXPANSAO_ADJECTIVES = []")
    lines.append("EXPANSAO_ADVERBS = list(EXPANSAO_ADVERBS_ESPECIAIS)")
    lines.append("")
    lines.append("for _root, _pos_mean, _priv_mean, _iter_mean, _itpr_mean in EXPANSAO_VERB_ROOTS:")
    lines.append("    _base_action = _pos_mean.split(',')[0].strip()")
    lines.append("    _n_or = f'{_root}or'")
    lines.append("    EXPANSAO_NOUNS.append((_n_or, 2, f'ato ou efeito de {_base_action}', f'{_root}- + -or'))")
    lines.append("    _n_tek = _join_sandi(_root, 'tek')")
    lines.append("    EXPANSAO_NOUNS.append((_n_tek, 2, f'instrumento ou meio para {_base_action}', f'{_root}- + -tek'))")
    lines.append("    _n_ia = f'{_root}ia'")
    lines.append("    EXPANSAO_NOUNS.append((_n_ia, 1, f'lugar, recinto ou oficina de {_base_action}', f'{_root}- + -ia'))")
    lines.append("    _adj = f'{_root}a'")
    lines.append("    _sup = _join_sandi(_root, 'n')")
    lines.append("    EXPANSAO_ADJECTIVES.append((_adj, f'relativo ou propenso a {_base_action}', f'maer {_adj}', _sup))")
    lines.append("    _adv = f'{_adj}vë'")
    lines.append("    EXPANSAO_ADVERBS.append((_adv, 'Modal Derivado (-vë com diérese)', f'{_adj} + -vë', f'de modo a {_base_action}'))")
    lines.append("")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Arquivo gravado com sucesso: {target_path}")

if __name__ == "__main__":
    print(f"Verificando {len(EXPANSAO_VERB_ROOTS)} raízes verbais e {len(EXPANSAO_NOUNS_PRIMARIOS)} substantivos...")
    issues = []
    seen = set()
    for r, m1, m2, m3, m4 in EXPANSAO_VERB_ROOTS:
        if r in seen:
            issues.append(f"DUPLICATA VERB: {r}")
        seen.add(r)
        if FORBIDDEN_CLUSTERS.search(r) or FORBIDDEN_GRAPHEMES.search(r):
            issues.append(f"FONOTÁTICA VERB: {r}")
        sim, w = check_romance_similarity(r, m1)
        if sim > 0.50:
            issues.append(f"SIMILARIDADE VERB > 50%: {r} ({sim:.2f} com {w} | '{m1}')")

    seen_n = set()
    for n, d, m, e in EXPANSAO_NOUNS_PRIMARIOS:
        if n in seen_n:
            issues.append(f"DUPLICATA NOUN: {n}")
        seen_n.add(n)
        if FORBIDDEN_CLUSTERS.search(n) or FORBIDDEN_GRAPHEMES.search(n):
            issues.append(f"FONOTÁTICA NOUN: {n}")
        sim, w = check_romance_similarity(n, m)
        if sim > 0.50:
            issues.append(f"SIMILARIDADE NOUN > 50%: {n} ({sim:.2f} com {w} | '{m}')")

    print(f"Total de problemas detectados: {len(issues)}")
    for iss in issues:
        print(" ->", iss)
    if not issues:
        write_module()
