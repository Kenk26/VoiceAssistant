"""
VoiceFlow AI Assistant - Main GUI Window
Built with Tkinter. Clean, modern dark theme.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_listener import VoiceListener
from tts_engine import TextToSpeech
from agent.voice_agent import VoiceAgent


# ─── Color Palette ────────────────────────────────────────────────────────────
BG_DARK     = "#0d1117"
BG_CARD     = "#161b22"
BG_INPUT    = "#21262d"
BORDER      = "#30363d"
ACCENT      = "#58a6ff"
ACCENT_GLOW = "#1f6feb"
GREEN       = "#3fb950"
RED         = "#f85149"
YELLOW      = "#d29922"
TEXT_PRI    = "#e6edf3"
TEXT_SEC    = "#8b949e"
TEXT_MUT    = "#484f58"
USER_BUBBLE = "#1c2d40"
BOT_BUBBLE  = "#1a2332"
FONT_MONO   = ("Consolas", 10)
FONT_MAIN   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_TITLE  = ("Segoe UI", 14, "bold")
FONT_SMALL  = ("Segoe UI", 8)


class VoiceAssistantApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VoiceFlow — AI Voice Assistant")
        self.root.geometry("820x700")
        self.root.minsize(600, 500)
        self.root.configure(bg=BG_DARK)

        # Core components
        self.listener  = VoiceListener()
        self.tts       = TextToSpeech()
        self.agent     = VoiceAgent()
        self.msg_queue = queue.Queue()

        # State
        self.is_listening   = False
        self.agent_ready    = False
        self.tts_enabled    = tk.BooleanVar(value=True)
        self.continuous_var = tk.BooleanVar(value=False)
        self._stop_event    = threading.Event()
        self._listen_thread = None

        self._build_ui()
        self._start_init_sequence()
        self.root.after(100, self._poll_queue)

    # ─── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_titlebar()
        self._build_main_area()
        self._build_input_row()
        self._build_statusbar()

    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=BG_CARD, height=56)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Logo / title
        tk.Label(
            bar, text="🎙 VoiceFlow", font=FONT_TITLE,
            bg=BG_CARD, fg=TEXT_PRI, padx=16
        ).pack(side="left", pady=10)

        # Model selector
        right = tk.Frame(bar, bg=BG_CARD)
        right.pack(side="right", padx=12)

        tk.Label(right, text="Model:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(
            side="left", padx=(0, 4)
        )
        self.model_var = tk.StringVar(value="minimax-m2.7:cloud")
        self.model_combo = ttk.Combobox(
            right, textvariable=self.model_var, width=14,
            values=VoiceAgent.get_available_models(), state="readonly"
        )
        self.model_combo.pack(side="left")
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_change)

        # TTS toggle
        tts_cb = tk.Checkbutton(
            right, text="🔊 TTS", variable=self.tts_enabled,
            bg=BG_CARD, fg=TEXT_SEC, selectcolor=BG_CARD,
            activebackground=BG_CARD, font=FONT_SMALL
        )
        tts_cb.pack(side="left", padx=8)

        # Clear button
        tk.Button(
            right, text="Clear", command=self._clear_chat,
            bg=BG_INPUT, fg=TEXT_SEC, relief="flat",
            font=FONT_SMALL, cursor="hand2", padx=8
        ).pack(side="left", padx=4)

    def _build_main_area(self):
        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=12, pady=(8, 4))

        # Chat display
        self.chat_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=FONT_MAIN,
            bg=BG_CARD,
            fg=TEXT_PRI,
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            cursor="arrow",
            state="disabled",
            insertbackground=ACCENT,
        )
        self.chat_text.pack(fill="both", expand=True)

        # Configure tags
        self.chat_text.tag_configure("user_name",   foreground=ACCENT,  font=FONT_BOLD)
        self.chat_text.tag_configure("user_text",   foreground=TEXT_PRI)
        self.chat_text.tag_configure("bot_name",    foreground=GREEN,   font=FONT_BOLD)
        self.chat_text.tag_configure("bot_text",    foreground=TEXT_PRI)
        self.chat_text.tag_configure("system_msg",  foreground=TEXT_SEC, font=FONT_SMALL)
        self.chat_text.tag_configure("error_msg",   foreground=RED,      font=FONT_SMALL)
        self.chat_text.tag_configure("tool_msg",    foreground=YELLOW,   font=FONT_SMALL)
        self.chat_text.tag_configure("divider",     foreground=TEXT_MUT)

    def _build_input_row(self):
        row = tk.Frame(self.root, bg=BG_DARK)
        row.pack(fill="x", padx=12, pady=(0, 4))

        # Text entry
        entry_frame = tk.Frame(row, bg=BG_INPUT, highlightbackground=BORDER,
                               highlightthickness=1)
        entry_frame.pack(side="left", fill="x", expand=True)

        self.text_entry = tk.Entry(
            entry_frame, font=FONT_MAIN, bg=BG_INPUT, fg=TEXT_PRI,
            relief="flat", bd=8, insertbackground=ACCENT,
        )
        self.text_entry.pack(fill="x", expand=True)
        self.text_entry.bind("<Return>", lambda e: self._send_text())
        self.text_entry.insert(0, "Type a message or click 🎤 to speak...")
        self.text_entry.config(fg=TEXT_MUT)
        self.text_entry.bind("<FocusIn>",  self._entry_focus_in)
        self.text_entry.bind("<FocusOut>", self._entry_focus_out)

        # Send button
        self.send_btn = tk.Button(
            row, text="Send ➤", command=self._send_text,
            bg=ACCENT_GLOW, fg="white", relief="flat", font=FONT_BOLD,
            cursor="hand2", padx=14, pady=8
        )
        self.send_btn.pack(side="left", padx=(6, 0))

        # Mic button
        self.mic_btn = tk.Button(
            row, text="🎤 Speak", command=self._toggle_listen,
            bg=BG_INPUT, fg=TEXT_PRI, relief="flat", font=FONT_BOLD,
            cursor="hand2", padx=14, pady=8,
            highlightbackground=BORDER, highlightthickness=1
        )
        self.mic_btn.pack(side="left", padx=6)

        # Continuous mode checkbox
        cont_cb = tk.Checkbutton(
            row, text="Continuous",
            variable=self.continuous_var,
            bg=BG_DARK, fg=TEXT_SEC, selectcolor=BG_DARK,
            activebackground=BG_DARK, font=FONT_SMALL
        )
        cont_cb.pack(side="left")

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG_CARD, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_dot = tk.Label(bar, text="●", fg=YELLOW, bg=BG_CARD, font=FONT_SMALL)
        self.status_dot.pack(side="left", padx=(10, 2))

        self.status_label = tk.Label(
            bar, text="Initializing...", fg=TEXT_SEC, bg=BG_CARD, font=FONT_SMALL
        )
        self.status_label.pack(side="left")

        # Right side info
        tk.Label(
            bar, text="Powered by Ollama + LangChain",
            fg=TEXT_MUT, bg=BG_CARD, font=FONT_SMALL
        ).pack(side="right", padx=10)

    # ─── Entry Placeholder ────────────────────────────────────────────────────

    def _entry_focus_in(self, _):
        if self.text_entry.cget("fg") == TEXT_MUT:
            self.text_entry.delete(0, tk.END)
            self.text_entry.config(fg=TEXT_PRI)

    def _entry_focus_out(self, _):
        if not self.text_entry.get():
            self.text_entry.insert(0, "Type a message or click 🎤 to speak...")
            self.text_entry.config(fg=TEXT_MUT)

    # ─── Chat Display ─────────────────────────────────────────────────────────

    def _append_message(self, sender: str, message: str, msg_type: str = "normal"):
        self.chat_text.config(state="normal")

        if msg_type == "system":
            self.chat_text.insert(tk.END, f"  ⚙  {message}\n", "system_msg")
        elif msg_type == "error":
            self.chat_text.insert(tk.END, f"  ✗  {message}\n", "error_msg")
        elif msg_type == "tool":
            self.chat_text.insert(tk.END, f"  ⚡ {message}\n", "tool_msg")
        elif sender == "You":
            self.chat_text.insert(tk.END, "\n  You  ", "user_name")
            self.chat_text.insert(tk.END, f"\n  {message}\n", "user_text")
        else:
            self.chat_text.insert(tk.END, "\n  VoiceFlow  ", "bot_name")
            self.chat_text.insert(tk.END, f"\n  {message}\n", "bot_text")

        self.chat_text.config(state="disabled")
        self.chat_text.see(tk.END)

    def _set_status(self, text: str, color: str = TEXT_SEC):
        self.status_label.config(text=text, fg=color)
        dot_color = GREEN if "ready" in text.lower() or "✅" in text else \
                    RED   if "error" in text.lower() or "❌" in text else \
                    YELLOW
        self.status_dot.config(fg=dot_color)

    def _clear_chat(self):
        self.chat_text.config(state="normal")
        self.chat_text.delete("1.0", tk.END)
        self.chat_text.config(state="disabled")
        self.agent.clear_memory()
        self._append_message("", "Chat cleared. Memory reset.", "system")

    # ─── Queue Polling ────────────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                action, *args = self.msg_queue.get_nowait()
                if action == "status":
                    self._set_status(args[0])
                elif action == "append":
                    self._append_message(*args)
                elif action == "agent_ready":
                    self.agent_ready = True
                    self._set_status("✅ Ready", GREEN)
                    self.mic_btn.config(state="normal")
                    self.send_btn.config(state="normal")
                elif action == "agent_fail":
                    self._set_status("❌ Agent failed — check Ollama", RED)
                    self._append_message("", args[0], "error")
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _q(self, *args):
        self.msg_queue.put(args)

    # ─── Initialization ───────────────────────────────────────────────────────

    def _start_init_sequence(self):
        self.mic_btn.config(state="disabled")
        self.send_btn.config(state="disabled")

        def _init():
            # Calibrate microphone
            self._q("status", "Calibrating microphone...")
            self.listener.calibrate(lambda m: self._q("status", m))

            # Initialize agent
            self._q("status", "Loading AI model...")
            ok = self.agent.initialize(lambda m: self._q("status", m))

            if ok:
                self._q("agent_ready")
                self._q("append", "VoiceFlow",
                        "Hello! I'm VoiceFlow, your AI voice assistant.\n"
                        "  • Say or type anything to chat with me\n"
                        "  • Say 'open YouTube' to open websites\n"
                        "  • Say 'open calculator' to launch apps\n"
                        "  • Say 'search for...' to search Google\n"
                        "  • Enable Continuous mode to keep listening")
            else:
                self._q("agent_fail",
                        "Could not connect to Ollama. "
                        "Make sure Ollama is running and the model is pulled.")

        threading.Thread(target=_init, daemon=True).start()

    # ─── Voice Input ──────────────────────────────────────────────────────────

    def _toggle_listen(self):
        if not self.agent_ready:
            self._append_message("", "Agent not ready yet. Please wait.", "error")
            return

        if self.is_listening:
            self._stop_listening()
        else:
            self._start_listening()

    def _start_listening(self):
        self.is_listening = True
        self.mic_btn.config(text="⏹ Stop", bg=RED, fg="white")
        self._set_status("🎤 Listening...")

        if self.continuous_var.get():
            self._stop_event.clear()
            self._listen_thread = self.listener.listen_continuous(
                on_result=self._on_voice_result,
                on_error=self._on_voice_error,
                on_status=lambda m: self._q("status", m),
                stop_event=self._stop_event,
            )
        else:
            self._listen_thread = self.listener.listen_once(
                on_result=self._on_voice_result,
                on_error=self._on_voice_error,
                on_status=lambda m: self._q("status", m),
            )
            # Auto-reset button after single listen
            def _reset():
                if self._listen_thread:
                    self._listen_thread.join(timeout=20)
                self.root.after(0, self._stop_listening)
            threading.Thread(target=_reset, daemon=True).start()

    def _stop_listening(self):
        self._stop_event.set()
        self.is_listening = False
        self.mic_btn.config(text="🎤 Speak", bg=BG_INPUT, fg=TEXT_PRI)
        if self.agent_ready:
            self._set_status("✅ Ready", GREEN)

    def _on_voice_result(self, text: str):
        self._q("append", "You", text)
        self._q("status", "🤖 Thinking...")
        self._process_input(text)

    def _on_voice_error(self, error: str):
        self._q("append", "", error, "error")
        self._q("status", "✅ Ready", GREEN)
        if not self.continuous_var.get():
            self.root.after(0, self._stop_listening)

    # ─── Text Input ───────────────────────────────────────────────────────────

    def _send_text(self):
        if not self.agent_ready:
            return
        text = self.text_entry.get().strip()
        if not text or text == "Type a message or click 🎤 to speak...":
            return
        self.text_entry.delete(0, tk.END)
        self._append_message("You", text)
        self._set_status("🤖 Thinking...")
        self._process_input(text)

    # ─── Agent Processing ─────────────────────────────────────────────────────

    def _process_input(self, user_input: str):
        def _run():
            response = self.agent.process(user_input)
            self._q("append", "VoiceFlow", response)
            self._q("status", "✅ Ready")

            # TTS
            if self.tts_enabled.get() and self.tts.is_available:
                self.tts.speak(response)

        threading.Thread(target=_run, daemon=True).start()

    # ─── Model Change ─────────────────────────────────────────────────────────

    def _on_model_change(self, _):
        new_model = self.model_var.get()
        self.agent_ready = False
        self.mic_btn.config(state="disabled")
        self.send_btn.config(state="disabled")
        self._append_message("", f"Switching to model: {new_model}...", "system")

        def _switch():
            ok = self.agent.change_model(
                new_model, lambda m: self._q("status", m)
            )
            if ok:
                self._q("agent_ready")
                self._q("append", "", f"Switched to {new_model}", "system")
            else:
                self._q("agent_fail", f"Failed to load model: {new_model}")

        threading.Thread(target=_switch, daemon=True).start()
