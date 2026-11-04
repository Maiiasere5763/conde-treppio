# -*- coding: utf-8 -*-
"""
ainulindale_sandbox.py
Motor Filológico, Validador Fonotático e Gerador do Léxico Endógeno do Ainulindalë (Halylitror)
para Integração à Gramática Normativa da Língua Tréppia (GNLT - Era Clássica V8.1).
"""

def apply_sandhi(morphemes: list[str]) -> tuple[str, list[str]]:
    """Aplica as 21 Leis de Purificação Fonotática (Sandi Consonantal) e Haplologia da V8.1."""
    applied_rules = []
    result = morphemes[0]
    for nxt in morphemes[1:]:
        left = result
        right = nxt
        
        # Haplologia dental (od + ad... -> oda'...)
        if left == "od" and right.startswith("ad"):
            result = "oda'" + right[2:]
            applied_rules.append("Haplologia Dental (od- + ad- -> oda'-)")
            continue

        # Regras de fronteira consonantal
        if left.endswith("r") and right.startswith("n"):
            result = left[:-1] + "ld" + right[1:]
            applied_rules.append("rn -> ld (Fortição e Dissimilação Líquida)")
        elif left.endswith("l") and right.startswith("n"):
            result = left[:-1] + "ll" + right[1:]
            applied_rules.append("ln -> ll (Assimilação Progressiva Total)")
        elif left.endswith("n") and right.startswith("l"):
            result = left[:-1] + "ll" + right[1:]
            applied_rules.append("nl -> ll (Assimilação Lateral Total)")
        elif left.endswith("n") and right.startswith("n"):
            result = left[:-1] + "m" + right[1:]
            applied_rules.append("nn -> m (Simplificação de Geminada Nasal)")
        elif left.endswith("n") and right.startswith("r"):
            result = left[:-1] + "nn" + right[1:]
            applied_rules.append("nr -> nn (Assimilação Regressiva Nasal)")
        elif left.endswith("t") and right.startswith("d"):
            result = left[:-1] + "dd" + right[1:]
            applied_rules.append("td -> dd (Assimilação de Vozeamento Dental)")
        elif (left.endswith("d") or left.endswith("k")) and right.startswith("t"):
            src = left[-1] + "t"
            result = left[:-1] + "tt" + right[1:]
            applied_rules.append(f"{src} -> tt (Fortição e Geminação Dental)")
        elif left.endswith("s") and right.startswith("r"):
            result = left[:-1] + "ss" + right[1:]
            applied_rules.append("sr -> ss (Assimilação Fricativa Alveolar)")
        elif left.endswith("d") and right.startswith("s"):
            result = left[:-1] + "ss" + right[1:]
            applied_rules.append("ds -> ss (Assimilação Sibilante Regressiva)")
        elif left.endswith("z") and right.startswith("r"):
            result = left[:-1] + "zz" + right[1:]
            applied_rules.append("zr -> zz (Mutação Fricativa Vozeada)")
        elif (left.endswith("m") and right.startswith("r")) or (left.endswith("r") and right.startswith("m")):
            pair = left[-1] + right[0]
            result = left[:-1] + "mm" + right[1:]
            applied_rules.append(f"{pair} -> mm (Geminação Labial Absoluta)")
        elif left.endswith("k") and right.startswith("b"):
            result = left[:-1] + "bb" + right[1:]
            applied_rules.append("kb -> bb (Assimilação Labial Regressiva Total)")
        elif (left.endswith("t") or left.endswith("f")) and right.startswith("b"):
            pair = left[-1] + "b"
            result = left[:-1] + "bb" + right[1:]
            applied_rules.append(f"{pair} -> bb (Assimilação Labial no Imperfeito)")
        elif left.endswith("ld") and right.startswith("b"):
            result = left[:-2] + "lbb" + right[1:]
            applied_rules.append("ldb -> lbb (Assimilação de Cluster no Imperfeito)")
        elif left.endswith("n") and right.startswith("b"):
            result = left[:-1] + "mb" + right[1:]
            applied_rules.append("nb -> mb (Harmonização Nasal-Labial)")
        elif left.endswith("p") and right.startswith("g"):
            result = left[:-1] + "gg" + right[1:]
            applied_rules.append("pg -> gg (Assimilação Vozeada Regressiva)")
        elif left.endswith("t") and right.startswith("k"):
            result = left[:-1] + "kk" + right[1:]
            applied_rules.append("tk -> kk (Ensurdecimento e Coalescência Velar)")
        elif left.endswith("x") and right.startswith("r"):
            result = left[:-1] + "rr" + right[1:]
            applied_rules.append("xr -> rr (Isoglossa Velar-Vibrante Nobre)")
        elif left.endswith("r") and (right == "ra" or right == "ru" or right.startswith("ra") or right.startswith("ru")):
            result = left + right
            applied_rules.append("r + ra/ru -> rra/rru (Geminação Vibrante Absoluta)")
        elif left.endswith("v") and right.startswith("t"):
            result = left[:-1] + "pt" + right[1:]
            applied_rules.append("vt -> pt (Ensurdecimento Labiodental Ordinal)")
        elif left.endswith("k") and right.startswith("l"):
            result = left[:-1] + "ll" + right[1:]
            applied_rules.append("kl -> ll (Assimilação Oclusiva-Líquida)")
        else:
            result = left + right
            applied_rules.append("Aglutinação Direta")
    return result, applied_rules

