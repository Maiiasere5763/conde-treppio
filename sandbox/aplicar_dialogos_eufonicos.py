# -*- coding: utf-8 -*-
"""
aplicar_dialogos_eufonicos.py
Substitui os diálogos nos 4 arquivos HTML pelo texto em Tréppio Clássico V8.1 puro e eufônico (revisado sem anomalias).
"""

import os
import re

new_dialogues_js = """    // --- ABA XII: DIÁLOGOS PRÁTICOS E CONVERSAÇÃO COTIDIANA (ECOS DA ERA ANTIGA À CLÁSSICA) ---
    const ECOS_DIALOGUES = [
      {
        id: 1,
        titulo: "Cena I: Chegada à Estalagem sob a Nevasca (Talles in Rixej)",
        subtitulo: "Diálogo de acolhida no calor da lareira de pedra após travessia na nevasca",
        falas: [
          { autor: "Tepypatte (Estalajadeiro)", treppio: "Moba'el ad ti, ynte! Avurvé et fer in rixej vurba. Tep ny vuran esu!", pt: "Bom dia a ti, viajante! Gelo e vento rugiam na serra. Nossa casa está aquecida!" },
          { autor: "Ynte (Viajante)", treppio: "Moba'el, Tepypatte! Faldem et luttorom vurom pasum. Avur in vari em fassa.", pt: "Bom dia, senhor da estalagem! Preciso de pão e carne assada quente. O frio na estrada castigou-me." },
          { autor: "Tepypatte (Estalajadeiro)", treppio: "In takej faldem et garvokom mobum! In vurrexi karem tor!", pt: "À mesa sirvo pão fresco e uma caneca de cerveja escura! Toma um assento junto à lareira!" },
          { autor: "Ynte (Viajante)", treppio: "Mobavë letum: faletom in tepi toruska? Vesdakoi falur pasum.", pt: "Peço-te com cortesia: tens um leito vago na casa? Após a ceia, repousar preciso." },
          { autor: "Tepypatte (Estalajadeiro)", treppio: "Torum! Falet vuran in faliaj esu. Zelta verreoi paror parru.", pt: "Tenho-o! Um leito aquecido aguarda no aposento. Por três moedas de bronze acertaremos o valor." }
        ]
      },
      {
        id: 2,
        titulo: "Cena II: Na Forja do Mestre Artífice (In Tekiai Tettey)",
        subtitulo: "Reparo da ferradura da montaria e encomenda de lâmina afiada",
        falas: [
          { autor: "Ynte (Viajante)", treppio: "Mobor ad ti, Tette! Mald ey in vari poketekom kossa. Tettek ty tekba ne?", pt: "Graça e paz a ti, mestre forjador! Minha montaria perdeu a ferradura no caminho pedregoso. Teu martelo está ativo?" },
          { autor: "Tette (Ferreiro)", treppio: "Vurrex tekba et verre vurran esu! Maldom in tepi tekur rukrum.", pt: "A forja trabalhava e o metal está incandescente! Posso ferrar o corcel aqui na oficina." },
          { autor: "Ynte (Viajante)", treppio: "Sfammirom saidet et sfartekom pasum, nam rixer vela esu. Kemyga paror esu?", pt: "Preciso também de uma espada afiada e um escudo, pois as serras são perigosas e sombrias. Quanto custará?" },
          { autor: "Tette (Ferreiro)", treppio: "Vexta verreoi sfammirom saidrum. Mobavë tekorom tekum!", pt: "Por cinco moedas de bronze afiarei a lâmina. Trabalho com lealdade e precisão!" }
        ]
      },
      {
        id: 3,
        titulo: "Cena III: A Travessia da Floresta com o Cão Loiro (Poke Xuna in Ecos)",
        subtitulo: "O encontro místico com o animal-guia luminoso através da bruma e do gelo",
        falas: [
          { autor: "Ynte (Viajante)", treppio: "Poke xuna! Alim ynus? In fervei lanom ty mirum.", pt: "Cão loiro e sagrado! Para onde andas? Através da névoa contemplo a tua aura luminosa." },
          { autor: "Interação", treppio: "Poke in filoxi keladba, et halkvestos ty in xelvéi ynnan.", pt: "O animal avançava pelo vale profundo, e nós seguimos tuas pegadas no chão nevado." },
          { autor: "Ynte (Viajante)", treppio: "Teggarom rixa mirum! In kadi kan durba, kora et avura. Litror kanye sukori ey keladu!", pt: "Avisto a fortaleza da montanha! No alto da colina ela resplandecia, antiga e coroada de gelo. A ressonância de seus ecos toca o meu coração!" }
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
    ];"""

html_files = [
    r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html",
    r"D:\Conde_Treppio\docs\index.html",
    r"D:\Conde_Treppio\sandbox\android_apk\app\src\main\assets\index.html",
    r"D:\Conde_Treppio\dist\Codice_Treppio_Portatil.html"
]

pattern = re.compile(r"    // --- ABA XII: DIÁLOGOS PRÁTICOS.*?const ECOS_DIALOGUES = \[.*?\];\n", re.DOTALL)

for fpath in html_files:
    if not os.path.exists(fpath):
        print("Arquivo não encontrado:", fpath)
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if pattern.search(content):
        content = pattern.sub(new_dialogues_js + "\n", content)
        content = content.replace("44.585", "56.342")
        content = content.replace("44585", "56342")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated com sucesso:", fpath)
    else:
        print("Padrão de diálogo não encontrado em:", fpath)
