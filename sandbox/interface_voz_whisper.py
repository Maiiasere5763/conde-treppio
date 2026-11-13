# -*- coding: utf-8 -*-
"""
interface_voz_whisper.py
Interface Gráfica Desktop (GUI) de Conversação por Voz Bidirecional (Whisper STT + Agy/Conde LLM + Neural TTS)
Estética: Obsidiana Soberana & Ouro Imperial (Era Clássica V8.2)
- Escuta o microfone do usuário e transcreve localmente com Faster-Whisper / OpenAI Whisper.
- Consulta o Códice Tréppio (153.005+ formas) e o agente Antigravity (agy.exe) / Motor Filológico do Conde.
- Responde em texto no chat da janela E fala a resposta em voz alta (Edge-TTS Neural pt-BR-AntonioNeural / FranciscaNeural + fallback SAPI).
"""
import asyncio
import ctypes
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import wave
import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np

# Ativar High-DPI no Windows para tipografia nítida
if os.name == "nt":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Caminhos principais
ROOT_DIR = r"D:\Conde_Treppio"
DICT_JSON = os.path.join(ROOT_DIR, "dicionario_formas_expandidas.json")
AGY_EXE = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Usuário"), ".gemini", "bin", "agy.exe")
VOICE_LOG_PATH = os.path.join(ROOT_DIR, "sandbox", "historico_conversa_voz.json")


class CondeVoiceBrain:
    """Cérebro híbrido que combina o Códice Tréppio (153.005+ formas) com o agente Antigravity."""

    def __init__(self):
        self.db = None
        self.reverse_map = {}
        self.pt_search_map = []
        self.conversation_id = None
        self.total_forms = 153005
        self.nouns_count = 1248
        self.verbs_count = 1108
        self.adjs_count = 281
        self._load_dictionary()

    def _load_dictionary(self):
        if not os.path.exists(DICT_JSON):
            return
        try:
            with open(DICT_JSON, "r", encoding="utf-8") as f:
                self.db = json.load(f)
            m = self.db.get("metadata", {})
            self.total_forms = m.get("total_expanded_word_forms", 153005)
            self.nouns_count = len(self.db.get("substantivos", {}))
            self.verbs_count = len(self.db.get("verbos_quadripartite", {})) * 4
            self.adjs_count = len(self.db.get("adjetivos", {}))

            for lemma, data in self.db.get("substantivos", {}).items():
                sig = data.get("significado", "")
                self.reverse_map[lemma.lower()] = f"Substantivo '{lemma}' ({data.get('declinacao')}ª decl.): {sig}"
                self.pt_search_map.append((sig.lower(), f"Substantivo '{lemma}': {sig}"))
            for root, axes in self.db.get("verbos_quadripartite", {}).items():
                pos = axes.get("1. Positivo", {})
                sig = pos.get("meaning", "")
                inf = pos.get("conjugation", {}).get("Infinitivo(-ur)", f"{root}ur")
                self.reverse_map[root.lower()] = f"Raiz verbal '{root}-' (Inf. {inf}): {sig}"
                self.reverse_map[inf.lower()] = f"Verbo '{inf}' (raiz {root}-): {sig}"
                self.pt_search_map.append((sig.lower(), f"Verbo '{inf}' (raiz {root}-): {sig}"))
            for adj, data in self.db.get("adjetivos", {}).items():
                sig = data.get("Significado", "")
                self.reverse_map[adj.lower()] = f"Adjetivo '{adj}' (Sup. {data.get('Superl.Sg(-n)')}): {sig}"
                self.pt_search_map.append((sig.lower(), f"Adjetivo '{adj}': {sig}"))
        except Exception as e:
            print(f"[Brain] Aviso ao carregar dicionário: {e}")

    def lookup_context(self, user_text: str) -> str:
        if not self.db:
            return ""
        words = [w.strip(".,?!:;\"'()[]") for w in user_text.lower().split() if len(w) >= 3]
        hits = []
        for w in words:
            if w in self.reverse_map:
                hits.append(self.reverse_map[w])
        for w in words:
            if len(w) >= 4:
                for pt_sig, desc in self.pt_search_map:
                    if re.search(rf"\b{re.escape(w)}\b", pt_sig):
                        if desc not in hits:
                            hits.append(desc)
                        if len(hits) >= 8:
                            break
            if len(hits) >= 8:
                break
        if not hits:
            return ""
        return f"Contexto do Códice Tréppio ({self.total_forms:,} formas): ".replace(",", ".") + " | ".join(hits[:8])

    def ask(self, user_text: str) -> str:
        ctx = self.lookup_context(user_text)
        prompt = (
            "Você está conversando por voz em tempo real com o usuário no modo assistente/Conde. "
            "Responda de forma natural, clara, direta e falada (sem blocos longos de markdown, máximo de 2 a 4 frases, "
            "pois sua resposta será lida em voz alta por síntese de voz). "
        )
        if ctx:
            prompt += f"\n[{ctx}]\n"
        prompt += f"\nUsuário disse: {user_text}"

        if os.path.exists(AGY_EXE):
            try:
                cmd = [AGY_EXE, "-p", prompt, "--disable-slash-commands", "--dangerously-skip-permissions"]
                if self.conversation_id:
                    cmd.extend(["--conversation", self.conversation_id])
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=28,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                out = (proc.stdout or "").strip()
                if out and proc.returncode == 0:
                    return self._clean_for_speech(out)
            except Exception as e:
                print(f"[Brain] Fallback local acionado ({e})")

        return self._local_conde_fallback(user_text, ctx)

    def _local_conde_fallback(self, user_text: str, ctx: str) -> str:
        if ctx:
            itens = re.sub(r"^Contexto do Códice Tréppio \([^)]+\):\s*", "", ctx)
            return (
                f"Consultei o Códice Imperial da Era Clássica V8.2 para você. Encontrei os seguintes registros: {itens}. "
                f"Deseja que eu decline ou conjugue algum desses termos?"
            )
        low = user_text.lower()
        if any(x in low for x in ["quantas palavras", "quantas formas", "dicionário", "dicionario", "tamanho"]):
            return (
                f"Atualmente o Códice Morfológico Exaustivo da Língua Tréppia conta com {self.total_forms:,} formas flexionadas e derivadas, "
                f"abrangendo {self.nouns_count:,} substantivos, {self.verbs_count:,} verbos na Matriz Quadripartite e {self.adjs_count} adjetivos."
            ).replace(",", ".")
        return (
            f"Ouvi perfeitamente o que você disse: '{user_text}'. "
            f"Estou conectado ao Códice Tréppio de {self.total_forms:,} formas. Diga uma palavra em português ou em tréppio para analisarmos, "
            f"ou peça qualquer tarefa!"
        ).replace(",", ".")

    @staticmethod
    def _clean_for_speech(text: str) -> str:
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"[*_`#>~]+", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        return text.strip()


