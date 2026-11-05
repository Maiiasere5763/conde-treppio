# -*- coding: utf-8 -*-
"""
injetar_evolucao_1500_anos.py
Injeta o vocabulário funcional e prático de 1.500 anos de evolução naturalista
(universo de Ecos de Uma Vida Perdida) no gerador integral do Tréppio.
"""

import os
import re

GERADOR_PY = r"D:\Conde_Treppio\sandbox\gerador_dicionario_integral_sandbox.py"

with open(GERADOR_PY, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Novos Substantivos de Ecos
new_nouns_code = '''
    # ==============================================================================
    # VOCABULÁRIO FUNCIONAL COTIDIANO (1.500 ANOS DE EVOLUÇÃO - ECOS DE UMA VIDA PERDIDA)
    # ==============================================================================
    # --- Saudações, Casa e Abrigo de Ecos ---
    ("alen", 2, "saudação matinal, bom dia, paz no caminho", "al- (luz) + -en"),
    ("vesen", 2, "boa noite, repouso da lareira, descanso", "ves- (noite) + -en"),
    ("doban", 2, "por favor, com licença, perdão coloquial", "redução coloquial de doobbam"),
    ("hallen", 2, "gratidão, agradecimento, obrigado", "hal- (sagrado/luz) + -en"),
    ("kastar", 2, "castelo de pedra, fortaleza, torre fortificada", "raiz de Ecos kastar"),
    ("husa", 1, "casa, morada, cabana, abrigo de madeira", "germano-trepiano hus- + -a"),
    ("stuba", 1, "aposento aquecido, quarto com lareira, estalagem", "trepiano clássico de Ecos stub- + -a"),
    ("kamin", 2, "lareira, fogão a lenha, fogo doméstico acolhedor", "kamin- + flexão 2"),
    ("brandor", 2, "brasa incandescente, carvão em brasa, lenha ardente", "brand- + -or"),
    ("tavla", 1, "mesa de refeição, tábua de madeira, balcão", "tavl- + -a"),
    ("stola", 1, "cadeira, banco de madeira, assento rústico", "stol- + -a"),
    ("porta", 1, "porta, portal de entrada, postigo de carvalho", "port- + -a"),
    ("fenstron", 2, "janela de postigo, fresta de luz, claraboia", "fenstr- + -on"),
    ("klavi", 2, "chave de ferro, tranca, ferrolho", "klav- + -i"),
    ("lektar", 2, "leito macio, cama de penas ou palha de dormir", "lekt- + -ar"),
    ("vellon", 2, "manta de lã espessa, cobertor pesado contra o gelo", "vell- + -on"),
    ("kandela", 1, "vela de sebo, lamparina de óleo, candeia", "kandel- + -a"),
    ("lampa", 1, "lanterna de metal, tocha de óleo", "lamp- + -a"),
    # --- Alimentação e Taberna de Ecos ---
    ("panna", 1, "pão rústico, broa de centeio ou trigo", "pann- + -a"),
    ("broda", 1, "caldo quente, sopa de legumes e carne", "brod- + -a"),
    ("karna", 1, "carne assada na brasa, provisão de caça", "karn- + -a"),
    ("piskon", 2, "peixe de rio gélido, truta das montanhas", "pisk- + -on"),
    ("kaso", 2, "queijo curado de cabra, laticínio das serras", "kas- + -o"),
    ("vinor", 2, "vinho tinto aquecido, vinho com especiarias", "vin- + -or"),
    ("alor", 2, "cerveja escura artesanal, hidromel espesso", "al- + -or"),
    ("akva", 1, "água fresca de degelo, água potável pura", "akv- + -a"),
    ("koppon", 2, "caneca de barro, copo de estanho, taça de taberna", "kopp- + -on"),
    ("diskor", 2, "prato de madeira torneada, tigela funda", "disk- + -or"),
    ("kulta", 1, "faca afiada de mesa, punhal de caça", "kult- + -a"),
    ("spanna", 1, "colher de pau, concha de sopa", "spann- + -a"),
    ("salor", 2, "sal de rocha, sal para conservar carnes", "sal- + -or"),
    ("fammor", 2, "fome voraz, apetite de viajante", "famm- + -or"),
    ("siddor", 2, "sede ardente, garganta seca pelo vento", "sidd- + -or"),
    ("sena", 1, "ceia noturna, jantar em torno da lareira", "sen- + -a"),
    # --- Clima, Natureza e Viagem de Ecos ---
    ("nivis", 2, "neve fresca acumulada, manto branco de inverno", "niv- + -is"),
    ("hielor", 2, "gelo espesso, geada cortante, carámbano", "hiel- + -or"),
    ("nebla", 1, "nevoeiro espesso, bruma densa que esconde caminhos", "nebl- + -a"),
    ("pinet", 2, "pinheiro silvestre, conífera das encostas", "pinet- + flexão 2"),
    ("silva", 1, "bosque cerrado, floresta de pinheiros", "silv- + -a"),
    ("strada", 1, "estrada batida, rota de caravana, caminho de pedra", "strad- + -a"),
    ("ponte", 1, "ponte de pedra sobre o abismo ou rio", "pont- + -e"),
    ("vestig", 2, "pegada na neve fresca, rastro de animal ou viajante", "vestig- + flexão 2"),
    ("aurora", 1, "aurora boreal, claridade suave que precede o dia", "auror- + -a"),
    ("krepus", 2, "crepúsculo avermelhado, hora do anoitecer", "krepus- + flexão 2"),
    ("stella", 1, "estrela guia, ponto brilhante no céu gelado", "stell- + -a"),
    ("mons", 2, "montanha escarpada, pico nevado inacessível", "mont- / mons-"),
    ("valis", 2, "vale protegido dos ventos, desfiladeiro habitado", "val- + -is"),
    # --- Companheirismo, Vida e Emoção em Ecos ---
    ("kanis", 2, "cão leal, o grande cachorro loiro de aura brilhante", "kan- + -is"),
    ("amiko", 2, "amigo fiel, companheiro leal de travessia", "amik- + -o"),
    ("hospit", 2, "hóspede acolhido, viajante abrigado do frio", "hospit- + flexão 2"),
    ("familia", 1, "família reunida, clã doméstico da lareira", "famili- + -a"),
    ("matra", 1, "mãe acolhedora, guardiã do fogo doméstico", "matr- + -a"),
    ("patro", 2, "pai protetor, chefe da morada", "patr- + -o"),
    ("infant", 2, "criança pequena, filho amado", "infant- + flexão 2"),
    ("equo", 2, "cavalo de carga e sela, montaria resistente", "equ- + -o"),
    ("kordis", 2, "coração caloroso, sede da coragem e do afeto", "kord- + -is"),
    ("alma", 1, "alma imortal, sopro de vida e dignidade", "alm- + -a"),
    ("nostal", 2, "nostalgia profunda, saudade dos ecos do passado", "nost- + -al"),
    ("dolor", 2, "dor suportada com bravura, sofrimento superado", "dol- + -or"),
    ("sanat", 2, "cura revigorante, alívio do corpo e da alma", "san- + -at"),
    # --- Ferramentas, Comércio e Armas de Ecos ---
    ("preti", 2, "preço de compra, valor em moedas", "pret- + -i"),
    ("argen", 2, "moeda de prata cunhada, prata de comércio", "arg- + -en"),
    ("kupro", 2, "moeda de cobre comum, trocado de taberna", "kupr- + -o"),
    ("merka", 1, "mercadoria valiosa, fardo de mercador", "merk- + -a"),
    ("merkator", 2, "mercador de caravana, negociante itinerante", "merk- + -ator"),
    ("taberna", 1, "estalagem de beira de estrada, taberna de montanha", "tabern- + -a"),
    ("ferrar", 2, "ferreiro da forja, artesão do ferro e do aço", "ferr- + -ar"),
    ("martel", 2, "martelo de ferreiro, ferramenta de artesão", "mart- + -el"),
    ("spada", 1, "espada de aço temperado, lâmina de defesa", "spad- + -a"),
    ("skuto", 2, "escudo de madeira com reforço de metal", "skut- + -o"),
'''

# 2. Novos Adjetivos de Ecos
new_adjectives_code = '''
    # --- Adjetivos de Ecos e da Vida Diária ---
    ("kaldan", "aquecido, acolhedor, quente pelo fogo", "maer kaldan", "kaldani"),
    ("frigan", "gélido, gelado, congelado pelo vento", "maer frigan", "frigani"),
    ("dulce", "doce, suave, terno ao paladar ou ao coração", "maer dulce", "dulcen"),
    ("amara", "amargo, áspero, marcado pela dor", "maer amara", "amaran"),
    ("bono", "bom, benéfico, nobre de caráter", "maer bono", "bonon"),
    ("malo", "mau, nocivo, traiçoeiro", "maer malo", "malon"),
    ("grando", "grande, vasto, imponente na paisagem", "maer grando", "grandon"),
    ("pikko", "pequeno, miúdo, singelo", "maer pikko", "pikkon"),
    ("fessan", "exausto, fatigado após longa jornada na neve", "maer fessan", "fessani"),
    ("refeik", "restaurado, revigorado pela ceia e descanso", "maer refeik", "refeiki"),
    ("karo", "precioso, caro, de alto valor", "maer karo", "karon"),
    ("barat", "barato, acessível, de custo justo", "maer barat", "barati"),
    ("seku", "seguro, protegido de intempéries e perigos", "maer seku", "sekun"),
    ("perik", "perigoso, traiçoeiro nas encostas íngremes", "maer perik", "periki"),
'''

# 3. Novos Advérbios de Ecos
new_adverbs_code = '''
    # --- Advérbios e Partículas Coloquiais de Ecos ---
    ("yo", "Afirmação Coloquial", "partícula afirmativa viva", "sim, certamente, sem dúvida"),
    ("nei", "Negação Coloquial Reforçada", "ne + partícula enfática -i", "não, de jeito nenhum"),
    ("kole", "Marcador de Atenção / Demonstrativo", "raiz kol- + vocálico", "olhe!, eis!, veja!"),
    ("sani", "Locativo Coloquial de Proximidade", "deítico San + locativo -i", "aqui, para cá"),
    ("tani", "Locativo Coloquial de Distância", "deítico Tan + locativo -i", "ali, acolá, para lá"),
    ("aure", "Temporal Imediato", "aur- (instante da luz) + -e", "agora, neste instante, já"),
    ("maure", "Temporal Posterior", "m- (seguinte) + aure", "amanhã, no dia seguinte"),
    ("kaure", "Temporal Anterior", "k- (pretérito) + aure", "ontem, no dia passado"),
    ("cito", "Modal de Velocidade", "raiz cit- + modal -o", "depressa, rapidamente, com agilidade"),
    ("lente", "Modal de Lentidão", "raiz lent- + modal -e", "lentamente, passo a passo com cautela"),
'''

# 4. Novos Verbos de Ação Cotidiana
new_verbs_code = '''
    # --- Verbos de Ação Cotidiana de Ecos (Matriz Quadripartida Completa) ---
    ("mand", "comer, alimentar-se", "jejuar, ficar sem comer", "voltar a comer, merendar habitualmente", "quebrar o jejum, voltar a alimentar-se"),
    ("bib", "beber, saciar a sede", "abster-se de beber, passar sede", "voltar a beber, bebericar socialmente", "cessar a sede extrema, recobrar sobriedade"),
    ("dorm", "dormir, repousar no leito", "vigiar à noite, sofrer de insônia", "voltar a dormir, tirar um cochilo", "despertar da insônia prolongada"),
    ("vig", "acordar, despertar para o dia", "adormecer pesadamente, cair no sono", "despertar novamente, reassumir vigilância", "cessar o despertar súbito"),
    ("ambul", "caminhar pela trilha, marchar na neve", "paralisar o passo, deter-se na geada", "voltar a caminhar, retomar a jornada", "interromper a paralisia, recomeçar a andar"),
    ("kurr", "correr, apressar o passo na tempestade", "desacelerar o passo, parar a corrida", "correr de novo, disparar em marcha rápida", "cessar a correria repentina"),
    ("sed", "sentar-se à mesa ou junto ao fogo", "levantar-se do assento, ficar em pé", "sentar-se de novo, reacomodar-se no banco", "desistir de levantar, permanecer sentado"),
    ("fok", "acender o fogo, avivar a lareira", "apagar o fogo, extinguir as chamas", "reacender a lareira, soprar as brasas", "evitar que as brasas se apaguem"),
    ("kok", "cozinhar na panela, assar na brasa", "deixar a carne crua, não cozinhar", "reaquecer o caldo, cozinhar de novo", "tirar a comida do fogo antes de queimar"),
    ("klaud", "fechar a porta ou janela contra o vento", "abrir, escancarar a porta para o sol", "fechar de novo, trancar com ferrolho", "destrancar a porta, reabrir a morada"),
    ("aud", "escutar com atenção, ouvir os passos", "ensurdecer, fazer-se desentendido", "ouvir novamente, reescutar os ecos", "voltar a ouvir após o silêncio"),
    ("kompr", "comprar mantimentos, adquirir na feira", "recusar a compra, não adquirir", "comprar de novo, reabastecer a despensa", "desfazer a compra, devolver a mercadoria"),
    ("vend", "vender mercadorias, comercializar bens", "reter a posse, recusar a venda", "revender com lucro, negociar novamente", "recomprar aquilo que foi vendido"),
    ("pag", "pagar a despesa, quitar moedas de prata", "ficar em débito, postergar o pagamento", "repagar, saldar dívidas antigas", "receber de volta o pagamento feito"),
    ("resp", "descansar na lareira, respirar aliviado", "fatigar-se na subida, afobar-se", "descansar mais uma vez, repousar na jornada", "recuperar o fôlego após cansaço extremo"),
    ("salut", "saudar fraternalmente, desejar bom dia", "passar em silêncio, ignorar o viajante", "retribuir a saudação, responder ao cumprimento", "quebrar a frieza inicial com um abraço"),
'''

# Injetar Substantivos antes de fechar NOUNS
if '("alen", 2,' not in code:
    code = code.replace("NOUNS = [", "NOUNS = [" + new_nouns_code, 1)

# Injetar Adjetivos antes de fechar ADJECTIVES
if '("kaldan",' not in code:
    code = code.replace("ADJECTIVES = [", "ADJECTIVES = [" + new_adjectives_code, 1)

# Injetar Advérbios antes de fechar ADVERBS
if '("yo",' not in code:
    code = code.replace("ADVERBS = [", "ADVERBS = [" + new_adverbs_code, 1)

# Injetar Verbos antes de fechar VERB_ROOTS
if '("mand",' not in code:
    code = code.replace("VERB_ROOTS = [", "VERB_ROOTS = [" + new_verbs_code, 1)

with open(GERADOR_PY, "w", encoding="utf-8") as f:
    f.write(code)

print("Injeção do vocabulário de 1.500 anos (Ecos) concluída com sucesso no gerador!")

