# -*- coding: utf-8 -*-
"""
expandir_lexico_v8_1_eufonico.py
Expansão lexical do Tréppio Clássico V8.1 (sandbox), em estrita obediência a:
  - gramatica_normativa_base.md (Sandi Consonantal, Haplologia, Lei 6.5 de Composição)
  - treppio_base.md (21 mutações, sufixos produtivos -ia, -te, -or, -tek, -il, -gar)
  - adendo_edicao_unificada_v8_1.md (Dativo vocalizado, Matriz Quadripartite, diacríticos)

Ações:
  1. Retifica 4 lemas defeituosos herdados da simulação anterior (violação de sandi ou colisão).
  2. Acrescenta 22 raízes verbais novas (88 verbos nos 4 eixos), substantivos derivados,
     adjetivos e advérbios, todos com a mutação consonantal aplicada na própria forma.
  3. Valida: sem duplicatas, sem encontros proibidos remanescentes, sem termos expurgados.
"""
import re
import sys

GEN = r"D:\Conde_Treppio\sandbox\gerador_dicionario_integral_sandbox.py"

# ---------------------------------------------------------------------------
# 1. RETIFICAÇÕES (lemas que violavam o Sandi ou colidiam com formas canônicas)
# ---------------------------------------------------------------------------
RETIFICACOES = [
    # doobbam é o imperfeito canônico de doot- (eu me entediava): colisão semântica intolerável.
    ('("doobbam", 2, "por favor, com licença, favor benevolente", "raiz doob- (benevolência) + -am")',
     '("mobalete", 1, "por favor, cortesia, palavra benevolente (fórmula de pedido)", "moba + lete")'),
    # kild- + tor-: o contato dental exige dt -> tt.
    ('("kildtor", 2,', '("kilttor", 2,'),
    ('"kild- (frio) + tor- (cobrir)"', '"kild- (frio) + tor- (cobrir), dt -> tt"'),
    # rn -> ld é mandatório (far + ne -> falde; mir + n -> mild).
    ('("marn", 2, "cavalo de montaria e carga, corcel resistente à neve", "raiz marn- (montaria equina)")',
     '("mald", 2, "cavalo de montaria e carga, corcel resistente à neve", "mar- (montaria) + -n, rn -> ld")'),
    # ln -> ll é mandatório (bel + n -> bell).
    ('("talnes", 2, "estalagem de beira de estrada, albergue de viajantes", "tal- (comércio) + nes- (pousada)")',
     '("talles", 2, "estalagem de beira de estrada, albergue de viajantes", "tal- (comércio) + nes- (pousada), ln -> ll")'),
]

# ---------------------------------------------------------------------------
# 2. NOVAS RAÍZES VERBAIS (Positivo, Privativo a-, Iterativo o-/od-, Iterativo-Privativo od-a-)
# ---------------------------------------------------------------------------
NEW_VERB_ROOTS = [
    ("lix", "lavar, limpar com água", "sujar, macular", "relavar, enxaguar", "voltar a sujar"),
    ("kerd", "cortar lenha, talhar madeira", "emendar, unir o que foi cortado", "recortar, aparar", "voltar a emendar"),
    ("zal", "pagar, quitar uma dívida", "dever, ficar inadimplente", "pagar de novo, reembolsar", "voltar a dever"),
    ("rux", "cozinhar ao fogo, assar no caldeirão", "deixar cru, retirar do fogo", "reaquecer a comida", "voltar a esfriar a comida"),
    ("hesk", "perguntar, indagar", "calar a pergunta, não indagar", "perguntar de novo, insistir", "voltar a calar a pergunta"),
    ("bod", "responder, replicar", "negar resposta, emudecer", "responder de novo, treplicar", "voltar a negar resposta"),
    ("nyk", "abrir porta ou baú", "fechar, trancar", "reabrir", "voltar a fechar"),
    ("sek", "sentar-se, assentar-se", "levantar-se, erguer-se do assento", "sentar-se de novo", "voltar a levantar-se"),
    ("kraz", "rir, alegrar-se", "chorar, lamentar", "voltar a rir", "voltar a chorar"),
    ("tav", "contar, enumerar moedas ou dias", "perder a conta", "recontar, conferir", "voltar a perder a conta"),
    ("hux", "vestir, cobrir com roupa", "despir, desnudar", "revestir, trocar de roupa", "voltar a despir"),
    ("pek", "quebrar, partir", "consertar, remendar", "voltar a quebrar", "voltar a consertar"),
    ("lyr", "esperar, aguardar com esperança", "desesperar, perder a esperança", "voltar a esperar", "voltar a desesperar"),
    ("gob", "trocar, negociar, mercadejar", "recusar a troca, desfazer negócio", "renegociar", "voltar a desfazer o negócio"),
    ("rop", "chamar, convocar pelo nome", "dispensar, mandar embora", "chamar de novo", "voltar a dispensar"),
    ("tuk", "cavar, escavar a terra", "aterrar, cobrir a cova", "recavar", "voltar a aterrar"),
    ("xel", "nevar, cair neve", "degelar, derreter a neve", "voltar a nevar", "voltar a degelar"),
    ("kask", "coser, costurar", "descoser, desfazer a costura", "recoser, remendar o pano", "voltar a descoser"),
    ("drak", "puxar, arrastar, rebocar", "soltar, largar a corda", "puxar de novo", "voltar a soltar"),
    ("gelm", "acender a candeia, atear fogo à mecha", "apagar a candeia", "reacender a candeia", "voltar a apagar a candeia"),
    ("sulv", "cantarolar, entoar baixinho", "emudecer o canto", "voltar a cantarolar", "voltar a emudecer o canto"),
    ("hab", "acolher, hospedar o viajante", "expulsar, negar abrigo", "voltar a acolher", "voltar a negar abrigo"),
]

