# -*- coding: utf-8 -*-
r"""
sincronizar_expansao_109k.py
Compila o dicionário integral, lê as métricas dinâmicas do JSON gerado,
atualiza os contadores visuais na UI e no README e sincroniza todos os artefatos
com G:\Meu Drive\Conde_Treppio e as skills do Conde.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, r"D:\Conde_Treppio\sandbox")
import gerador_dicionario_integral_sandbox as gen


def _fmt_pt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def main():
    # 1. Executar primeira passagem para obter o JSON atualizado com a contagem exata
    gen.generate_all_files()

    json_p = r"D:\Conde_Treppio\dicionario_formas_expandidas.json"
    with open(json_p, "r", encoding="utf-8") as f:
        m = json.load(f)["metadata"]

    forms_raw = str(m["total_expanded_word_forms"])
    forms_pt = _fmt_pt(m["total_expanded_word_forms"])
    nouns_c = str(m["nouns_count"])
    verbs_c = str(m["verb_stems_quadripartite"])
    adjs_c = str(m["adjectives_count"])
    advs_c = str(m["adverbs_count"])

    # 2. Atualizar contadores dinâmicos em ui_dicionario/index.html
    ui_path = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"
    with open(ui_path, "r", encoding="utf-8") as f:
        src = f.read()

    src = re.sub(r'(<strong id="stat-forms">)[\d\.]+(</strong>)', rf"\g<1>{forms_pt}\2", src)
    src = re.sub(r'(<strong id="stat-nouns">)\d+(</strong>)', rf"\g<1>{nouns_c}\2", src)
    src = re.sub(r'(<strong id="stat-verbs">)\d+(</strong>)', rf"\g<1>{verbs_c}\2", src)
    src = re.sub(r'(<strong id="stat-adjs">)\d+(</strong>)', rf"\g<1>{adjs_c}\2", src)
    src = re.sub(r'(<span class="tab-count" id="hub-cnt-dict">)[\d\.]+(</span>)', rf"\g<1>{forms_pt}\2", src)
    src = re.sub(r'(Conjugador Verbal <span class="tab-count">)\d+ Verbos(</span>)', rf"\g<1>{verbs_c} Verbos\2", src)
    src = re.sub(r'Buscar em [\d\.]+ formas', f"Buscar em {forms_pt} formas", src)
    src = re.sub(r'm\.total_expanded_word_forms \|\| \d+', f"m.total_expanded_word_forms || {forms_raw}", src)

    with open(ui_path, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"[OK] UI atualizada dinamicamente ({forms_pt} formas, {nouns_c} nomes, {verbs_c} verbos): {ui_path}")

    # 3. Atualizar README.md
    readme_path = r"D:\Conde_Treppio\README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        rd = f.read()

    rd = re.sub(r"\*\*[\d\.]+ formas flexionadas e derivadas\*\*", f"**{forms_pt} formas flexionadas e derivadas**", rd)
    rd = re.sub(r"\d+ substantivos, \d+ verbos da matriz quadripartida, \d+ adjetivos, \d+ advérbios",
                f"{nouns_c} substantivos, {verbs_c} verbos da matriz quadripartida, {adjs_c} adjetivos, {advs_c} advérbios", rd)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(rd)
    print(f"[OK] README atualizado dinamicamente: {readme_path}")

    # 4. Reexecutar generate_all_files() para propagar o HTML atualizado para docs/, dist/ e android_apk/
    gen.generate_all_files()

    # 5. Sincronizar com G:\Meu Drive\Conde_Treppio e skills/conde
    src_root = r"D:\Conde_Treppio"
    targets = [
        r"G:\Meu Drive\Conde_Treppio",
        r"C:\Users\Usuário\.gemini\config\skills\conde",
        r"C:\Users\Usuário\.gemini\skills\conde",
    ]

    rel_files = [
        "README.md",
        "dicionario_formas_expandidas.json",
        r"docs\index.html",
        r"docs\dados_dicionario_conde.js",
        r"docs\dicionario_formas_expandidas.json",
        r"dist\Codice_Treppio_Portatil.html",
        r"sandbox\fila_temas_expansao_horaria.json",
        r"sandbox\lexico_expansao_v8_1.py",
        r"sandbox\validar_sandi_e_colisoes.py",
        r"sandbox\proposta_lexical_expansao_100_raizes.md",
        r"sandbox\gerador_dicionario_integral_sandbox.py",
        r"sandbox\dicionario_geral_treppio_sandbox.md",
        r"sandbox\dicionario_exaustivo\dicionario_formas_expandidas.json",
        r"sandbox\dicionario_exaustivo\verbos_matriz_quadripartite_completa.md",
        r"sandbox\ui_dicionario\index.html",
        r"sandbox\ui_dicionario\dados_dicionario_conde.js",
    ]

    for tgt in targets:
        if not os.path.exists(tgt):
            print(f"[SKIP] Destino não encontrado: {tgt}")
            continue
        copied = 0
        for rf in rel_files:
            s_file = os.path.join(src_root, rf)
            t_file = os.path.join(tgt, rf)
            if os.path.exists(s_file):
                os.makedirs(os.path.dirname(t_file), exist_ok=True)
                if os.path.exists(t_file) and os.path.samefile(s_file, t_file):
                    copied += 1
                    continue
                shutil.copy2(s_file, t_file)
                copied += 1
        print(f"[OK] Sincronizados {copied} arquivos para: {tgt}")


if __name__ == "__main__":
    main()
