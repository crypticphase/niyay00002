"""
NEXUS GOD WRITER - Entry Point

Run: python main.py
"""

import threading
import sys
import os
from nexus_god.ui.app import run_app
from nexus_god.ui.project_selector import show_project_selector

def terminal_listener():
    """Listen for terminal commands to stop the program."""
    while True:
        try:
            cmd = sys.stdin.readline().strip().lower()
            if cmd in ['exit', 'stop', 'quit']:
                print("Stopping Nexus God Writer...")
                os._exit(0)
        except EOFError:
            break

if __name__ == "__main__":
    # Start terminal listener thread
    threading.Thread(target=terminal_listener, daemon=True).start()
    print("Nexus God Writer started. Type 'exit' or 'stop' in terminal to quit.")
    
    # แสดงหน้าเลือกโปรเจกต์ก่อน
    selected_project = show_project_selector()
    
    # ถ้าเลือกโปรเจกต์แล้ว ให้เข้าโปรแกรม
    if selected_project:
        run_app()
