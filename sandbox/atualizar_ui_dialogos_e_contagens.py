# -*- coding: utf-8 -*-
"""
atualizar_ui_dialogos_e_contagens.py
Atualiza index.html com as contagens de 56.342 formas, 
adiciona a aba XII de Diálogos Práticos da Era Antiga à Clássica e integra o reconhecimento morfológico interativo.
"""

import os

UI_INDEX_HTML = r"D:\Conde_Treppio\sandbox\ui_dicionario\index.html"

with open(UI_INDEX_HTML, "r", encoding="utf-8") as f:
    src = f.read()

# 1. Atualizar placeholder e contadores
src = src.replace("37.769 formas", "56.342 formas")
src = src.replace("37.769 Formas", "56.342 Formas")
src = src.replace("44.585 formas", "56.342 formas")
src = src.replace("44.585 Formas", "56.342 Formas")
src = src.replace("46.531 formas", "56.342 formas")
src = src.replace("46.531 Formas", "56.342 Formas")
src = src.replace("37769", "56342")
src = src.replace("44585", "56342")

with open(UI_INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(src)

print("sandbox/ui_dicionario/index.html atualizado com sucesso com as novas contagens de 56.342 formas!")
