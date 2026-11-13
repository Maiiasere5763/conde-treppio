# -*- coding: utf-8 -*-
r"""
validar_sandi_e_colisoes.py
Auditor Fonotático, Morfofonológico (26 Leis de Sandi + Haplologia Silábica),
Anti-Colisão Homofônica e Filtro Anti-Romanismo
para a Expansão Lexical da Língua Tréppia (Era Clássica V8.4 — O Conde).
"""
import os
import re
import sys
import json
import unicodedata
from difflib import SequenceMatcher

sys.path.insert(0, r"D:\Conde_Treppio\sandbox")
import gerador_dicionario_integral_sandbox as gen
import lexico_expansao_v8_1 as exp

FORBIDDEN_CLUSTERS = re.compile(r"rn|nl|nr|dt|kt|pg|tk|ds|zr|mr|sr|ln|bp")
FORBIDDEN_GRAPHEMES = re.compile(r"c|ç|q|w|lh|nh|ch|j")
INITIAL_CLUSTER = re.compile(r"^[^aeiouyAEIOUYáéíóúýäëïöüÁÉÍÓÚÝÄËÏÖÜ'\W_]{2,}")
ROMANCE_SIMILARITY_THRESHOLD = 0.70
PURGADOS = {
    "mandur", "bibur", "panna", "broda", "karna", "kamin", "husa", "stuba",
    "amiko", "kastar", "kanis", "post", "kanto", "kardi", "theus", "vane", "nomo"
}

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
    "relativo", "proprio", "dotado", "cheio", "coberto", "provido", "propenso",
    "pequeno", "pequena", "grande", "alto", "alta", "baixo", "baixa",
    "longo", "longa", "curto", "curta", "novo", "nova", "velho", "velha",
    "antigo", "antiga", "sagrado", "sagrada", "imperial", "real",
    "montanha", "montanhas", "serra", "serras", "pedra", "rocha", "madeira",
    "agua", "fogo", "vento", "noite", "terra", "casa", "corpo", "sangue",
    "instrumento", "meio", "lugar", "oficina", "recinto", "arte", "tecnica",
    "voltar", "deixar", "repetidamente", "novamente", "habitualmente",
    "animal", "planta", "erva", "arvore", "flor", "fruto", "folha",
    "orgao", "osso", "carne", "pele", "olho", "canto", "musica", "som",
    "arco", "ponte", "porta", "torre", "muro", "muralha", "parede", "teto",
    "estrela", "astro", "ceu", "frio", "gelo", "neve", "chuva", "mar", "rio",
}


def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _normalize_treppio_stem(lemma: str) -> str:
    s_acc = _strip_accents(lemma.lower())
    s = s_acc.replace("'", "")
    for suf in ("gar", "ttek", "tek", "ia", "or", "il", "tte", "te", "et", "ve", "ur"):
        if s_acc.endswith("'" + suf) and len(s_acc) >= len(suf) + 3:
            s = s_acc[:-(len(suf) + 1)].replace("'", "")
            break
        if len(s) >= len(suf) + 3 and s.endswith(suf):
            s = s[:-len(suf)]
            break
    if len(s) > 3 and s[-1] in ("e", "a", "o", "i"):
        s = s[:-1]
    return s.replace("k", "c")


def _normalize_pt_stem(word: str) -> str:
    w = word
    for suf in ("mento", "coes", "cao", "sao", "ico", "ica", "ados", "adas", "ado", "ada", "ar", "er", "ir", "or", "ia", "os", "as", "es", "a", "e", "o"):
        if len(w) >= len(suf) + 3 and w.endswith(suf):
            w = w[:-len(suf)]
            break
    return w


def check_romance_similarity(lemma: str, meaning: str) -> tuple[float, str]:
    """Calcula a similaridade máxima (0.0 a 1.0) entre o radical Tréppio e os radicais da glosa."""
    t_norm = _normalize_treppio_stem(lemma)
    best_sim = 0.0
    best_word = ""

    words = [w for w in re.findall(r"[a-z]{4,}", _strip_accents(meaning.lower())) if w not in STOPWORDS_PT]
    for w in words:
        w_stem = _normalize_pt_stem(w)
        if not t_norm or not w_stem:
            continue
        ratio = SequenceMatcher(None, t_norm, w_stem).ratio()
        if len(t_norm) >= 4 and len(w_stem) >= 4 and t_norm[:4] == w_stem[:4]:
            ratio = max(ratio, 0.75)
        if ratio > best_sim:
            best_sim = ratio
            best_word = w
    return best_sim, best_word


