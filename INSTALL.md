# VoiceFlow AI Assistant — Installation Guide

## Prerequisites

### 1. Python
- **Version required:** Python 3.9 or higher
- Download from: https://www.python.org/downloads/
- Verify: `python --version`

---

### 2. Ollama (Local LLM Runtime)

Ollama runs LLMs locally on your machine — no API keys needed.

**Install Ollama:**
- **Windows / macOS:** https://ollama.com/download
- **Linux:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

**Pull a model** (choose one based on your RAM):
```bash
# Recommended — fast and capable (~2GB RAM)
ollama pull llama3.2

# Smaller/faster alternative (~1.5GB RAM)
ollama pull phi3

# Larger — better quality (~5GB RAM)
ollama pull mistral

# Large — best quality (~8GB RAM)
ollama pull llama3.1
```

**Start Ollama server** (it may start automatically, but you can also run):
```bash
ollama serve
```
The server runs at `http://localhost:11434` by default.

---

### 3. PyAudio (Microphone Access)

PyAudio requires native system libraries. Follow the steps for your OS:

#### Windows
```bash
pip install pyaudio
```
If that fails, download the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio:
```bash
pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl  # adjust for your Python version
```

#### macOS
```bash
brew install portaudio
pip install pyaudio
```

#### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install python3-dev portaudio19-dev python3-pyaudio
pip install pyaudio
```

#### Fedora / RHEL
```bash
sudo dnf install python3-devel portaudio-devel
pip install pyaudio
```

---

### 4. Tkinter (GUI)

Tkinter ships with Python on Windows and macOS.

**Linux** (if missing):
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

## Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/voiceflow-assistant.git
cd voiceflow-assistant

# 2. Create a virtual environment (recommended)
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Make sure Ollama is running
ollama serve   # in a separate terminal (if not auto-started)

# 5. Launch the app
python main.py
```

---

## Troubleshooting

### "No module named 'pyaudio'"
Follow the PyAudio installation steps above for your OS.

### "Connection refused" / Agent fails to initialize
- Make sure Ollama is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434`
- Pull the model: `ollama pull llama3.2`

### "No speech detected"
- Check your microphone is connected and not muted
- Grant microphone permissions to your terminal/Python
- Try increasing the microphone volume in system settings

### App window doesn't open
- Verify `python3-tk` is installed (Linux)
- Try running with `python3 main.py`

### "ollama: command not found"
- Make sure Ollama is installed and in your PATH
- Restart your terminal after installing Ollama

---

## Configuration

Edit `agent/voice_agent.py` to change defaults:
```python
VoiceAgent(
    model_name="llama3.2",           # Change default model
    base_url="http://localhost:11434", # Change if Ollama runs on different port
    temperature=0.7,                   # 0.0 = deterministic, 1.0 = creative
    memory_window=10,                  # Number of conversation turns to remember
)
```
