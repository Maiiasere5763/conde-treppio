# -*- coding: utf-8 -*-
r"""
servidor_ui_dicionario.py
Servidor HTTP local para a UI do Dicionário Geral da Língua Tréppia (Era Clássica V8.1).
Alimenta a interface diretamente da base de dados do /conde (D:\Conde_Treppio) e permite
recompilar o banco morfológico ao vivo pelo endpoint POST /api/recompilar.
"""

import os
import sys
import json
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = r"D:\Conde_Treppio"
SANDBOX_DIR = os.path.join(BASE_DIR, "sandbox")
UI_DIR = os.path.join(SANDBOX_DIR, "ui_dicionario")
JSON_DB_PATH = os.path.join(SANDBOX_DIR, "dicionario_exaustivo", "dicionario_formas_expandidas.json")

if SANDBOX_DIR not in sys.path:
    sys.path.insert(0, SANDBOX_DIR)

import gerador_dicionario_integral_sandbox as gerador


class CondeDictionaryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/db"):
            if not os.path.exists(JSON_DB_PATH):
                gerador.generate_all_files()
            with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
                payload = f.read().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/recompilar"):
            gerador.generate_all_files()
            with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
                db_data = json.load(f)
            resp = json.dumps({"status": "ok", "db": db_data}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        self.send_error(404, "Endpoint nao encontrado")


def run_server(port: int = 8765, open_browser: bool = False):
    gerador.generate_all_files()
    server = ThreadingHTTPServer(("127.0.0.1", port), CondeDictionaryHandler)
    url = f"http://localhost:{port}"
    print(f"=== Servidor da UI do Dicionario Treppio (/conde) ativo em {url} ===")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.server_close()


if __name__ == "__main__":
    should_open = "--open" in sys.argv
    run_server(port=8765, open_browser=should_open)