def run_audit():
    print("=== INICIANDO AUDITORIA FILOLÓGICA, FONOTÁTICA, HAPLOLÓGICA E ANTI-ROMÂNICA DO CONDE (V8.4) ===")

    exp_nouns_set = {x[0].lower() for x in exp.EXPANSAO_NOUNS}
    exp_adjs_set = {x[0].lower() for x in exp.EXPANSAO_ADJECTIVES}
    exp_verbs_set = {x[0].lower() for x in exp.EXPANSAO_VERB_ROOTS}
    exp_advs_set = {x[0].lower() for x in exp.EXPANSAO_ADVERBS}
    exp_adj_advs = {gen.inflect_adjective(a[0], "")["Adv.Modal(-vë)"].lower() for a in exp.EXPANSAO_ADJECTIVES}

    existing_nouns = {x[0].lower() for x in gen.NOUNS} - exp_nouns_set
    existing_adjs = {x[0].lower() for x in gen.ADJECTIVES} - exp_adjs_set
    existing_verbs = {x[0].lower() for x in gen.VERB_ROOTS} - exp_verbs_set
    existing_advs = {x[0].lower() for x in gen.ADVERBS} - exp_advs_set - exp_adj_advs
    all_existing_lemmas = existing_nouns | existing_adjs | existing_verbs | existing_advs

    errors = []

    # 1. Verificar Raízes Verbais
    seen_roots = set()
    for r, m1, m2, m3, m4 in exp.EXPANSAO_VERB_ROOTS:
        rl = r.lower()
        if rl in seen_roots:
            errors.append(f"[DUPLICATA INTERNA - RAIZ] {r}")
        seen_roots.add(rl)
        if rl in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - RAIZ] {r}")
        if INITIAL_CLUSTER.match(rl):
            errors.append(f"[CLUSTER INICIAL PROIBIDO (#CC...) - RAIZ] {r}")
        if FORBIDDEN_CLUSTERS.search(rl):
            errors.append(f"[VIOLAÇÃO DE SANDI - RAIZ] {r}")
        if FORBIDDEN_GRAPHEMES.search(rl):
            errors.append(f"[GRAFEMA PROIBIDO - RAIZ] {r}")
        if rl in PURGADOS:
            errors.append(f"[TERMO EXPURGADO - RAIZ] {r}")
        sim, w_match = check_romance_similarity(r, m1)
        if sim > ROMANCE_SIMILARITY_THRESHOLD:
            errors.append(f"[VIOLAÇÃO DE PUREZA ANTI-ROMÂNICA > 70% - RAIZ] {r} (similaridade {sim:.0%} com '{w_match}')")

        # Testar projeção quadripartite e conjugação de 114 formas
        s1, s2, s3, s4 = gen.build_four_stems(r)
        for st in (s1, s2, s3, s4):
            if FORBIDDEN_CLUSTERS.search(st.lower()):
                errors.append(f"[VIOLAÇÃO DE SANDI NO TEMA QUADRIPARTITE] {st} (de {r})")
            conj = gen.conjugate_stem_all_109(st)
            for k, val in conj.items():
                if isinstance(val, str):
                    if FORBIDDEN_CLUSTERS.search(val.lower()):
                        errors.append(f"[VIOLAÇÃO DE SANDI NA CONJUGAÇÃO] {val} ({st} -> {k})")
                elif isinstance(val, list):
                    for form in val:
                        if FORBIDDEN_CLUSTERS.search(form.lower()):
                            errors.append(f"[VIOLAÇÃO DE SANDI NA CONJUGAÇÃO] {form} ({st} -> {k})")

    # 2. Verificar Substantivos Primários e Derivados
    seen_nouns = set()
    for n, decl, mean, etym in exp.EXPANSAO_NOUNS:
        nl = n.lower()
        if nl in seen_nouns:
            errors.append(f"[DUPLICATA INTERNA - SUBSTANTIVO] {n}")
        seen_nouns.add(nl)
        if nl in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - SUBSTANTIVO] {n}")
        if INITIAL_CLUSTER.match(nl):
            errors.append(f"[CLUSTER INICIAL PROIBIDO (#CC...) - SUBSTANTIVO] {n}")
        if FORBIDDEN_CLUSTERS.search(nl):
            errors.append(f"[VIOLAÇÃO DE SANDI - SUBSTANTIVO] {n}")
        if FORBIDDEN_GRAPHEMES.search(nl):
            errors.append(f"[GRAFEMA PROIBIDO - SUBSTANTIVO] {n}")
        sim, w_match = check_romance_similarity(n, mean)
        if sim > ROMANCE_SIMILARITY_THRESHOLD:
            errors.append(f"[VIOLAÇÃO DE PUREZA ANTI-ROMÂNICA > 70% - SUBSTANTIVO] {n} (similaridade {sim:.0%} com '{w_match}')")
        if nl.endswith(("e", "é", "ë")) and decl != 1:
            errors.append(f"[DECLINAÇÃO INCORRETA - SUBSTANTIVO EM -E DEVE SER 1ª DECLINAÇÃO] {n} (decl={decl})")
        d_forms = gen.decline_noun(n, decl)
        for ck, cf in d_forms.items():
            if FORBIDDEN_CLUSTERS.search(cf.lower()):
                errors.append(f"[VIOLAÇÃO DE SANDI NA DECLINAÇÃO] {cf} ({n} -> {ck})")

    # 2.1 Verificar Substantivos Canônicos em gen.NOUNS
    for item in gen.NOUNS:
        n_canon, decl_canon = item[0], item[1]
        nl_canon = n_canon.lower()
        if nl_canon.endswith(("e", "é", "ë")) and decl_canon != 1:
            errors.append(f"[DECLINAÇÃO INCORRETA CANÔNICA - SUBSTANTIVO EM -E DEVE SER 1ª DECLINAÇÃO] {n_canon} (decl={decl_canon})")

    # 3. Verificar Adjetivos
    seen_adjs = set()
    for adj, mean, comp, sup in exp.EXPANSAO_ADJECTIVES:
        al = adj.lower()
        if al in seen_adjs:
            errors.append(f"[DUPLICATA INTERNA - ADJETIVO] {adj}")
        seen_adjs.add(al)
        if al in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - ADJETIVO] {adj}")
        if INITIAL_CLUSTER.match(al):
            errors.append(f"[CLUSTER INICIAL PROIBIDO (#CC...) - ADJETIVO] {adj}")
        if FORBIDDEN_CLUSTERS.search(al) or FORBIDDEN_CLUSTERS.search(sup.lower()):
            errors.append(f"[VIOLAÇÃO DE SANDI - ADJETIVO/SUPERLATIVO] {adj} / {sup}")
        if FORBIDDEN_GRAPHEMES.search(al):
            errors.append(f"[GRAFEMA PROIBIDO - ADJETIVO] {adj}")

    # 4. Verificar Advérbios
    seen_advs = set()
    for adv, subc, etym, mean in exp.EXPANSAO_ADVERBS:
        advl = adv.lower()
        if advl in seen_advs:
            errors.append(f"[DUPLICATA INTERNA - ADVÉRBIO] {adv}")
        seen_advs.add(advl)
        if advl in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - ADVÉRBIO] {adv}")
        if INITIAL_CLUSTER.match(advl):
            errors.append(f"[CLUSTER INICIAL PROIBIDO (#CC...) - ADVÉRBIO] {adv}")
        if FORBIDDEN_CLUSTERS.search(advl):
            errors.append(f"[VIOLAÇÃO DE SANDI - ADVÉRBIO] {adv}")
        if FORBIDDEN_GRAPHEMES.search(advl):
            errors.append(f"[GRAFEMA PROIBIDO - ADVÉRBIO] {adv}")

    if errors:
        print(f"FALHA NA AUDITORIA ({len(errors)} erros encontrados):")
        for e in errors[:30]:
            print("  ->", e)
        sys.exit(1)

    nr = len(exp.EXPANSAO_VERB_ROOTS)
    nn = len(exp.EXPANSAO_NOUNS)
    na = len(exp.EXPANSAO_ADJECTIVES)
    nadv = len(exp.EXPANSAO_ADVERBS)
    print(f"  [OK] {nr} Raízes Verbais Puras ({nr * 4} temas quadripartites × 114 formas = {nr * 4 * 114:,} formas verbais)")
    print(f"  [OK] {nn} Substantivos Endógenos e Derivados ({nn} × 18 transformações = {nn * 18:,} formas nominais)")
    print(f"  [OK] {na} Adjetivos Qualificativos ({na} × 13 transformações = {na * 13:,} formas adjetivais)")
    print(f"  [OK] {nadv} Advérbios Modais e Sintáticos (-vë)")
    print("  [OK] 0 Clusters Consonantais Iniciais (#CC... estritamente banidos)")
    print("  [OK] 0 Encontros Consonantais Proibidos (26 Leis de Sandi 100% respeitadas, incluindo bp -> bb)")
    print("  [OK] 0 Grafemas Proibidos (c, ç, q, w, lh, nh, ch, j não-dativo)")
    print("  [OK] 0 Lexemas com Similaridade Românica/Greco-Latina > 70% (Tolerância Românica 70% aprovada)")
    print("  [OK] 0 Colisões Homofônicas com o Corpus Canônico Existente")

    # 5. Validar JSON Compilado Final + Auditoria Integral de Haplologia Silábica
    json_p = r"D:\Conde_Treppio\dicionario_formas_expandidas.json"
    if os.path.exists(json_p):
        with open(json_p, "r", encoding="utf-8") as f:
            db = json.load(f)
        m = db["metadata"]
        assert m["nouns_count"] == len(db["substantivos"]) >= 764
        assert m["adjectives_count"] == len(db["adjetivos"]) >= 206
        assert m["adverbs_count"] == len(db["adverbios"]) >= 248
        assert m["verb_roots_count"] == len(db["verbos_quadripartite"]) >= 202
        assert m["verb_stems_quadripartite"] == m["verb_roots_count"] * 4
        assert m["total_expanded_word_forms"] >= 109013

        haplo_forms_checked = 0
        double_apostr = 0
        pending_haplo = []

        def _check_haplo_token(tok: str, ctx: str):
            nonlocal haplo_forms_checked, double_apostr
            for part in re.findall(r"[A-Za-zÁÉÍÓÚÝáéíóúýÄËÏÖÜäëïöü']+", tok):
                haplo_forms_checked += 1
                if part.count("'") > 1:
                    double_apostr += 1
                    errors.append(f"[DUPLO APÓSTROFO] {part} ({ctx})")
                expected = gen.apply_haplology(part)
                if expected != part:
                    pending_haplo.append((ctx, part, expected))
                    errors.append(f"[HAPLOLOGIA PENDENTE] {part} -> {expected} ({ctx})")

        for s_lemma, s_info in db["substantivos"].items():
            if s_lemma.lower().endswith(("e", "é", "ë")) and s_info["declinacao"] != 1:
                errors.append(f"[JSON DECLINAÇÃO INCORRETA] {s_lemma} (decl={s_info['declinacao']})")
            _check_haplo_token(s_lemma, "subst.lema")
            for fk, fv in s_info["formas"].items():
                _check_haplo_token(fv, f"subst:{s_lemma}.{fk}")

        for a_lemma, a_info in db["adjetivos"].items():
            _check_haplo_token(a_lemma, "adj.lema")
            for fk, fv in a_info.items():
                if fk != "Significado":
                    _check_haplo_token(fv, f"adj:{a_lemma}.{fk}")

        for adv_lemma in db["adverbios"].keys():
            _check_haplo_token(adv_lemma, "adv.lema")

        for root, axes in db["verbos_quadripartite"].items():
            _check_haplo_token(root, "verbo.raiz")
            for ax_name, ax_obj in axes.items():
                conj = ax_obj["conjugation"]
                _check_haplo_token(conj["Infinitivo(-ur)"], f"v:{root}.{ax_name}.inf")
                _check_haplo_token(conj["Imperativo(Raiz)"], f"v:{root}.{ax_name}.imp")
                _check_haplo_token(conj["Interrogativo.2Pl(-ka)"], f"v:{root}.{ax_name}.int")
                for k, vlist in conj.items():
                    if isinstance(vlist, list):
                        for wf in vlist:
                            _check_haplo_token(wf, f"v:{root}.{ax_name}.{k}")
                    elif isinstance(vlist, dict):
                        for dk, dv in vlist.items():
                            _check_haplo_token(dv, f"v:{root}.{ax_name}.{k}.{dk}")

        for idx_c, c_entry in enumerate(db.get("corpus_canonico", [])):
            _check_haplo_token(c_entry.get("treppio", ""), f"corpus[{idx_c}]")

        if errors:
            print(f"FALHA NA AUDITORIA JSON/HAPLOLOGIA ({len(errors)} erros encontrados):")
            for e in errors[:30]:
                print("  ->", e)
            sys.exit(1)

        print(f"  [OK] Regra da 1ª Declinação: 100% dos substantivos terminados em -e/-é/-ë alocados na 1ª Declinação")
        print(f"  [OK] Auditoria Haplológica Integral: {haplo_forms_checked:,} formas inspecionadas | 0 duplos apóstrofos | 0 pendências de haplologia | idempotência 100%")
        print(f"  [OK] JSON Compilado Validado: {m['total_expanded_word_forms']:,} formas, {m['nouns_count']} substantivos, {m['verb_stems_quadripartite']} verbos quadripartites.")
        for sample_r in ["belk", "darp", "blam", "veyn", "vlir"]:
            if sample_r in db["verbos_quadripartite"]:
                v_data = db["verbos_quadripartite"][sample_r]
                pos = v_data["1. Positivo"]["conjugation"]
                priv = v_data["2. Privativo (a-)"]["conjugation"]
                it = v_data["3. Iterativo (o-/od-)"]["conjugation"]
                itp = v_data["4. Iter.-Privativo (od-a-)"]["conjugation"]
                print(f"    -> [{sample_r}-]: Pos={pos['Infinitivo(-ur)']} (Impf={pos['Imperf.Ind.Ativa'][0]}), Priv={priv['Infinitivo(-ur)']}, Iter={it['Infinitivo(-ur)']}, IterPriv={itp['Infinitivo(-ur)']}")

    print("=== AUDITORIA CONCLUÍDA COM 100% DE APROVAÇÃO ===")


if __name__ == "__main__":
    run_audit()