# ---------------------------------------------------------------------------
# 3. NOVOS SUBSTANTIVOS (lema, declinação, significado, etimologia com sandi explícito)
# ---------------------------------------------------------------------------
NEW_NOUNS = [
    # --- Saudações e cortesia ---
    ("Mobanir", 2, "boa noite (saudação noturna)", "moba + nir"),
    ("Mobafea", 1, "bom sol, boa tarde (saudação vespertina)", "moba + fea"),
    # --- Agentes e pessoas (-te, dt/kt -> tt) ---
    ("ynte", 1, "viajante, caminhante, andarilho", "yn- + -te"),
    ("Tepypatte", 1, "hospedeiro, senhor da estalagem, pai da casa", "tepy + Patte (Lei 6.5, camada clássico-genitiva)"),
    ("habte", 1, "anfitrião, acolhedor de viajantes", "hab- + -te"),
    ("kertte", 1, "lenhador, talhador de madeira", "kerd- + -te, dt -> tt"),
    ("ruxte", 1, "cozinheiro, mestre do caldeirão", "rux- + -te"),
    ("gobte", 1, "mercador, negociante, mascate", "gob- + -te"),
    ("zalte", 1, "pagador, tesoureiro", "zal- + -te"),
    ("tutte", 1, "mineiro, coveiro, cavador", "tuk- + -te, kt -> tt"),
    ("kastte", 1, "alfaiate, costureiro", "kask- + -te, kt -> tt"),
    ("apette", 1, "remendão, consertador de utensílios", "a- + pek- + -te, kt -> tt"),
    ("dratte", 1, "carreteiro, condutor de trenó", "drak- + -te, kt -> tt"),
    ("mixil", 2, "criança, pequena pessoa", "mixi + -il"),
    ("kranil", 2, "menina", "kran + -il"),
    ("kronil", 2, "menino", "kron + -il"),
    # --- Casa, abrigo e utensílios (-ia, -tek, -il) ---
    ("nyke", 1, "porta", "nyk- + -e"),
    ("nykil", 2, "janela, portinhola", "nyke + -il"),
    ("nyttek", 2, "chave", "nyk- + -tek, kt -> tt"),
    ("anyttek", 2, "fechadura, tranca", "a- + nyk- + -tek, kt -> tt"),
    ("falia", 1, "quarto de dormir, aposento", "fal- + -ia"),
    ("ruxia", 1, "cozinha", "rux- + -ia"),
    ("ruxtek", 2, "caldeirão, panela de ferro", "rux- + -tek"),
    ("ruxet", 2, "ensopado, prato cozido (particípio nominalizado)", "rux- + -et"),
    ("lixia", 1, "casa de banho, lavadouro", "lix- + -ia"),
    ("lixtek", 2, "bacia, gamela de lavar", "lix- + -tek"),
    ("komia", 1, "taberna, casa de beber", "kom- + -ia"),
    ("komtek", 2, "copo, cálice cotidiano", "kom- + -tek"),
    ("komor", 2, "bebida, trago", "kom- + -or"),
    ("makia", 1, "despensa, refeitório", "mak- + -ia"),
    ("makor", 2, "refeição, alimento servido", "mak- + -or"),
    ("sekil", 2, "banquinho, mocho", "sek- + -il"),
    ("lanil", 2, "candeia, vela de sebo", "lan + -il"),
    ("lantek", 2, "lanterna, lamparina", "lan + -tek"),
    ("gelmtek", 2, "pederneira, isqueiro de mecha", "gelm- + -tek"),
    ("vuria", 1, "fornalha, forja", "vur + -ia"),
    ("vurtek", 2, "atiçador do fogo", "vur + -tek"),
    ("fertek", 2, "fole de forja", "fer + -tek"),
    ("vétek", 2, "balde, vasilha de água", "Vé + -tek"),
    ("kerttek", 2, "machado de lenha", "kerd- + -tek, dt -> tt"),
    ("tuttek", 2, "pá, enxada", "tuk- + -tek, kt -> tt"),
    ("kasttek", 2, "agulha de coser", "kask- + -tek, kt -> tt"),
    ("drattek", 2, "corda de reboque, arreio", "drak- + -tek, kt -> tt"),
    ("poketek", 2, "ferradura, arreio de animal", "poke + -tek"),
    ("yntek", 2, "cajado, bordão de viagem", "yn- + -tek"),
    ("huxor", 2, "roupa, vestimenta", "hux- + -or"),
    ("huxgar", 2, "capa, manto pesado de viagem", "hux- + -gar"),
    ("huxil", 2, "camisa, túnica leve", "hux- + -il"),
    ("kitil", 2, "carta, bilhete", "kit- + -il"),
    # --- Comércio e contagem ---
    ("gobia", 1, "mercado, feira", "gob- + -ia"),
    ("gobor", 2, "troca, negócio", "gob- + -or"),
    ("zalor", 2, "pagamento, quitação", "zal- + -or"),
    ("azalor", 2, "dívida pendente, inadimplência", "a- + zal- + -or"),
    ("tavor", 2, "contagem, número, soma", "tav- + -or"),
    ("paror", 2, "preço, valor merecido", "par- + -or"),
    ("lauril", 2, "moeda de ouro", "lauri + -il"),
    ("verril", 2, "moeda de bronze", "verre + -il"),
    # --- Fala e emoção ---
    ("heskor", 2, "pergunta", "hesk- + -or"),
    ("bodor", 2, "resposta", "bod- + -or"),
    ("ropor", 2, "chamado, convocação", "rop- + -or"),
    ("krazor", 2, "riso, alegria", "kraz- + -or"),
    ("akrazor", 2, "pranto, lamento", "a- + kraz- + -or"),
    ("lyror", 2, "esperança, espera", "lyr- + -or"),
    ("alyror", 2, "desespero", "a- + lyr- + -or"),
    ("sulvor", 2, "cantiga, canção de ninar", "sulv- + -or"),
    # --- Natureza, tempo e paisagem ---
    ("xelvé", 1, "neve", "xel- + Vé"),
    ("xelor", 2, "nevada, tempestade de neve", "xel- + -or"),
    ("nirlan", 2, "lua", "nir + lan"),
    ("mirvé", 1, "lágrima", "mir + Vé"),
    ("korvé", 1, "seiva, resina", "kor + Vé"),
    ("farvé", 1, "cerveja de trigo", "far- + Vé"),
    ("korgar", 2, "floresta densa, bosque ancestral", "kor + -gar"),
    ("rixil", 2, "seixo, pedrinha", "rixe + -il"),
    ("varil", 2, "trilha, atalho", "var + -il"),
    ("belvar", 2, "jornada, um dia de caminho", "bel + var"),
    ("tonkril", 2, "instante, momento", "tonkre + -il"),
    ("veksixil", 2, "garoa, chuvisco", "veksixi + -il"),
    ("pokil", 2, "filhote, cãozinho", "poke + -il"),
    ("tukia", 1, "mina, escavação", "tuk- + -ia"),
]