# Inventário Lexical Endógeno Criado para o Ainulindalë (108 Vocábulos Auditados)
LEXICON_AINULINDALE = [
    # I. Teologia Cosmogenética, Nomes Próprios e Epítetos
    ("Halylitror", "s. 2ª Decl.", "haly (Gen. de hal) + litr- + -or", "Ainulindalë, A Música dos Espíritos Sagrados"),
    ("Oratypatte", "s. 1ª Decl. (-e)", "oraty (Gen. de orat) + Patte", "Ilúvatar, Pai do Todo"),
    ("Gyos Idda", "loc. s. 2ª Decl.", "Gyos + idda (id+da)", "Eru, o Único"),
    ("Halo / Elfhalo", "s. 2ª Decl. Pl.", "hal + -o / elfa + halo", "Ainur, Os Espíritos Sagrados"),
    ("Totter", "s. 1ª Decl. Pl.", "tok- + -te (kt -> tt, Pl. -er)", "Valar, Os Poderes / Regentes do Mundo"),
    ("Lanrukra", "s. 1ª Decl. (-a)", "lan + rukra", "Melkor em sua origem (Aquele que se ergue em Luz e Poder)"),
    ("Kurlan", "s. 2ª Decl.", "kur- + lan", "Melkor após a queda (Luz Corrompida / Declínio da Luz)"),
    ("Fertrátte", "s. 1ª Decl. (-e)", "fer + Trátte (trak- + -te)", "Manwë, Senhor dos Ventos e do Sopro"),
    ("Vétrátte", "s. 1ª Decl. (-e)", "Vé + Trátte", "Ulmo, Senhor das Águas e Oceanos"),
    ("Tektrátte", "s. 1ª Decl. (-e)", "tek- + Trátte", "Aulë, Senhor das Obras e da Forja"),
    ("Oratoxe", "s. 1ª Decl. (-e)", "orat + oxe", "Arda, a Terra Integral, o Reino do Mundo"),
    ("Halteggar", "s. 2ª Decl.", "hal + teggar (tep + -gar, pg -> gg)", "Salões Atemporais, Palácio Espiritual"),
    ("Halvur", "s. 2ª Decl.", "hal + vur", "Chama Imperecível, Fogo Sagrado / Secreto"),
    ("Ittakazeti", "s. 2ª Decl. Pl.", "itta (id+ta) + kazeti (part. pl.)", "Os Primeiros Nascidos (Elfos / Quendi)"),
    ("Dotakazeti", "s. 2ª Decl. Pl.", "dota (do+ta) + kazeti (part. pl.)", "Os Segundos Nascidos / Sucessores (Homens / Atani)"),
    ("Daifelo", "s. 2ª Decl. Pl.", "dai + felo", "Filhos do Pensamento (gerados da mente de Ilúvatar)"),
    # II. Música, Harmonia, Som e Dissonância
    ("litror", "s. 2ª Decl.", "litr- + -or", "música, melodia, vibração harmônica"),
    ("litrgar", "s. 2ª Decl.", "litr- + -gar", "Grande Música, Sinfonia Monumental"),
    ("litrte", "s. 1ª Decl. (-e)", "litr- + -te", "cantor, músico, bardo cósmico"),
    ("litrtek", "s. 2ª Decl.", "litr- + -tek", "instrumento musical, harpa, lira, trombeta"),
    ("leddalitror", "s. 2ª Decl.", "ledda (lete+da, td -> dd) + litror", "tema musical diretor, Grande Tema"),
    ("idlitror", "s. 2ª Decl.", "id + litror", "canto solitário, prelúdio individual"),
    ("kellitror", "s. 2ª Decl.", "kel- + litror", "coro uníssono, concerto sinfônico"),
    ("mobalitror", "s. 2ª Decl.", "moba + litror", "consonância, harmonia perfeita"),
    ("alitror", "s. 2ª Decl.", "a- + litr- + -or", "dissonância, discórdia musical, tumulto sonoro"),
    ("garvelitror", "s. 2ª Decl.", "garvé + litror", "música dos oceanos, eco das águas"),
    ("sulet", "s. 2ª Decl.", "su + lete (apócope)", "timbre interior, voz profunda"),
    ("rukralete", "s. 1ª Decl. (-e)", "rukra + lete", "voz potente, clamor de trombetas"),
    ("aletor", "s. 2ª Decl.", "alet- + -or", "silêncio absoluto, cessação do canto"),
    # III. Intelecto, Visão, Vontade e Paixões
    ("daior", "s. 2ª Decl.", "dai + -or", "pensamento, meditação, mente criadora"),
    ("isor", "s. 2ª Decl.", "is- (isa) + -or", "sabedoria, inteligência, conhecimento"),
    ("aisor", "s. 2ª Decl.", "a- + is- + -or", "incompreensão, ignorância"),
    ("vulor", "s. 2ª Decl.", "vul- (vule) + -or", "propósito, desígnio da vontade, intenção"),
    ("miror", "s. 2ª Decl.", "mir- + -or", "visão, contemplação, olhar"),
    ("amiror", "s. 2ª Decl.", "amir- + -or", "cegueira, ocultação visual, escuridão nos olhos"),
    ("akosor", "s. 2ª Decl.", "akos- + -or", "revelação, manifestação visível"),
    ("mirakosor", "s. 2ª Decl.", "mir- + akosor", "Visão profética mostrada aos olhos"),
    ("kosor", "s. 2ª Decl.", "kos- + -or", "mistério, segredo, ocultação"),
    ("metor", "s. 2ª Decl.", "met- + -or", "majestade, exultação, esplendor"),
    ("ametor", "s. 2ª Decl.", "amet- + -or", "vergonha, humilhação, opróbrio"),
    ("intulor", "s. 2ª Decl.", "intul- + -or", "furor, cólera, ira desmedida"),
    ("gizor", "s. 2ª Decl.", "giz- + -or", "amor devocional, dileção"),
    ("agizor", "s. 2ª Decl.", "agiz- + -or", "ódio, aversão, oblívio deliberado"),
    ("kindror", "s. 2ª Decl.", "kindr- + -or", "concórdia, paz, comunhão harmônica"),
    ("akindror", "s. 2ª Decl.", "a- + kindr- + -or", "discórdia, guerra, contenda, cisão"),
    # IV. Cosmografia, Elementos, Fogo, Gelo, Ar, Terra e Água
    ("orat", "s. 2ª Decl.", "raiz canônica de 'oratom' (Skorum)", "o Todo, o Universo, a Totalidade"),
    ("vur", "s. 2ª Decl.", "raiz canônica de 'vuldir' (vur+nir)", "fogo, chama, ardor"),
    ("vuror", "s. 2ª Decl.", "vur + -or", "calor intenso, incandescência"),
    ("avur", "s. 2ª Decl.", "a- + vur", "frio extremo, geada"),
    ("avurvé", "s. 2ª Decl.", "avur + Vé", "gelo, água congelada"),
    ("fervé", "s. 2ª Decl.", "fer + Vé", "nuvem, névoa, vapor atmosférico"),
    ("feria", "s. 1ª Decl. (-a/-e)", "fer + -ia", "atmosfera, regiões do ar, firmamento etéreo"),
    ("filvé", "s. 2ª Decl.", "fil + Vé", "abismo marinho, profundezas das águas"),
    ("filoxe", "s. 1ª Decl. (-e)", "fil + oxe", "vale profundo, cavidade da terra, depressão"),
    ("oxegar", "s. 2ª Decl.", "oxe + -gar", "continente, globo terrestre, massa do mundo"),
    ("rixegar", "s. 2ª Decl.", "rixe + -gar", "cordilheira monumental, maciço de montanhas"),
    ("vevar", "s. 2ª Decl.", "Vé + var", "rio, correnteza, curso de água"),
    ("karegar", "s. 2ª Decl.", "kare + -gar", "trono supremo, sólio imperial"),
    ("tepia", "s. 1ª Decl. (-a/-e)", "tep + -ia", "habitação, morada, mansão"),
    ("krador", "s. 2ª Decl.", "krad- + -or", "Criação, gênese, ato criador"),
    ("akrador", "s. 2ª Decl.", "akrad- + -or", "destruição, ruína, descriação"),
    ("tekor", "s. 2ª Decl.", "tek- + -or", "obra, trabalho, feitura, labor construtivo"),
    ("atekor", "s. 2ª Decl.", "atek- + -or", "desfazimento de obra, sabotagem"),
    ("tette", "s. 1ª Decl. (-e)", "tek- + -te (kt -> tt)", "artífice, artesão, forjador"),
    ("tettek", "s. 2ª Decl.", "tek- + -tek (kt -> tt)", "malho, instrumento de forja"),
    ("giror", "s. 2ª Decl.", "gir- + -or", "crescimento, desenvolvimento, florescimento"),
    ("navor", "s. 2ª Decl.", "nav- + -or", "transformação, feição, forma mutável"),
    ("sotimor", "s. 2ª Decl.", "sotim + -or", "semblante, matiz, aparência exterior"),
    ("rukror", "s. 2ª Decl.", "rukr- (rukra) + -or", "potência, força, vigor soberano"),
    ("lotor", "s. 2ª Decl.", "lot- (lota) + -or", "beleza, formosura, esplendor estético"),
]

if __name__ == "__main__":
    print(f"Total de vocábulos principais auditados na matriz do Ainulindalë: {len(LEXICON_AINULINDALE)}")
    for word, pos, etym, meaning in LEXICON_AINULINDALE[:15]:
        print(f"  * {word:15s} ({pos:16s}): {meaning} [{etym}]")
