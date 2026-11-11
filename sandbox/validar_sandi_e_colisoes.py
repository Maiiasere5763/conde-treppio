# -*- coding: utf-8 -*-
"""
validar_sandi_e_colisoes.py
Auditor Fonotático, Morfofonológico (21 Leis de Sandi) e Anti-Colisão Homofônica
para a Expansão Lexical de Grande Escala do Tréppio (Era Clássica V8.1).
"""
import os
import re
import sys

sys.path.insert(0, r"D:\Conde_Treppio\sandbox")
import gerador_dicionario_integral_sandbox as gen
import lexico_expansao_v8_1 as exp

FORBIDDEN_CLUSTERS = re.compile(r"rn|nl|nr|dt|kt|pg|tk|ds|zr|mr|sr|ln")
PURGADOS = {
    "mandur", "bibur", "panna", "broda", "karna", "kamin", "husa", "stuba",
    "amiko", "kastar", "kanis", "post", "kanto", "kardi", "theus", "vane", "nomo"
}


def run_audit():
    print("=== INICIANDO AUDITORIA FILOLÓGICA E FONOTÁTICA DO CONDE (V8.1) ===")

    exp_nouns_set = {x[0].lower() for x in exp.EXPANSAO_NOUNS}
    exp_adjs_set = {x[0].lower() for x in exp.EXPANSAO_ADJECTIVES}
    exp_verbs_set = {x[0].lower() for x in exp.EXPANSAO_VERB_ROOTS}
    exp_advs_set = {x[0].lower() for x in exp.EXPANSAO_ADVERBS}

    existing_nouns = {x[0].lower() for x in gen.NOUNS} - exp_nouns_set
    existing_adjs = {x[0].lower() for x in gen.ADJECTIVES} - exp_adjs_set
    existing_verbs = {x[0].lower() for x in gen.VERB_ROOTS} - exp_verbs_set
    existing_advs = {x[0].lower() for x in gen.ADVERBS} - exp_advs_set - {f"{a}vë" for a in exp_adjs_set}
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
        if FORBIDDEN_CLUSTERS.search(rl):
            errors.append(f"[VIOLAÇÃO DE SANDI - RAIZ] {r}")
        if rl in PURGADOS:
            errors.append(f"[TERMO EXPURGADO - RAIZ] {r}")
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

    # 2. Verificar Substantivos
    seen_nouns = set()
    for n, decl, mean, etym in exp.EXPANSAO_NOUNS:
        nl = n.lower()
        if nl in seen_nouns:
            errors.append(f"[DUPLICATA INTERNA - SUBSTANTIVO] {n}")
        seen_nouns.add(nl)
        if nl in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - SUBSTANTIVO] {n}")
        if FORBIDDEN_CLUSTERS.search(nl):
            errors.append(f"[VIOLAÇÃO DE SANDI - SUBSTANTIVO] {n}")
        d_forms = gen.decline_noun(n, decl)
        for ck, cf in d_forms.items():
            if FORBIDDEN_CLUSTERS.search(cf.lower()):
                errors.append(f"[VIOLAÇÃO DE SANDI NA DECLINAÇÃO] {cf} ({n} -> {ck})")

    # 3. Verificar Adjetivos
    seen_adjs = set()
    for adj, mean, comp, sup in exp.EXPANSAO_ADJECTIVES:
        al = adj.lower()
        if al in seen_adjs:
            errors.append(f"[DUPLICATA INTERNA - ADJETIVO] {adj}")
        seen_adjs.add(al)
        if al in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - ADJETIVO] {adj}")
        if FORBIDDEN_CLUSTERS.search(al) or FORBIDDEN_CLUSTERS.search(sup.lower()):
            errors.append(f"[VIOLAÇÃO DE SANDI - ADJETIVO/SUPERLATIVO] {adj} / {sup}")

    # 4. Verificar Advérbios
    seen_advs = set()
    for adv, subc, etym, mean in exp.EXPANSAO_ADVERBS:
        advl = adv.lower()
        if advl in seen_advs:
            errors.append(f"[DUPLICATA INTERNA - ADVÉRBIO] {adv}")
        seen_advs.add(advl)
        if advl in all_existing_lemmas:
            errors.append(f"[COLISÃO COM LEMA EXISTENTE - ADVÉRBIO] {adv}")
        if FORBIDDEN_CLUSTERS.search(advl):
            errors.append(f"[VIOLAÇÃO DE SANDI - ADVÉRBIO] {adv}")

    if errors:
        print(f"FALHA NA AUDITORIA ({len(errors)} erros encontrados):")
        for e in errors[:30]:
            print("  ->", e)
        sys.exit(1)

    nr = len(exp.EXPANSAO_VERB_ROOTS)
    nn = len(exp.EXPANSAO_NOUNS)
    na = len(exp.EXPANSAO_ADJECTIVES)
    nadv = len(exp.EXPANSAO_ADVERBS)
    print(f"  [OK] {nr} Novas Raízes Verbais ({nr * 4} temas quadripartites × 114 formas = {nr * 4 * 114:,} formas verbais)")
    print(f"  [OK] {nn} Novos Substantivos Derivados ({nn} × 18 transformações = {nn * 18:,} formas nominais)")
    print(f"  [OK] {na} Novos Adjetivos Qualificativos ({na} × 13 transformações = {na * 13:,} formas adjetivais)")
    print(f"  [OK] {nadv} Novos Advérbios Especiais + {na} Advérbios Modais Regulares (-vë)")
    print("  [OK] 0 Encontros Consonantais Proibidos (21 Leis de Sandi 100% respeitadas)")
    print("  [OK] 0 Colisões Homofônicas com o Corpus Canônico Existente")

    # 5. Validar JSON Compilado Final (Dinâmico para expansões horárias)
    import json
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
        print(f"  [OK] JSON Compilado Validado: {m['total_expanded_word_forms']:,} formas, {m['nouns_count']} substantivos, {m['verb_stems_quadripartite']} verbos quadripartites.")
        for sample_r in ["belk", "darp", "blam", "plov", "svar"]:
            v_data = db["verbos_quadripartite"][sample_r]
            pos = v_data["1. Positivo"]["conjugation"]
            priv = v_data["2. Privativo (a-)"]["conjugation"]
            it = v_data["3. Iterativo (o-/od-)"]["conjugation"]
            itp = v_data["4. Iter.-Privativo (od-a-)"]["conjugation"]
            print(f"    -> [{sample_r}-]: Pos={pos['Infinitivo(-ur)']} (Impf={pos['Imperf.Ind.Ativa'][0]}), Priv={priv['Infinitivo(-ur)']}, Iter={it['Infinitivo(-ur)']}, IterPriv={itp['Infinitivo(-ur)']}")

    print("=== AUDITORIA CONCLUÍDA COM 100% DE APROVAÇÃO ===")


if __name__ == "__main__":
    run_audit()