# ---------------------------------------------------------------------------
# 4. NOVOS ADJETIVOS (forma -a; superlativo regular em -n como lota -> lotan)
# ---------------------------------------------------------------------------
NEW_ADJECTIVES = [
    ("xela", "nevado, coberto de neve", "maer xela", "xelan"),
    ("nyka", "aberto", "maer nyka", "nykan"),
    ("anyka", "fechado, trancado", "maer anyka", "anykan"),
    ("kraza", "alegre, risonho", "maer kraza", "krazan"),
    ("akraza", "choroso, triste", "maer akraza", "akrazan"),
    ("lyra", "esperançoso", "maer lyra", "lyran"),
    ("lixa", "limpo, lavado", "maer lixa", "lixan"),
    ("alixa", "sujo, maculado", "maer alixa", "alixan"),
    ("peka", "quebrado, partido", "maer peka", "pekan"),
    ("apeka", "consertado, inteiro", "maer apeka", "apekan"),
    ("maka", "saciado, bem alimentado", "maer maka", "makan"),
    ("amaka", "faminto", "maer amaka", "amakan"),
    ("fala", "sonolento", "maer fala", "falan"),
    ("zala", "pago, quite", "maer zala", "zalan"),
    ("azala", "devedor, em dívida", "maer azala", "azalan"),
    ("ruxa", "cozido, assado", "maer ruxa", "ruxan"),
    ("aruxa", "cru", "maer aruxa", "aruxan"),
    ("huxa", "vestido, agasalhado", "maer huxa", "huxan"),
    ("nirlana", "lunar, enluarado", "maer nirlana", "nirlanan"),
    ("tonkrila", "breve, momentâneo", "maer tonkrila", "tonkrilan"),
    ("habа", "hospitaleiro", "maer haba", "haban"),
]
NEW_ADJECTIVES = [(a.replace("а", "a"), m, c, s) for a, m, c, s in NEW_ADJECTIVES]  # saneamento de grafema

