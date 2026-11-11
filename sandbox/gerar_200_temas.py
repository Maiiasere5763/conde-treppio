# -*- coding: utf-8 -*-
"""
gerar_200_temas.py
Expande a fila de campos semânticos em D:\Conde_Treppio\sandbox\fila_temas_expansao_horaria.json
de 24 para 200 temas enciclopédicos distintos (organizados nos 10 Livros Civilizatórios de Ecos),
preservando integralmente ultimo_indice_executado e historico_execucoes.
"""
import json
import os

FILA_PATH = r"D:\Conde_Treppio\sandbox\fila_temas_expansao_horaria.json"

TEMAS_200 = [
    # --- LIVRO I: CIÊNCIAS NATURAIS, COSMOLOGIA, GEOGRAFIA E ECOLOGIA DE ECOS (1–20) ---
    ("Astronomia, Cosmologia e Calendário Sideral", "Constelações de Ecos, fases lunares, solstícios, equinócios, eclipses, cometas, órbitas celestes e medição do tempo astral."),
    ("Botânica, Herbologia e Flora dos Ermos", "Árvores coníferas e caducifólias, ervas medicinais, raízes curativas, fungos, líquens da tundra, resinas, flores alpinas e venenos vegetais."),
    ("Zoologia, Fauna Selvagem e Bestiário do Norte", "Predadores da taiga, aves de rapina, cervídeos, animais de toca, peixes de rios gelados, insetos, rastros, pelagens e hábitos animais."),
    ("Anatomia Humana, Medicina e Arte da Cura", "Órgãos internos, ossos, articulações, sentidos, febres, cataplasmas, suturas, cauterização, convalescença e longevidade."),
    ("Arquitetura Sacra, Cantaria Monumental e Fortificações", "Abóbadas, colunas, capitéis, criptas, contrafortes, pontes de arco, aquedutos, portões encouraçados, torres de vigia e salões reais."),
    ("Música, Organologia e Acústica Coral", "Instrumentos de corda, sopro e percussão, modos musicais, intervalos, ressonância, polifonia, cadências e cânticos de gesta."),
    ("Tecelagem, Tinturaria, Bordado e Indumentária Nobre", "Fibras têxteis, pigmentos minerais e vegetais, teares, brocados, peles nobres, insígnias, bainhas, bordados heráldicos e adereços."),
    ("Comércio, Moedas, Pesos, Medidas e Mercados", "Balanças de precisão, cunhagem de moedas, câmbio, caravanas mercantes, impostos de passagem, armazéns, contratos e fianças."),
    ("Agricultura de Vale, Irrigação, Pomares e Colheita", "Arados, sulcos, adubação, enxertia, poda, canais de rega, celeiros, debulha, feno, silos e conservação de sementes."),
    ("Direito Imperial, Magistratura, Chancelaria e Diplomacia", "Editos, selos imperiais, embaixadas, tratados de aliança, tributos, apelações, testemunhos, penas, banimento e anistia."),
    ("Geologia, Mineração Profunda, Gemologia e Cristais", "Veios metálicos, galerias subterrâneas, escoramento de minas, pedras preciosas, lapidação, mármores, basalto, enxofre e carvão."),
    ("Vidraria, Cerâmica, Alquimia e Destilação", "Fornos de alta temperatura, sopro de vidro, esmaltes, porcelana, alambiques, elixires, ácidos, sais, cadinhos e transmutação."),
    ("Marinha, Construção Naval e Meteorologia Oceânica", "Quilhas, mastros, cordame, lemes, marés, correntes marinhas, trombas d'água, recifes, faróis, naufrágios e portos de abrigo."),
    ("Genealogia, Parentesco, Casamento e Ritos de Passagem", "Graus de consanguinidade, dotes, alianças matrimoniais, adoção, maioridade, bênçãos de berço, heranças e linhagens dinásticas."),
    ("Retórica, Filologia, Caligrafia e Iluminura de Códices", "Pergaminhos, tintas de galha, penas de cálamo, encadernação, glosas, tropos poéticos, métrica, silogismos e debate filosófico."),
    ("Cavalaria, Falcoaria, Cinofilia e Caça Real", "Adestramento de corcéis, selaria, esporas, falcões de caça, matilhas de rastreamento, armadilhas, trompas de caça e coutadas."),
    ("Gastronomia de Corte, Panificação Fina e Vinicultura", "Banquetes reais, especiarias, assados, pastelaria, queijos maturados, vindima, prensas de vinho, tonéis de carvalho e hidromel."),
    ("Psicologia, Sonhos, Memória, Intuição e Presságios", "Visões oníricas, melancolia, êxtase, remorso, pressentimento, discernimento, temperamentos da alma e meditação."),
    ("Tática Militar de Campanha, Engenharia de Cerco e Logística", "Catapultas, aríetes, torres móveis, minas de sapa, comboios de suprimentos, sinais de fogo, formações em cunha e fortificações de campanha."),
    ("Hidráulica, Moinhos, Relojoaria e Mecanismos Antigos", "Rodas d'água, engrenagens, polias, alavancas, clepsidras, relógios de sol, comportas, represas e autômatos de forja."),

    # --- LIVRO II: FENÔMENOS DA TERRA, CLIMA, ÁGUAS E ECOSSISTEMAS (21–40) ---
    ("Fenômenos Ópticos, Cores, Luz, Sombra e Pintura Mural", "Matizes cromáticos, refração, espelhos, afrescos, mosaicos, claro-escuro, auroras polares, miragens e pigmentação."),
    ("Geografia Política, Fronteiras, Toponímia e Cartografia", "Mapas em pergaminho, bússolas, marcos miliários, províncias, enclaves, desfiladeiros estratégicos, rotas reais e postos de muda."),
    ("Ética, Virtudes Cardeais, Honra e Filosofia Moral", "Magnanimidade, temperança, justiça distributiva, lealdade feudal, hospitalidade sagrada, piedade filial e sabedoria prática."),
    ("Escatologia, Cosmogonia Profunda e Mistérios do Halylitror", "Salões Atemporais, Chama Imperecível, acordes primordiais, destino dos povos, renovação do mundo e coros angélicos."),
    ("Glaciologia, Campos de Neve, Avalanches e Criosfera", "Banquisas, seracs, fendas glaciais, nevascas uivantes, geada cristalina, pontes de gelo e degelo de altitude."),
    ("Espeleologia, Cavernas Abissais e Rios Subterrâneos", "Estalactites, estalagmites, galerias kársticas, lagos cegos, ecos de caverna, vapores termais e ressonância subterrânea."),
    ("Vulcanismo, Fontes Termais e Geotermia Primordial", "Crateras fumegantes, fumarolas, gêiseres, obsidiana vítrea, cinza vulcânica, enxofre ardente e tremores de terra."),
    ("Limnologia, Lagos Alpinos, Pântanos e Turfeiras", "Águas paradas, juncais, nenúfares, turfa escura, gás dos pântanos, lodo fértil e espelhos d'água glaciais."),
    ("Potamologia, Cachoeiras, Corredeiras e Estuários", "Meandros, cheias sazonais, redemoinhos, bancos de cascalho, deltas, confluências, vaus pedregosos e represamentos naturais."),
    ("Oceanografia Costeira, Falésias, Fiordes e Marés", "Canais glaciais profundos, arrebentação, espuma marinha, cavernas de maré, ressacas, brisas salinas e praias de seixos."),
    ("Anemologia, Rosa dos Ventos e Tempestades Continentais", "Ventos boreais, brisas de vale, ciclones, rajadas descendentes, redemoinhos de poeira e calmarias carregadas."),
    ("Nefologia, Nuvens, Nevoeiros e Precipitações", "Cirros altos, cúmulos de trovoada, cerração matinal, garoa fria, saraiva, orvalho congelado e arco-íris duplo."),
    ("Silvicultura Antiga, Bosques Sagrados e Árvores Seculares", "Carvalhos ancestrais, teixos longevos, bétulas brancas, abetos gigantes, anéis de crescimento, copas fechadas e clareiras."),
    ("Micologia, Fermentos Naturais, Líquens e Musgos", "Esporos, micélios subterrâneos, cogumelos luminescentes, bolores nobres, leveduras selvagens e tapetes de musgo."),
    ("Entomologia, Abelhas, Borboletas e Insetos da Floresta", "Colmeias silvestres, casulos, metamorfose, besouros de casca, libélulas de rio, formigueiros e vaga-lumes."),
    ("Ornitologia, Aves Canoras, Migrações e Ninhos", "Canto matinal, plumagens nupciais, rotas migratórias, ninhos em penhascos, corujas noturnas, corvos e cisnes."),
    ("Ictiologia, Pesca de Rio, Cardumes e Vida Aquática", "Desova do salmão, trutas prateadas, enguias, esturjões, escamas, guelras, águas oxigenadas e armadilhas de vime."),
    ("Herpetologia e Anfíbios de Charco e Pedra", "Salamandras de fogo e água, rãs de lagoa, serpentes de urzal, muda de pele, hibernação no lodo e venenos."),
    ("Mastozoologia da Tundra: Ursos, Lobos e Grandes Herbívoros", "Alces, renas, bisões da estepe, ursos pardos e brancos, linces, tocas de inverno, chifres e disputas de bando."),
    ("Pedologia, Solos, Argilas, Areias e Fertilidade da Terra", "Húmus florestal, barro de oleiro, areia quartzosa, cascalho de rio, terras calcárias, erosão e terraços agrícolas."),

    # --- LIVRO III: MEDICINA, FISIOLOGIA, CICLO VITAL E SAÚDE (41–60) ---
    ("Osteologia, Esqueleto, Crânio e Articulações", "Vértebras, costelas, medula óssea, ligamentos, tendões, cartilagens, consolidação de fraturas e postura corporal."),
    ("Cardiologia Antiga, Sangue, Pulso e Circulação Vital", "Batimentos cardíacos, veias, artérias, estancamento de hemorragias, calor vital, palidez e rubor sanguíneo."),
    ("Pneumologia, Respiração, Voz e Fôlego Poético", "Pulmões, traqueia, diafragma, suspiros, fôlego de canto, ar rarefeito das montanhas e vapores balsâmicos."),
    ("Neurologia Clássica, Sentidos, Visão e Audição", "Pupila, foco visual, labirinto auditivo, tato fino, olfato, paladar, reflexos rápidos e equilíbrio."),
    ("Odontologia, Mastigação e Saúde Bucal Antiga", "Dentes, esmalte, gengivas, ervas antissépticas, cravo medicinal, extrações e elixires bucais."),
    ("Obstetrícia, Gestação, Parto e Primeiros Cuidados", "Parteiras sábias, berços, amamentação, cordão umbilical, proteção materna, cantigas de ninar e crescimento infantil."),
    ("Pediatria Tradicional, Infância, Jogos e Aprendizado", "Primeiros passos, aquisição da fala, brinquedos de madeira, contos educativos, imunidade e vigor juvenil."),
    ("Gerontologia, Sabedoria Senil, Memória e Longevidade", "Cabelos prateados, rugas de expressão, conselho de anciãos, bastões de apoio, preservação da mente e serenidade."),
    ("Epidemiologia, Quarentena, Higiene e Banhos Termais", "Purificação da água, vapores de enxofre, casas de banho, sabões de cinza e ervas, isolamento e limpeza pública."),
    ("Toxicologia, Venenos, Peçonhas e Antídotos", "Contraveneos, triaga, carvão ativado, lavagens, picadas, plantas alcaloides, imunização gradual e diagnóstico."),
    ("Cirurgia de Campanha, Instrumentos Médicos e Anestesia", "Bisturis de aço e obsidiana, pinças, agulhas curvas, fios de seda, esponjas soporíferas e cautérios."),
    ("Oftalmologia, Colírios, Lentes de Cristal e Visão", "Águas florais para os olhos, fadiga de leitura em códices, cristais de aumento, proteção contra o brilho da neve."),
    ("Dermatologia, Cicatrizes, Unguentos e Queimaduras", "Bálsamos de calêndula e mel, regeneração da epiderme, queimaduras de frio, proteção solar e óleos essenciais."),
    ("Ortopedia, Massagens, Trações e Reabilitação Física", "Alinhamento de membros, talas anatômicas, muletas, banhos quentes de sal, fortalecimento muscular e marcha."),
    ("Nutrição, Dietética, Jejuns e Equilíbrio dos Humores", "Alimentos quentes e frios, caldos restauradores, hidratação, reserva energética de inverno e digestão."),
    ("Fisiologia do Sono, Repouso, Vigília e Ritmos Circadianos", "Sono profundo, fases da noite, despertar matinal, insônia, chás calmantes e restauração das forças."),
    ("Psiquiatria Clássica, Serenidade, Melancolia e Musicoterapia", "Cura pela música de harpa, passeios em jardins, equilíbrio emocional, alívio da angústia e clareza mental."),
    ("Farmacotécnica, Almofarizes, Pílulas, Xaropes e Tinturas", "Maceração, decocção, destilação de essências, pesagem em grãos, conservação em potes de cerâmica esmaltada."),
    ("Anatomia Comparada e Medicina Veterinária de Corcéis", "Cuidado de cascos, ferraduras ortopédicas, cura de montarias, saúde do rebanho e vigor de cães de guarda."),
    ("Embalsamamento, Aromas Sacros e Conservação Memorial", "Resinas de cedro, mirra, linho puro, câmaras frias de rocha, máscaras mortuárias e preservação histórica."),

    # --- LIVRO IV: METALURGIA, ENGENHARIA, OFÍCIOS E ARTES MECÂNICAS (61–80) ---
    ("Siderurgia, Altos-Fornos, Carvão Mineral e Aço Damasco", "Redução do minério de ferro, escória, lupas incandescentes, dobramento de lâminas, têmpera seletiva e aço nobre."),
    ("Ourivesaria, Filigrana, Cravação de Gemas e Coroas", "Fios de ouro e prata, granulação, engastes, cinzelamento microscópico, polimento com ágata e joias reais."),
    ("Fundição de Bronze, Sinos Monumentais e Estatuária", "Cera perdida, moldes de barro e areia, liga de cobre e estanho, afinação acústica de sinos e pátina."),
    ("Armaria Defensiva: Cotas de Malha, Couraças e Elmos", "Anéis de ferro rebitados, placas articuladas, viseiras, grevas, manoplas, forros de couro acolchoado e escudos."),
    ("Cutelaria e Forja de Espadas, Lanças e Machados", "Espigas, guardas, pomos equilibrados, gumes duplos, sulcos de alívio, pedras de amolar e bainhas."),
    ("Serralheria Artística, Fechaduras, Chaves e Grades", "Mecanismos de segredo, ferrolhos, dobradiças forjadas, cofres de ferro, portões ornamentais e cadeados."),
    ("Cantaria de Precisão, Estereotomia e Arcos Góticos", "Pedras de fecho, aduelas, mísulas, rosáceas de pedra, gárgulas, escadas helicoidais e encaixes secos."),
    ("Carpintaria Naval e de Grandes Tesouras de Telhado", "Vigas mestras, encaixes de malhete, cavilhas de carvalho, curvatura de madeira a vapor e zimbórios."),
    ("Marcenaria Fina, Ebanisteria, Marchetaria e Mobiliário", "Tronos entalhados, arcas de casamento, escrivaninhas de escribas, incrustações de marfim e vernizes naturais."),
    ("Tanoaria, Barricas, Tonéis e Cubas de Fermentação", "Aduelas de carvalho curvadas ao fogo, arcos de ferro, vedação com junco, torneiras de madeira e envelhecimento."),
    ("Olaria, Porcelana Imperial, Azulejaria e Terracota", "Roda de oleiro, argila decantada, vidrados coloridos, queima em mufla, ânforas, telhas e ladrilhos."),
    ("Sopro de Vidro, Vitrais Coloridos, Lentes e Espelhos", "Cana de vidreiro, óxidos metálicos corantes, chumbo de vitral, espelhos de prata polida e frascos alquímicos."),
    ("Engenharia de Pontes, Viadutos, Calçadas e Estradas Reais", "Fundações subaquáticas com ensecadeiras, arcos de alvenaria, pavimentação em lajes de basalto e drenagem."),
    ("Engenharia Hidráulica: Aquedutos, Cisternas e Fontes", "Sifões invertidos, decantadores, canais cobertos, chafarizes públicos, comportas de bronze e distribuição."),
    ("Relojoaria Mecânica, Engrenagens, Pêndulos e Astrolábios", "Escapamentos, rodas dentadas de latão, pesos motores, mostradores astronômicos e autômatos sonoros."),
    ("Óptica Instrumental: Lunetas, Sextantes, Prismas eCâmaras", "Polimento de lentes côncavas e convexas, tubos de latão, medição de ângulos estrelares e projeção de luz."),
    ("Fabricação de Papel, Pergaminho, Velino e Papiro", "Banho de cal, raspagem com faca lunar, pedra-pomes, polpa de trapos de linho, formas de arame e prensagem."),
    ("Química de Pigmentos, Tintas, Vernizes e Lacas", "Azul ultramarino de lápis-lazúli, vermelhão, ocre dourado, tinta ferrogálica, goma-arábica e óleo de linhaça."),
    ("Cordoaria, Cabos Navais, Redes,Polias e Guindastes", "Torção de cânhamo e linho, alcatroamento de cabos, cadernais de múltiplos gornes, cabrestantes e içamento."),
    ("Engenharia Térmica: Hipocaustos, Lareiras, Chaminés e Estufas", "Pisos aquecidos por dutos de ar quente, fornos de alvenaria, tiragem de fumaça, braseiros e isolamento térmico."),

    # --- LIVRO V: AGRICULTURA, PECUÁRIA, FLORESTAS E SUBSISTÊNCIA (81–100) ---
    ("Cerealicultura: Trigo, Cevada, Centeio e Aveia", "Lavra, semeadura a lanço, monda, ceifa com foice, feixes, eira de debulha, ciranda e armazenamento."),
    ("Viticultura, Enologia, Vindima e Caves Subterrâneas", "Cepas de encosta, poda de inverno, lagares, mosto, fermentação malolática, trasfega e vinhos de guarda."),
    ("Olivicultura, Prensas de Azeite e Óleos Vegetais", "Colheita de outono, moinhos de pedra, prensas de fuso, decantação do azeite virgem, óleo de noz e linhaça."),
    ("Pomicultura: Macieiras, Pereiras, Cerejeiras e Enxertia", "Enxerto de garfo e borbulha, florada de primavera, colheita de frutas, cidra, secagem de frutos e geleias."),
    ("Horticultura, Raízes Comestíveis, Leguminosas e Estufas", "Canteiros elevados, rotação de culturas, lentilhas, favas, nabos, alhos, cebolas e proteção contra geada."),
    ("Apicultura, Mel, Cera Virgem, Própolis e Hidromel", "Cortiços, fumigadores de ervas, favos hexagonais, centrifugação do mel, velas de cera pura e fermentação de mel."),
    ("Ovinocultura, Pastoreio de Altitude, Tosquia e Laticínios", "Transumância entre vales e picos, cães pastores, redil de pedra, tosquia de primavera, coalho e queijos curados."),
    ("Bovinocultura, Tração Pesada, Jugos, Arados e Couros", "Bois de canga, pastagens de várzea, feno de inverno, estábulos aquecidos, ordenha, manteiga e curtimento."),
    ("Equinocultura, Haras Reais, Linhagens de Corcéis eDoma", "Potros, redondel de doma, passo, trote, galope, ferrageamento, ração de aveia e genealogia equestre."),
    ("Avicultura, Pombais de Correio, Patos, Gansos e Plumas", "Pombos-correio treinados, anilhas de mensagem, penas de escrita, édredons de pluma de ganso e postura."),
    ("Cunicultura, Criação de Pequenos Animais e Pelaria", "Coelheiras, manejo de inverno, peles macias para forro de mantos, alimentação de raízes e reprodução."),
    ("Piscicultura em Tanques, Açudes, Viveiros e Defumação", "Tanques de pedra com água corrente, criação de trutas e carpas, comportas de tela, salga e defumadouros."),
    ("Caça Maior e Menor, Armadilhas, Rastreamento e Coutadas", "Leis de proteção da fauna na estação de cria, arcos de caça, lanças de javali, redes e conservação da presa."),
    ("Coleta Florestal: Castanhas, Nozes, Pinhões, Bagas e Trufas", "Outono nos bosques, cestos de dorso, secagem de castanhas em caniços, farinha de bolota e cogumelos secos."),
    ("Moagem Hidráulica e Eólica: Mós, Farinhas e Sêmolas", "Mós dormentes e corredoras, picagem da pedra, regulagem da granulometria, peneiras de seda e farelo."),
    ("Panificação Tradicional: Fermento Natural, Fornos e Pães", "Levain ancestral, amassadura, fermentação lenta, pães de centeio, broas, biscoitos de viagem e fornos a lenha."),
    ("Charcutaria, Salga, Cura no Frio e Provisões de Inverno", "Salmouras aromáticas, câmaras de vento gélido, embutidos, carne seca, banha conservante e despensas."),
    ("Laticínios Finos: Maturação em Cavernas, Manteigas e Soros", "Coalhadas, prensagem em formas de madeira, lavagem de casca com salmoura e vinho, cura em grutas frias."),
    ("Arte Culinária: Caldeirões, Assados no Espeto, Caldos e Molhos", "Fundos aromáticos, reduções, ervas finas, espetos giratórios, panelas de barro e ferro, e serviço de mesa."),
    ("Destilaria, Cervejaria, Maltagem, Lúpulo e Infusões", "Germinação da cevada, secagem do malte, brassagem, mostura, lúpulo aromático, alambiques de cobre e licores."),

    # --- LIVRO VI: ARTES TÊXTEIS, VESTUÁRIO, JOIAS E VIDA DOMÉSTICA (101–120) ---
    ("Fiação de Lã, Linho, Cânhamo e Seda: Rocas e Fusos", "Cardagem, penteadura, maceração do linho no rio, espadelagem, fuso de peso, roda de fiar e meadas."),
    ("Tecelagem em Tear de Alto e Baixo Liço: Sarja, Cetim e Damasco", "Urdidura, trama, navetas, liços, pedais, pentes de tear, padrões geométricos e tecidos adamascados."),
    ("Tinturaria Natural: Índigo, Garança, Pastel, Açafrão ePúrpura", "Mordentes de alúmen e ferro, cubas de tingimento a quente, fixação de cor, lavagem em água corrente e secagem."),
    ("Feltragem, Pisões Hidráulicos, Capas Impermeáveis e Tapetes", "Lã prensada com água quente e sabão, martelos de pisão, feltros densos para tendas, botas e mantos de neve."),
    ("Alfaiataria Imperial: Mantos, Túnicas, Pelotes e Capuzes", "Moldes, corte em viés, costuras invisíveis, forros de arminho e marta, golas altas, mangas e caimento."),
    ("Bordado de Ouro, Prata, Seda e Pérolas (Arte Plumária e Têxtil)", "Bastidores, pontos de matiz, fios metálicos, aplicação de gemas, estandartes reais e paramentos litúrgicos."),
    ("Tapeçaria Historiada, Arraiolos, Cortinados e Dosséis", "Cartões de pintores, tecelagem de cenas épicas para aquecer muralhas de pedra, franjas e cordões."),
    ("Curtume Vegetal e Mineral: Pelica, Camurça, Pergaminho e Sola", "Tanino de casca de carvalho, banho de cal, descarne, engraxe com óleos, cilindragem e tingimento de couro."),
    ("Sapataria, Botas de Marcha na Neve,Polainas e Raquetes", "Formas de madeira, solas cravejadas, costura encerada, botas altas impermeáveis e raquetes de freixo e couro."),
    ("Selaria, Arreios, Estribos, Brigas, Alforjes eBainhas", "Selas de guerra e viagem, cabeçadas lavradas, peitorais, alforjes de couro cru e coldres."),
    ("Peleteria de Inverno: Casacos, Gorros, Luvas e Mantas", "Costura de peles de raposa, lobo, castor e ovelha, conservação do pelo, luvas forradas e cobertores."),
    ("Cestaria, Trançado de Vime, Junco, Palha e Esteiras", "Cestos de vindima e carga, berços de vime, chapéus, esteiras de piso, balaios e armadilhas de pesca."),
    ("Passamanaria, Rendas de Bilros, Galões, Fitas e Borlas", "Almofadas de bilros, agulhas de rede, cordões de sinete, cintos trançados, fechos e alamares."),
    ("Perfumaria, Águas de Cheiro, Incensos, Saboaria e Óleos", "Extração por enfleurage, água de rosas e lavanda, resinas de olíbano e pinho, sabões finos e unguentos."),
    ("Iluminação Doméstica e Urbana: Candeias, Tochas, Velas e Lustres", "Candeias de azeite, velas de cera de abelha, arandelas de ferro, lustres de roda, lanternas de chifre e vidro."),
    ("Mobiliário Doméstico: Camas de Dossel, Arcas, Mesas e Bancos", "Colchões de lã e plumas, travesseiros, baús ferrados, mesas de cavalete, cadeiras de braços e estantes."),
    ("Utensílios de Mesa e Cozinha: Baixelas, Cálices, Talheres e Caldeirões", "Taças de prata e estanho, pratos de cerâmica, colheres de chifre e madeira, facas de mesa e saleiros."),
    ("Organização da Casa, Chaves, Despensas, Adegas e Sótãos", "Economia doméstica, conservação de roupas com lavanda e cedro, controle de estoque de lenha e víveres."),
    ("Jogos de Salão, Xadrez Imperial, Dados, Enigmas e Passatempos", "Tabuleiros marchetados, peças esculpidas em marfim e ébano, estratégias, charadas poéticas e convívio."),
    ("Hospitalidade, Etiqueta de Corte, Saudações, Presentes e Banquetes", "Ritos de recepção ao viajante, lavagem de mãos, lugares à mesa por precedência, brindes e despedidas."),

    # --- LIVRO VII: TRANSPORTE, NAVEGAÇÃO, COMÉRCIO E COMUNICAÇÃO (121–140) ---
    ("Arquitetura Naval: Galés, Dracares, Cocas e Caravelas", "Cavername, sobrequilha, castelos de proa e popa, escotilhas, porões de carga, figuras de proa e calado."),
    ("Aparelho de Velas, Mastreação, Vergas, Maçame e Manobras", "Velas latinas e redondas, adriças, escotas, estais, enxárcias, rizes, cambar e bordejar contra o vento."),
    ("Navegação Astronômica, Cartas Náuticas, Prumo e Bússola", "Rosa dos ventos, linha de barquinha, ampulhetas de quarto, declinação magnética, faróis e balizas."),
    ("Portos, Molhes, Diques Secos, Estaleiros e Alfândegas", "Quebra-mares de cantaria, guindastes portuários, carreiras de lançamento, armazéns reais e quarentena naval."),
    ("Navegação Fluvial: Barcaças, Balsas, Eclusas e Caminhos de Sirga", "Reboque por parelhas nas margens, canais navegáveis, pontes levadiças, travessia de corredeiras e pedágios."),
    ("Transporte de Inverno: Trenós, Esquis, Parelhas de Cães e Renas", "Patins de madeira ferrada, trenós de carga e correio, esquis de bétula, arreios de neve e abrigos de montanha."),
    ("Carruagens, Carroças de Quatro Rodas, Eixos, Raios e Suspensão", "Rodas com aros de ferro a quente, cubos engraxados, lanças de atrelagem, freios de alavanca e liteiras."),
    ("Pontes, Vaus, Barcas de Passagem, Pontões e Túneis", "Pontes pênseis de corda, pontes de barcas, galerias escavadas na rocha viva, guarda-corpos e marcos."),
    ("Estalagens, Albergues de Montanha, Mudas de Cavalos e Postas", "Pátios de carruagens, cavalariças de troca rápida, salões aquecidos, quartos de viajantes e segurança de estrada."),
    ("Correio Imperial, Mensageiros a Cavalo, Pombos e Torres de Sinal", "Estafetas reais, bolsas seladas, código de fachos luminosos e fumaça entre picos, tambores e trompas."),
    ("Caravanas Mercantes, Rotas da Seda, do Âmbar, do Sal e das Peles", "Comboios escoltados, pousos fortificados, guias de montanha, fardos impermeáveis e feiras anuais."),
    ("Pesos e Medidas Oficiais: Côvados, Braças, Talentos, Minas e Ânforas", "Padrões de bronze guardados na Chancelaria, balanças de braços iguais, medidas de grãos e líquidos."),
    ("Numismática, Cunhagem de Ouro e Prata, Ensaio de Metais e Câmbio", "Cunhos gravados, discos monetários, toque na pedra de lídia, cambistas, cartas de crédito e letras."),
    ("Contabilidade, Livros de Razão, Ábacos, Quitações e Arquivos", "Tábuas de cálculo, registro de entradas e saídas, recibos selados, inventários de bens e auditoria real."),
    ("Sociedades Mercantis, Guildas de Ofícios, Corporações e Aprendizes", "Mestres artesãos, companheiros, obras-primas de exame, estatutos de guilda, insígnias e auxílio mútuo."),
    ("Feiras Francas, Mercados Cobertos, Leilões, Preços e Regulação", "Bancas de mercadores, pregões, fiscais de qualidade e peso, tabelamento em tempos de escassez e câmbio."),
    ("Direito Marítimo e Comercial: Fretes, Seguros, Avarias e Salvados", "Contratos de fretamento, divisão de risco em tempestades, alijamento de carga e direito de naufrágio."),
    ("Armazenagem: Silos Subterrâneos, Celeiros Elevados e Gelo Estival", "Poços de neve compactada com palha para conservar alimentos no verão, celeiros ventilados e adegas."),
    ("Cartografia Terrestre, Agrimensura, Groma, Cordas e Marcos de Divisa", "Medição de terras, triangulação visual, plantas cadastrais, limites de municípios e desenhos topográficos."),
    ("Exploração de Terras Incógnitas, Expedições, Diários de Bordo e Relatos", "Preparação de expedições, contato com povos distantes, coleta de espécimes, mapas de rota e crônicas."),

    # --- LIVRO VIII: ARTE MILITAR, DEFESA, DIREITO E GOVERNO IMPERIAL (141–160) ---
    ("Arquitetura Militar: Muralhas Duplas, Barbacãs, Torres e Fossos", "Ameias, seteiras, matacães, pontes levadiças, rastrilhos de ferro, poternas secretas e cidadelas."),
    ("Poliorcética (Arte do Cerco): Aríetes, Trabucos, Balistas e Minas", "Contra-baterias, galerias de solapamento, manteletes de proteção, escadas de assalto, fogo grego e defesa."),
    ("Infantaria Pesada e Leve: Falanges, Parede de Escudos e Piqueiros", "Formações cerradas, carga de lanças, combate aproximado, escudeiros, revezamento de linhas e disciplina."),
    ("Arquearia e Besteiros: Arcos Longos, Compostos, Aljavas e Virotes", "Arcos de teixo e chifre, cordas de linho encerado, flechas emplumadas, bestas de polia, mira e cadência."),
    ("Cavalaria de Choque e Ligeira: Lanceiros, Couraceiros e Batedores", "Carga em cunha, lanças em riste, ginetes de flanco, reconhecimento de terreno e perseguição."),
    ("Esgrima Histórica, Combate Singular, Guardas, Estocadas e Paradas", "Posturas de combate, fintas, contra-ataques, desarme, honra de duelo, mestres de armas e treino."),
    ("Logística de Exército: Comboios, Forrageamento, Acampamentos e Pontes", "Tendas de comando, cozinhas de campanha, ferradores móveis, hospitais de sangue e linhas de suprimento."),
    ("Sinais de Comando: Estandartes, Flâmulas, Clarins, Tambores e Senhas", "Toques de alvorada, carga, reagrupamento e retirada, senhas noturnas de sentinela e insígnias de legião."),
    ("Marinha de Guerra: Abordagem, Esporões, Brulotes eBatalhas Navais", "Manobras de flanqueamento no mar, arpéus de abordagem, arqueiros de gávea, defesa costeira e bloqueio."),
    ("Diplomacia de Guerra: Arautos, Tréguas, Reféns, Resgates e Tratados", "Imunidade de parlamentares, bandeiras de parlamento, troca de prisioneiros, indenizações e paz jurada."),
    ("Soberania Imperial: Coroação, Cetro, Orbe, Trono e Conselho de Estado", "Insígnias imperiais, juramento de fidelidade, ministros, chanceleres, audiências solenes e sucessão."),
    ("Administração Provincial: Governadores, Fronteiras, Censos e Tributos", "Divisão territorial, recenseamento de fogos, coleta equitativa, manutenção de estradas e ordem pública."),
    ("Processo Judicial: Petições, Citações, Provas, Testemunhas e Sentenças", "Juízes togados, contraditório, documentos autênticos, perícias, deliberação do tribunal e recursos."),
    ("Direito Civil: Propriedade, Posse, Servidões, Contratos e Obrigações", "Compra e venda, locação, empréstimo, depósito, fiança, penhor, hipoteca, usucapião e vizinhança."),
    ("Direito de Família e Sucessões: Testamentos, Legados, Tutela e Curatela", "Partilha de herança, proteção de órfãos e viúvas, codicilos, administração de patrimônio familiar."),
    ("Direito Penal e Equidade: Delitos, Penas, Circunstâncias, Indulto e Asilo", "Proporcionalidade da pena, reparação do dano, exílio, perdão imperial, santuários de asilo e reabilitação."),
    ("Chancelaria e Diplomática: Bulas, Cartas-Patentes, Selos de Cera e Chumbo", "Fórmulas de abertura e fecho, validação de documentos, arquivos imperiais, criptografia e copistas."),
    ("Heráldica Imperial: Brasões, Esmaltes, Metais, Timbres e Divisas", "Escudos esquartelados, leões, águias, estrelas, árvores, lemas em Tréppio Clássico e livros de armaria."),
    ("Ordem Pública, Guarda Urbana, Vigias Noturnos e Combate a Incêndios", "Rondas de lanterna, toque de recolher, bombas manuais de água, baldes de couro, ganchos e prevenção."),
    ("Cidadania, Direitos Municipais, Assembleias, Magistrados Locais e Obras", "Forais de cidade livre, conselhos de cidadãos, eleição de alcaides, manutenção de fontes e muralhas."),

    # --- LIVRO IX: FILOSOFIA, CIÊNCIAS DO ESPÍRITO, LETRAS E BELAS-ARTES (161–180) ---
    ("Metafísica e Ontologia: Ser, Essência, Substância, Causa e Fim", "Primeiros princípios, ato e potência, necessidade e contingência, unidade, verdade, bondade e beleza."),
    ("Lógica Formal, Dialética, Silogismos, Definições e Argumentação", "Premissas, termos, dedução, indução, refutação de sofismas, categorias do pensamento e demonstração."),
    ("Epistemologia: Conhecimento, Percepção, Razão, Intuição e Ciência", "Graus de certeza, evidência, memória intelectiva, abstração, método investigativo e sabedoria."),
    ("Filosofia da Natureza: Tempo, Espaço, Movimento, Elementos e Cosmos", "Ciclos naturais, harmonia das esferas, transformação da matéria, leis físicas e ordem universal."),
    ("Retórica e Oratória: Exórdio, Narração, Provas, Peroração e Eloquência", "Gêneros deliberativo, judicial e epidítico, figuras de linguagem, cadência da frase, voz e gesto."),
    ("Gramática, Filologia, Etimologia, Fonologia e Crítica Textual", "Sandi consonantal, haplologia, raízes, declinações, matriz verbal, colação de manuscritos e glosas."),
    ("Poética, Métrica, Ritmo, Aliteração, Assonância e Gêneros Literários", "Epopéias, hinos sagrados, elegias, odes, baladas, pés métricos, cesuras, estrofes e rima toante."),
    ("Historiografia, Anais, Crônicas, Genealogias e Método Histórico", "Fontes primárias, crítica de testemunhos, sucessão de eras, memória dos reis e lições da história."),
    ("Pedagogia, Escolas, Academias, Trivium, Quadrivium e Disputatio", "Relação mestre-discípulo, leitura comentada, exercícios de estilo, matemática, música, astronomia e graus."),
    ("Biblioteconomia, Scriptoria, Catálogos, Conservação e Encadernação", "Estantes de códices, correntes de segurança, capas de couro lavrado com fechos de bronze e restauração."),
    ("Caligrafia e Paleografia: Escritas Uncial, Chanceleresca e Glífica", "Ductus da pena, proporção das letras, capitulares historiadas, abreviaturas, rúbricas em vermelhão e ouro."),
    ("Iluminura e Pintura de Cavalete: Folha de Ouro, Têmpera e Afresco", "Brunimento de ouro sobre bolo armênio, têmpera de ovo, preparação de gesso, perspectiva e retrato."),
    ("Escultura em Mármore, Pedra, Madeira Policromada e Marfim", "Desbaste com ponteiro, escopro, gradina, polimento com areia fina, panejamento, relevo e proporção áurea."),
    ("Teoria Musical: Modos, Contraponto, Harmonia, Consonância e Notação", "Tetracordes, intervalos justos, quintas e oitavas, neumas, pautas musicais, cânones e coros a quatro vozes."),
    ("Instrumentos de Corda: Harpas, Alaúdes, Violas, Saltérios eLiras", "Tampas harmônicas de abeto, cordas de tripa e prata, cravelhas, cavaletes, arcos de crina e dedilhado."),
    ("Instrumentos de Sopro e Percussão: Órgãos, Flautas, Trompas e Tímpanos", "Tubos de estanho e madeira, foles de órgão, palhetas, trombetas de prata, tambores de pele e carrilhões."),
    ("Arte Dramática, Teatro, Tragédia, Comédia, Coro e Cenografia", "Anfiteatros, acústica, máscaras expressivas, diálogo dramático, catarse, figurinos e representação."),
    ("Dança de Corte e Tradicional: Coreografia, Compasso, Roda e Solenidade", "Passos medidos, reverências, danças de roda nas festas de colheita, danças de espadas e cortejos."),
    ("Aritmética, Álgebra, Proporções, Frações e Teoria dos Números", "Operações fundamentais, números primos, razões harmônicas, progressões, raízes e cálculo prático."),
    ("Geometria Plana e Espacial, Trigonometria, Compasso e Simetria", "Polígonos regulares, sólidos platônicos, seção áurea, medição de alturas por sombras e abóbadas."),

    # --- LIVRO X: PSICOLOGIA PROFUNDA, ESPIRITUALIDADE, LITURGIA E LORE DE ECOS (181–200) ---
    ("Afetos Luminosos: Amor, Amizade, Gratidão, Compaixão e Júbilo", "Benevolência, ternura familiar, concórdia fraterna, entusiasmo criador, paz interior e admiração."),
    ("Afetos Sombrios e Luta Interior: Ira, Medo, Inveja, Orgulho e Remorso", "Arrependimento sincero, superação do temor, domínio da paixão, humildade verdadeira e perdão."),
    ("Vontade, Liberdade, Escolha, Deliberação, Firmeza e Perseverança", "Propósito inabalável, coragem moral, paciência nas adversidades, autodomínio e cumprimento do dever."),
    ("Imaginação, Criatividade, Inspiração Poética, Visão e Genialidade", "Fantasia construtiva, síntese de imagens, iluminação súbita do artista, beleza ideal e obra-prima."),
    ("Onirologia: Sonhos Proféticos, Pesadelos, Símbolos e Interpretação", "Vigilância da alma durante o sono, mensagens veladas, paz noturna e discernimento de visões."),
    ("Teologia Tréppia: Oratypatte (O Pai do Todo), Gyos e os Atributos Divinos", "Onipotência, eternidade, providência, bondade infinita, criação pelo Verbo Musical e transcendência."),
    ("Angelologia de Ecos: Os Halo (Ainur), Ferytrátte, Vétrátte e Tektrátte", "Espíritos do pensamento, potências regentes dos ventos, das águas e da forja da terra, e harmonia."),
    ("Cosmogonia Musical: O Halylitror, Os Três Grandes Temas e a Visão", "Prelúdio nos Salões Atemporais, dissonância de Kurlan, vitória do Terceiro Tema e o decreto Esu!"),
    ("Antropologia Sacra: Ittakazeti (Primeiros Nascidos) e Dotakazeti (Homens)", "Dons dos filhos de Ilúvatar, imortalidade e mortalidade, destino além dos círculos do mundo e aliança."),
    ("Liturgia Imperial: Oração, Hinos, Bênçãos, Procissões e Ano Litúrgico", "Ofício das horas, incensação, cânticos antifonais, festas das estações, vigílias de luz e consagração."),
    ("Arquitetura e Espaço do Templo: Altar, Nave, Coro, Batistério e Sacristia", "Orientação solar do santuário, lâmpada perpétua, vasos sagrados, véus, relíquias e silêncio reverente."),
    ("Vida Monástica e Eremítica: Votos, Regra, Contemplação, Trabalho e Estudo", "Mosteiros de montanha, claustros, leitura espiritual, cópia de manuscritos, hospitalidade e oração contínua."),
    ("Sacramentos, Juramentos Sagrados, Alianças, Votos e Expiar de Faltas", "Confissão de culpa, penitência medicinal, reconciliação, unção dos enfermos e fidelidade até a morte."),
    ("Ritos Funerários, Mausoléus, Epitáfios, Sufrágios e Memória dos Mortos", "Velório com cânticos de esperança, sepultamento em rocha, estelas gravadas e comunhão dos ancestrais."),
    ("Tradição Oral das Casas Nobres: Korikeste, Linhagens e Crônicas de Clã", "Genealogias recitadas, relíquias de família, espadas ancestrais, dever de honra e hospitalidade da Casa."),
    ("Topografia Sagrada de Ecos: Treppênia, Koryvela, Rixelaka e Ferykrope", "Geografia mítica e histórica do Império, picos gélidos, florestas ancestrais, campinas dos ventos e cidades."),
    ("Sociolinguística Tréppia: Norma Culta da Chancelaria vs. Dialetos Plebeus", "Pureza da Era Clássica V8.1, Síncrese de Celia, estigmatização de variantes vulgares e preservação da língua."),
    ("Simbolismo dos Números, das Pedras, das Árvores e dos Astros em Ecos", "Significado místico do sete e do doze, virtudes das gemas, emblemas reais e correspondências cósmicas."),
    ("Profecias, Esperança Escatológica, A Última Batalha e a Segunda Música", "Cura final das feridas de Arda/Oratoxe, derrota definitiva de Kurlan e sinfonia plena dos filhos de Deus."),
    ("Síntese Filológica Suprema: O Códice Perpétuo e a Arte da Glotopoiese", "Perfeição morfofonológica, eufonia das 21 leis, plenitude lexical e imortalidade da língua Tréppia."),
]

assert len(TEMAS_200) == 200, f"Esperado 200 temas, encontrado {len(TEMAS_200)}"


def main():
    if os.path.exists(FILA_PATH):
        with open(FILA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"ultimo_indice_executado": 3, "historico_execucoes": []}

    data["descricao"] = (
        "Fila Enciclopédica de 200 Campos Semânticos para a Expansão Lexical a cada 30 Minutos "
        "(*/30 * * * *) do Tréppio (Era Clássica V8.1) pelo Conde"
    )
    data["intervalo_cron"] = "*/30 * * * *"
    data["total_temas_planejados"] = 200
    data["temas"] = [
        {"id": idx, "titulo": titulo, "escopo": escopo}
        for idx, (titulo, escopo) in enumerate(TEMAS_200, 1)
    ]

    with open(FILA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(data['temas'])} temas gravados com sucesso em {FILA_PATH}!")
    print(f"[OK] Último índice executado preservado: {data['ultimo_indice_executado']} ({len(data['historico_execucoes'])} lotes no histórico).")


if __name__ == "__main__":
    main()