def to_treppio_tts_pt_br(token: str) -> str:
    """Converte um vocábulo Tréppio para aproximação fonética em TTS pt-BR (G=/g/ guitarra, S=/s/ sapato, X=/x/)."""
    w = re.sub(r"([gG])(?=[eiyéíêýEIYÉÍÊÝ])", lambda m: m.group(1) + "u", token.replace("'", " "))
    w = re.sub(r"([aeiouyáéíóúýäëïöüAEIOUYÁÉÍÓÚÝÄËÏÖÜ])s([aeiouyáéíóúýäëïöüAEIOUYÁÉÍÓÚÝÄËÏÖÜ])", r"\1ss\2", w)
    w = w.replace("x", "rr").replace("X", "Rr").replace("ë", "é").replace("Ë", "É")
    return w


def speak_text_aloud(text: str, voice: str = "pt-BR-AntonioNeural"):
    """Fala a resposta em voz alta usando Edge-TTS Neural (com fallback para SAPI nativo do Windows)."""
    norm_txt = re.sub(r"`([^`\n]+)`", lambda m: " ".join(to_treppio_tts_pt_br(tok) for tok in m.group(1).split()), text)
    clean_txt = CondeVoiceBrain._clean_for_speech(norm_txt)
    if not clean_txt:
        return

    try:
        import edge_tts
        tmp_mp3 = os.path.join(tempfile.gettempdir(), f"conde_reply_{int(time.time()*1000)}.mp3")

        async def _gen():
            comm = edge_tts.Communicate(clean_txt, voice=voice, rate="+5%")
            await comm.save(tmp_mp3)

        asyncio.run(_gen())

        if os.path.exists(tmp_mp3) and os.path.getsize(tmp_mp3) > 200:
            ps_play = (
                f"Add-Type -AssemblyName presentationCore; "
                f"$p = New-Object System.Windows.Media.MediaPlayer; "
                f"$p.Open([Uri]::new('{tmp_mp3}')); "
                f"$p.Play(); "
                f"Start-Sleep -Milliseconds 400; "
                f"while ($p.NaturalDuration.HasTimeSpan -and $p.Position -lt $p.NaturalDuration.TimeSpan) {{ Start-Sleep -Milliseconds 200 }}; "
                f"$p.Close()"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_play],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                timeout=60,
            )
            try:
                os.remove(tmp_mp3)
            except Exception:
                pass
            return
    except Exception as e:
        print(f"[TTS] Edge-TTS indisponível ({e}), usando voz nativa do Windows...")

    safe_ps_txt = clean_txt.replace("'", " ").replace('"', " ").replace("\n", " ")
    ps_sapi = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Speak('{safe_ps_txt}')"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_sapi],
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        timeout=60,
    )


class WhisperVoiceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Códice Imperial Tréppio V8.2 — Conversação por Voz com O Conde (Whisper + Voz Neural)")
        self.root.geometry("880x660")
        self.root.configure(bg="#06080d")

        self.is_recording = False
        self.audio_frames = []
        self.stream = None
        self.samplerate = 16000
        self.whisper_model = None
        self.brain = CondeVoiceBrain()
        self.last_reply = (
            f"Saudações da Chancelaria Imperial de Treppênia! O Códice V8.2 conta agora com "
            f"{self.brain.total_forms:,} formas validadas. Como posso servi-lo hoje?".replace(",", ".")
        )
        self.selected_voice = tk.StringVar(value="pt-BR-AntonioNeural")

        self._build_ui()
        threading.Thread(target=self._preload_whisper, daemon=True).start()

    def _build_ui(self):
        # Borda Dourada Superior
        gold_strip = tk.Frame(self.root, bg="#d4af37", height=2)
        gold_strip.pack(fill=tk.X)

        # Header Imperial
        header = tk.Frame(self.root, bg="#0f1422", pady=14, padx=22)
        header.pack(fill=tk.X)

        top_row = tk.Frame(header, bg="#0f1422")
        top_row.pack(fill=tk.X)

        title_lbl = tk.Label(
            top_row,
            text="𝓣  CHANCELARIA VOCAL DO CONDE — WHISPER STT & VOZ NEURAL (V8.2)",
            font=("Georgia", 13, "bold"),
            fg="#fde28e",
            bg="#0f1422",
        )
        title_lbl.pack(side=tk.LEFT)

        stats_txt = (
            f"⚡ {self.brain.total_forms:,} Formas • {self.brain.nouns_count:,} Nomes • "
            f"{self.brain.verbs_count:,} Verbos"
        ).replace(",", ".")
        stats_lbl = tk.Label(
            top_row,
            text=stats_txt,
            font=("Consolas", 9, "bold"),
            fg="#34c787",
            bg="#141a2c",
            padx=10,
            pady=4,
        )
        stats_lbl.pack(side=tk.RIGHT)

        sub_row = tk.Frame(header, bg="#0f1422")
        sub_row.pack(fill=tk.X, pady=(6, 0))

        self.status_lbl = tk.Label(
            sub_row,
            text="⏳ Inicializando motor acústico Faster-Whisper em cache local...",
            font=("Segoe UI", 9, "bold"),
            fg="#9da9c5",
            bg="#0f1422",
        )
        self.status_lbl.pack(side=tk.LEFT)

        # Seletor de Voz Neural + Botão Repetir
        voice_frame = tk.Frame(sub_row, bg="#0f1422")
        voice_frame.pack(side=tk.RIGHT)

        tk.Label(
            voice_frame,
            text="Voz Neural:",
            font=("Segoe UI", 9),
            fg="#d4af37",
            bg="#0f1422",
        ).pack(side=tk.LEFT, padx=(0, 4))

        voice_menu = tk.OptionMenu(
            voice_frame,
            self.selected_voice,
            "pt-BR-AntonioNeural",
            "pt-BR-FranciscaNeural",
        )
        voice_menu.config(
            bg="#141a2c",
            fg="#fde28e",
            activebackground="#232c45",
            activeforeground="#fde28e",
            highlightthickness=1,
            highlightbackground="#d4af37",
            relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"),
        )
        voice_menu.pack(side=tk.LEFT, padx=(0, 8))

        repeat_btn = tk.Button(
            voice_frame,
            text="🔊 Ouvir Última Resposta",
            font=("Segoe UI", 8, "bold"),
            bg="#161d31",
            fg="#fde28e",
            activebackground="#d4af37",
            activeforeground="#06080d",
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.repeat_last_reply,
        )
        repeat_btn.pack(side=tk.LEFT)

        # Área de Chat Obsidiana
        chat_frame = tk.Frame(self.root, bg="#06080d", padx=20, pady=12)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_box = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0f1422",
            fg="#f2f5fc",
            insertbackground="#fde28e",
            relief=tk.FLAT,
             highlightthickness=1,
            highlightbackground="#232c45",
            padx=16,
            pady=16,
        )
        self.chat_box.pack(fill=tk.BOTH, expand=True)
        self.chat_box.tag_config("user", foreground="#579cf8", font=("Segoe UI", 11, "bold"))
        self.chat_box.tag_config("conde", foreground="#fde28e", font=("Georgia", 11, "bold"))
        self.chat_box.tag_config("sys", foreground="#9da9c5", font=("Segoe UI", 10, "italic"))

        self._append_chat(
            "Chancelaria Imperial (/conde)",
            f"Bem-vindo à Audiência Vocal do Conde! O Códice V8.2 está carregado com {self.brain.total_forms:,} formas "
            f"e a fila de 200 temas semânticos opera a cada 30 minutos.\n"
            f"Clique em '🎙️ INICIAR GRAVAÇÃO DE VOZ' abaixo (ou digite no campo) para falar comigo e ouvir minha resposta!".replace(",", "."),
            "sys",
        )

        # Controles Inferiores
        ctrl_frame = tk.Frame(self.root, bg="#0f1422", pady=14, padx=20)
        ctrl_frame.pack(fill=tk.X)

        self.rec_btn = tk.Button(
            ctrl_frame,
            text="🎙️ INICIAR GRAVAÇÃO DE VOZ",
            font=("Segoe UI", 11, "bold"),
            bg="#d4af37",
            fg="#06080d",
            activebackground="#fde28e",
            activeforeground="#06080d",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.toggle_recording,
        )
        self.rec_btn.pack(side=tk.LEFT, padx=(0, 12))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            ctrl_frame,
            textvariable=self.entry_var,
            font=("Segoe UI", 11),
            bg="#06080d",
            fg="#f2f5fc",
            insertbackground="#fde28e",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#d4af37",
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_typed_message())

        send_btn = tk.Button(
            ctrl_frame,
            text="Enviar ➔",
            font=("Segoe UI", 10, "bold"),
            bg="#161d31",
            fg="#fde28e",
            activebackground="#d4af37",
            activeforeground="#06080d",
            relief=tk.FLAT,
            padx=16,
            pady=9,
            cursor="hand2",
            command=self.send_typed_message,
        )
        send_btn.pack(side=tk.RIGHT)

    def _preload_whisper(self):
        try:
            from faster_whisper import WhisperModel
            self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            self._set_status("✅ Pronto! Microfone ativo + Faster-Whisper (base) + Voz Neural carregados.")
        except Exception:
            try:
                import whisper
                self.whisper_model = whisper.load_model("base")
                self._set_status("✅ Pronto! Microfone ativo + OpenAI Whisper (base) carregado.")
            except Exception as e:
                self._set_status(f"⚠️ Erro ao carregar Whisper: {e}")

    def _set_status(self, msg: str):
        self.root.after(0, lambda: self.status_lbl.config(text=msg))

    def _append_chat(self, speaker: str, text: str, tag: str):
        def _do():
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, f"{speaker}: ", tag)
            self.chat_box.insert(tk.END, f"{text}\n\n")
            self.chat_box.see(tk.END)
            self.chat_box.config(state=tk.DISABLED)
        self.root.after(0, _do)

    def repeat_last_reply(self):
        if not self.last_reply:
            return
        voice = self.selected_voice.get()
        self._set_status(f"🔊 Reproduzindo última resposta ({voice})...")
        threading.Thread(target=self._speak_and_restore, args=(self.last_reply, voice), daemon=True).start()

    def _speak_and_restore(self, text: str, voice: str):
        speak_text_aloud(text, voice=voice)
        self._set_status("✅ Pronto! Clique em '🎙️ INICIAR GRAVAÇÃO DE VOZ' para falar novamente.")

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        import sounddevice as sd
        self.audio_frames = []
        self.is_recording = True
        self.rec_btn.config(text="⏹️ PARAR E ENVIAR FALA", bg="#e25c68", fg="#ffffff", activebackground="#ff7b86")
        self._set_status("🔴 Ouvindo seu microfone... Fale agora e clique em 'PARAR E ENVIAR FALA' quando concluir.")

        def _callback(indata, frames, time_info, status):
            if self.is_recording:
                self.audio_frames.append(indata.copy())

        try:
            self.stream = sd.InputStream(samplerate=self.samplerate, channels=1, dtype="int16", callback=_callback)
            self.stream.start()
        except Exception as e:
            self.is_recording = False
            self.rec_btn.config(text="🎙️ INICIAR GRAVAÇÃO DE VOZ", bg="#d4af37", fg="#06080d")
            self._set_status(f"⚠️ Erro ao abrir microfone: {e}")

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        self.rec_btn.config(text="🎙️ INICIAR GRAVAÇÃO DE VOZ", bg="#d4af37", fg="#06080d", activebackground="#fde28e")
        if not self.audio_frames:
            self._set_status("⚠️ Nenhum áudio capturado.")
            return

        self._set_status("⏳ Transcrevendo sua fala com o Whisper...")
        frames_copy = list(self.audio_frames)
        threading.Thread(target=self._process_recorded_audio, args=(frames_copy,), daemon=True).start()

    def _process_recorded_audio(self, frames):
        audio = np.concatenate(frames, axis=0)
        tmp_wav = os.path.join(tempfile.gettempdir(), "conde_gui_voice.wav")
        with wave.open(tmp_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio.tobytes())

        try:
            from faster_whisper import WhisperModel
            if isinstance(self.whisper_model, WhisperModel):
                segments, _ = self.whisper_model.transcribe(tmp_wav, language="pt", beam_size=5)
                user_text = " ".join(s.text.strip() for s in segments).strip()
            else:
                import whisper
                if self.whisper_model is None:
                    self.whisper_model = whisper.load_model("base")
                res = self.whisper_model.transcribe(tmp_wav, language="pt", fp16=False)
                user_text = res.get("text", "").strip()
        except Exception as e:
            self._set_status(f"⚠️ Erro na transcrição: {e}")
            return

        if not user_text:
            self._set_status("⚠️ Nenhuma fala detectada no áudio. Tente falar mais próximo ao microfone.")
            return

        self._handle_user_message(user_text)

    def send_typed_message(self):
        txt = self.entry_var.get().strip()
        if not txt:
            return
        self.entry_var.set("")
        threading.Thread(target=self._handle_user_message, args=(txt,), daemon=True).start()

    def _handle_user_message(self, user_text: str):
        self._append_chat("Você", user_text, "user")
        self._set_status("🧠 Consultando o Conde / Antigravity...")

        reply = self.brain.ask(user_text)
        self.last_reply = reply
        self._append_chat("O Conde / Antigravity", reply, "conde")

        try:
            hist = []
            if os.path.exists(VOICE_LOG_PATH):
                with open(VOICE_LOG_PATH, "r", encoding="utf-8") as f:
                    hist = json.load(f)
            hist.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "voce": user_text, "resposta": reply})
            with open(VOICE_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(hist[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        voice = self.selected_voice.get()
        self._set_status(f"🔊 Falando resposta em voz alta ({voice})...")
        speak_text_aloud(reply, voice=voice)
        self._set_status("✅ Pronto! Clique em '🎙️ INICIAR GRAVAÇÃO DE VOZ' para falar novamente.")


if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperVoiceApp(root)
    root.mainloop()
