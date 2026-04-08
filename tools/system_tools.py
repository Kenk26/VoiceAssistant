"""
System Tools Module
Handles OS-level actions: opening apps, URLs, files, etc.
These are exposed as LangChain tools for the AI agent.
"""

import os
import sys
import subprocess
import webbrowser
from langchain.tools import tool


# ─── URL / Website Mappings ───────────────────────────────────────────────────

WEBSITE_MAP = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.com",
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
    "maps": "https://maps.google.com",
    "translate": "https://translate.google.com",
    "drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "slides": "https://slides.google.com",
    "calendar": "https://calendar.google.com",
    "meet": "https://meet.google.com",
    "zoom": "https://zoom.us",
}

# ─── App Mappings per OS ──────────────────────────────────────────────────────

APP_MAP = {
    "windows": {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "vlc": "vlc.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code",
    },
    "linux": {
        "terminal": "x-terminal-emulator",
        "file manager": "nautilus",
        "text editor": "gedit",
        "calculator": "gnome-calculator",
        "settings": "gnome-control-center",
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code",
        "firefox": "firefox",
        "chrome": "google-chrome",
        "vlc": "vlc",
    },
    "darwin": {
        "terminal": "Terminal",
        "finder": "Finder",
        "safari": "Safari",
        "chrome": "Google Chrome",
        "firefox": "Firefox",
        "calculator": "Calculator",
        "textedit": "TextEdit",
        "vs code": "Visual Studio Code",
        "vscode": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
        "spotify": "Spotify",
        "vlc": "VLC",
        "notes": "Notes",
    }
}


def get_platform():
    if sys.platform.startswith("win"):
        return "windows"
    elif sys.platform.startswith("darwin"):
        return "darwin"
    else:
        return "linux"


@tool
def open_website(site_name: str) -> str:
    """
    Opens a website or URL in the default browser.
    Provide either a known site name (like 'youtube', 'google', 'github')
    or a full URL (like 'https://example.com').
    """
    site_lower = site_name.strip().lower()

    # Check known sites
    if site_lower in WEBSITE_MAP:
        url = WEBSITE_MAP[site_lower]
    elif site_lower.startswith("http://") or site_lower.startswith("https://"):
        url = site_name
    else:
        # Try as a generic search or add https
        url = f"https://www.{site_lower}.com"

    try:
        webbrowser.open(url)
        return f"✅ Opened {site_name} at {url}"
    except Exception as e:
        return f"❌ Failed to open {site_name}: {e}"


@tool
def open_application(app_name: str) -> str:
    """
    Opens a desktop application by name.
    Examples: 'notepad', 'calculator', 'vs code', 'terminal', 'file manager'.
    """
    platform = get_platform()
    app_lower = app_name.strip().lower()
    app_map = APP_MAP.get(platform, {})

    command = app_map.get(app_lower, app_lower)  # fallback to raw name

    try:
        if platform == "windows":
            os.startfile(command) if command.endswith(":") else subprocess.Popen(
                command, shell=True
            )
        elif platform == "darwin":
            subprocess.Popen(["open", "-a", command])
        else:
            subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"✅ Opened application: {app_name}"
    except Exception as e:
        return f"❌ Could not open '{app_name}': {e}. Make sure it's installed."


@tool
def search_web(query: str) -> str:
    """
    Performs a Google search for the given query in the default browser.
    Use this when the user wants to search for something online.
    """
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}"
    try:
        webbrowser.open(url)
        return f"✅ Searching Google for: {query}"
    except Exception as e:
        return f"❌ Failed to open search: {e}"


@tool
def search_youtube(query: str) -> str:
    """
    Searches YouTube for the given query in the default browser.
    Use this when the user wants to find videos on YouTube.
    """
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    try:
        webbrowser.open(url)
        return f"✅ Searching YouTube for: {query}"
    except Exception as e:
        return f"❌ Failed to open YouTube search: {e}"


@tool
def get_system_info() -> str:
    """
    Returns basic system information like OS, Python version, etc.
    Use when user asks about their system.
    """
    import platform
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Python": platform.python_version(),
        "Processor": platform.processor() or "Unknown",
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())


@tool
def open_file_path(path: str) -> str:
    """
    Opens a file or folder at the given path using the default system application.
    Example: '/home/user/documents' or 'C:\\Users\\docs'
    """
    try:
        platform = get_platform()
        if platform == "windows":
            os.startfile(path)
        elif platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return f"✅ Opened: {path}"
    except Exception as e:
        return f"❌ Could not open path '{path}': {e}"


# Export all tools as a list
SYSTEM_TOOLS = [
    open_website,
    open_application,
    search_web,
    search_youtube,
    get_system_info,
    open_file_path,
]
