import sys
import os

# Ensure the project root is always on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from ui.app_window import VoiceAssistantApp


def main():
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()