# -*- coding: utf-8 -*-
import re
import subprocess
import tempfile
import os

HTML_PATH = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

scripts = re.findall(r"<script(?![^>]*src=)[^>]*>([\s\S]*?)</script>", html)
print(f"[INFO] Encontrados {len(scripts)} blocos <script> inline.")

for idx, code in enumerate(scripts, 1):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
        tf.write(code)
        tmp_path = tf.name
    res = subprocess.run(["node", "--check", tmp_path], capture_output=True, text=True)
    os.remove(tmp_path)
    if res.returncode != 0:
        print(f"[ERRO] Bloco <script> #{idx} falhou no node --check:\n{res.stderr}")
        raise SystemExit(1)
    else:
        print(f"[OK] Bloco <script> #{idx} validado com 0 erros de sintaxe ({len(code):,} chars)!")

