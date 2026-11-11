import re

def extract_gnlt_payload(root_dir: str) -> dict:
    """Extrai e compila a Gramática Normativa da Língua Tréppia (Base e V8.1)."""
    import html, re
    base_path = os.path.join(root_dir, "gramatica_normativa_base.md")
    v81_path = os.path.join(root_dir, "adendo_edicao_unificada_v8_1.md")
    
    with open(base_path, "r", encoding="utf-8") as f:
        t_base = f.read()
    with open(v81_path, "r", encoding="utf-8") as f:
        t_v81 = f.read()

    def format_inline(txt: str) -> str:
        txt = html.escape(txt)
        txt = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", txt)
        txt = re.sub(r"\*(.+?)\*", r"<em>\1</em>", txt)
        txt = re.sub(r"`(.+?)`", r'<code class="treppio-code">\1</code>', txt)
        return txt

    def render_table(rows):
        if not rows:
            return ""
        html_parts = ['<div class="data-table-wrapper"><table class="data-table">']
        header_done = False
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if len(cells) > 0 and all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue
            if not header_done:
                html_parts.append("<thead><tr>" + "".join(f"<th>{format_inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                header_done = True
            else:
                html_parts.append("<tr>" + "".join(f"<td>{format_inline(c)}</td>" for c in cells) + "</tr>")
        if header_done:
            html_parts.append("</tbody>")
        html_parts.append("</table></div>")
        return "\n".join(html_parts)

    def md_to_html(md_text: str) -> str:
        lines = md_text.strip().split("\n")
        out = []
        in_table = False
        table_rows = []
        in_list = False
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("|") and line_str.endswith("|"):
                if in_list:
                    out.append("</ul>")
                    in_list = False
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(line_str)
                continue
            elif in_table:
                out.append(render_table(table_rows))
                in_table = False
                table_rows = []

            if line_str.startswith("- ") or line_str.startswith("* "):
                if not in_list:
                    in_list = True
                    out.append('<ul class="gnlt-list">')
                out.append(f"<li>{format_inline(line_str[2:].strip())}</li>")
                continue
            elif in_list:
                out.append("</ul>")
                in_list = False

            if not line_str:
                continue

            if line_str.startswith("### "):
                out.append(f'<h3 class="gnlt-h3">{format_inline(line_str[4:])}</h3>')
            elif line_str.startswith("#### "):
                out.append(f'<h4 class="gnlt-h4">{format_inline(line_str[5:])}</h4>')
            elif line_str.startswith("> "):
                out.append(f'<blockquote class="gnlt-quote">{format_inline(line_str[2:])}</blockquote>')
            elif line_str.startswith("---"):
                out.append('<hr class="gnlt-divider" />')
            else:
                out.append(f'<p class="gnlt-p">{format_inline(line_str)}</p>')

        if in_table:
            out.append(render_table(table_rows))
        if in_list:
            out.append("</ul>")
        return "\n".join(out)

    def parse_file(content):
        raw_blocks = re.split(r"\n(?=## \d+\. )", content)
        intro = raw_blocks[0].strip()
        chapters = []
        for b in raw_blocks[1:]:
            lines = b.strip().split("\n")
            header = lines[0].replace("## ", "").strip()
            num_match = re.match(r"^(\d+)\.\s*(.*)", header)
            num = int(num_match.group(1)) if num_match else len(chapters) + 1
            title = num_match.group(2) if num_match else header
            full_md = "\n".join(lines[1:]).strip()
            chapters.append({
                "num": num,
                "title": title,
                "md": full_md,
                "html": md_to_html(full_md)
            })
        return intro, chapters

    intro_base, chs_base = parse_file(t_base)
    intro_v81, chs_v81 = parse_file(t_v81)

    unified_chapters = []
    for c1, c2 in zip(chs_base, chs_v81):
        unified_chapters.append({
            "num": c1["num"],
            "title": c2["title"] if c2["title"] else c1["title"],
            "base_md": c1["md"],
            "v81_md": c2["md"],
            "base_html": c1["html"],
            "v81_html": c2["html"]
        })

    return {
        "title": "Gramática Normativa da Língua Tréppia (GNLT)",
        "subtitulo": "Cânone Gramatical da Era Clássica V8.1 | Chancelaria Imperial",
        "intro_base": intro_base,
        "intro_v81": intro_v81,
        "capitulos": unified_chapters
    }

# -*- coding: utf-8 -*-
r"""
gerador_dicionario_integral_sandbox.py
Compilador e Gerador Morfofonológico Exaustivo do Dicionário Geral da Língua Tréppia (Era Clássica V8.1)
Opera estritamente em ambiente de Sandbox (D:\Conde_Treppio\sandbox\).
Transforma cada verbete existente em todas as suas terminações flexionais e derivacionais possíveis,
aplicando rigorosamente as 21 Leis de Sandi Consonantal, Haplologia e Reforma Vocalizada do Dativo.
"""

import os
import json

# ==============================================================================
# 1. MOTOR MORFOFONOLÓGICO (21 LEIS DE SANDI CONSONANTAL + HAPLOLOGIA V8.1)
# ==============================================================================

def join_morphemes(left: str, right: str) -> str:
    """Une dois morfemas aplicando todas as leis de sandi consonantal e haplologia da V8.1."""
    if not left:
        return right
    if not right:
        return left

    # Remover acento agudo de Vé quando aglutinado no interior de composto
    if left == "Vé" and right not in ("y", "i", "om", "o", "ye", "oi", "os"):
        left_clean = "ve"
    else:
        left_clean = left

    # Haplologia dental (od + ad... -> oda'...)
    if left_clean == "od" and right.startswith("ad"):
        return "oda'" + right[2:]

    # Se left termina em vogal e right começa em vogal (elidir vogal temática -e/-a diante de sufixo vocálico)
    if left_clean[-1] in "ae" and right[0] in "aeiouy":
        left_stem = left_clean[:-1]
    else:
        left_stem = left_clean

    if not left_stem:
        return right

    # Regras de Sandi Consonantal na fronteira left_stem + right
    # 1. rn -> ld
    if left_stem.endswith("r") and right.startswith("n"):
        return left_stem[:-1] + "ld" + right[1:]
    # 2. ln -> ll
    if left_stem.endswith("l") and right.startswith("n"):
        return left_stem[:-1] + "ll" + right[1:]
    # 3. nl -> ll
    if left_stem.endswith("n") and right.startswith("l"):
        return left_stem[:-1] + "ll" + right[1:]
    # 4. nn / mn / nm -> m
    if left_stem.endswith("mn") and right.startswith("n"):
        return left_stem[:-2] + "m" + right[1:]
    if left_stem.endswith("n") and right.startswith("n"):
        return left_stem[:-1] + "m" + right[1:]
    # 5. nr -> nn
    if left_stem.endswith("n") and right.startswith("r"):
        return left_stem[:-1] + "nn" + right[1:]
    # 6. td -> dd
    if left_stem.endswith("t") and right.startswith("d"):
        return left_stem[:-1] + "dd" + right[1:]
    # 7. dt / kt -> tt
    if (left_stem.endswith("d") or left_stem.endswith("k")) and right.startswith("t"):
        return left_stem[:-1] + "tt" + right[1:]
    # 8. sr -> ss
    if left_stem.endswith("s") and right.startswith("r"):
        return left_stem[:-1] + "ss" + right[1:]
    # 9. ds -> ss
    if left_stem.endswith("d") and right.startswith("s"):
        return left_stem[:-1] + "ss" + right[1:]
    # 10. zr -> zz
    if left_stem.endswith("z") and right.startswith("r"):
        return left_stem[:-1] + "zz" + right[1:]
    # 11. mr / rm -> mm
    if (left_stem.endswith("m") and right.startswith("r")) or (left_stem.endswith("r") and right.startswith("m")):
        return left_stem[:-1] + "mm" + right[1:]
    # 12. ldb -> lbb
    if left_stem.endswith("ld") and right.startswith("b"):
        return left_stem[:-2] + "lbb" + right[1:]
    # 13. kb / tb / fb -> bb
    if (left_stem.endswith("k") or left_stem.endswith("t") or left_stem.endswith("f")) and right.startswith("b"):
        return left_stem[:-1] + "bb" + right[1:]
    # 14. nb -> mb
    if left_stem.endswith("n") and right.startswith("b"):
        return left_stem[:-1] + "mb" + right[1:]
    # 15. pg -> gg
    if left_stem.endswith("p") and right.startswith("g"):
        return left_stem[:-1] + "gg" + right[1:]
    # 16. tk -> kk
    if left_stem.endswith("t") and right.startswith("k"):
        return left_stem[:-1] + "kk" + right[1:]
    # 17. xr -> rr
    if left_stem.endswith("x") and right.startswith("r"):
        return left_stem[:-1] + "rr" + right[1:]
    # 18. r + ra/ru -> rra/rru
    if left_stem.endswith("r") and (right.startswith("ra") or right.startswith("ru")):
        return left_stem + right
    # 19. vt -> pt
    if left_stem.endswith("v") and right.startswith("t"):
        return left_stem[:-1] + "pt" + right[1:]
    # 20. kl -> ll
    if left_stem.endswith("k") and right.startswith("l"):
        return left_stem[:-1] + "ll" + right[1:]
    # 21. ss -> ç (em fronteira morfológica interna)
    if left_stem.endswith("s") and right.startswith("s"):
        return left_stem[:-1] + "ss" + right[1:]
    # 22. bp -> bb
    if left_stem.endswith("b") and right.startswith("p"):
        return left_stem[:-1] + "bb" + right[1:]

    return left_stem + right


def decline_noun(lemma: str, decl: int) -> dict[str, str]:
    """Declina um substantivo nos 8 casos/números canônicos e gera suas derivações sufixais."""
    if decl == 1:
        # 1ª Declinação: Temas em -e (ou -a/-i) e variantes tônicas (-é/-ë)
        if lemma.endswith("e") or lemma.endswith("a") or lemma.endswith("é") or lemma.endswith("ë"):
            stem = lemma[:-1]
            v = "e" if lemma[-1] in ("e", "é", "ë") else lemma[-1]
        else:
            stem = lemma
            v = "e"
        cases = {
            "Nom.Sg": lemma,
            "Gen.Sg": f"{stem}{v}dy",
            "Dat.Sg": f"{stem}{v}j",
            "Acu.Sg": f"{stem}{v}m",
            "Nom.Pl": f"{stem}{v}r",
            "Gen.Pl": f"{stem}{v}dye",
            "Dat.Pl": f"{stem}{v}rj",
            "Acu.Pl": f"{stem}{v}s",
        }
        base_stem = stem
    else:
        # 2ª Declinação: Temas Consonantais (Reforma Vocalizada do Dativo V8.1: -i / -oi)
        stem = lemma
        # Subgrupo Dai: dai -> dao, daoi, daos
        if lemma == "dai":
            cases = {
                "Nom.Sg": "dai",
                "Gen.Sg": "daiy",
                "Dat.Sg": "daii",
                "Acu.Sg": "daiom",
                "Nom.Pl": "dao",
                "Gen.Pl": "daiye",
                "Dat.Pl": "daoi",
                "Acu.Pl": "daos",
            }
        elif lemma.endswith("ti") or lemma.endswith("ro") or lemma.endswith("lo") or lemma.endswith("oi"):
            # Formas já plurais coletivas (ex.: Halo, Ittakazeti, Dotakazeti, Rukroro, kuroi)
            b = lemma[:-2] if lemma.endswith("ti") else lemma[:-1]
            if lemma.endswith("ti"):
                # Particípio plural em -eti (Nom.Sg -et)
                s = lemma[:-1]
                cases = {
                    "Nom.Sg": s,
                    "Gen.Sg": f"{s}y",
                    "Dat.Sg": f"{s}i",
                    "Acu.Sg": f"{s}om",
                    "Nom.Pl": lemma,
                    "Gen.Pl": f"{s}ye",
                    "Dat.Pl": f"{s}oi",
                    "Acu.Pl": f"{s}os",
                }
            else:
                cases = {
                    "Nom.Sg": b,
                    "Gen.Sg": f"{b}y",
                    "Dat.Sg": f"{b}i",
                    "Acu.Sg": f"{b}om",
                    "Nom.Pl": f"{b}o",
                    "Gen.Pl": f"{b}ye",
                    "Dat.Pl": f"{b}oi",
                    "Acu.Pl": f"{b}os",
                }
        else:
            cases = {
                "Nom.Sg": stem,
                "Gen.Sg": f"{stem}y",
                "Dat.Sg": f"{stem}i",
                "Acu.Sg": f"{stem}om",
                "Nom.Pl": f"{stem}o",
                "Gen.Pl": f"{stem}ye",
                "Dat.Pl": f"{stem}oi",
                "Acu.Pl": f"{stem}os",
            }
        base_stem = stem

    # Transformações Derivacionais Potenciais do Radical Nominal
    clean_root = "v" if lemma.lower() in ("vé", "ve") else base_stem.replace("vé", "v").lower()
    if lemma in ("fea", "le"):
        clean_root = lemma
    elif clean_root.endswith("e") or clean_root.endswith("a"):
        clean_root = clean_root[:-1]

    ag_form = lemma if (lemma.endswith("te") or lemma.endswith("tte")) else join_morphemes(clean_root, "te")
    inst_form = lemma if lemma.endswith("tek") else join_morphemes(clean_root.rstrip("t") if clean_root.endswith("tt") else clean_root, "tek")
    lug_form = lemma if lemma.endswith("ia") else f"{clean_root}ia"
    abst_form = lemma if clean_root.endswith("or") else f"{clean_root}or"
    dim_form = lemma if clean_root.endswith("il") else f"{clean_root}il"
    aum_form = lemma if clean_root.endswith("gar") else join_morphemes(clean_root, "gar")
    adj_form = "va" if lemma == "Vé" else (lemma if lemma.endswith("a") else f"{clean_root}a")
    adv_form = "vavë" if lemma == "Vé" else f"{adj_form}vë"

    derivations = {
        "Adj(-a)": adj_form,
        "Adv(-vë)": adv_form,
        "Superl.Sg(-n)": join_morphemes(clean_root, "n"),
        "Superl.Pl(-ni)": join_morphemes(clean_root, "ni"),
        "Lugar(-ia)": lug_form,
        "Agente(-te)": ag_form,
        "Abstrato(-or)": abst_form,
        "Instrum(-tek)": inst_form,
        "Dimin(-il)": dim_form,
        "Aument(-gar)": aum_form,
    }
    return {**cases, **derivations}


def inflect_adjective(adj: str, meaning: str, comp: str = "", superl_override: str = "") -> dict[str, str]:
    """Transforma um adjetivo em todos os seus graus, advérbio modal (-vë) e declinação nominalizada."""
    stem = adj[:-1] if (adj.endswith("a") or adj.endswith("e")) else adj
    superl_sg = superl_override if superl_override else join_morphemes(stem, "n")
    superl_pl = f"{superl_sg}i" if not superl_sg.endswith("i") else superl_sg
    comparative = comp if comp else f"maer {adj}"
    adv = f"{adj}vë" if adj.endswith("a") else f"{stem}avë"
    abstr = f"{stem}or"
    verb_fact = f"in{stem}ur" if not stem.startswith("l") else f"il{stem}ur"
    return {
        "Positivo.Sg": adj,
        "Gen.Sg": f"{adj}dy" if adj.endswith("a") or adj.endswith("e") else f"{adj}y",
        "Dat.Sg": f"{adj}j" if adj.endswith("a") or adj.endswith("e") else f"{adj}i",
        "Acu.Sg": f"{adj}m" if adj.endswith("a") or adj.endswith("e") else f"{adj}om",
        "Nom.Pl": f"{adj}r" if adj.endswith("a") or adj.endswith("e") else f"{adj}o",
        "Gen.Pl": f"{adj}dye" if adj.endswith("a") or adj.endswith("e") else f"{adj}ye",
        "Dat.Pl": f"{adj}rj" if adj.endswith("a") or adj.endswith("e") else f"{adj}oi",
        "Acu.Pl": f"{adj}s" if adj.endswith("a") or adj.endswith("e") else f"{adj}os",
        "Comparativo": comparative,
        "Superl.Sg(-n)": superl_sg,
        "Superl.Pl(-ni)": superl_pl,
        "Adv.Modal(-vë)": adv,
        "Subst.Abstrato(-or)": abstr,
        "Significado": meaning,
    }


def build_four_stems(pos_root: str) -> tuple[str, str, str, str]:
    """Projeta uma raiz verbal positiva nos 4 Estados Ontológicos da Matriz Quadripartite."""
    # 1. Estado Positivo
    s1 = pos_root
    # 2. Estado Privativo (a-)
    if pos_root.startswith("a"):
        s2 = pos_root
    else:
        s2 = "a" + pos_root
    # 3. Estado Iterativo (o- antes de consoante, od- antes de vogal)
    if pos_root[0] in "aeiouy":
        s3 = "od" + pos_root
    else:
        s3 = "o" + pos_root
    # 4. Estado Iterativo-Privativo (od- + privativo a-..., disparando haplologia dental se pos_root começa com d)
    if pos_root.startswith("d"):
        s4 = "oda'" + pos_root[1:]
    else:
        s4 = "od" + s2
    return s1, s2, s3, s4


def conjugate_stem_all_109(stem: str) -> dict[str, any]:
    """Gera todas as 109 formas flexionadas de um radical verbal (100 finitas + 1 inf + 8 part) + 4 derivados nominais."""
    persons = [("1Sg", "m"), ("2Sg", "s"), ("3Sg/Pl", ""), ("1Pl", "n"), ("2Pl", "t")]
    tenses = [
        ("Pres.Ind", "u"),
        ("Pres.Subj", "uke"),
        ("Pass.Ind", "ra"),
        ("Pass.Subj", "rake"),
        ("Dur.Ind", "ai"),
        ("Dur.Subj", "aike"),
        ("Fut.Ind", "ru"),
        ("Fut.Subj", "ruke"),
        ("Imperf.Ind", "ba"),
        ("Imperf.Subj", "bake"),
    ]
    forms = {}
    for t_name, t_suf in tenses:
        base_t = join_morphemes(stem, t_suf)
        act_list = []
        pas_list = []
        for p_name, p_suf in persons:
            act_form = base_t + p_suf
            pas_form = base_t + "se" + p_suf
            act_list.append(act_form)
            pas_list.append(pas_form)
        forms[f"{t_name}.Ativa"] = act_list
        forms[f"{t_name}.Passiva"] = pas_list

    # Formas Nominais e Imperativo
    inf = f"{stem}ur"
    imp = stem.capitalize() + "!"
    part_sg = f"{stem}et"
    part_cases = {
        "Nom.Sg": part_sg,
        "Gen.Sg": f"{part_sg}y",
        "Dat.Sg": f"{part_sg}i",
        "Acu.Sg": f"{part_sg}om",
        "Nom.Pl": f"{part_sg}i",
        "Gen.Pl": f"{part_sg}ye",
        "Dat.Pl": f"{part_sg}oi",
        "Acu.Pl": f"{part_sg}os",
    }
    # Interrogativo 2ª Pl Presente (tk -> kk)
    interrog_2pl = join_morphemes(f"{stem}ut", "ka") + "?"
    # Derivados Nominais do Verbo
    deriv = {
        "Agente(-te)": join_morphemes(stem, "te"),
        "Abstrato(-or)": f"{stem}or",
        "Instrum(-tek)": join_morphemes(stem, "tek"),
        "Lugar(-ia)": f"{stem}ia",
    }
    forms["Infinitivo(-ur)"] = inf
    forms["Imperativo(Raiz)"] = imp
    forms["Participio(8_Casos)"] = part_cases
    forms["Interrogativo.2Pl(-ka)"] = interrog_2pl
    forms["Derivados.Nominais"] = deriv
    return forms

print("Motor Morfofonológico carregado com sucesso.")

# ==============================================================================
# 2. INVENTÁRIO COMPLETO DE TODOS OS VERBETES EXISTENTES NO TRÉPPIO (V8.1)
# ==============================================================================

# 2.1. SUBSTANTIVOS, TOPÔNIMOS, CASAS NOBRES E TEÔNIMOS (Lema, Declinação [1 ou 2], Significado, Etimologia)
NOUNS = [
    # ==============================================================================
    # LÉXICO PRÁTICO E COTIDIANO: 1.500 ANOS DE EVOLUÇÃO (ERA ANTIGA -> ERA CLÁSSICA V8.1)
    # Desenvolvido nas montanhas, florestas de pinheiros e castelos boreais (Ecos de Uma Vida Perdida)
    # Rigorosamente estruturado a partir das raízes canônicas e morfologia do Tréppio
    # ==============================================================================
    # --- Saudações, Casa e Abrigo na Neve ---
    ("alen", 2, "saudação matinal, bom dia, claridade benfazeja", "al- (luz) + -en"),
    ("vesen", 2, "boa noite, repouso noturno da lareira", "ves- (noite) + -en"),
    ("mobalete", 1, "por favor, cortesia, palavra benevolente (fórmula de pedido)", "moba + lete"),
    ("hallen", 2, "gratidão, agradecimento, bênção recebida", "hal- (sagrado/luz) + -en"),
    ("nesor", 2, "lar, morada acolhedora, habitação familiar", "raiz nes- (ser/morar) + -or"),
    ("toret", 2, "teto, telhado de ardósia, abrigo contra a neve", "raiz tor- (cobrir/proteger) + -et"),
    ("rixtor", 2, "castelo de pedra, fortaleza montanhesa, torre de guarda", "rix- (rocha) + tor- (abrigo)"),
    ("vurtep", 2, "lareira de pedra, fogão a lenha, fogo central da morada", "vur (fogo) + tep (casa)"),
    ("vildor", 2, "brasa incandescente, carvão ardente da lareira", "vur- + dur- (operante), sandi rn->ld"),
    ("daktake", 1, "mesa de refeição maciça, bancada rústica de carvalho", "dak- (comer/refeição) + take (mesa)"),
    ("sektek", 2, "banco de madeira ou pedra, assento de espaldar alto", "sek- (assentar-se) + -tek (instrumento)"),
    ("nyketek", 2, "batente de porta espessa de carvalho, umbral fortificado", "nyke (porta) + -tek (estrutura)"),
    ("alfrin", 2, "janela de postigo, fresta de luz da cabana", "al- (luz) + frin- (abertura)"),
    ("kladdor", 2, "tranca de ferro, ferrolho de segurança contra o vento", "raiz klad- (fechar) + -or"),
    ("falet", 2, "leito macio, cama de palha e mantas de dormir", "raiz fal- (repousar) + -et"),
    ("kilttor", 2, "manta pesada de lã, cobertura grossa contra a geada", "kild- (frio) + tor- (cobrir), dt -> tt"),
    ("aldor", 2, "tocha de breu, archote de resina para iluminar o caminho", "raiz al- (luz) + -dor (instrumento)"),
    ("allin", 2, "lamparina de óleo, candeia modesta da cabeceira", "al- (luz) + -in (diminutivo)"),
    # --- Alimento, Bebida e a Mesa da Estalagem ---
    ("dakkor", 2, "alimento diário, refeição farta, sustento", "raiz dak- (consumir/alimentar) + -or"),
    ("oxedak", 2, "pão de centeio rústico, broa de pedra, cereal cozido", "oxe- (terra/cereal) + dak- (alimento)"),
    ("ruxvé", 1, "caldo quente, sopa nutritiva de raízes e legumes", "rux- (cozer) + Vé (água)"),
    ("luttor", 2, "carne assada na brasa, provisão de caça", "raiz lut- (caça/animal silvestre) + -or"),
    ("garvlut", 2, "peixe de rio gélido, pesca das montanhas", "garv- (água viva/rio) + lut- (pesca/caça)"),
    ("keldas", 2, "queijo curado de cabra das serras", "raiz keld- (coalhar/prensar) + -as"),
    ("garva", 1, "água pura potável, água fresca de degelo", "raiz garv- (fluir/nascente) + -a"),
    ("laural", 2, "cerveja encorpada escura, hidromel espesso da taberna", "laur- (dourado) + al- (cereal)"),
    ("garvok", 2, "caneca de cerâmica, taça de estanho da estalagem", "garv- (beber) + -ok (recipiente)"),
    ("dakil", 2, "tigela de madeira torneada, prato fundo de refeição", "dak- (comer) + -il (recipiente)"),
    ("verresaittek", 2, "faca afiada de mesa, punhal utilitário de caça", "verre (metal) + saittek (lâmina)"),
    ("kordaktek", 2, "colher de pau torneada, concha de sopa", "kor (madeira) + dak- (comer) + -tek"),
    ("garveoxe", 1, "sal marinho e de rocha, cristal para conservar carnes e queijos", "garvé (oceano) + oxe (terra/cristal)"),
    ("dakvul", 2, "fome, apetite voraz do viajante na nevasca", "dak- (comer) + vul- (desejo/anseio)"),
    ("garvvul", 2, "sede ardente, garganta seca pelo vento da serra", "garv- (beber) + vul- (desejo/anseio)"),
    ("vesdak", 2, "ceia noturna, refeição acolhedora ao pé da lareira", "ves- (noite) + dak- (refeição)"),
    # --- Clima, Natureza e Viagem nas Terras Boreais (Ecos) ---
    ("kildar", 2, "neve fresca acumulada, manto branco de inverno", "raiz kild- (frio/gelo) + -ar"),
    ("kildrix", 2, "gelo compacto, geada cortante, carâmbanos de pedra", "kild- (gelo) + rix- (pedra)"),
    ("veksun", 2, "nevoeiro denso, bruma fria que encobre caminhos", "raiz veks- (névoa/chuva) + -un"),
    ("filox", 2, "floresta de coníferas, bosque de pinheiros nevado", "fil- (árvore) + ox- (terra)"),
    ("drinet", 2, "pinheiro silvestre, conífera alta das encostas", "drin- (madeira/resina) + -et"),
    ("halkvar", 2, "estrada de pedra, trilha batida na neve, rota montanhesa", "halk- (caminhar) + var (caminho)"),
    ("rixtorr", 2, "ponte de pedra sobre o abismo ou rio torrentoso", "rix- (pedra) + torr- (passagem)"),
    ("halkoxe", 1, "pegada na neve fresca, rastro de viajante no solo", "halk- (passo) + oxe (chão/solo)"),
    ("alves", 2, "aurora boreal, claridade mística no céu nublado de inverno", "al- (luz) + ves- (noite)"),
    ("rixekade", 1, "montanha escarpada, cume rochoso coberto de gelo", "rixe (montanha/rocha) + kade (cume)"),
    ("kropefil", 2, "várzea abrigada entre serras, vale plano protegido", "krope (planície) + fil (depressão)"),
    # --- Companheirismo, Criaturas e Afeto (Ecos) ---
    ("sfarpoke", 1, "cão guardião leal, sabujo doméstico de guarda", "sfar- (guardar/proteger) + poke (animal)"),
    ("zenor", 2, "amigo fiel de travessia, companheiro leal de jornada", "raiz zen- (lealdade) + -or"),
    ("mald", 2, "cavalo de montaria e carga, corcel resistente à neve", "mar- (montaria) + -n, rn -> ld"),
    ("kindar", 2, "família da lareira, clã do abrigo doméstico", "raiz kind- (laço/pacto) + -ar"),
    ("odmad", 2, "avó, matriarca protetora do lar, guardiã da lareira", "od- (geração anterior) + mad (mãe)"),
    ("odpatte", 1, "avô, patriarca protetor do lar, chefe da morada", "od- (geração anterior) + Patte (pai)"),
    ("kradet", 2, "criança pequena, filho amado, rebento do lar", "raiz kradd- (nascer/gerar) + -et"),
    ("sukorfas", 2, "nostalgia profunda, pesadume no peito, saudade dos ecos do passado", "sukor (coração) + fas (dor)"),
    ("viltor", 2, "cura revigorante, alívio de dor e cansaço", "raiz vilt- (curar) + -or"),
    ("sukoror", 2, "coragem serena, firmeza de ânimo diante da tormenta", "sukor (coração) + -or (abstrato)"),
    # --- Forja, Ferramentas, Comércio e Armas ---
    ("gobbaror", 2, "preço justo acordado, cotação de troca em mercado", "gob- (negociar) + paror (preço), bp -> bb"),
    ("lanverril", 2, "moeda de prata cunhada, metal claro de troca comercial", "lan (claro/prata) + verril (moeda)"),
    ("lauren", 2, "moeda imperial de ouro, metal nobre de alto valor", "raiz laur- (ouro) + -en"),
    ("verretette", 1, "ferreiro da bigorna, mestre forjador de metal", "verre (metal) + Tette (artífice)"),
    ("durtek", 2, "martelo de ferreiro, marreta pesada de forja", "dur- (bater) + tek- (forja)"),
    ("sfammirgar", 2, "espadão de aço temperado, lâmina pesada de guarda", "sfammir (espada < sfar+mir) + -gar"),
    ("verresfartek", 2, "escudo reforçado com metal, broquel de proteção", "verre (metal) + sfartek (escudo)"),
    ("gobtepia", 1, "estalagem de beira de estrada, albergue de viajantes", "gob- (comércio) + tepia (morada)"),
    ("gobynte", 1, "mercador de caravana, negociante itinerante", "gob- (comerciar) + ynte (viajante)"),

    # --- Letra A ---
    ("aelfor", 2, "sacrilégio, profanação, mácula litúrgica", "aelf- + -or"),
    ("Agáltte", 1, "O Falso Pastor (exônimo erodido de Hal'gáltte)", "a- + gald- + -te (dt -> tt)"),
    ("agizor", 2, "ódio, aversão volitiva, oblívio deliberado", "agiz- + -or"),
    ("aisor", 2, "incompreensão, ignorância cognitiva", "a- + is- + -or"),
    ("akindror", 2, "discórdia, contenda, cisão, guerra cósmica", "a- + kindr- + -or"),
    ("akitia", 1, "tribunal de clemência, câmara de anistia", "akit- + -ia"),
    ("akitor", 2, "anistia imperial, indulto, remissão formal", "akit- + -or"),
    ("akitte", 1, "magistrado do perdão, censor cartorial", "akit- + -te"),
    ("akrador", 2, "destruição, ruína, descriação", "akrad- + -or"),
    ("akura", 1, "virgem, incorrupta, imaculada", "a- + kura"),
    ("aletor", 2, "silêncio absoluto, censura, cessação do som", "alet- + -or"),
    ("alitror", 2, "dissonância, discórdia musical, tumulto sonoro", "a- + litr- + -or"),
    ("Alvarok", 2, "Rito Escarlate, genocídio (exônimo de Tóldemme)", "Halyvar Voka erodido"),
    ("ametor", 2, "vergonha, humilhação, opróbrio", "amet- + -or"),
    ("amiror", 2, "cegueira física ou espiritual, treva nos olhos", "amir- + -or"),
    ("Aralani", 1, "Casa da Coroa (Grande Casa Imperial)", "ar- + lan-"),
    ("Arume", 1, "Império, domínio imperial supremo", "raiz arum-"),
    ("asfaror", 2, "aniquilação total, expurgo bélico, devastação", "asfar- + -or"),
    ("asfarte", 1, "destruidor, tropa de extermínio, aniquilador", "asfar- + -te"),
    ("askoror", 2, "apostasia, heresia, incredulidade", "askor- + -or"),
    ("askorte", 1, "apóstata, infiel, renegado", "askor- + -te"),
    ("atekor", 2, "desfazimento de obra, sabotagem, ruína", "atek- + -or"),
    ("atokor", 2, "anarquia, sedição, crise de desgoverno", "atok- + -or"),
    ("atonkre", 1, "eternidade, sempiternidade, fora do tempo", "a- + tonkre"),
    ("atotte", 1, "usurpador, tirano ilegítimo, rebelde", "atok- + -te (kt -> tt)"),
    ("avur", 2, "frio extremo, geada amarga, algidez", "a- + vur"),
    ("avurvé", 1, "gelo, água congelada, cristal de geada", "avur + Vé"),
    # --- Letra B ---
    ("xunkorfel", 2, "fruto dourado meridional (coloquial: Banánna)", "xun (amarelo) + kor (árvore) + fel (fruto)"),
    ("baxi", 1, "gato, felino doméstico", "raiz bax-"),
    ("bel", 2, "dia, claridade solar", "raiz primária bel"),
    ("belor", 2, "claridade abstrata, esplendor diurno", "bel + -or"),
    # --- Letra C ---
    ("Calaiva", 1, "Casa de Lan'ani (Grande Casa Nobre)", "topônimo/linhagem"),
    ("Celia", 1, "Região da Coroa (berço da Síncrese de Celia)", "topônimo imperial"),
    # --- Letra D ---
    ("dai", 2, "ideia, pensamento, estrela abstrata", "raiz primária dai (Pl. dao)"),
    ("Daifel", 2, "Filho do Pensamento (Ainur gerados por Oratypatte)", "dai + fel (Pl. Daifelo)"),
    ("daior", 2, "pensamento, mente criadora, meditação", "dai + -or"),
    ("dak", 2, "mão direita, flanco destro", "raiz primária dak"),
    ("datte", 1, "a Direita (assento de honra e poder)", "dak + -te (kt -> tt)"),
    ("doote", 1, "tédio, fastio, apatia", "raiz doot-"),
    ("Dotakazeti", 2, "Os Segundos Nascidos, Sucessores (Homens)", "dota + kazeti"),
    # --- Letra E ---
    ("edel", 2, "nobreza, aristocracia de sangue", "raiz primária edel"),
    ("Elfhalo", 2, "Os Espíritos Sagrados (Ainur)", "elfa + halo"),
    ("elfia", 1, "santuário, capela, recinto consagrado", "elf- + -ia"),
    ("elfor", 2, "santidade, pureza ritual, consagração", "elf- + -or"),
    ("elftek", 2, "vaso sagrado, cálice ritual, relíquia", "elf- + -tek"),
    ("enulfe", 1, "confusão, tumulto, baderna, caos", "raiz enulf-"),
    ("Erzmira", 1, "Casa da Joia (regentes de Mirypalkia)", "erz- + mir + -a"),
    # --- Letra F ---
    ("fain", 2, "pirata, corsário, saqueador marítimo", "raiz primária fain"),
    ("falde", 1, "pão, alimento consagrado de trigo", "far- + -ne (rn -> ld)"),
    ("falte", 1, "ofensa, dívida moral, pecado, transgressão", "raiz falt-"),
    ("farkrope", 1, "campo de trigo, seara, terras aráveis", "far- + krope"),
    ("farte", 1, "agricultor, lavrador de trigo, moleiro", "far- + -te"),
    ("fas", 2, "dor, sofrimento físico, suplício", "raiz primária fas"),
    ("fassukor", 2, "tristeza profunda, melancolia, luto", "fas + sukor"),
    ("fea", 1, "sol, astro rei", "raiz primária fea"),
    ("feabel", 2, "solstício, meio-dia solar, zênite", "fea + bel"),
    ("fealan", 2, "alvorada, aurora, clarão do sol nascente", "fea + lan"),
    ("fel", 2, "filho, descendente legítimo", "raiz primária fel"),
    ("feldir", 2, "outono, estação dos ventos noturnos", "fer + nir (rn -> ld)"),
    ("fer", 2, "vento, ar em movimento, sopro atmosférico", "raiz primária fer"),
    ("feria", 1, "atmosfera, regiões superiores do ar, éter", "fer + -ia"),
    ("fervé", 1, "nuvem, névoa, vapor atmosférico", "fer + Vé (Pl. ferveo)"),
    ("Ferylinde", 1, "Casa do Vento (regentes de Ferykrope)", "fery + linde"),
    ("Ferytrátte", 1, "Manwë, Senhor dos Ventos (var. Fertrátte)", "fery + Trátte"),
    ("fil", 2, "cerne, abismo, princípio primordial", "raiz primária fil"),
    ("fila", 1, "tristeza ancestral proto-tréppia", "fil + -a"),
    ("filia", 1, "profundidade abissal, âmago", "fil + -ia"),
    ("filoxe", 1, "vale profundo, cavidade da terra, depressão", "fil + oxe"),
    ("filvé", 1, "abismo marinho, profundezas das águas", "fil + Vé"),
    ("Flibuste", 1, "Casa de Celia (senhores da navegação)", "linhagem nobre"),
    # --- Letra G ---
    ("galdia", 1, "guarnição, arsenal, tesouraria fortificada", "gald- + -ia"),
    ("galtte", 1, "custódio secular, intendente de fortaleza", "gald- + -te (dt -> tt)"),
    ("garvé", 1, "oceano, mar aberto, grande massa de água", "gar + Vé"),
    ("garvelitror", 2, "música dos oceanos, sinfonia das águas", "garvé + litror"),
    ("gassfammir", 2, "espada longa de guerra, montante", "gar + sfammir"),
    ("girbel", 2, "primavera, estação do crescimento diurno", "gir- + bel"),
    ("giror", 2, "crescimento, desenvolvimento, florescimento", "gir- + -or"),
    ("gizor", 2, "amor devocional, afeição, caridade", "giz- + -or"),
    ("Gyos", 2, "Deus, Espírito Supremo (substitui Theus/vane)", "teônimo sagrado"),
    ("Gyos Idda", 2, "Eru, o Único, Criador Supremo Incriado", "Gyos + idda"),
    # --- Letra H ---
    ("hal", 2, "espírito, sopro sagrado (Pl. Halo: Ainur)", "raiz primária hal"),
    ("Hal'gáltte", 1, "O Pastor Sagrado (endônimo cerimonial)", "hal + gald + -te (haplologia + dt -> tt)"),
    ("Halkele", 1, "Igreja, Santa Assembleia, Comunhão", "hal + kel- + -e"),
    ("Hállemme", 1, "A Memória Sagrada (endônimo de Kúr'ete)", "hal + nemre (nl/nr -> ll/mm)"),
    ("Halylitror", 2, "Ainulindalë, A Música dos Espíritos Sagrados (var. Hallitror)", "haly + litror"),
    ("Halyteggar", 2, "Os Salões Atemporais (var. Halteggar)", "haly + teggar"),
    ("Halyvar", 2, "Bosque Sagrado", "haly + var"),
    ("Halyvaria", 1, "Fronteiras Sagradas, Terras do Bosque Sagrado", "haly + var + -ia"),
    ("Halyvur", 2, "A Chama Imperecível, Fogo Secreto (var. Halvur)", "haly + vur"),
    # --- Letra I ---
    ("idda", 2, "o Único, imutavelmente o Um", "id + da (haplologia cristalizada)"),
    ("idlitror", 2, "canto solitário, solo, prelúdio individual", "id + litror"),
    ("illanor", 2, "iluminação interior, inspiração luminosa", "in- + lan- + -or (nl -> ll)"),
    ("illotor", 2, "adorno, ornamento, embelezamento criativo", "in- + lot- + -or (nl -> ll)"),
    ("intulor", 2, "furor, cólera ardente, ira desmedida", "intul- + -or"),
    ("irdor", 2, "resplendor dos antigos, glória ancestral", "ir + dur + -or"),
    ("isor", 2, "sabedoria, inteligência, conhecimento", "is- + -or"),
    ("Ittakazeti", 2, "Os Primeiros Nascidos (Elfos / Quendi)", "itta + kazeti"),
    # --- Letra K ---
    ("kade", 1, "monte, colina, elevação", "raiz kad-"),
    ("karan", 2, "reino, domínio soberano, jurisdição", "raiz primária karan"),
    ("kare", 1, "cadeira, assento", "raiz kar-"),
    ("karegar", 2, "trono supremo, sólio imperial ou divino", "kare + -gar"),
    ("Karytírë", 1, "Casa dos Passos (regentes de Xerypalkia)", "linhagem nobre"),
    ("kazor", 2, "vitalidade, existência encarnada, sopro vital", "kaz- + -or"),
    ("kelador", 2, "avanço de vanguarda, investida, aproximação", "kelad- + -or"),
    ("kellitror", 2, "coro uníssono, polifonia, sinfonia coletiva", "kel- + litror"),
    ("kelor", 2, "manobra tática, formação de marcha, estratégia", "kel- + -or"),
    ("kel'unte", 1, "batedor de escolta, guarda-costas imperial", "kel'un- + -te"),
    ("kindre", 1, "família, comunhão, irmandade (Pl. kindrer/kindro)", "raiz kindr-"),
    ("kindror", 2, "concórdia, paz duradoura, aliança fraterna", "kindr- + -or"),
    ("kitia", 1, "Arquivo Imperial, chancelaria de registros", "kit- + -ia"),
    ("kitor", 2, "escritura pública, código escrito, édito", "kit- + -or"),
    ("kitte", 1, "escriba imperial, tabelião, notário", "kit- + -te"),
    ("kittek", 2, "estilete de inscrição, cálamo, cinzel", "kit- + -tek"),
    ("koldir", 2, "inverno silvático, estação da dormência", "kor + nir (rn -> ld)"),
    ("kor", 2, "árvore, madeira viva", "raiz primária kor"),
    ("koril", 2, "arbusto, muda, pequena árvore", "kor + -il"),
    ("Korikeste", 1, "Casa da Árvore (Grande Casa Nobre)", "kori + keste"),
    ("Koryvela", 1, "Floresta de Treppênia (vulgar: Coryvela)", "kory + vela"),
    ("kosia", 1, "cripta, sepulcro, necrópole, câmara secreta", "kos- + -ia"),
    ("kosor", 2, "segredo, mistério oculto, arcano", "kos- + -or"),
    ("kradet", 2, "criatura, ser criado, obra da criação", "krad- + -et (Pl. kradeti)"),
    ("krador", 2, "Criação, gênese, ato criador", "krad- + -or"),
    ("kran", 2, "mulher, dama (Dat. Pl. kranoi)", "raiz primária kran"),
    ("Kratte", 1, "O Criador, Artífice Supremo", "krad- + -te (dt -> tt)"),
    ("kron", 2, "homem, varão, mortal (Pl. krono)", "raiz primária kron"),
    ("krope", 1, "campina, planície aberta (expurgado kropé)", "raiz krop-"),
    ("kue", 1, "cor vermelha, rubro, escarlate", "raiz ku-"),
    ("kul", 2, "cor laranja, açafrão", "raiz primária kul"),
    ("kulav", 2, "casa de campo, vila rústica", "raiz kulav"),
    ("Kurdor", 2, "homens-mortos, carne corrompida", "kur- + dur"),
    ("Kurlan", 2, "Melkor / Morgoth após a queda (Luz Corrompida)", "kur- + lan"),
    ("kuroi", 2, "pecadores, transgressores (Dat./Nom. Pl. de kura)", "kur- + -oi"),
    ("Kúr'ete", 1, "A Falsa Palavra (exônimo de Hállemme)", "kura + lete (haplologia)"),
    # --- Letra L ---
    ("lake", 1, "mal, perversidade, infortúnio", "raiz lak-"),
    ("lamir", 2, "noite clara de luar", "lan + nir (nn -> m)"),
    ("lan", 2, "luz, clarão sagrado", "raiz primária lan"),
    ("Lan'ani", 2, "em luz absoluta, plenitude luminosa", "lan + lani (haplologia)"),
    ("Lanrukra", 1, "Melkor em sua glória original (Luz e Poder)", "lan + rukra"),
    ("lauri", 1, "ouro, metal nobre (Síncrese de Laurie)", "raiz laur-"),
    ("le", 1, "luz elementar, raio luminoso", "raiz primária le"),
    ("ledda", 1, "palavra ideal, mandamento, decreto", "lete + da (td -> dd)"),
    ("leddakitor", 2, "Código Imperial de Mandamentos, Constituição", "ledda + kitor"),
    ("leddalitror", 2, "tema musical diretor, Grande Tema", "ledda + litror"),
    ("lete", 1, "palavra, vocábulo, voz articulada", "raiz let-"),
    ("letor", 2, "eloquência, retórica de Chancelaria, discurso", "let- + -or"),
    ("lette", 1, "orador oficial, arauto, legado", "let- + -te"),
    ("lettek", 2, "megafone, trombeta de comando, instrumento de voz", "let- + -tek"),
    ("lexe", 1, "estrela; no plural (lexer): Os Santos", "raiz lex-"),
    ("litrgar", 2, "Grande Música, Sinfonia Monumental", "litr- + -gar"),
    ("litror", 2, "música, melodia, vibração harmônica", "litr- + -or"),
    ("litrte", 1, "cantor, músico, menestrel cósmico", "litr- + -te"),
    ("litrtek", 2, "instrumento musical, harpa, lira, órgão", "litr- + -tek"),
    ("lotor", 2, "beleza, esplendor estético, formosura", "lot- + -or"),
    # --- Letra M ---
    ("mad", 2, "mãe, matriz geradora", "raiz primária mad"),
    ("massu", 2, "útero, ventre materno", "mad- + su (ds -> ss)"),
    ("mektep", 2, "casebre, choupana plebeia (vulgar: mectep)", "mek + tep"),
    ("mete", 1, "glória, honra litúrgica", "raiz met-"),
    ("metor", 2, "majestade, exultação, esplendor", "met- + -or"),
    ("mexfammir", 2, "adaga ritual, punhal curto", "mek + sfar + mir (rm -> mm)"),
    ("mixunkorfel", 2, "variedade botânica menor de fruto dourado meridional (coloquial: Mibanánna)", "mi + xunkorfel"),
    ("mir", 2, "joia, gema preciosa; olho, olhar", "raiz primária mir"),
    ("mirakosor", 2, "Visão profética mostrada aos olhos", "mir- + akosor"),
    ("mirgar", 2, "torre de vigia, atalaia monumental", "mir + -gar"),
    ("mirkron", 2, "testemunha ocular, inspetor imperial", "mir + kron"),
    ("miror", 2, "visão, contemplação intelectual, vigilância", "mir- + -or"),
    ("mirte", 1, "ourives, lapidador de gemas", "mir + -te"),
    ("Mirypalkia", 1, "Cinturão das Gemas (província de Erzmira)", "miry + palk + -ia"),
    ("mixi", 1, "pessoa, cidadão, indivíduo (Síncrese de Mixie)", "raiz mix-"),
    ("Moba'el", 2, "bom dia (saudação formal de Chancelaria)", "moba + bel (haplologia b-b)"),
    ("mobalitror", 2, "consonância, harmonia musical perfeita", "moba + litror"),
    ("mobor", 2, "graça abstrata, benevolência, favor divino", "mob- + -or"),
    ("mollete", 1, "sentença, julgamento, veredito", "mon + lete (nl -> ll)"),
    ("molletek", 2, "cetro judicial, balança de julgamento", "mollet- + -tek"),
    ("molletia", 1, "Corte Suprema, tribunal de justiça, fórum", "mollet- + -ia"),
    ("mollette", 1, "juiz, magistrado imperial", "mollet- + -te"),
    ("mon", 2, "nome, designação sagrada (substitui nomo)", "raiz primária mon"),
    ("mone", 1, "meia, vestimenta de pé", "raiz mon-"),
    # --- Letra N ---
    ("navor", 2, "transformação, feição, configuração, forma", "nav- + -or"),
    ("Nemkura", 1, "memória corrompida, esquecimento maldito", "nemre + kura"),
    ("nemre", 1, "memória, lembrança histórica (var. nemme)", "raiz nemr-"),
    ("Nesu", 2, "o Nada absoluto, o Vazio abissal", "ne + su"),
    ("nir", 2, "noite, escuridão noturna", "raiz primária nir"),
    ("nirkron", 2, "espião, infiltrado, herege noturno", "nir + kron"),
    ("nuvíke", 1, "demônio do poço escarlate", "entidade abissal"),
    # --- Letra O ---
    ("okazor", 2, "ressurreição, renascimento, restauração vital", "okaz- + -or"),
    ("orat", 2, "o Todo, a Totalidade, o Universo inteiro", "raiz de oratom (Skorum)"),
    ("Oratoxe", 1, "Arda / Eä, A Terra Integral, o Mundo Realizado", "orat + oxe"),
    ("Oratypatte", 1, "Ilúvatar, O Pai do Todo (var. Oratpatte)", "oraty + Patte"),
    ("otrakor", 2, "retirada estratégica, recuo tático ordenado", "otrak- + -or"),
    ("oxe", 1, "chão, terra, solo firme", "raiz ox-"),
    ("oxegar", 2, "globo terrestre, continente, massa do mundo", "oxe + -gar"),
    ("oxéor", 2, "guerra campal, campanha bélica em larga escala", "oxe/oxte + -or"),
    ("oxte", 1, "guerreiro, soldado combatente", "oxe + -te"),
    # --- Letra P ---
    ("paise", 1, "lugar, região, localidade", "raiz pais-"),
    ("palk", 2, "passo, desfiladeiro, cinturão geográfico", "raiz primária palk"),
    ("Patte", 1, "Pai (tratado com dativo misto Pattej no Corpus)", "raiz patt-"),
    ("piskre", 1, "idiota, néscio, estúpido", "raiz piskr-"),
    ("poke", 1, "animal, besta, criatura irracional", "raiz pok-"),
    # --- Letra R ---
    ("rase", 1, "língua, idioma, vernáculo (vulgar: raçe)", "raiz ras-"),
    ("rixe", 1, "montanha, pico rochoso", "raiz rix-"),
    ("rixegar", 2, "cordilheira monumental, maciço alpino", "rixe + -gar"),
    ("Rixelaka", 1, "Os Picos Gélidos (cordilheira setentrional)", "rixe + laka"),
    ("rose", 1, "burro, jumento, besta de carga", "raiz ros-"),
    ("rukralete", 1, "voz potente, brado de comando, clamor", "rukra + lete"),
    ("rukror", 2, "poder, potência, vigor soberano", "rukr- + -or"),
    ("Rukroro", 2, "As Potências (designação solene dos Valar)", "rukror + -o"),
    # --- Letra S ---
    ("saitte", 1, "armeiro, cuteleiro, forjador de lâminas", "said- + -te (dt -> tt)"),
    ("saittek", 2, "pedra de amolar, rebolo de campanha", "said- + -tek (dt -> tt)"),
    ("sfammir", 2, "espada, lâmina de combate", "sfar + mir (rm -> mm)"),
    ("sfaror", 2, "defesa, salvaguarda, proteção militar", "sfar- + -or"),
    ("sfarte", 1, "sentinela, guarda de muralha, defensor", "sfar- + -te"),
    ("sfartek", 2, "escudo, égide, broquel, armadura", "sfar- + -tek"),
    ("sife", 1, "história, crônica, narrativa do tempo", "raiz sif-"),
    ("sifte", 1, "cronista imperial, historiador oficial", "sif- + -te"),
    ("siftek", 2, "anais do Império, rolo de crônicas, códice", "sif- + -tek"),
    ("sin", 2, "mão esquerda, flanco sinistro", "raiz primária sin"),
    ("sinte", 1, "a Esquerda (direção ou ala)", "sin + -te"),
    ("skoror", 2, "fé, crença dogmática, fidelidade espiritual", "skor- + -or"),
    ("skorte", 1, "fiel, crente, iniciado nos mistérios", "skor- + -te"),
    ("sotim", 2, "rosto, face, semblante (Síncrese de Sotime)", "raiz primária sotim"),
    ("sotimor", 2, "semblante, matiz, cor aparente, aspecto", "sotim + -or"),
    ("Sprezzatura", 1, "Casa do Caminho (senhores de Varkaria)", "linhagem condal"),
    ("su", 2, "núcleo, cerne, essência interior", "raiz primária su"),
    ("sukor", 2, "coração, órgão vital e centro afetivo", "su + kor"),
    ("sulet", 2, "timbre vocal, voz interior, acorde", "su + lete"),
    # --- Letra T ---
    ("take", 1, "mesa, tábua de banquete ou conselho", "raiz tak-"),
    ("teggar", 2, "palácio, fortaleza monumental, corte", "tep + -gar (pg -> gg)"),
    ("tekor", 2, "obra, trabalho, labor construtivo, feitura", "tek- + -or"),
    ("Tektrátte", 1, "Aulë, Senhor das Obras e da Forja", "tek- + Trátte"),
    ("tep", 2, "casa, lar, edifício", "raiz primária tep"),
    ("tepia", 1, "habitação, morada estabelecida, mansão", "tep + -ia"),
    ("tepil", 2, "cabana, tenda, abrigo humilde", "tep + -il"),
    ("Tette", 1, "O Artífice, forjador, artesão", "tek- + -te (kt -> tt)"),
    ("tettek", 2, "malho de forja, bigorna, ferramenta", "tek- + -tek (kt -> tt)"),
    ("tokor", 2, "soberania, autoridade de Estado, regência", "tok- + -or"),
    ("Tóldemme", 1, "O Refúgio dos Antigos / Oferenda da Memória", "tor + nemre"),
    ("tonkre", 1, "tempo, hora, momento histórico", "raiz tonkr-"),
    ("torexte", 1, "sitiante, conquistador, tomador de praça", "torex- + -te"),
    ("Totte", 1, "Vala, Poder ou Regente do Mundo (Pl. Totter)", "tok- + -te (kt -> tt)"),
    ("Trátte", 1, "Comandante, Senhor Supremo", "trak- + -te (kt -> tt)"),
    ("Treppênia", 1, "Capital do Condado e sede da Chancelaria", "topônimo imperial"),
    ("Treppenín", 2, "vassalo ou gentílico de Treppenwitz", "gentílico"),
    ("Treppenwitz", 2, "Casa Condal soberana de Treppênia", "linhagem condal"),
    ("Tréppia", 1, "Terra do Norte, nação tréppia", "topônimo nacional"),
    ("Tréppio", 2, "o idioma Tréppio; cidadão tréppio", "endônimo"),
    ("tul", 2, "loucura, delírio, insânia", "raiz primária tul"),
    # --- Letra V ---
    ("var", 2, "caminho, estrada, via", "raiz primária var"),
    ("Varkaria", 1, "Labirinto de Encruzilhadas (feudo de Sprezzatura)", "var + kar + -ia"),
    ("varte", 1, "encontro, cruzamento de vias", "var + -te"),
    ("Vé", 1, "água (único substantivo com acento agudo diferencial)", "raiz primária Vé"),
    ("Ve'el", 2, "Domínio das Sombras (expurgado Vé'el)", "vel + el (haplologia)"),
    ("veike", 1, "jardim, horto fechado", "raiz veik-"),
    ("veksixi", 1, "chuva, tempestade costeira, aguaceiro", "ve + ksixi"),
    ("vel", 2, "sombra benigna, penumbra protetora", "raiz primária vel"),
    ("velbel", 2, "crepúsculo, ocaso, entardecer", "vel + bel"),
    ("vellir", 2, "noite sem estrelas, trevas absolutas", "vel + nir (ln -> ll)"),
    ("Veloxe", 1, "Submundo, Infernos, mansão dos mortos", "vel + oxe"),
    ("Velsu", 2, "O Exânime (entidade abissal)", "vel + su"),
    ("velvé", 1, "águas sombrias, Porto das Sombras", "vel + Vé"),
    ("Vepalkia", 1, "Faixa dos Vaus (província fluvial)", "Vé + palk + -ia"),
    ("Véporos", 2, "Casa das Águas (Grande Casa Nobre)", "Vé + poros"),
    ("verre", 1, "bronze, liga metálica militar", "raiz verr-"),
    ("Vétrátte", 1, "Ulmo, Senhor das Águas e Oceanos (var. Vetrátte)", "Vé + Trátte"),
    ("vevar", 2, "rio, correnteza fluvial, curso de água", "Vé + var"),
    ("vevaril", 2, "riacho, córrego, arroio cristalino", "vevar + -il"),
    ("votte", 1, "executor, açougueiro, carrasco (vulgar: vocte)", "vok + -te (kt -> tt)"),
    ("vok", 2, "sangue, fluido vital (Dat. arcaico sideral: vox)", "raiz primária vok"),
    ("Vokátte", 1, "O Guia de Sangue (exônimo plebeu: Vokát)", "vok + -átte"),
    ("vokor", 2, "carne viva, músculo irrigado, corpo", "vok + -or"),
    ("Vokkura", 1, "carne/sangue corrompido, mortos-vivos", "vok + kura"),
    ("Volleta", 1, "órgão viril diminuto (termo satírico)", "vok + lita (kl -> ll)"),
    ("vuldir", 2, "verão, estação das noites quentes", "vur + nir (rn -> ld)"),
    ("vule", 1, "vontade, arbítrio, determinação", "raiz vul-"),
    ("vulor", 2, "propósito, desígnio da vontade, anseio", "vul- + -or"),
    ("vur", 2, "fogo, chama, brasa ardente", "raiz primária vur"),
    ("vuror", 2, "calor extremo, incandescência, conflagração", "vur + -or"),
    # --- Letra X / Y ---
    ("xer", 2, "céu, firmamento superior (var. 1ª Decl. xere)", "raiz primária xer"),
    ("xere", 1, "céu, firmamento (variante temática de 1ª Declinação de xer)", "raiz xer-"),
    ("Xerypalk", 2, "Passo do Céu (forma atemática de Xerypalkia)", "xery + palk"),
    ("Xerypalkia", 1, "Serras do Firmamento (província de Karytírë)", "xery + palk + -ia"),
    ("xun", 2, "cor amarela imperial, dourado solar (expurgado xün)", "raiz primária xun"),
    ("Yamakoz", 2, "Cidade Imortal / título de Giovanni Sprezzatura", "topônimo/título"),
    # --- Entradas Adicionais Auditadas nos Textos Integrais (Halylitror, Liturgia e Crônicas) ---
    ("akosor", 2, "revelação, manifestação visível, desvelamento", "akos- + -or"),
    ("Daifelo", 2, "Os Filhos do Pensamento (plural solene de Daifel)", "dai + felo"),
    ("don", 2, "dom, dádiva soberana (Arcaísmo Litúrgico cristalizado no Halylitror IV: donoi; forma clássica endógena: moboril)", "fóssil litúrgico do Halylitror"),
    ("moboril", 2, "dom, dádiva concedida, presente soberano (equivalente clássico endógeno do arcaísmo litúrgico don)", "mobor (graça/dádiva) + -il"),
    ("Fertrátte", 1, "Manwë, Senhor dos Ventos (forma radical de Ferytrátte)", "fer + Trátte"),
    ("Ferykrope", 1, "Campina dos Ventos (feudo da Casa Ferylinde; vulg. Ferychope)", "fery + krope"),
    ("font", 2, "fonte, manancial (Arcaísmo Litúrgico cristalizado no Halylitror VI/IX: fontom; forma clássica endógena: vefil)", "fóssil litúrgico do Halylitror"),
    ("vefil", 2, "fonte, manancial, nascente de água viva (equivalente clássico endógeno do arcaísmo litúrgico font)", "Vé (água) + fil (cerne/origem)"),
    ("fratror", 2, "irmão cósmico (Arcaísmo Litúrgico cristalizado no Halylitror IV/IX: fratroi; forma clássica endógena: kindrfel)", "fóssil litúrgico do Halylitror"),
    ("kindrfel", 2, "irmão, confrade de sangue ou espírito (equivalente clássico endógeno do arcaísmo litúrgico fratror)", "kindre (família/irmandade) + fel (filho)"),
    ("Giovanni Sprezzatura", 1, "Conde de Varkaria, 'O Yamakoz'", "antropônimo condal"),
    ("Hallitror", 2, "Ainulindalë (forma radical assimilada ll de Halylitror)", "hal + litror (nl/ll)"),
    ("Halo", 2, "Os Espíritos Sagrados, Ainur (plural solene de hal)", "hal + -o"),
    ("Halteggar", 2, "Salões Atemporais (forma radical de Halyteggar)", "hal + teggar"),
    ("Halvur", 2, "Chama Imperecível, Fogo Secreto (forma radical de Halyvur)", "hal + vur"),
    ("harpe", 1, "harpa (Arcaísmo Litúrgico cristalizado no Halylitror III: harper; forma clássica endógena: sulettek)", "fóssil litúrgico do Halylitror"),
    ("sulettek", 2, "harpa clássica, lira de cordas dedilhadas (equivalente clássico endógeno do arcaísmo litúrgico harpe)", "sulet (timbre/acorde) + -tek"),
    ("Jesus", 2, "Jesus (antropônimo litúrgico no Metuses Maria e Skorum)", "antropônimo sagrado"),
    ("Kristus", 2, "Cristo, o Ungido (epíteto sagrado no Skorum)", "antropônimo sagrado"),
    ("Maria", 1, "Santa Maria (antropônimo litúrgico no Metuses Maria e Skorum)", "antropônimo sagrado"),
    ("Mirypalk", 2, "Passo das Joias (forma atemática de Mirypalkia)", "miry + palk"),
    ("nemme", 1, "memória, lembrança (variante geminada mr -> mm de nemre)", "nemr- (mr -> mm)"),
    ("Oratpatte", 1, "Ilúvatar, Pai do Todo (forma radical de Oratypatte)", "orat + Patte"),
    ("Pontius Pilatus", 2, "Pôncio Pilatos (antropônimo histórico no Skorum)", "antropônimo histórico"),
    ("timor", 2, "temor sagrado (Arcaísmo Litúrgico cristalizado no Halylitror VII: timorom; forma clássica endógena: halfas)", "fóssil litúrgico do Halylitror"),
    ("halfas", 2, "temor reverencial, assombro sagrado (equivalente clássico endógeno do arcaísmo litúrgico timor)", "hal (espírito) + fas (comoção/tremor)"),
    ("todo", 2, "todos (Arcaísmo Litúrgico cristalizado no Halylitror II/IV: todos; forma clássica endógena: orata)", "fóssil litúrgico do Halylitror"),
    ("orata", 1, "totalidade dos seres, todos sem exceção (equivalente clássico endógeno do arcaísmo litúrgico todo)", "orat (o Todo) + -a"),
    ("Totter", 1, "Os Poderes, Valar, Regentes do Mundo (plural de Totte)", "tok- + -te + -r"),
    ("Treppenína", 1, "vassala ou gentílica feminina de Treppenwitz", "Treppen- + -ína"),
    ("Treppeníno", 2, "vassalo ou gentílico masculino de Treppenwitz", "Treppen- + -íno"),
    ("Vêpalk", 2, "Passo das Águas (forma atemática de Vepalkia)", "Vé + palk"),
    ("Vetrátte", 1, "Ulmo, Senhor das Águas (variante gráfica de Vétrátte)", "ve + Trátte"),
    ("viole", 1, "viola (Arcaísmo Litúrgico cristalizado no Halylitror III: violer; forma clássica endógena: sulettor)", "fóssil litúrgico do Halylitror"),
    ("sulettor", 2, "viola de arco, cordofone sustentado (equivalente clássico endógeno do arcaísmo litúrgico viole)", "sulet (timbre) + tor- (sustentar)"),
    # --- Expansão Eufônica V8.1 (substantivos) ---
    ('Mobanir', 2, 'boa noite (saudação noturna)', 'moba + nir'),
    ('Mobafea', 1, 'bom sol, boa tarde (saudação vespertina)', 'moba + fea'),
    ('ynte', 1, 'viajante, caminhante, andarilho', 'yn- + -te'),
    ('Tepypatte', 1, 'hospedeiro, senhor da estalagem, pai da casa', 'tepy + Patte (Lei 6.5, camada clássico-genitiva)'),
    ('habte', 1, 'anfitrião, acolhedor de viajantes', 'hab- + -te'),
    ('kertte', 1, 'lenhador, talhador de madeira', 'kerd- + -te, dt -> tt'),
    ('ruxte', 1, 'cozinheiro, mestre do caldeirão', 'rux- + -te'),
    ('gobte', 1, 'mercador, negociante, mascate', 'gob- + -te'),
    ('zalte', 1, 'pagador, tesoureiro', 'zal- + -te'),
    ('tutte', 1, 'mineiro, coveiro, cavador', 'tuk- + -te, kt -> tt'),
    ('kastte', 1, 'alfaiate, costureiro', 'kask- + -te, kt -> tt'),
    ('apette', 1, 'remendão, consertador de utensílios', 'a- + pek- + -te, kt -> tt'),
    ('dratte', 1, 'carreteiro, condutor de trenó', 'drak- + -te, kt -> tt'),
    ('mixil', 2, 'criança, pequena pessoa', 'mixi + -il'),
    ('kranil', 2, 'menina', 'kran + -il'),
    ('kronil', 2, 'menino', 'kron + -il'),
    ('nyke', 1, 'porta', 'nyk- + -e'),
    ('nykil', 2, 'janela, portinhola', 'nyke + -il'),
    ('nyttek', 2, 'chave', 'nyk- + -tek, kt -> tt'),
    ('anyttek', 2, 'fechadura, tranca', 'a- + nyk- + -tek, kt -> tt'),
    ('falia', 1, 'quarto de dormir, aposento', 'fal- + -ia'),
    ('ruxia', 1, 'cozinha', 'rux- + -ia'),
    ('ruxtek', 2, 'caldeirão, panela de ferro', 'rux- + -tek'),
    ('ruxet', 2, 'ensopado, prato cozido (particípio nominalizado)', 'rux- + -et'),
    ('lixia', 1, 'casa de banho, lavadouro', 'lix- + -ia'),
    ('lixtek', 2, 'bacia, gamela de lavar', 'lix- + -tek'),
    ('komia', 1, 'taberna, casa de beber', 'kom- + -ia'),
    ('komtek', 2, 'copo, cálice cotidiano', 'kom- + -tek'),
    ('komor', 2, 'bebida, trago', 'kom- + -or'),
    ('makia', 1, 'despensa, refeitório', 'mak- + -ia'),
    ('makor', 2, 'refeição, alimento servido', 'mak- + -or'),
    ('sekil', 2, 'banquinho, mocho', 'sek- + -il'),
    ('lanil', 2, 'candeia, vela de sebo', 'lan + -il'),
    ('lantek', 2, 'lanterna, lamparina', 'lan + -tek'),
    ('gelmtek', 2, 'pederneira, isqueiro de mecha', 'gelm- + -tek'),
    ('vuria', 1, 'fornalha, forja', 'vur + -ia'),
    ('vurtek', 2, 'atiçador do fogo', 'vur + -tek'),
    ('fertek', 2, 'fole de forja', 'fer + -tek'),
    ('vétek', 2, 'balde, vasilha de água', 'Vé + -tek'),
    ('kerttek', 2, 'machado de lenha', 'kerd- + -tek, dt -> tt'),
    ('tuttek', 2, 'pá, enxada', 'tuk- + -tek, kt -> tt'),
    ('kasttek', 2, 'agulha de coser', 'kask- + -tek, kt -> tt'),
    ('drattek', 2, 'corda de reboque, arreio', 'drak- + -tek, kt -> tt'),
    ('poketek', 2, 'ferradura, arreio de animal', 'poke + -tek'),
    ('yntek', 2, 'cajado, bordão de viagem', 'yn- + -tek'),
    ('huxor', 2, 'roupa, vestimenta', 'hux- + -or'),
    ('huxgar', 2, 'capa, manto pesado de viagem', 'hux- + -gar'),
    ('huxil', 2, 'camisa, túnica leve', 'hux- + -il'),
    ('kitil', 2, 'carta, bilhete', 'kit- + -il'),
    ('gobia', 1, 'mercado, feira', 'gob- + -ia'),
    ('gobor', 2, 'troca, negócio', 'gob- + -or'),
    ('zalor', 2, 'pagamento, quitação', 'zal- + -or'),
    ('azalor', 2, 'dívida pendente, inadimplência', 'a- + zal- + -or'),
    ('tavor', 2, 'contagem, número, soma', 'tav- + -or'),
    ('paror', 2, 'preço, valor merecido', 'par- + -or'),
    ('lauril', 2, 'moeda de ouro', 'lauri + -il'),
    ('verril', 2, 'moeda de bronze', 'verre + -il'),
    ('heskor', 2, 'pergunta', 'hesk- + -or'),
    ('bodor', 2, 'resposta', 'bod- + -or'),
    ('ropor', 2, 'chamado, convocação', 'rop- + -or'),
    ('krazor', 2, 'riso, alegria', 'kraz- + -or'),
    ('akrazor', 2, 'pranto, lamento', 'a- + kraz- + -or'),
    ('lyror', 2, 'esperança, espera', 'lyr- + -or'),
    ('alyror', 2, 'desespero', 'a- + lyr- + -or'),
    ('sulvor', 2, 'cantiga, canção de ninar', 'sulv- + -or'),
    ('xelvé', 1, 'neve', 'xel- + Vé'),
    ('xelor', 2, 'nevada, tempestade de neve', 'xel- + -or'),
    ('nirlan', 2, 'lua', 'nir + lan'),
    ('mirvé', 1, 'lágrima', 'mir + Vé'),
    ('korvé', 1, 'seiva, resina', 'kor + Vé'),
    ('farvé', 1, 'cerveja de trigo', 'far- + Vé'),
    ('korgar', 2, 'floresta densa, bosque ancestral', 'kor + -gar'),
    ('rixil', 2, 'seixo, pedrinha', 'rixe + -il'),
    ('varil', 2, 'trilha, atalho', 'var + -il'),
    ('belvar', 2, 'jornada, um dia de caminho', 'bel + var'),
    ('tonkril', 2, 'instante, momento', 'tonkre + -il'),
    ('veksixil', 2, 'garoa, chuvisco', 'veksixi + -il'),
    ('pokil', 2, 'filhote, cãozinho', 'poke + -il'),
    ('tukia', 1, 'mina, escavação', 'tuk- + -ia'),
]

# 2.2. ADJETIVOS PRIMÁRIOS, DERIVADOS E SUPLETIVOS (Adjetivo, Significado, Comparativo, Superlativo Sg)
ADJECTIVES = [
    # --- Adjetivos Práticos da Vida Diária (Era Antiga -> Era Clássica V8.1) ---
    ("kildan", "gélido, nevado, congelado pelo vento da serra", "maer kildan", "kildann"),
    ("vuran", "aquecido pela lareira, acolhedor, fumegante", "maer vuran", "vurann"),
    ("drinan", "de madeira maciça, entalhado em carvalho", "maer drinan", "drinann"),
    ("rixan", "pétreo, sólido como rocha, resistente", "maer rixan", "rixann"),
    ("zenan", "leal, fiel, amigo sincero de travessia", "maer zenan", "zenann"),
    ("dakkan", "nutritivo, farto, substancioso e saboroso", "maer dakkan", "dakkann"),
    ("garvan", "límpido, cristalino como água fresca de degelo", "maer garvan", "garvann"),
    ("goban", "justo no preço, correto na medida e no trato", "maer goban", "gobann"),
    ("verran", "metálico, duro como lâmina de bronze e aço", "maer verran", "verrann"),
    ("sukoran", "corajoso, de peito aquecido diante do perigo", "maer sukoran", "sukorann"),
    ("veksan", "brumoso, encoberto pela névoa fria", "maer veksan", "veksann"),
    ("halkfasan", "fatigado da longa marcha, exausto na neve", "maer halkfasan", "halkfasann"),
    ("viltan", "curado, revigorado pela ceia e pelo sono", "maer viltan", "viltann"),

    ("aetika", "dissonante, estranho, alheio à harmonia", "maer aetika", "aetikan"),
    ("akura", "virgem, incorrupto, imaculado", "maer akura", "akuran"),
    ("alota", "horrendo, disforme, intolerável", "maer alota", "alotan"),
    ("amatte", "esfomeado, faminto (de amak- + -te, kt -> tt; vulgar: amocte)", "maer amatte", "amatten"),
    ("amyga", "inumerável, incontável (var. amygata)", "maer amyga", "amygan"),
    ("amygata", "inumerável, incontável (forma ordinalizada de Myga)", "maer amygata", "amygatan"),
    ("aruma", "imperial, soberano", "maer aruma", "aruman"),
    ("atola", "feio, desfigurado", "maer atola", "atolan"),
    ("avura", "gélido, glacial, congelante", "maer avura", "avuran"),
    ("barsexi", "irritante, importuno", "maer barsexi", "barsexin"),
    ("bela", "diurno, claro, relativo ao dia", "maer bela", "bell"),
    ("daia", "ideal, estelar, relativo à ideia (var. da)", "maer daia", "daian"),
    ("edela", "nobre, aristocrático", "maer edela", "edell"),
    ("elfa", "sacro, sagrado, consagrado", "maer elfa", "elfan"),
    ("faina", "pirateado, ilícito, clandestino", "maer faina", "fainan"),
    ("fera", "ventoso, aéreo, tempestuoso", "maer fera", "feld"),
    ("fila", "abissal, primordial, profundo", "maer fila", "fill"),
    ("gura", "chato, enfadonho, maçante", "maer gura", "guran"),
    ("halvura", "imperecível, inflamado pelo fogo sagrado", "maer halvura", "halvuran"),
    ("hoka", "tolo, ignorante, néscio", "maer hoka", "hokan"),
    ("idda", "único, exclusivo, indivisível", "maer idda", "iddan"),
    ("ilora", "estelar, sideral, celeste", "maer ilora", "iloran"),
    ("isa", "inteligente, sábio, perspicaz", "maer isa", "isan"),
    ("kindra", "familiar, fraterno, comunitário", "maer kindra", "kindran"),
    ("kora", "amadeirado, arbóreo, silvestre", "maer kora", "kold"),
    ("krana", "feminino, mulheril", "maer krana", "kranan"),
    ("krona", "masculino, viril", "maer krona", "kronan"),
    ("kua", "avermelhado, rubro, escarlate", "maer kua", "kuan"),
    ("kula", "alaranjado, cor de açafrão", "maer kula", "kulan"),
    ("kura", "corrompido, degenerado, mau (Supleção Teológica)", "krer", "kuran"),
    ("laka", "mau, perverso, maligno", "maer laka", "lakan"),
    ("lana", "luminoso, cheio, pleno de luz (var. lany)", "maer lana", "lan'an"),
    ("laura", "dourado, áureo", "maer laura", "lauran"),
    ("leta", "verbal, oratório, literal", "maer leta", "letan"),
    ("lexa", "estelar, santo, divino", "maer lexa", "lexan"),
    ("lita", "diminuto, curto, suave, brando", "maer lita", "litan"),
    ("lota", "belo, formoso (metátese: tola)", "maer lota", "lotan"),
    ("meta", "glorioso, majestoso", "maer meta", "metan"),
    ("mira", "precioso, gemular, visual", "maer mira", "mild"),
    ("mirakosora", "admirável, prodigioso, maravilhoso", "maer mirakosora", "mirakosoran"),
    ("moba", "bom, harmonioso, justo (Supleção Teológica)", "maer", "moban"),
    ("molleta", "severo, austero, julgador", "maer molleta", "molletan"),
    ("nakad", "informe, nu, ainda não desabrochado", "maer nakad", "nakadn"),
    ("nemra", "memorial, imemorial, histórico", "maer nemra", "nemm"),
    ("nira", "noturno, escuro", "maer nira", "niran"),
    ("oxea", "terrestre, telúrico, terreno", "maer oxea", "oxean"),
    ("piskra", "idiota, estúpido", "maer piskra", "piskran"),
    ("poka", "animal, selvagem, ferino", "maer poka", "pokan"),
    ("rixa", "montanhoso, alpino, escarpado", "maer rixa", "rixan"),
    ("rosa", "asnar, teimoso, burro", "maer rosa", "rosan"),
    ("rukra", "forte, poderoso, potente", "maer rukra", "rukran"),
    ("sua", "nuclear, essencial, central", "maer sua", "suan"),
    ("sukora", "cardíaco, cordial, íntimo", "maer sukora", "sukold"),
    ("tola", "bonito, gracioso (variante de lota)", "maer tola", "tolan"),
    ("tonkra", "temporal, secular, passageiro", "maer tonkra", "tonkran"),
    ("tula", "louco, insano, furioso", "maer tula", "tull"),
    ("va", "molhado, aquático, líquido (sincopado de Vé)", "maer va", "van"),
    ("vara", "viário, errante, relativo ao caminho", "maer vara", "veld"),
    ("vela", "sombrio, umbroso, velado", "maer vela", "vell"),
    ("verra", "abronzeado, brônzeo", "maer verra", "verran"),
    ("vurora", "incandescente, flamejante, ígneo", "maer vurora", "vuroran"),
    ("xera", "celeste, elevado, sideral", "maer xera", "xeld"),
    ("xuna", "loiro, amarelado, flavente", "maer xuna", "xunan"),
    # --- Adjetivos Adicionais Auditados nos Textos Litúrgicos e no Halylitror ---
    ("da", "ideal, relativo à ideia (forma sincopada de daia em idda/ledda)", "maer da", "dan"),
    ("katro", "poucos, raros, escassos (plural quantitativo)", "maer katro", "katron"),
    ("lany", "cheio de luz, pleno (variante litúrgica de lana)", "maer lany", "lan'an"),
    ("luda", "cheia, plena (adjetivo litúrgico arcaico no Metuses Maria)", "maer luda", "ludan"),
    ("rukraleta", "dotado de voz potente, altissonante, trovejante", "maer rukraleta", "rukraletan"),
    # --- Expansão Eufônica V8.1 (adjetivos) ---
    ('xela', 'nevado, coberto de neve', 'maer xela', 'xelan'),
    ('nyka', 'aberto', 'maer nyka', 'nykan'),
    ('anyka', 'fechado, trancado', 'maer anyka', 'anykan'),
    ('kraza', 'alegre, risonho', 'maer kraza', 'krazan'),
    ('akraza', 'choroso, triste', 'maer akraza', 'akrazan'),
    ('lyra', 'esperançoso', 'maer lyra', 'lyran'),
    ('lixa', 'limpo, lavado', 'maer lixa', 'lixan'),
    ('alixa', 'sujo, maculado', 'maer alixa', 'alixan'),
    ('peka', 'quebrado, partido', 'maer peka', 'pekan'),
    ('apeka', 'consertado, inteiro', 'maer apeka', 'apekan'),
    ('maka', 'saciado, bem alimentado', 'maer maka', 'makan'),
    ('amaka', 'faminto', 'maer amaka', 'amakan'),
    ('fala', 'sonolento', 'maer fala', 'falan'),
    ('zala', 'pago, quite', 'maer zala', 'zalan'),
    ('azala', 'devedor, em dívida', 'maer azala', 'azalan'),
    ('ruxa', 'cozido, assado', 'maer ruxa', 'ruxan'),
    ('aruxa', 'cru', 'maer aruxa', 'aruxan'),
    ('huxa', 'vestido, agasalhado', 'maer huxa', 'huxan'),
    ('nirlana', 'lunar, enluarado', 'maer nirlana', 'nirlanan'),
    ('tonkrila', 'breve, momentâneo', 'maer tonkrila', 'tonkrilan'),
    ('haba', 'hospitaleiro', 'maer haba', 'haban'),
]

# 2.3. RAÍZES VERBAIS PRIMÁRIAS E DERIVADAS (Raiz Positiva sem -ur, Significado Positivo, Significado Privativo, Significado Iterativo, Significado Iterativo-Privativo)
VERB_ROOTS = [
    # --- Verbos de Ação Cotidiana (Era Antiga -> Era Clássica V8.1) ---
    ("dak", "comer alimento sólido, nutrir-se", "jejuar, abster-se de comida", "comer habitualmente, merendar de novo", "quebrar o jejum, voltar a comer"),
    ("garv", "beber água pura, saciar a sede", "abster-se de beber, passar sede", "bebericar repetidamente, sorver caneca a caneca", "esvaziar a última gota da caneca"),
    ("fal", "repousar no leito, dormir serenamente", "velar à noite, vigiar sem dormir", "dormir o sono habitual, tirar um cochilo", "despertar do repouso, encerrar o sono"),
    ("sfar", "enxergar na bruma, avistar os caminhos", "fechar os olhos, cegar temporariamente na neve", "vigiar atentamente, contemplar de novo", "interromper a vigília, descansar a vista"),
    ("halk", "caminhar pela trilha, marchar na neve", "deter o passo, paralisar a marcha no frio", "caminhar continuamente, peregrinar pelas serras", "dar o passo final e atingir o destino"),
    ("vur", "aquecer com fogo, avivar a lareira", "apagar as chamas, deixar o fogo extinguir-se", "reacender a lareira, soprar as brasas", "manter as brasas vivas sob as cinzas"),
    ("tek", "forjar o ferro, lavrar a pedra, construir", "deixar a obra inacabada, desconstruir", "reforjar a lâmina, martelar repetidas vezes", "concluir a forja e temperar no aço"),
    ("ruxp", "ferver o caldo, apurar sopa no caldeirão", "deixar o caldo frio, não ferver", "reaquecer o caldo, ferver de novo na panela", "tirar a panela do fogo no ponto exato"),
    ("klad", "trancar a porta com ferrolho contra a tempestade", "destrancar, abrir a porta para a luz", "retrancar com segurança, fechar de novo", "abrir a tranca após a tempestade passar"),
    ("lut", "caçar nas montanhas, rastrear animais silvestres", "abster-se da caça, poupar a presa", "caçar regularmente para abastecer a estalagem", "retornar da caçada com provisões"),
    ("zul", "aferir peso na balança, medir mercadoria", "errar a medida, desnivelar a balança", "reaferir o peso no mercado", "concluir a pesagem justa"),
    ("vilt", "curar ferimento, sarar doente com bálsamo", "adoecer, fraquejar o corpo", "recobrar gradualmente a saúde dia a dia", "cicatrizar a marca definitiva"),

    ("bar", "irritar, importunar", "acalmar, apaziguar", "voltar a irritar", "voltar a apaziguar"),
    ("dai", "pensar, conceber na mente", "esvaziar pensamento, desconceber", "repensar, meditar de novo", "voltar a esvaziar o pensamento (oda'ai-)"),
    ("dak", "flanquear à direita, ordenar ala destra", "desalinhar a direita", "reordenar a direita", "voltar a desalinhar a direita (oda'ak-)"),
    ("doot", "entediar-se, enfadar-se", "estimular, despertar interesse", "voltar a entediar-se", "voltar a despertar do tédio (oda'oot-)"),
    ("dur", "brilhar, resplandecer", "obscurecer, apagar brilho", "voltar a brilhar", "voltar a obscurecer (oda'ur-)"),
    ("elf", "sacralizar, consagrar, santificar", "profanar, dessacralizar", "ressacralizar, reconsagrar", "voltar a profanar"),
    ("es", "ser, estar, existir", "deixar de ser, inexistir", "restituir ao ser (odes-)", "voltar a inexistir (odaes-)"),
    ("fas", "padecer, sofrer dor", "aliviar a dor, consolar", "voltar a padecer", "voltar a aliviar a dor"),
    ("gald", "guardar, carregar, custodiar", "abandonar custódia, desguarnecer", "re-guardar, reassumir guarda", "voltar a abandonar"),
    ("galdex", "sacar, desembainhar lâmina", "reembainhar, guardar arma", "voltar a desembainhar", "voltar a reembainhar"),
    ("gel", "transladar, levar, conduzir", "reter, imobilizar carga", "retransladar, trazer de volta", "voltar a reter"),
    ("gir", "crescer, erguer-se, brotar", "diminuir, minguar, abater", "voltar a crescer, reerguer", "voltar a diminuir"),
    ("giz", "amar, estimar com devoção", "odiar, esquecer volitivamente", "voltar a amar", "voltar a odiar"),
    ("illan", "iluminar por dentro, inspirar luz (in+lan)", "apagar a luz interior", "reiluminar internamente (odillan-)", "voltar a apagar a luz interior"),
    ("illot", "embelezar, adornar (in+lota)", "desadornar, desfeiar", "readornar, reembelezar (odillot-)", "voltar a desadornar"),
    ("in", "iniciar, dar princípio a", "interromper início, abortar", "reiniciar, recomeçar (odin-)", "voltar a interromper"),
    ("intul", "enlouquecer, inflamar-se em furor", "recobrar a razão, serenar", "voltar a enlouquecer (odintul-)", "voltar a serenar"),
    ("is", "compreender, saber, conhecer", "ignorar, desconhecer", "voltar a compreender (odis-)", "voltar a ignorar"),
    ("kam", "embriagar, inebriar", "tornar sóbrio, desencantar", "voltar a embriagar", "voltar a tornar sóbrio"),
    ("kaz", "viver, nascer, habitar", "perecer, morrer, falecer", "ressuscitar, renascer", "voltar a perecer"),
    ("kel", "mover em conjunto, manobrar", "dispersar, desbandar", "reagrupar em marcha", "voltar a dispersar"),
    ("kelad", "aproximar-se, vir, convocar", "afastar-se, retirar-se", "retornar, voltar a aproximar-se", "voltar a afastar-se"),
    ("kelex", "escapar, evadir-se", "estagnar, ficar retido", "voltar a escapar", "voltar a ficar retido"),
    ("kellitr", "cantar em coro, harmonizar em conjunto", "desfazer o coro", "reunir o coro novamente", "voltar a desfazer o coro"),
    ("kel'un", "escoltar, acompanhar em guarda", "abandonar escolta", "reescoltar", "voltar a abandonar escolta"),
    ("kit", "escrever, lavrar em registro", "perdoar institucionalmente, rasurar", "reescrever, relavrar", "voltar a rasurar/perdoar"),
    ("kom", "beber, sorver", "privar de fluidos, dar sede", "voltar a beber", "voltar a dar sede"),
    ("kos", "esconder, sepultar, escavar", "expor, revelar, transbordar", "reesconder, resepultar", "voltar a expor/revelar"),
    ("krad", "criar, dar existência", "destruir, descriar, arruinar", "recriar, regenerar", "voltar a destruir"),
    ("lakanav", "amaldiçoar, votar ao mal", "desfazer maldição", "voltar a amaldiçoar", "voltar a desfazer maldição"),
    ("lan", "emanar luz, alumiar", "obliterar a luz, eclipsar", "reiluminar, voltar a alumiar", "voltar a obliterar a luz"),
    ("let", "falar, dizer, proferir, chamar", "silenciar, calar", "reiterar a fala, repetir", "voltar a silenciar"),
    ("litr", "vibrar, cantar, soar em música", "desafinar, semear dissonância", "voltar a entoar, recantar", "voltar a desafinar"),
    ("mak", "comer, alimentar-se", "esfomear, privar de alimento", "voltar a comer", "voltar a esfomear"),
    ("met", "glorificar, regozijar-se, exaltar", "humilhar, envergonhar", "reglorificar, voltar a exaltar", "voltar a humilhar"),
    ("mir", "ver, olhar, vigiar, contemplar", "cegar, tirar a visão", "rever, tornar a contemplar", "voltar a cegar"),
    ("mob", "beneficiar, dar, conceder", "privar de favor, lesar", "voltar a conceder", "voltar a privar de favor"),
    ("mobanav", "bendizer, abençoar", "retirar bênção", "voltar a abençoar", "voltar a retirar bênção"),
    ("mollet", "julgar, sentenciar (mon+let)", "revogar juízo, absolver sem mérito", "rejulgar, revisar processo", "voltar a revogar juízo"),
    ("nav", "transformar, tornar-se, converter", "petrificar, impedir mutação", "retransformar", "voltar a impedir mutação"),
    ("par", "merecer, ser digno, ter parte em", "desmerecer, perder direito", "voltar a merecer", "voltar a desmerecer"),
    ("pas", "precisar, necessitar, desejar", "prescindir, dispensar", "voltar a precisar", "voltar a prescindir"),
    ("said", "afiar, amolar, esculpir na rocha", "embotar lâmina, cegar fio", "reafiar, reesculpir", "voltar a embotar"),
    ("sfar", "proteger, defender, livrar", "aniquilar, exterminar", "voltar a proteger", "voltar a aniquilar"),
    ("sif", "contar histórias, narrar crônica", "omitir crônica, silenciar história", "recontar história", "voltar a omitir crônica"),
    ("sin", "flanquear à esquerda", "desguarnecer a esquerda", "reordenar a esquerda", "voltar a desguarnecer a esquerda"),
    ("skor", "crer, professar fé", "descrer, apostatar", "voltar a crer", "voltar a descrer"),
    ("tek", "fazer, fabricar, construir, forjar", "desfazer obra, sabotar, demolir", "refazer, reconstruir", "voltar a desfazer obra"),
    ("tok", "governar, reger com soberania", "desgovernar, subverter ordem", "voltar a governar", "voltar a desgovernar"),
    ("tol", "formar com beleza, aformosear", "desfigurar, deformar", "reaformosear", "voltar a desfigurar"),
    ("tor", "possuir, deter, agarrar", "perder a posse, largar", "reaver, retomar posse", "voltar a perder posse"),
    ("torex", "tomar à força, conquistar", "restituir à força, devolver presa", "retomar à força", "voltar a restituir à força"),
    ("trak", "marchar, comandar vanguarda", "retrair-se, hesitar", "recuar taticamente (otrak-)", "voltar a retrair-se"),
    ("vur", "arder, queimar em chama", "congelar, esfriar, extinguir ardor", "voltar a arder", "voltar a congelar"),
    ("yn", "andar, caminhar, entrar, descer", "estancar o passo, deter-se", "voltar a caminhar (odyn-)", "voltar a estancar o passo"),
    # --- Expansão Eufônica V8.1 (raízes verbais) ---
    ('lix', 'lavar, limpar com água', 'sujar, macular', 'relavar, enxaguar', 'voltar a sujar'),
    ('kerd', 'cortar lenha, talhar madeira', 'emendar, unir o que foi cortado', 'recortar, aparar', 'voltar a emendar'),
    ('zal', 'pagar, quitar uma dívida', 'dever, ficar inadimplente', 'pagar de novo, reembolsar', 'voltar a dever'),
    ('rux', 'cozinhar ao fogo, assar no caldeirão', 'deixar cru, retirar do fogo', 'reaquecer a comida', 'voltar a esfriar a comida'),
    ('hesk', 'perguntar, indagar', 'calar a pergunta, não indagar', 'perguntar de novo, insistir', 'voltar a calar a pergunta'),
    ('bod', 'responder, replicar', 'negar resposta, emudecer', 'responder de novo, treplicar', 'voltar a negar resposta'),
    ('nyk', 'abrir porta ou baú', 'fechar, trancar', 'reabrir', 'voltar a fechar'),
    ('sek', 'sentar-se, assentar-se', 'levantar-se, erguer-se do assento', 'sentar-se de novo', 'voltar a levantar-se'),
    ('kraz', 'rir, alegrar-se', 'chorar, lamentar', 'voltar a rir', 'voltar a chorar'),
    ('tav', 'contar, enumerar moedas ou dias', 'perder a conta', 'recontar, conferir', 'voltar a perder a conta'),
    ('hux', 'vestir, cobrir com roupa', 'despir, desnudar', 'revestir, trocar de roupa', 'voltar a despir'),
    ('pek', 'quebrar, partir', 'consertar, remendar', 'voltar a quebrar', 'voltar a consertar'),
    ('lyr', 'esperar, aguardar com esperança', 'desesperar, perder a esperança', 'voltar a esperar', 'voltar a desesperar'),
    ('gob', 'trocar, negociar, mercadejar', 'recusar a troca, desfazer negócio', 'renegociar', 'voltar a desfazer o negócio'),
    ('rop', 'chamar, convocar pelo nome', 'dispensar, mandar embora', 'chamar de novo', 'voltar a dispensar'),
    ('tuk', 'cavar, escavar a terra', 'aterrar, cobrir a cova', 'recavar', 'voltar a aterrar'),
    ('xel', 'nevar, cair neve', 'degelar, derreter a neve', 'voltar a nevar', 'voltar a degelar'),
    ('kask', 'coser, costurar', 'descoser, desfazer a costura', 'recoser, remendar o pano', 'voltar a descoser'),
    ('drak', 'puxar, arrastar, rebocar', 'soltar, largar a corda', 'puxar de novo', 'voltar a soltar'),
    ('gelm', 'acender a candeia, atear fogo à mecha', 'apagar a candeia', 'reacender a candeia', 'voltar a apagar a candeia'),
    ('sulv', 'cantarolar, entoar baixinho', 'emudecer o canto', 'voltar a cantarolar', 'voltar a emudecer o canto'),
    ('hab', 'acolher, hospedar o viajante', 'expulsar, negar abrigo', 'voltar a acolher', 'voltar a negar abrigo'),
]

# Adição das 13 raízes verbais primárias e poéticas canônicas (totalizando 68 raízes na Matriz Quadripartite = 272 verbos)
VERB_ROOTS.extend([
    ("fain", "piratear, saquear no mar", "proteger comércio naval", "voltar a piratear", "voltar a proteger rota naval"),
    ("far", "cultivar trigo, alimentar com pão", "esterilizar solo", "recultivar seara", "voltar a esterilizar"),
    ("fer", "soprar (o vento), ventar", "acalmar os ventos", "voltar a soprar", "voltar a acalmar os ventos"),
    ("kindr", "unir em comunhão, aliar", "cindir, criar discórdia", "reunificar em aliança", "voltar a cindir"),
    ("mad", "conceber no ventre, gerar (part. madet)", "abortar, tornar estéril", "voltar a conceber", "voltar a tornar estéril"),
    ("nemr", "lembrar, recordar na memória (fut. nemnu, nr -> nn)", "apagar da memória, olvidar", "relembrar, comemorar", "voltar a apagar da memória"),
    ("oub", "entoar em prelúdio, elevar cântico (imperf. oubba no Halylitror)", "calar prelúdio", "voltar a entoar prelúdio (odoub-)", "voltar a calar prelúdio (odaoub-)"),
    ("ox", "guerrear, combater em campo", "pacificar o campo", "voltar a guerrear", "voltar a pacificar"),
    ("tim", "temer, reverenciar com assombro sagrado", "perder o temor, ousar", "voltar a temer", "voltar a perder o temor"),
    ("tul", "delirar, perder a razão", "recobrar lucidez", "voltar a delirar", "voltar a recobrar lucidez"),
    ("vel", "sombrear, cobrir de penumbra", "desvelar, dissipar sombra", "voltar a sombrear", "voltar a dissipar sombra"),
    ("vok", "sangrar, verter sangue", "estancar sangue", "voltar a sangrar", "voltar a estancar sangue"),
    ("vul", "querer, determinar pela vontade", "abster-se de querer, renunciar", "voltar a determinar", "voltar a renunciar"),
])

# Integração da Expansão Lexical de Grande Escala V8.1 (O Conde)
import sys as _sys
_sandbox_dir = os.path.dirname(os.path.abspath(__file__))
if _sandbox_dir not in _sys.path:
    _sys.path.insert(0, _sandbox_dir)
from lexico_expansao_v8_1 import (
    EXPANSAO_VERB_ROOTS,
    EXPANSAO_NOUNS,
    EXPANSAO_ADJECTIVES,
    EXPANSAO_ADVERBS,
)

NOUNS.extend(EXPANSAO_NOUNS)
ADJECTIVES.extend(EXPANSAO_ADJECTIVES)
VERB_ROOTS.extend(EXPANSAO_VERB_ROOTS)

# Deduplicação canônica preservando a primeira ocorrência
def _dedup_by_first(items):
    seen = set()
    out = []
    for item in items:
        k = item[0]
        if k not in seen:
            seen.add(k)
            out.append(item)
    return out

NOUNS = _dedup_by_first(NOUNS)
ADJECTIVES = _dedup_by_first(ADJECTIVES)
VERB_ROOTS = _dedup_by_first(VERB_ROOTS)
VERB_ROOTS.sort(key=lambda x: x[0])

print(f"Inventário carregado: {len(NOUNS)} substantivos, {len(ADJECTIVES)} adjetivos, {len(VERB_ROOTS)} raízes verbais primárias ({len(VERB_ROOTS)*4} verbos nos 4 eixos).")

# 2.4. ADVÉRBIOS (Temporais, Locativos, Sintáticos e Modais em -vë)
ADVERBS = [
    # --- Advérbios e Partículas da Vida Diária (Era Antiga -> Era Clássica V8.1) ---
    ("yo", "Afirmação Prática", "partícula afirmativa arcaica", "sim, certamente, com certeza"),
    ("ne", "Negação Prática Pré-Verbal", "raiz primária ne", "não (negação factual antes do verbo)"),
    ("kildanvë", "Modal de Frio", "kildan + -vë", "gélidamente, sob frio cortante"),
    ("vuranvë", "Modal de Aconchego", "vuran + -vë", "calorosamente, ao calor da lareira"),
    ("zenanvë", "Modal de Fidelidade", "zenan + -vë", "lealmente, de coração amigo sincero"),
    ("halkanvë", "Modal de Marcha", "halkan + -vë", "a passo firme, marchando resolutamente"),
    ("dakkanvë", "Modal de Fartura", "dakkan + -vë", "com fartura, regaladamente"),
    ("gobanvë", "Modal de Justiça Comercial", "goban + -vë", "honestamente, por preço justo"),
    ("alenvë", "Temporal Matinal", "alen + -vë", "ao raiar da manhã, com o nascer do sol"),
    ("vesenvë", "Temporal Noturno", "vesen + -vë", "à noite fechada, na hora do repouso"),

    # Temporais, Locativos e de Afirmação/Negação
    ("alim", "Temporal / Locativo", "raiz primária alim", "onde; outrora, antes que"),
    ("ne", "Negação Sintática Pré-Verbal", "raiz primária ne", "não (negação factual simples antes do verbo)"),
    ("sambel", "Temporal Composto", "san (este) + bel (dia) (nb -> mb)", "hoje, neste dia"),
    ("santonk", "Temporal Composto", "san (este) + tonkre (tempo)", "agora, neste instante, no presente"),
    ("zo", "Afirmativo / Modal Cósmico", "raiz primária zo (origem de o-/od-)", "assim, deste modo (em 'Zo es': Assim sê! / Amém)"),
    # --- Expansão Eufônica V8.1 (advérbios e interrogativos) ---
    ('krazavë', 'Modal de Alegria', 'kraza + -vë', 'alegremente, com riso'),
    ('lyravë', 'Modal de Esperança', 'lyra + -vë', 'esperançosamente'),
    ('habavë', 'Modal de Hospitalidade', 'haba + -vë', 'hospitaleiramente'),
    ('tonkrilavë', 'Modal Temporal', 'tonkrila + -vë', 'brevemente, num instante'),
    ('xelavë', 'Modal de Clima', 'xela + -vë', 'sob neve, nevadamente'),
    ('kemyga', 'Interrogativo de Quantidade', 'ke + myga', 'quanto? quantos? (kemyga paror esu? = quanto custa?)'),
    ('kebel', 'Interrogativo Temporal', 'ke + bel', 'quando? em que dia?'),
    ('kemixi', 'Interrogativo Pessoal', 'ke + mixi', 'quem?'),
    ('kesan', 'Interrogativo Neutro', 'ke + san', 'o quê? que coisa?'),
]
# Adicionar todos os advérbios modais em -vë gerados a partir de cada adjetivo
for adj, meaning, _, _ in ADJECTIVES:
    stem = adj[:-1] if (adj.endswith("a") or adj.endswith("e")) else adj
    adv_form = f"{adj}vë" if adj.endswith("a") else f"{stem}avë"
    ADVERBS.append((adv_form, "Modal Regulado (-vë com diérese)", f"{adj} + -vë", f"de modo {meaning.split(',')[0]}"))

# Adicionar advérbios especiais do Halylitror e da Expansão V8.1
ADVERBS.append(("rukraletavë", "Modal Composto (-vë)", "rukraleta + -vë", "em altíssima voz, com clamor trovejante"))
ADVERBS.extend(EXPANSAO_ADVERBS)
ADVERBS = _dedup_by_first(ADVERBS)
ADVERBS.sort(key=lambda x: x[0])

# 2.5. PRONOMES (Pessoais Retos, Possessivos, Oblíquos e Demonstrativos Dêiticos)
PERSONAL_PRONOUNS = [
    ("1ª Pessoa Singular (Eu)", "eo (pro-drop compulsório)", "ey", "em", "ej / ei"),
    ("2ª Pessoa Singular (Tu)", "to (pro-drop compulsório)", "ty", "tim", "tij / ti"),
    ("1ª Pessoa Plural (Nós)", "no (pro-drop compulsório)", "ny", "nom", "noj / noi"),
    ("2ª Pessoa Plural (Vós)", "vo (pro-drop compulsório)", "vy", "vom", "voj / voi"),
]

DEMONSTRATIVE_PRONOUNS = [
    ("San", "1ª Deíxe (Este / Isto: próximo ao locutor)", "San", "Sany", "Sani (arc. Sanj)", "Sanom", "Sano (1ª Decl. Saner)", "Sanye", "Sanoi", "Sanos"),
    ("Tan", "2ª Deíxe (Esse / Isso: próximo ao interlocutor ou anafórico)", "Tan", "Tany", "Tani (arc. Tanj)", "Tanom", "Tano", "Tanye", "Tanoi", "Tanos"),
    ("Kan", "3ª Deíxe (Aquele / Aquilo / Ele: distante ou transcendente)", "Kan", "Kany", "Kani (arc. Kanj)", "Kanom", "Kano", "Kanye", "Kanoi", "Kanos"),
]

# 2.6. NUMERAIS (Cardinais, Ordinais em -ta, Dezenas, Centenas, Milhares)
NUMERALS = [
    ("1", "id", "Itta (dt -> tt)", "Itte / Itta", "Ittady / Itty", "Ittaj / Itti", "Ittam / Ittom", "idda (id+da: único)"),
    ("2", "do", "Dota", "Dote / Dota", "Dotady / Doty", "Dotaj / Doti", "Dotam / Dotom", "Dokrom (20), Dotakazeti"),
    ("3", "zel", "Zelta", "Zelte / Zelta", "Zeltady / Zelty", "Zeltej / Zelti", "Zeltam / Zeltom", "Zelkrom (30)"),
    ("4", "kat", "Katta (tt)", "Katte / Katta", "Kattady / Katty", "Kattaj / Katti", "Kattam / Kattom", "Katkom (40)"),
    ("5", "vex", "Vexta", "Vexte / Vexta", "Vextady / Vexty", "Vextaj / Vexti", "Vextam / Vextom", "Vexkrom (50)"),
    ("6", "tir", "Tirta", "Tirte / Tirta", "Tirtady / Tirty", "Tirtaj / Tirti", "Tirtam / Tirtom", "Tirkrom (60)"),
    ("7", "san", "Santa", "Sante / Santa", "Santady / Santy", "Santaj / Santi", "Santam / Santom", "Sankrom (70)"),
    ("8", "nyr", "Nyrta (Ablaut de nir)", "Nyrte / Nyrta", "Nyrtady / Nyrty", "Nyrtaj / Nyrti", "Nyrtam / Nyrtom", "Nyrkrom (80)"),
    ("9", "nev", "Nepta (vt -> pt)", "Nepte / Nepta", "Neptady / Nepty", "Neptaj / Nepti", "Neptam / Neptom", "Nevkrom (90)"),
    ("10", "krom", "Kromta", "Kromte / Kromta", "Kromtady / Kromty", "Kromtaj / Kromti", "Kromtam / Kromtom", "Dokrom (20), Zelkrom (30)"),
    ("100", "Dygum", "Dygumta", "Dygumte / Dygumta", "Dygumy", "Dygumi", "Dygumom", "Centena de Chancelaria"),
    ("1000", "Myga", "Mygata", "Mygate / Mygata", "Mygady / Mygay", "Mygaj / Mygai", "Mygam / Mygaom", "amyga / amygata (inumerável)"),
]

# 2.7. PREPOSIÇÕES, CONJUNÇÕES, PARTÍCULAS E AFIXOS PRODUTIVOS
PARTICLES_AND_AFFIXES = [
    ("ad", "Preposição Direcional e Final", "Rege obrigatoriamente Acusativo (direção: ad Veloxem, ad xeros) ou Infinitivo Absoluto em -ur (finalidade: ad molletur, ad kradur)."),
    ("ex", "Preposição de Origem e Proveniência", "Rege obrigatoriamente Dativo (ex lakej, ex Hali Hali, ex akuraj Mariaj, ex Kani). Em composição verbal: kelex-, galdex-, torex- (dispara xr -> rr no passado/futuro)."),
    ("in", "Preposição Bipolar (Movimento vs. Estado)", "Rege Acusativo para movimento/entrada (in Oratoxem, in oratom) e Dativo para posição estática ou temporal (in xeri, in oxej, in fili, in tonkrej). Em composição: in+lota -> illot-, in+lan -> illan- (nl -> ll)."),
    ("ponu", "Preposição de Subordinação", "Sob, debaixo do poder ou jurisdição de (ex.: fassa ponu Pontius Pilatus; ponu vulej vy)."),
    ("et", "Conjunção Coordenativa Aditiva", "E (une sintagmas nominais do mesmo caso ou orações coordenadas)."),
    ("u", "Conjunção Coordenativa Alternativa", "Ou (alternância lógica ou retórica)."),
    ("ke", "Conjunção Integrante e Pronome Relativo", "Que, o qual (invariável: Patte ny, ke in xeri esu; ad ke = para que, com Subjuntivo)."),
    ("ko", "Conjunção Comparativa e Temporal", "Como, assim como, enquanto, quando (in oxej ko in xeri; ko no akitun)."),
    ("so", "Conjunção Condicional e Concessiva", "Se (Realis com Indicativo; Irrealis com Subjuntivo em ambas as orações); desde que, embora."),
    ("nam", "Conjunção Explicativa e Adversativa", "Pois, porque; mas, ora (em narrativa histórica e cosmogônica)."),
    ("ta", "Partícula Conclusiva e Adversativa", "Portanto, contudo, todavia, ainda assim."),
    ("ante ke", "Locução Conjuntiva Temporal", "Antes que (rege Subjuntivo: ante ke Felo Oratypattedy okazbake)."),
    ("-ka", "Clítico Interrogativo Enclítico", "Aglutinado ao final do verbo conjugado sem alterar a ordem da frase (Miruska?; na 2ª Pl dispara tk -> kk: Letut + -ka -> Letukka?)."),
    ("a-", "Prefixo Verbal e Nominal Privativo", "2º Eixo da Matriz Quadripartite: inverte organicamente a substância da ação ou qualidade (sfar- -> asfar-, giz- -> agiz-, kit- -> akit-, tonkre -> atonkre)."),
    ("o- / od-", "Prefixo Verbal Iterativo e Restitutivo", "3º Eixo da Matriz Quadripartite (de zo): repetição, retorno ou ressurreição; o- antes de consoante (okaz-, osfar-), od- antes de vogal (odes-)."),
    ("od-a-", "Prefixo Verbal Iterativo-Privativo", "4º Eixo da Matriz Quadripartite: repetição de ação negada (odasfar-, odakaz-); dispara haplologia dental antes de d- (od-a-dur- -> oda'ur-)."),
    ("-ia", "Sufixo Derivacional Toponímico e Locativo", "Forma substantivos de lugar, instituição ou província (Treppênia, Mirypalkia, molletia, kitia, tepia, elfia)."),
    ("-te", "Sufixo Derivacional de Agente", "Forma substantivos de agente ou ofício; dispara dt/kt -> tt (Kratte, Trátte, Totte, Tette, galtte, saitte, mirte, litrte)."),
    ("-or / -re", "Sufixo Derivacional de Abstração e Obra", "Forma substantivos abstratos ou resultados de ação na 2ª Declinação (belor, mobor, litror, daior, isor, tekor, krador)."),
    ("-tek", "Sufixo Derivacional de Instrumento", "Forma substantivos de ferramenta ou utensílio na 2ª Declinação; dispara dt/kt -> tt (lettek, litrtek, tettek, sfartek, saittek)."),
    ("-il", "Sufixo Derivacional Diminutivo", "Forma diminutivos ou afetivos na 2ª Declinação (tepil, koril, vevaril)."),
    ("-gar / -ar / -on", "Sufixo Derivacional Aumentativo e Solene", "Forma aumentativos monumentais na 2ª Declinação; dispara pg -> gg (teggar, litrgar, oxegar, karegar, mirgar, rixegar)."),
    ("-n / -ni", "Sufixo do Superlativo Absoluto Orgânico", "Acoplado à raiz no singular (-n) e plural (-ni); dispara rn -> ld (mild, kold, feld), ln -> ll (bell, vell, fill) e nn/mn -> m (nemm)."),
    ("-vë", "Sufixo Adverbial Modal com Diérese", "Único morfema com trema diferencial na V8.1; converte adjetivos em advérbios de modo (mobavë, kuravë, elfavë, rukravë)."),
    ("-ta", "Sufixo de Numeral Ordinal", "Converte cardinais em ordinais; dispara dt -> tt (Itta) e vt -> pt (Nepta)."),
]

# 2.8. REGISTRO DIACRÔNICO, FÓRMULAS LITÚRGICAS CRISTALIZADAS, VARIANTES PLEBEIAS (C/Ç) E FORMAS PRÉ-SÍNCRESE
DIACHRONIC_AND_VARIANT_ENTRIES = [
    # Fórmulas Litúrgicas e Siderais Cristalizadas
    ("Metuses", "Fórmula Litúrgica Cristalizada (Optativo Arcaico)", "metur (glorificar)", "Ave! / Salve! / Sejas glorificada! (abertura solene do Metuses Maria; forma regular moderna: Metse!)."),
    ("Metse", "Imperativo Médio-Passivo Regular", "met- + -se", "Alegra-te! / Sê glorificada! (equivalente regular moderno do arcaísmo Metuses)."),
    ("vox", "Dativo Sideral / Litúrgico Arcaico", "vok + -j (kj -> x)", "ao sangue / no sangue (forma pré-vocalização preservada na poesia sideral; na V8.1 padrão: voki)."),
    ("Durrum", "Fórmula Sideral Cristalizada", "dur- + -ru + -m", "Brilharão / Brilharei (fórmula gnômica em 'Lexer durrum in fily': As estrelas brilharão no cerne)."),
    ("Zo es", "Fórmula Sacra de Fechamento", "zo (assim) + es (sê!)", "Assim sê! / Amém! (fechamento litúrgico canônico das três orações e do Halylitror)."),
    # Variantes Plebeias / Vulgares e Dialetais (Estigmatizadas pela Chancelaria Imperial)
    ("Coriceçte", "Variante Vulgar / Plebeia (C/Ç)", "Korikeste", "Grafia e pronúncia plebeia (com ç e c por k) da Grande Casa Nobre Korikeste."),
    ("Coryvela", "Variante Vulgar / Plebeia", "Koryvela", "Grafia plebeia com c inicial para a Floresta de Treppênia (norma culta: Koryvela)."),
    ("façucor", "Variante Vulgar / Plebeia (Ç)", "fassukor", "Forma popular com ç intervocálico por ss para 'tristeza profunda' (norma culta: fassukor)."),
    ("Ferychope", "Variante Dialetal / Plebeia", "Ferykrope", "Forma popular palatalizada para a província de Ferykrope (Campina dos Ventos)."),
    ("mectep", "Variante Vulgar / Plebeia", "mektep", "Grafia popular com ct para 'casebre, choupana' (norma culta: mektep)."),
    ("raçe", "Variante Vulgar / Plebeia (Ç)", "rase", "Pronúncia plebeia com ç para 'língua, idioma' (norma culta: rase)."),
    ("Rixelac", "Variante Vulgar / Apocopada", "Rixelaka", "Forma apocopada com c final para a cordilheira de Rixelaka (Os Picos Gélidos)."),
    ("Vokát", "Exônimo Plebeu Apocopado", "Vokátte", "Designação popular apocopada para o entidade/título Vokátte (O Guia de Sangue)."),
    # Formas Arcaicas Pré-Síncrese de Celia e Termos Expurgados Documentados nos Manuais
    ("Laurie", "Forma Arcaica Pré-Síncrese de Celia", "lauri", "Forma antiga com ditongo final -ie para 'ouro', reduzida a lauri pela Síncrese de Celia."),
    ("Mixie", "Forma Arcaica Pré-Síncrese de Celia", "mixi", "Forma antiga para 'pessoa, indivíduo', reduzida a mixi pela Síncrese de Celia."),
    ("Sotime", "Forma Arcaica Pré-Síncrese de Celia", "sotim", "Forma antiga de 1ª Declinação para 'rosto, face', apocopada para sotim (2ª Decl.)."),
    ("Xune / xün", "Forma Arcaica Pré-Síncrese / Grafia Expurgada", "xun", "Antigas formas para 'amarelo imperial', padronizadas na Era Clássica V8.1 como xun."),
    ("Theus / vane", "Termos Arcaicos Expurgados", "Gyos", "Designações pré-imperiais para 'Deus', formalmente banidas e substituídas por Gyos."),
    ("nomo", "Termo Arcaico Expurgado", "mon", "Antigo vocábulo para 'nome', expurgado pela Chancelaria em favor da raiz sagrada mon."),
    ("kropé", "Grafia Arcaica Expurgada", "krope", "Grafia com acento agudo final expurgada pela Lei da Restrição Diacrítica (unicidade de Vé)."),
    ("Vé'el", "Grafia Arcaica Expurgada", "Ve'el", "Grafia com acento agudo + apóstrofo expurgada em favor de Ve'el (Domínio das Sombras)."),
    ("duru'u", "Hiato Arcaico Expurgado", "durru", "Antigo futuro com hiato de durur, substituído pela geminação vibrante durru (r+ru -> rru)."),
    ("mobu- / amobu-", "Tema Verbal Pré-Reforma", "mob- / amob-", "Antiga raiz verbal com -u- temático intrínseco, purificada para mob- / amob- (inf. mobur/amobur)."),
    ("dagbam / magbam / togbam / tragbam / tekbam", "Imperfeitos Pré-Assimilação Labial", "dabbam / mabbam / tobbam / trabbam / tebbam", "Estágios fonéticos intermediários de sonorização (kb -> gb) antes da Assimilação Labial Regressiva Total (kb -> bb)."),
]

# ==============================================================================
# 3. GERAÇÃO DO DICIONÁRIO GERAL EM SANDBOX E DO CORPUS EXAUSTIVO DE FORMAS
# ==============================================================================

def generate_all_files():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = r"D:\Conde_Treppio\sandbox"
    ex_dir = os.path.join(out_dir, "dicionario_exaustivo")
    os.makedirs(ex_dir, exist_ok=True)

    total_word_forms = 0
    full_json_db = {
        "metadata": {
            "title": "Dicionário Geral e Códice Morfológico Exaustivo da Língua Tréppia (Era Clássica V8.1)",
            "environment": "Sandbox",
            "nouns_count": len(NOUNS),
            "adjectives_count": len(ADJECTIVES),
            "adverbs_count": len(ADVERBS),
            "verb_roots_count": len(VERB_ROOTS),
            "verb_stems_quadripartite": len(VERB_ROOTS) * 4,
        },
        "substantivos": {},
        "adjetivos": {},
        "adverbios": {},
        "pronomes": {},
        "numerais": {},
        "particulas_e_afixos": {},
        "verbos_quadripartite": {},
    }

    md_lines = []
    md_lines.append("# Dicionário Geral e Códice Flexional Exaustivo da Língua Tréppia (Era Clássica V8.1 — Sandbox)\n")
    md_lines.append("**Autor:** O Conde (Assistente Filológico e Glotopoético do Tréppio)  ")
    md_lines.append("**Estatuto Documental:** Compilação Integral em Ambiente de Sandbox (`D:\\Conde_Treppio\\sandbox\\`)\n")
    md_lines.append("> [!IMPORTANT]")
    md_lines.append("> **Arquitetura Deste Dicionário Integral:**")
    md_lines.append(f"> Este códice reúne **todos os verbetes existentes no idioma Tréppio (V8.1)** separados estritamente por classe gramatical (**{len(NOUNS)} Substantivos e Nomes Próprios**, **{len(ADJECTIVES)} Adjetivos**, **{len(ADVERBS)} Advérbios**, **Pronomes Pessoais e Demonstrativos**, **Numerais**, **Preposições/Conjunções/Partículas/Afixos**, e **{len(VERB_ROOTS)} Raízes Verbais Primárias** projetadas nos **4 Eixos da Matriz Quadripartite = {len(VERB_ROOTS)*4} Verbos Independentes**). Cada verbete foi submetido ao motor morfofonológico das 21 Leis de Sandi Consonantal e Haplologia para exibir todas as suas terminações flexionais e derivacionais possíveis.\n")
    md_lines.append("---\n")

    # --------------------------------------------------------------------------
    # PARTE I: SUBSTANTIVOS (TODAS AS 8 FLEXÕES CASUAIS + 10 TERMINAÇÕES DERIVACIONAIS)
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte I: Substantivos Comuns, Abstratos, Topônimos e Nomes Próprios ({len(NOUNS)} Verbetes × 18 Transformações)\n")
    md_lines.append("Cada substantivo abaixo apresenta: **(1) Todas as 8 flexões casuais** (*Nom. Sg., Gen. Sg., Dat. Sg., Acu. Sg., Nom. Pl., Gen. Pl., Dat. Pl., Acu. Pl.*, observando a Reforma Vocalizada do Dativo `-i / -oi` na 2ª Declinação e `-ej / -erj` na 1ª Declinação) e **(2) Todas as 10 transformações derivacionais possíveis** de seu radical (*Adjetivo `-a`, Advérbio `-vë`, Superlativo Sg. `-n` e Pl. `-ni`, Lugar `-ia`, Agente `-te`, Abstrato `-or`, Instrumento `-tek`, Diminutivo `-il` e Aumentativo `-gar`*, com aplicação automática de `rn → ld`, `ln → ll`, `dt/kt → tt`, `pg → gg`).\n")
    md_lines.append("| Verbete (Nom. Sg.) | Decl. | Significado e Etimologia | Flexão Casual Singular (Gen. / Dat. / Acu.) | Flexão Casual Plural (Nom. / Gen. / Dat. / Acu.) | Transformações Derivacionais do Radical (`-a`, `-vë`, `-n/-ni`, `-ia`, `-te`, `-or`, `-tek`, `-il`, `-gar`) |")
    md_lines.append("| :--- | :---: | :--- | :--- | :--- | :--- |")

    for lemma, decl, meaning, etym in sorted(NOUNS, key=lambda x: x[0].lower()):
        d = decline_noun(lemma, decl)
        full_json_db["substantivos"][lemma] = {"declinacao": decl, "significado": meaning, "etimologia": etym, "formas": d}
        total_word_forms += len(d)
        sg_cases = f"*{d['Gen.Sg']} / {d['Dat.Sg']} / {d['Acu.Sg']}*"
        pl_cases = f"*{d['Nom.Pl']} / {d['Gen.Pl']} / {d['Dat.Pl']} / {d['Acu.Pl']}*"
        derivs = (
            f"Adj: **{d['Adj(-a)']}** | Adv: **{d['Adv(-vë)']}** | Sup: **{d['Superl.Sg(-n)']}/{d['Superl.Pl(-ni)']}** | "
            f"Lug: *{d['Lugar(-ia)']}* | Ag: *{d['Agente(-te)']}* | Abst: *{d['Abstrato(-or)']}* | "
            f"Inst: *{d['Instrum(-tek)']}* | Dim: *{d['Dimin(-il)']}* | Aum: *{d['Aument(-gar)']}*"
        )
        md_lines.append(f"| **{lemma}** | {decl}ª | {meaning} (`{etym}`) | {sg_cases} | {pl_cases} | {derivs} |")

    md_lines.append("\n---\n")

    # --------------------------------------------------------------------------
    # PARTE II: ADJETIVOS (POSITIVO, 8 CASOS NOMINALIZADOS, COMPARATIVO, SUPERLATIVO -n/-ni, ADVÉRBIO -vë, ABSTRATO -or)
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte II: Adjetivos Primários, Derivados e Supletivos ({len(ADJECTIVES)} Verbetes × 13 Transformações)\n")
    md_lines.append("Cada adjetivo abaixo é transformado em: **(1) Seus 8 casos quando substantivado/nominalizado**, **(2) Grau Comparativo** (incluindo a Supleção Teológica *moba → maer* e *kura → krer*), **(3) Grau Superlativo Absoluto Orgânico** (`-n` Sg. / `-ni` Pl., aplicando `rn → ld`, `ln → ll`, `nn/mn → m`), **(4) Advérbio Modal** (`-vë`) e **(5) Substantivo Abstrato** (`-or`).\n")
    md_lines.append("| Adjetivo (Positivo) | Significado | Flexão Singular (`Gen. / Dat. / Acu.`) | Flexão Plural (`Nom. / Gen. / Dat. / Acu.`) | Comparativo | Superlativo Orgânico (`-n / -ni`) | Advérbio (`-vë`) e Abstrato (`-or`) |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for adj, meaning, comp, sup_ov in sorted(ADJECTIVES, key=lambda x: x[0].lower()):
        inf = inflect_adjective(adj, meaning, comp, sup_ov)
        full_json_db["adjetivos"][adj] = inf
        total_word_forms += 13
        sg_c = f"*{inf['Gen.Sg']} / {inf['Dat.Sg']} / {inf['Acu.Sg']}*"
        pl_c = f"*{inf['Nom.Pl']} / {inf['Gen.Pl']} / {inf['Dat.Pl']} / {inf['Acu.Pl']}*"
        md_lines.append(
            f"| **{adj}** | {meaning} | {sg_c} | {pl_c} | **{inf['Comparativo']}** | "
            f"**{inf['Superl.Sg(-n)']} / {inf['Superl.Pl(-ni)']}** | **{inf['Adv.Modal(-vë)']}** / *{inf['Subst.Abstrato(-or)']}* |"
        )

    md_lines.append("\n---\n")

    # --------------------------------------------------------------------------
    # PARTE III: ADVÉRBIOS (TEMPORAIS, LOCATIVOS, SINTÁTICOS E MODAIS EM -vë)
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte III: Advérbios Temporais, Locativos, Sintáticos e Modais ({len(ADVERBS)} Verbetes)\n")
    md_lines.append("Os advérbios são invariáveis em caso, mas os advérbios modais exibem obrigatoriamente a **diérese diferencial (`-vë`)** para isolar a fronteira morfológica do radical adjetival.\n")
    md_lines.append("| Advérbio | Subclasse Adverbial | Etimologia e Morfologia | Significado e Uso Sintático |")
    md_lines.append("| :--- | :--- | :--- | :--- |")

    for adv, subc, etym, mean in ADVERBS:
        full_json_db["adverbios"][adv] = {"subclasse": subc, "etimologia": etym, "significado": mean}
        total_word_forms += 1
        md_lines.append(f"| **{adv}** | {subc} | `{etym}` | {mean} |")

    md_lines.append("\n---\n")

    # --------------------------------------------------------------------------
    # PARTE IV: SISTEMA PRONOMINAL (PESSOAIS E DEMONSTRATIVOS DÊITICOS COM TODAS AS FLEXÕES)
    # --------------------------------------------------------------------------
    md_lines.append("## Parte IV: Sistema Pronominal Completo (Pessoais e Demonstrativos em Todos os Casos)\n")
    md_lines.append("### 4.1. Pronomes Pessoais (Com Lei do Pro-Drop Compulsório no Nominativo)\n")
    md_lines.append("| Pessoa Gramatical | Nominativo (Reto)* | Genitivo (Possessivo) | Acusativo (Objeto Direto / Dir. `ad, in`) | Dativo Vocalizado / Litúrgico (Obj. Indireto / `ex, in`) |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for p_label, nom, gen, acu, dat in PERSONAL_PRONOUNS:
        full_json_db["pronomes"][p_label] = {"Nom": nom, "Gen": gen, "Acu": acu, "Dat": dat}
        total_word_forms += 6
        md_lines.append(f"| **{p_label}** | **{nom}** | **{gen}** | **{acu}** | **{dat}** |")

    md_lines.append("\n### 4.2. Pronomes Demonstrativos Dêiticos (Declinados nos 8 Casos/Números)\n")
    md_lines.append("| Pronome Base | Esfera Dêitica | Nom. Sg. | Gen. Sg. | Dat. Sg. | Acu. Sg. | Nom. Pl. | Gen. Pl. | Dat. Pl. | Acu. Pl. |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for d_base, esfera, n_sg, g_sg, d_sg, a_sg, n_pl, g_pl, d_pl, a_pl in DEMONSTRATIVE_PRONOUNS:
        full_json_db["pronomes"][d_base] = {
            "esfera": esfera, "Nom.Sg": n_sg, "Gen.Sg": g_sg, "Dat.Sg": d_sg, "Acu.Sg": a_sg,
            "Nom.Pl": n_pl, "Gen.Pl": g_pl, "Dat.Pl": d_pl, "Acu.Pl": a_pl
        }
        total_word_forms += 10
        md_lines.append(f"| **{d_base}** | {esfera} | **{n_sg}** | *{g_sg}* | *{d_sg}* | *{a_sg}* | **{n_pl}** | *{g_pl}* | *{d_pl}* | *{a_pl}* |")

    md_lines.append("\n---\n")

    # --------------------------------------------------------------------------
    # PARTE V: SISTEMA NUMÉRICO (CARDINAIS, ORDINAIS EM -ta E TODAS AS FLEXÕES CASUAIS)
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte V: Numerais Cardinais, Ordinais (`-ta`) e Flexões Casuais ({len(NUMERALS)} Séries)\n")
    md_lines.append("| Valor | Cardinal | Ordinal (`-ta` com Sandi) | Nom. (1ª/2ª Decl.) | Gen. Sg. (`-dy / -y`) | Dat. Sg. (`-j / -i`) | Acu. Sg. (`-m / -om`) | Compostos e Derivados Canônicos |")
    md_lines.append("| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for val, card, ord_f, nom_f, gen_f, dat_f, acu_f, comps in NUMERALS:
        full_json_db["numerais"][val] = {
            "cardinal": card, "ordinal": ord_f, "Nom": nom_f, "Gen": gen_f, "Dat": dat_f, "Acu": acu_f, "compostos": comps
        }
        total_word_forms += 10
        md_lines.append(f"| **{val}** | **{card}** | **{ord_f}** | *{nom_f}* | *{gen_f}* | *{dat_f}* | *{acu_f}* | {comps} |")

    md_lines.append("\n---\n")

    # --------------------------------------------------------------------------
    # PARTE VI: PREPOSIÇÕES, CONJUNÇÕES, PARTÍCULAS, CLÍTICOS E AFIXOS PRODUTIVOS
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte VI: Preposições, Conjunções, Partículas, Clíticos e Afixos ({len(PARTICLES_AND_AFFIXES)} Entradas)\n")
    md_lines.append("| Morfema / Partícula | Classificação Gramatical | Regência Sintática, Comportamento Fonotático e Exemplos |")
    md_lines.append("| :--- | :--- | :--- |")
    for p_form, p_cls, p_desc in PARTICLES_AND_AFFIXES:
        full_json_db["particulas_e_afixos"][p_form] = {"classe": p_cls, "descricao": p_desc}
        total_word_forms += 1
        md_lines.append(f"| **{p_form}** | {p_cls} | {p_desc} |")

    md_lines.append("\n---\n")

    # --------------------------------------------------------------------------
    # PARTE VII: VERBOS — MATRIZ QUADRIPARTITE E CONJUGAÇÃO INTEGRAL DE TODAS AS TERMINAÇÕES
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte VII: Verbos — Todas as {len(VERB_ROOTS)} Raízes nos 4 Eixos Ontológicos ({len(VERB_ROOTS)*4} Verbos Independentes × 114 Formas = {len(VERB_ROOTS)*4*114:,} Formas Verbais)\n")
    md_lines.append("O sistema verbal aglutinante do Tréppio opera pela equação invariável `RAIZ + TEMPO + (MODO -ke) + (VOZ -se) + PESSOA (-m, -s, ∅, -n, -t)`.\n")
    md_lines.append("Abaixo, **cada uma das raízes verbais da língua** é projetada em seus **4 Estados Ontológicos** (*1. Positivo, 2. Privativo `a-`, 3. Iterativo `o-/od-`, 4. Iterativo-Privativo `od-a-`*) e transformada em **todas as suas terminações temporais, modais, vocais, pessoais, nominais e interrogativas**.\n")

    # Gerar também o arquivo separado com todas as 264 tabelas completas pessoa por pessoa
    verbs_full_md = []
    verbs_full_md.append(f"# Códice Verbal Exaustivo da Língua Tréppia: {len(VERB_ROOTS)*4} Verbos × 114 Formas ({len(VERB_ROOTS)*4*114:,} Formas Conjugadas)\n")

    for idx, (root, m_pos, m_priv, m_iter, m_itpr) in enumerate(VERB_ROOTS, 1):
        s1, s2, s3, s4 = build_four_stems(root)
        stems_info = [
            ("1. Positivo", s1, m_pos),
            ("2. Privativo (a-)", s2, m_priv),
            ("3. Iterativo (o-/od-)", s3, m_iter),
            ("4. Iter.-Privativo (od-a-)", s4, m_itpr),
        ]
        md_lines.append(f"### 7.{idx}. Família Verbal da Raiz `{root}-` ({m_pos})\n")
        md_lines.append("| Eixo Ontológico | Infinitivo (`-ur`) e Imperativo | Presente Ind. Ativa (`1Sg, 2Sg, 3ª, 1Pl, 2Pl`) e Passiva (`-se`) | Passado Aoristo (`-ra`) e Futuro (`-ru`) (`1Sg, 2Sg, 3ª, 1Pl, 2Pl`) | Imperfeito (`-ba`) e Durativo (`-ai`) (`1Sg, 2Sg, 3ª, 1Pl, 2Pl`) | Subjuntivos (`-uke / -rake / -ruke / -bake / -aike` 1Sg–3ª) | Particípio Declinado (8 Casos) e Derivados (`-te, -or, -tek, -ia, -ka`) |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

        verbs_full_md.append(f"## {idx}. Raiz `{root}-` ({m_pos})\n")
        full_json_db["verbos_quadripartite"][root] = {}

        for axis_label, st, axis_meaning in stems_info:
            c = conjugate_stem_all_109(st)
            full_json_db["verbos_quadripartite"][root][axis_label] = {"stem": st, "meaning": axis_meaning, "conjugation": c}
            total_word_forms += 114

            pres_a = ", ".join(c["Pres.Ind.Ativa"])
            pres_p = ", ".join(c["Pres.Ind.Passiva"])
            pass_a = ", ".join(c["Pass.Ind.Ativa"])
            fut_a = ", ".join(c["Fut.Ind.Ativa"])
            impf_a = ", ".join(c["Imperf.Ind.Ativa"])
            dur_a = ", ".join(c["Dur.Ind.Ativa"])
            subjs = (
                f"Pres: *{c['Pres.Subj.Ativa'][0]}/{c['Pres.Subj.Ativa'][2]}* (Pass: *{c['Pres.Subj.Passiva'][2]}*) | "
                f"Pass: *{c['Pass.Subj.Ativa'][0]}/{c['Pass.Subj.Ativa'][2]}* | "
                f"Fut: *{c['Fut.Subj.Ativa'][0]}/{c['Fut.Subj.Ativa'][2]}* | "
                f"Impf: *{c['Imperf.Subj.Ativa'][0]}/{c['Imperf.Subj.Ativa'][2]}* | "
                f"Dur: *{c['Dur.Subj.Ativa'][0]}/{c['Dur.Subj.Ativa'][2]}*"
            )
            pt = c["Participio(8_Casos)"]
            dn = c["Derivados.Nominais"]
            part_and_deriv = (
                f"Part: **{pt['Nom.Sg']}** (*{pt['Gen.Sg']}, {pt['Dat.Sg']}, {pt['Acu.Sg']}; Pl: {pt['Nom.Pl']}, {pt['Gen.Pl']}, {pt['Dat.Pl']}, {pt['Acu.Pl']}*) | "
                f"Ag: **{dn['Agente(-te)']}** | Abst: **{dn['Abstrato(-or)']}** | Inst: **{dn['Instrum(-tek)']}** | Lug: **{dn['Lugar(-ia)']}** | Int: **{c['Interrogativo.2Pl(-ka)']}**"
            )

            md_lines.append(
                f"| **{axis_label}**<br>`{st}-` (*{axis_meaning}*) | Inf: **{c['Infinitivo(-ur)']}**<br>Imp: **{c['Imperativo(Raiz)']}** | "
                f"**Ativa:** *{pres_a}*<br>**Passiva:** *{pres_p}* | "
                f"**Pass (`-ra`):** *{pass_a}*<br>**Fut (`-ru`):** *{fut_a}* | "
                f"**Impf (`-ba`):** *{impf_a}*<br>**Dur (`-ai`):** *{dur_a}* | "
                f"{subjs} | {part_and_deriv} |"
            )

            # Adicionar também ao arquivo exaustivo de verbos todas as 100 formas finitas + nominais
            verbs_full_md.append(f"### {axis_label}: **{c['Infinitivo(-ur)']}** (*{axis_meaning}*)\n")
            verbs_full_md.append(f"- **Infinitivo:** `{c['Infinitivo(-ur)']}` | **Imperativo:** `{c['Imperativo(Raiz)']}` | **Interrogativo 2ª Pl:** `{c['Interrogativo.2Pl(-ka)']}`")
            verbs_full_md.append(f"- **Particípio (8 Casos):** Nom.Sg `{pt['Nom.Sg']}`, Gen.Sg `{pt['Gen.Sg']}`, Dat.Sg `{pt['Dat.Sg']}`, Acu.Sg `{pt['Acu.Sg']}`, Nom.Pl `{pt['Nom.Pl']}`, Gen.Pl `{pt['Gen.Pl']}`, Dat.Pl `{pt['Dat.Pl']}`, Acu.Pl `{pt['Acu.Pl']}`")
            verbs_full_md.append(f"- **Derivados Nominais:** Agente `{dn['Agente(-te)']}`, Abstrato `{dn['Abstrato(-or)']}`, Instrumento `{dn['Instrum(-tek)']}`, Lugar `{dn['Lugar(-ia)']}`")
            for k_tense in ["Pres.Ind", "Pres.Subj", "Pass.Ind", "Pass.Subj", "Dur.Ind", "Dur.Subj", "Fut.Ind", "Fut.Subj", "Imperf.Ind", "Imperf.Subj"]:
                verbs_full_md.append(f"  - **{k_tense} Ativa:** `{', '.join(c[k_tense + '.Ativa'])}` | **Passiva:** `{', '.join(c[k_tense + '.Passiva'])}`")
            verbs_full_md.append("")

        md_lines.append("")

    md_lines.append("---\n")

    # --------------------------------------------------------------------------
    # PARTE VIII: REGISTRO DIACRÔNICO, FÓRMULAS LITÚRGICAS, VARIANTES PLEBEIAS (C/Ç) E FORMAS PRÉ-SÍNCRESE
    # --------------------------------------------------------------------------
    md_lines.append(f"## Parte VIII: Registro Diacrônico, Fórmulas Litúrgicas Cristalizadas, Variantes Vulgares (C/Ç) e Formas Pré-Síncrese ({len(DIACHRONIC_AND_VARIANT_ENTRIES)} Entradas)\n")
    md_lines.append("Para garantir **100% de exaustividade filológica** sobre todos os documentos da base de dados do `/conde` (incluindo as notas históricas da *Gramática Normativa*, do *Adendo V8.1* e dos relatórios de *sandbox*), esta seção cataloga todas as formas litúrgicas cristalizadas, variantes plebeias ou dialetais (`c/ç`) e formas arcaicas pré-Síncrese de Celia ou expurgadas mencionadas nos manuais.\n")
    md_lines.append("| Forma Documentada | Estatuto Diacrônico / Sociolinguístico | Equivalente Canônico (V8.1) | Análise Filológica e Ocorrência nos Manuais |")
    md_lines.append("| :--- | :--- | :--- | :--- |")
    full_json_db["registro_diacronico_e_variantes"] = {}
    for d_form, d_stat, d_canon, d_desc in DIACHRONIC_AND_VARIANT_ENTRIES:
        full_json_db["registro_diacronico_e_variantes"][d_form] = {
            "estatuto": d_stat,
            "equivalente_canonico": d_canon,
            "analise": d_desc,
        }
        total_word_forms += 1
        md_lines.append(f"| **{d_form}** | {d_stat} | **{d_canon}** | {d_desc} |")

    full_json_db["corpus_canonico"] = [
        {
            "titulo": "I. Patte Ny (Oração Dominical)",
            "categoria": "Liturgia Canônica (GNLT Seção 8.1)",
            "treppio": "Patte ny, ke in xeri esu, elfase mon vy. Keladuke karan vy. Tekuse vule vy, in oxej ko in xeri. Faldem ny sambela mob noj sambel. Et akit faltes ny, ko no akitun faltetoi ny. Et ne gel nom in tulom, ta sfar nom ex lakej. Zo es.",
            "portugues": "Pai nosso, que estás no céu, santificado seja o vosso nome. Venha o vosso reino. Seja feita a vossa vontade, na terra como no céu. O pão nosso de cada dia dai-nos hoje. E perdoai as nossas ofensas, assim como nós perdoamos aos nossos ofensores. E não nos deixeis cair em tentação, mas livrai-nos do mal. Assim sê."
        },
        {
            "titulo": "II. Metuses Maria (Saudação Angélica)",
            "categoria": "Liturgia Canônica (GNLT Seção 8.2)",
            "treppio": "Metuses Maria, lana mety, Trátte esu tij. Mobanavet esus in kranoi, et mobanavet esu fel massuy ty, Jesus. Elfa Maria, Mad Gyosy, let ad Gyos pro noj kuroi, santonk et in tonkrej akazory ny. Zo es.",
            "portugues": "Ave Maria, cheia de graça, o Senhor é convosco. Bendita sois vós entre as mulheres, e bendito é o fruto do vosso ventre, Jesus. Santa Maria, Mãe de Deus, rogai a Deus por nós, pecadores, agora e na hora de nossa morte. Assim sê."
        },
        {
            "titulo": "III. Skorum (Símbolo Apostólico / Credo)",
            "categoria": "Liturgia Canônica (GNLT Seção 8.3)",
            "treppio": "Skorum in Gyos, Patte rukran, Kratte xery et oxedy. Et in Jesus Kristus, Fel idda Kany, Trátte ny, ke madet essa ex Hali Hali, kazza ex akuraj Mariaj, fassa ponu Pontius Pilatus, akazza et kossa; ynna ad Veloxem; in zelta beli okazza ex akazetoi; ynna ad xeros, esu in dattej Pattedy rukrany; ex Kani keladru ad molletur kazetos et akazetos. Skorum in Halom Halom, elfam Halkelem, kindrem lexedye, akitorom faltedye, okazorom vokory, et kazorom in atonkrej. Zo es.",
            "portugues": "Creio em Deus, Pai todo-poderoso, Criador do céu e da terra. E em Jesus Cristo, seu único Filho, nosso Senhor, que foi concebido pelo Espírito Santo, nasceu da Virgem Maria, padeceu sob Pôncio Pilatos, morreu e foi sepultado; desceu aos infernos; no terceiro dia ressuscitou dos mortos; subiu aos céus, está sentado à direita de Deus Pai todo-poderoso; de lá há de vir a julgar os vivos e os mortos. Creio no Espírito Santo, na Santa Igreja, na comunhão dos santos, na remissão dos pecados, na ressurreição da carne e na vida eterna. Assim sê."
        },
        {
            "titulo": "IV. Halylitror — Iº Movimento: A Gênese dos Espíritos do Pensamento",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Essa Gyos Idda, ke in Tréppia Oratypatte letuse. Et Kan itta Halo kradda, Daifelo ex daiori Kany; et Kano in Kani essan ante ke idda maer kraddase. Et Oratypatte ad Kanos ledda, et Kanoi leddalitroros mobra; et Kano in sotimi Kany litrran, et Kan mebba. Ta durai Katte idlitrorom litrba, u katro in kindrej, nam aetikos ne isban; nam itta idda tanom isba ex daiori Oratypattedy ex ke kazza, et in aletori girba.",
            "portugues": "Havia Eru, o Único, que em Tréppia é chamado Ilúvatar (Pai do Todo). E Ele criou primeiro os Ainur, os Sagrados, que foram os Filhos do seu Pensamento; e eles estavam com Ele antes que qualquer outra coisa fosse criada. E falou a eles, propondo-lhes temas musicais; e cantaram perante Ele, e Ele se regozijava."
        },
        {
            "titulo": "V. Halylitror — IIº Movimento: A Convocação da Grande Música",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Ta ko Halo maer isban, kindrorom et kellitrorom gizzan. Et Oratypatte todos Halos keladra, et Kanoi ledda: Ex leddalitrori ke voj akossam, vulum santonk ke in mobalitrori kellitruket Litrgarom! Et ko Kanoi Halvurom illanram, akosut isoros et rukroros vy ad illotur leddalitrorom ex daiori iddy.",
            "portugues": "Contudo, à medida que compreendiam mais, cresceram em concórdia e harmonia coral. E Ilúvatar convocou todos os Espíritos Sagrados e declarou-lhes: Do tema que vos revelei, quero agora que em harmonia façais juntos uma Grande Música! E como vos inspirei com a Chama Imperecível, demonstrareis vossos poderes para adornar o tema."
        },
        {
            "titulo": "VI. Halylitror — IIIº Movimento: O Despertar da Sinfonia nos Salões Atemporais",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Ta suleto Halye, ko harper et violer, ko litrteko et rukraleter, ko kellitroro amygatar ke in leddamo litrban, Litrgarom Kany inran. Et sulet mobalitrory, ke ne alim oletuse, in fili et in xeri ynna; et Halyteggar lana essa, et Litror exkosai in Nesuom ynna, et Nesu ne maer nesua essa.",
            "portugues": "Então as vozes dos Espíritos Sagrados, como harpas e violas, como trombetas e órgãos e como coros incontáveis que cantam com palavras, começaram a transformar o tema de Ilúvatar em uma Grande Música; e os Salões Atemporais transbordaram, e a música alcançou o Vazio, e ele deixou de ser vazio."
        },
        {
            "titulo": "VII. Halylitror — IVº Movimento: A Soberania de Lanrukra e a Busca no Vazio",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Oratypatte esba et kellitrorom mirba, et moba Kani esba. Ta ko leddalitror girba, in sukori Lanrukrady inna ad illotur daioros ex vulej Kany ke ne in leddalitrori Oratypattedy esban; nam Kani isoro et rukroro mobani mobrassen, et in donoi fratroro Kany parba. Kan in Nesuom ynna ad mirur Halvurom, nam in intulori vulba kradur Kradetos Kany; ta Halvurom ne mirra, nam in Oratypattej esu.",
            "portugues": "Ilúvatar sentou-se e escutou, e pareceu-Lhe bom. Mas, conforme o tema progredia, entrou no coração de Melkor entretecer assuntos de sua própria imaginação que não estavam de acordo com o tema de Ilúvatar; pois a ele tinham sido dados os maiores dons de poder e conhecimento. Ele fora sozinho ao Vazio buscar a Chama Imperecível, mas não a encontrou, pois ela está com Ilúvatar."
        },
        {
            "titulo": "VIII. Halylitror — Vº Movimento: A Dissonância de Kurlan e os Três Grandes Temas",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Ex daiori iddi Kurlany alitror girra, et Halo in Kani doobban, et suleto aetika essan, et kellitror akindrra. Ta Oratypatte esba et mirba, antetonk ko in Halyteggari feroxéor girra. Ta Oratypatte girra, et Halo mirran ke lita mebba; et dattem Kany girra, et Dota Leddalitror in alitrori inna, maer lota et maer rukra. Et ko alitror Kurlany ogirra, Oratypatte Zelta Leddalitrorom inra: lita et fassukora in fili, ta rukra ko garvelitror in atonkrej.",
            "portugues": "Dos pensamentos solitários de Melkor brotou a dissonância, e muitos ao seu redor desalentaram-se, e a unidade foi rompida. Então Ilúvatar ergueu-se, e os Ainur perceberam que Ele sorria; ergueu a mão esquerda, e um novo tema começou em meio à tormenta; e novamente ergueu a mão direita, e um terceiro tema cresceu em poder profundo."
        },
        {
            "titulo": "IX. Halylitror — VIº Movimento: O Acorde Final e a Revelação da Visão",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Ta Oratypatte in rukrori girra, et dattem et sintem in idda girra; et in idda leddaj Litror alerra. Et Oratypatte ledda: Rukrar esu Halo, et in kanoi Kurlan rukran esu; ta isru ke ne idda leddalitror litrukeso so ne ex Ej fontom toruke, et ke in Em alitror tekuse, lotorom tekoroy Ey inru! Ta Oratypatte Halyteggaros agaldra, et Halos in Nesuom gelra, et ledda: Mir! San esu Litror vy! Et Mirakosor akosrase: Oratoxe in Nesui, ko oxegar in lani in velliri.",
            "portugues": "Então Ilúvatar ergueu-se em majestade e levantou ambas as mãos, e num acorde mais profundo que o Abismo a Música cessou. E disse: Poderosos são os Ainur, e mais poderoso entre eles é Melkor; mas ele saberá que nenhum tema pode ser tocado sem ter em Mim sua fonte! E conduziu-os ao Vazio e disse: Olhai! Esta é a vossa Música! E uma Visão lhes foi revelada: um Mundo globado em meio ao Vazio."
        },
        {
            "titulo": "X. Halylitror — VIIº Movimento: O Despertar dos Filhos de Ilúvatar (Ittakazeti e Dotakazeti)",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Et ko Halo Mirakosorom mirban, mirran ke in Zelta Leddalitrori kradeto aetika esban, ke ne in daiori Halye esban: Felo Oratypattedy, Ittakazeti et Dotakazeti, ke ex Kani Iddi kraddassen! Et Halo Kanos gizzan, nam lotan esban; et Kurlan illotorom Kany inra, ad ke Felos Oratypattedy torexuke.",
            "portugues": "E enquanto os Ainur contemplavam esta Visão, viram que no Terceiro Tema havia coisas estranhas que não provinham do pensamento deles: eram os Filhos de Ilúvatar, os Primeiros Nascidos e os Sucessores, concebidos por Ele sozinho! E os Ainur os amaram, mas Melkor fingiu ocultar seu desejo de dominá-los."
        },
        {
            "titulo": "XI. Halylitror — VIIIº Movimento: ODomínio de Ferytrátte, Vétrátte e Tektrátte",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "In Halo, Ferytrátte daiorom Oratypattedy isan isba, et ferom, feriam et ferveos gizza. Vétrátte garveos et vevaros gizza, et in garvelitrori Oratypattej ledda. Tektrátte oxegaros, rixegaros, lauriom et verrem gizza, nam isorom et tekorom ko Oratypatte torba. Et Vétrátte et Ferytrátte ex fili in kindrori essan: in ferveoi et in veksixij Vé et fer keladun.",
            "portugues": "Dentre os Ainur, Manwë (Ferytrátte) conhecia mais claramente a mente de Ilúvatar, amando os ventos e o ar; Ulmo (Vétrátte) voltou seu pensamento às águas e oceanos; e Aulë (Tektrátte) voltou-se à estrutura da terra, às rochas e aos metais. E Ulmo e Manwë estiveram desde o princípio aliados nas nuvens e nas chuvas."
        },
        {
            "titulo": "XII. Halylitror — IXº a XIIº Movimentos: O Decreto de Eä (Esu!) e a Guerra de Construção",
            "categoria": "Cosmogonia Sagrada (GNLT Seção 8.5)",
            "treppio": "Ta Oratypatte Mirakosorom kossa, et in Halo vulor girra ad ynur in Oratoxem. Et Oratypatte ledda: Isum vulorom vy, ad ke sano ke mirrat esuke! Ta Mobum: Esu! Et Kan Halvurom in suom Nesuy gelra, et Oratoxe essa! Et Halo, ke Totter et Rukroro letusen, in Oratoxem ynnan; ta nakad esba. Et ko Totter oxegaros tekban, Kurlan in vurori et in avuri keladra, et tekoros Tottedye akradba: filoxer kossa, rixegaros akradda, garveos akossa. Ta tekor Tottedye ne nesua essa: in avuri et in avurvéj Kurlany, Vétrátte et Ferytrátte ferveos et veksixis kraddan, et Oratoxe ad Ittakazetos illotrase. Zo es!",
            "portugues": "Então Ilúvatar recolheu a Visão, e despertou nos Ainur o desejo de que aquelas coisas existissem. E Ilúvatar declarou: Sei do desejo de vossas mentes! Portanto, digo: Eä! Que estas coisas Sejam! E enviou a Chama Imperecível ao coração do Vazio, e o Mundo Passou a Ser! Os Valar desceram a Arda e travaram com Melkor a guerra da edificação do mundo, preparando a Terra para os Primeiros Nascidos. Assim sê!"
        }
    ]

    full_json_db["metadata"]["total_expanded_word_forms"] = total_word_forms
    full_json_db["gnlt"] = extract_gnlt_payload(root_dir)

    # Salvar o Dicionário Geral em Sandbox
    sandbox_md_path = os.path.join(out_dir, "dicionario_geral_treppio_sandbox.md")
    with open(sandbox_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Salvar o Códice Verbal Exaustivo (todas as 31.008 formas verbais detalhadas)
    verbs_md_path = os.path.join(ex_dir, "verbos_matriz_quadripartite_completa.md")
    with open(verbs_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(verbs_full_md))

    # Salvar o JSON estruturado com todas as 37.769 formas expandidas
    json_path = os.path.join(ex_dir, "dicionario_formas_expandidas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_json_db, f, ensure_ascii=False, indent=2)
    root_json_path = os.path.join(root_dir, "dicionario_formas_expandidas.json")
    with open(root_json_path, "w", encoding="utf-8") as f:
        json.dump(full_json_db, f, ensure_ascii=False, indent=2)

    # Salvar o bundle JS direto para alimentar a UI do Dicionário (funciona tanto via servidor quanto via file://)
    ui_dir = os.path.join(out_dir, "ui_dicionario")
    os.makedirs(ui_dir, exist_ok=True)
    js_bundle_path = os.path.join(ui_dir, "dados_dicionario_conde.js")
    json_compact_str = json.dumps(full_json_db, ensure_ascii=False)
    with open(js_bundle_path, "w", encoding="utf-8") as f:
        f.write("// Banco de Dados Automático da UI do Dicionário Tréppio (/conde V8.1)\n")
        f.write("window.CONDE_DB = ")
        f.write(json_compact_str)
        f.write(";\n")

    # Gerar diretório docs/ na raiz de D:\Conde_Treppio para publicação direta no GitHub Pages
    root_dir = r"D:\Conde_Treppio"
    docs_dir = os.path.join(root_dir, "docs")
    dist_dir = os.path.join(root_dir, "dist")
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)

    ui_index_path = os.path.join(ui_dir, "index.html")
    if os.path.exists(ui_index_path):
        with open(ui_index_path, "r", encoding="utf-8") as f:
            html_template = f.read()

        # 1. Salvar site completo em docs/ (GitHub Pages: index.html + dados_dicionario_conde.js + dicionario_formas_expandidas.json)
        with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_template)
        with open(os.path.join(docs_dir, "dados_dicionario_conde.js"), "w", encoding="utf-8") as f:
            f.write("window.CONDE_DB = " + json_compact_str + ";\n")
        with open(os.path.join(docs_dir, "dicionario_formas_expandidas.json"), "w", encoding="utf-8") as f:
            f.write(json_compact_str)

        # 2. Gerar arquivo único 100% autocontido (dist/Codice_Treppio_Portatil.html) para envio a amigos / Google Drive
        inline_script = f"<script>window.CONDE_DB = {json_compact_str};</script>"
        portable_html = re.sub(r'<script src="dados_dicionario_conde\.js[^"]*"></script>', inline_script, html_template)
        portable_html_path = os.path.join(dist_dir, "Codice_Treppio_Portatil.html")
        with open(portable_html_path, "w", encoding="utf-8") as f:
            f.write(portable_html)

        # 3. Salvar asset único autocontido no projeto Android APK (sandbox/android_apk/app/src/main/assets/)
        # Deduplicado: evita triplicar ~3.6 MB x 3 no pacote APK
        android_assets_dir = os.path.join(out_dir, "android_apk", "app", "src", "main", "assets")
        os.makedirs(android_assets_dir, exist_ok=True)
        with open(os.path.join(android_assets_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(portable_html)
        for redundant_asset in ("dados_dicionario_conde.js", "dicionario_formas_expandidas.json"):
            redundant_path = os.path.join(android_assets_dir, redundant_asset)
            if os.path.exists(redundant_path):
                try:
                    os.remove(redundant_path)
                except OSError:
                    pass

    print(f"=== GERAÇÃO CONCLUÍDA COM SUCESSO ===")
    print(f" -> Dicionário Geral Markdown: {sandbox_md_path} ({os.path.getsize(sandbox_md_path):,} bytes)")
    print(f" -> Códice Verbal Exaustivo:   {verbs_md_path} ({os.path.getsize(verbs_md_path):,} bytes)")
    print(f" -> Banco JSON de Formas:      {json_path} ({os.path.getsize(json_path):,} bytes)")
    print(f" -> Total de formas flexionadas e derivadas geradas e validadas: {total_word_forms:,}")

if __name__ == "__main__":
    generate_all_files()