# ---------------------------------------------------------------------------
# 5. NOVOS ADVÉRBIOS (-vë) E PARTÍCULAS INTERROGATIVAS
# ---------------------------------------------------------------------------
NEW_ADVERBS = [
    ("krazavë", "Modal de Alegria", "kraza + -vë", "alegremente, com riso"),
    ("lyravë", "Modal de Esperança", "lyra + -vë", "esperançosamente"),
    ("habavë", "Modal de Hospitalidade", "haba + -vë", "hospitaleiramente"),
    ("tonkrilavë", "Modal Temporal", "tonkrila + -vë", "brevemente, num instante"),
    ("xelavë", "Modal de Clima", "xela + -vë", "sob neve, nevadamente"),
    ("kemyga", "Interrogativo de Quantidade", "ke + myga", "quanto? quantos? (kemyga paror esu? = quanto custa?)"),
    ("kebel", "Interrogativo Temporal", "ke + bel", "quando? em que dia?"),
    ("kemixi", "Interrogativo Pessoal", "ke + mixi", "quem?"),
    ("kesan", "Interrogativo Neutro", "ke + san", "o quê? que coisa?"),
]

FORBIDDEN_CLUSTERS = re.compile(r"rn|nl|nr|dt|kt|pg|tk|ds|zr|mr|sr|ln")
PURGADOS = {"mandur", "bibur", "panna", "broda", "karna", "kamin", "husa", "stuba",
            "amiko", "kastar", "kanis", "post", "kanto", "kardi"}


def literal(t):
    return "    (" + ", ".join(repr(x) if isinstance(x, str) else str(x) for x in t) + "),\n"


def inject(src, header, entries, label):
    start = src.index(header)
    end = src.index("\n]\n", start)
    block = f"    # --- Expansão Eufônica V8.1 ({label}) ---\n" + "".join(literal(e) for e in entries)
    return src[:end + 1] + block + src[end + 1:]


def main():
    with open(GEN, "r", encoding="utf-8") as f:
        src = f.read()

    if "Expansão Eufônica V8.1" in src:
        print("Expansão já aplicada; nada a fazer.")
        return

    for old, new in RETIFICACOES:
        if old not in src:
            print("AVISO: alvo de retificação não encontrado:", old[:60])
        src = src.replace(old, new)

    existing = set(re.findall(r'^\s*\("([^"]+)",', src, flags=re.M))
    for group in (NEW_NOUNS, NEW_ADJECTIVES, NEW_VERB_ROOTS, NEW_ADVERBS):
        dups = [e[0] for e in group if e[0] in existing]
        if dups:
            sys.exit(f"Duplicatas detectadas: {dups}")
    new_lemmas = [e[0] for g in (NEW_NOUNS, NEW_ADJECTIVES, NEW_VERB_ROOTS, NEW_ADVERBS) for e in g]
    viol = [w for w in new_lemmas if FORBIDDEN_CLUSTERS.search(w.lower())]
    if viol:
        sys.exit(f"Encontros proibidos nos novos lemas: {viol}")
    if PURGADOS & set(new_lemmas):
        sys.exit("Termo expurgado reintroduzido!")

    src = inject(src, "NOUNS = [", NEW_NOUNS, "substantivos")
    src = inject(src, "ADJECTIVES = [", NEW_ADJECTIVES, "adjetivos")
    src = inject(src, "VERB_ROOTS = [", NEW_VERB_ROOTS, "raízes verbais")
    src = inject(src, "ADVERBS = [", NEW_ADVERBS, "advérbios e interrogativos")

    with open(GEN, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"Injetados: {len(NEW_NOUNS)} substantivos, {len(NEW_ADJECTIVES)} adjetivos, "
          f"{len(NEW_VERB_ROOTS)} raízes verbais ({len(NEW_VERB_ROOTS)*4} verbos), {len(NEW_ADVERBS)} advérbios.")


if __name__ == "__main__":
    main()
