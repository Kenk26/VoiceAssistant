# 🎙 VoiceFlow — AI Voice Assistant

A Python-based AI voice assistant powered by Ollama (local & cloud LLMs) and LangChain. Speak or type your commands — VoiceFlow listens, thinks, and responds. It can open websites, launch apps, search the web, and hold conversations, all through a clean dark-themed GUI.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain--Core-0.3+-green)
![Ollama](https://img.shields.io/badge/Ollama-local_%26_cloud-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎤 **Voice Input** | Speak commands via microphone using Google Speech Recognition |
| 🤖 **Ollama LLM** | Supports local models (llama3.2, mistral, phi3) and cloud models (minimax-m2.7:cloud, kimi-k2.5:cloud) |
| 🔗 **LangChain Tool Agent** | `bind_tools()` agent with manual tool dispatch loop — no deprecated APIs |
| 🔊 **Text-to-Speech** | Spoken responses via pyttsx3 (fully offline) |
| 🌐 **Open Websites** | "Open YouTube", "Open GitHub" — launches in your default browser |
| 💻 **Launch Apps** | "Open Notepad", "Open VS Code" — launches desktop applications |
| 🔍 **Web Search** | "Search for X" — opens Google search results |
| 📺 **YouTube Search** | "Search YouTube for X" — opens YouTube results |
| 💬 **Conversation Memory** | Remembers recent chat turns for contextual follow-ups |
| 🔄 **Continuous Mode** | Keep listening automatically for hands-free use |
| 🎨 **Dark UI** | Modern dark-themed Tkinter interface with chat bubbles |
| 🔀 **Model Switching** | Switch between any Ollama model at runtime from the dropdown |

---

## 🗂 Project Structure

```
VoiceAssistant/
├── main.py                  # Entry point
├── voice_listener.py        # Microphone input & speech-to-text
├── tts_engine.py            # Text-to-speech output (pyttsx3)
├── requirements.txt         # Python dependencies
├── INSTALL.md               # Detailed OS-specific setup guide
├── README.md                # This file
│
├── agent/
│   ├── __init__.py
│   └── voice_agent.py       # ChatOllama + bind_tools() agent loop
│
├── tools/
│   ├── __init__.py
│   └── system_tools.py      # LangChain tools: websites, apps, search
│
└── ui/
    ├── __init__.py
    └── app_window.py        # Tkinter GUI — dark theme, chat display
```

---

## 🚀 Quick Start

### 1. Install Ollama
Download from [https://ollama.com/download](https://ollama.com/download), then run a model:

```bash
# Local model
ollama pull llama3.2

# OR use a cloud model (no pull needed)
ollama run minimax-m2.7:cloud
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

> See [INSTALL.md](INSTALL.md) for OS-specific PyAudio installation (required for microphone).

### 3. Run the app

```bash
python main.py
```

---

## 🛠 How It Works

```
User Voice / Text
       │
       ▼
Speech Recognition          ← SpeechRecognition + Google STT
       │
       ▼
 ChatOllama + bind_tools()  ← langchain-ollama + langchain-core
       │
       ├── Tool call? ──► Execute Tool     ← os, subprocess, webbrowser
       │                      │
       │                 ToolMessage ──► LLM again for final answer
       │
       └── Direct answer ──► LLM response
                                  │
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
             TTS (pyttsx3)                 Tkinter UI
             Spoken aloud            Displayed in chat
```

---

## 🤖 Supported Models

VoiceFlow works with any model available in Ollama — local or cloud.

### Local Models
```bash
ollama pull llama3.2       # Fast, general purpose (~2GB)
ollama pull mistral        # Strong instruction following (~4GB)
ollama pull phi4           # Small but capable (~3GB)
ollama pull gemma3         # Google's model (~5GB)
ollama pull qwen2.5        # Great multilingual support
ollama pull deepseek-r1    # Strong reasoning
```

### Cloud Models (via Ollama)
These run in the cloud through Ollama — no local download needed:
```bash
ollama run minimax-m2.7:cloud   # ← Default model in this app
ollama run kimi-k2.5:cloud
```

> Cloud models require an internet connection and Ollama account.

---

## 💬 Example Commands

**Open websites**
```
"Open YouTube"
"Go to GitHub"
"Open Google Maps"
"Open Spotify"
```

**Launch apps**
```
"Open Notepad"
"Launch Calculator"
"Open VS Code"
"Open Terminal"
```

**Search**
```
"Search for Python tutorials"
"Search YouTube for lofi music"
"Look up machine learning"
```

**Conversation**
```
"What is machine learning?"
"Explain recursion simply"
"Write a short poem about coding"
"What's today's date?"
```

---

## ⚙ Configuration

### Change the default model
In `agent/voice_agent.py`, line 36:
```python
model_name: str = "minimax-m2.7:cloud",  # change to any Ollama model
```

### Add more cloud / custom models to the dropdown
In `agent/voice_agent.py`, inside `get_available_models()`:
```python
cloud_models = ["minimax-m2.7:cloud", "kimi-k2.5:cloud"]  # add yours here
```

### Add new website shortcuts
In `tools/system_tools.py`:
```python
WEBSITE_MAP = {
    ...
    "mysite": "https://mysite.com",
}
```

### Add new app shortcuts
In `tools/system_tools.py`:
```python
APP_MAP = {
    "windows": {
        ...
        "my app": "myapp.exe",
    }
}
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `langchain-ollama` | ChatOllama LLM client |
| `langchain-core` | Messages, prompts, tool interfaces |
| `SpeechRecognition` | Voice to text |
| `pyaudio` | Microphone audio capture |
| `pyttsx3` | Offline text-to-speech |
| `requests` | HTTP client |
| `tkinter` | GUI (Python standard library) |

---

## 🔒 Privacy

- **LLM:** Local models run entirely on your machine. Cloud models (e.g. `minimax-m2.7:cloud`) send prompts to Ollama's cloud infrastructure.
- **Speech Recognition:** Uses Google STT by default — your audio is sent to Google for transcription. For fully offline STT, modify `voice_listener.py` to use `recognize_vosk()` or `recognize_whisper()`.
- **No telemetry** is collected by this app itself.

---

## 🤝 Contributing

1. Fork the repository
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.com) — local & cloud LLM runtime
- [LangChain](https://langchain.com) — LLM tooling framework
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) — voice input
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) — offline TTS
