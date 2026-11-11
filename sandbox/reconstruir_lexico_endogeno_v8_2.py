# -*- coding: utf-8 -*-
"""
reconstruir_lexico_endogeno_v8_2.py
Reconstrói integralmente todos os lexemas com >50% de similaridade românica/greco-latina
em gerador_dicionario_integral_sandbox.py e lexico_expansao_v8_1.py, utilizando
exclusivamente raízes primárias canônicas do Tréppio e composição endógena com as 21 Leis de Sandi.
"""
import os
import re
import sys
import unicodedata
from difflib import SequenceMatcher

sys.path.insert(0, r"D:\Conde_Treppio\sandbox")

FORBIDDEN_CLUSTERS = re.compile(r"rn|nl|nr|dt|kt|pg|tk|ds|zr|mr|sr|ln")
FORBIDDEN_GRAPHEMES = re.compile(r"c|ç|q|w|lh|nh|ch|j")

STOPWORDS_PT = {
    "para", "como", "pelo", "pela", "pelos", "pelas", "entre", "sobre",
    "contra", "desde", "após", "ante", "perante", "segundo", "durante",
    "dentro", "fora", "acima", "abaixo", "através", "perto", "longe",
    "muito", "pouco", "mais", "menos", "todo", "toda", "todos", "todas",
    "outro", "outra", "outros", "outras", "mesmo", "mesma", "cada",
    "qualquer", "algum", "alguma", "nenhum", "nenhuma", "este", "esta",
    "esse", "essa", "aquele", "aquela", "isto", "isso", "aquilo", "onde",
    "quando", "quanto", "quanta", "quem", "qual", "quais", "cujo", "cuja",
    "fazer", "feito", "feita", "tornar", "modo", "forma", "ação", "efeito",
    "relativo", "próprio", "dotado", "cheio", "coberto", "provido",
    "pequeno", "pequena", "grande", "alto", "alta", "baixo", "baixa",
    "longo", "longa", "curto", "curta", "novo", "nova", "velho", "velha",
    "antigo", "antiga", "sagrado", "sagrada", "imperial", "real",
    "montanha", "montanhas", "serra", "serras", "pedra", "rocha", "madeira",
    "água", "fogo", "vento", "noite", "terra", "casa", "corpo", "sangue",
    "instrumento", "lugar", "oficina", "recinto", "arte", "técnica",
    "voltar", "deixar", "repetidamente", "novamente", "habitualmente",
}

def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

def normalize_treppio_for_comparison(lemma: str) -> str:
    s = strip_accents(lemma.lower().replace("'", ""))
    for suf in ("gar", "tek", "ia", "or", "il", "te", "et", "ve", "ur"):
        if len(s) > len(suf) + 2 and s.endswith(suf):
            s = s[:-len(suf)]
            break
    if len(s) > 3 and s[-1] in ("e", "a", "o", "i"):
        s = s[:-1]
    return s.replace("k", "c")

def extract_gloss_words(meaning: str) -> list[str]:
    cleaned = strip_accents(meaning.lower())
    words = re.findall(r"[a-z]{4,}", cleaned)
    return [w for w in words if w not in STOPWORDS_PT]

def max_romance_similarity(lemma: str, meaning: str) -> tuple[float, str]:
    t_norm = normalize_treppio_for_comparison(lemma)
    t_raw = strip_accents(lemma.lower().replace("'", "")).replace("k", "c")
    best_sim = 0.0
    best_word = ""
    for w in extract_gloss_words(meaning):
        w_stem = w[:-1] if len(w) > 4 and w[-1] in "aeos" else w
        for cand_t in (t_norm, t_raw):
            for cand_w in (w, w_stem):
                if not cand_t or not cand_w:
                    continue
                ratio = SequenceMatcher(None, cand_t, cand_w).ratio()
                # Check prefix match too (e.g. "abietor" vs "abeto", "kranior" vs "cranio")
                if len(cand_t) >= 4 and len(cand_w) >= 4 and cand_t[:4] == cand_w[:4]:
                    ratio = max(ratio, 0.75)
                if ratio > best_sim:
                    best_sim = ratio
                    best_word = w
    return best_sim, best_word

if __name__ == "__main__":
    import lexico_expansao_v8_1 as exp
    bad_nouns = []
    for n, d, m, e in exp.EXPANSAO_NOUNS_PRIMARIOS:
        sim, w = max_romance_similarity(n, m)
        if sim > 0.50 or FORBIDDEN_GRAPHEMES.search(n.lower()):
            bad_nouns.append((n, sim, w, m))
    print(f"Audit of current EXPANSAO_NOUNS_PRIMARIOS: {len(bad_nouns)}/{len(exp.EXPANSAO_NOUNS_PRIMARIOS)} flagged.")
    bad_verbs = []
    for r, m1, m2, m3, m4 in exp.EXPANSAO_VERB_ROOTS:
        sim, w = max_romance_similarity(r, m1 + " " + m2)
        if sim > 0.50 or FORBIDDEN_GRAPHEMES.search(r.lower()):
            bad_verbs.append((r, sim, w, m1))
    print(f"Audit of current EXPANSAO_VERB_ROOTS: {len(bad_verbs)}/{len(exp.EXPANSAO_VERB_ROOTS)} flagged.")

