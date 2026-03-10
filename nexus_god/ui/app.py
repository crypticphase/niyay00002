from __future__ import annotations

import json
import logging
import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from nexus_god.ai.service import AIService
from nexus_god.core.data_manager import NexusDataManager
from nexus_god.core.logging_utils import configure_logging, install_thread_excepthook, log_error, log_debug, log_info
from nexus_god.ui.tabs import (
    WorldTab, PlotTab, MemoryTab, ItemsTab, SettingsTab, 
    ExportTab, ReviewTab, ChatTab, CharactersTab, EditorTab, WizardTab
)

configure_logging()
install_thread_excepthook()

class NexusGodWriter:
    def __init__(self, root):
        log_debug("Initializing NexusGodWriter main window")
        self.root = root
        self.root.title("🌌 NEXUS GOD WRITER - ULTIMATE CREATOR EDITION (ภาษาไทย)")
        
        self.root.geometry("1500x950")
        self.root.minsize(1000, 600)
        self.root.state('zoomed' if sys.platform == 'win32' else 'normal')
        
        self.root.report_callback_exception = self.handle_exception
        
        self.window_width = 1500
        self.window_height = 950
        
        try:
            self.dm = NexusDataManager()
            self.ai_service = AIService(self.dm.config)
        except Exception as e:
            log_error(f"Critical error initializing: {e}")
            messagebox.showerror("ข้อผิดพลาดร้ายแรง", f"ไม่สามารถเริ่มต้นระบบได้: {e}")
            sys.exit(1)
            
        self.current_tab = "chat"
        self.last_selected_chapter = "ตอนที่ 1"
        
        # Themes
        self.themes = {
            "dark": {
                "bg": "#0f172a", "sidebar": "#1e293b", "card": "#1e293b", "input": "#0f172a",
                "accent": "#38bdf8", "text": "#f8fafc", "muted": "#94a3b8", "border": "#334155",
                "success": "#10b981", "danger": "#ef4444", "warning": "#f59e0b"
            },
            "light": {
                "bg": "#f1f5f9", "sidebar": "#e2e8f0", "card": "#ffffff", "input": "#f8fafc",
                "accent": "#0ea5e9", "text": "#0f172a", "muted": "#64748b", "border": "#cbd5e1",
                "success": "#059669", "danger": "#dc2626", "warning": "#d97706"
            }
        }
        self.colors = self.themes.get(self.dm.config.get("theme", "dark"), self.themes["dark"])
        self.root.configure(bg=self.colors["bg"])
        
        if self.dm.data.get("is_new_project", True):
            from nexus_god.ui.project_setup import show_project_setup
            if not show_project_setup(self.dm, parent=self.root):
                sys.exit(0)
        
        self.build_layout()
        self.setup_responsive_handlers()
        self.start_autosave()
        self.switch_tab("wizard")

    def handle_exception(self, exc, val, tb):
        err_msg = "".join(traceback.format_exception(exc, val, tb))
        log_error(f"Unhandled Exception: {err_msg}")
        messagebox.showerror("เกิดข้อผิดพลาด", f"โปรแกรมพบข้อผิดพลาด: {str(val)}")

    def setup_responsive_handlers(self):
        self.root.bind('<Configure>', lambda e: self.update_responsive_layout(e.width, e.height))
    
    def update_responsive_layout(self, width, height):
        self.window_width = width
        self.window_height = height
        scale_factor = min(max(width / 1500, 0.5), 1.5)
        responsive_padx = max(20, int(40 * scale_factor))
        responsive_pady = max(20, int(30 * scale_factor))
        
        if hasattr(self, 'container'):
            self.container.config(padx=responsive_padx, pady=responsive_pady)
        if hasattr(self, 'sidebar'):
            self.sidebar.config(width=280 if width >= 1200 else 250)

    def build_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors["card"], bd=1, relief="solid", highlightbackground=self.colors["border"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=10, pady=10)
        header = tk.Frame(card, bg=self.colors["sidebar"], pady=12, padx=20)
        header.pack(fill="x")
        tk.Label(header, text=title, font=("Segoe UI", 11, "bold"), bg=self.colors["sidebar"], fg=self.colors["accent"]).pack(side="left")
        content = tk.Frame(card, bg=self.colors["card"], padx=25, pady=20)
        content.pack(fill="both", expand=True)
        return content

    def create_input(self, parent, label, height=1):
        f = tk.Frame(parent, bg=parent["bg"], pady=8)
        f.pack(fill="x")
        tk.Label(f, text=label, font=("Segoe UI", 9, "bold"), bg=parent["bg"], fg=self.colors["muted"]).pack(anchor="w")
        if height > 1:
            inp = scrolledtext.ScrolledText(f, bg=self.colors["input"], fg=self.colors["text"], font=("Segoe UI", 10), height=height, bd=0, wrap=tk.WORD)
        else:
            inp = tk.Entry(f, bg=self.colors["input"], fg=self.colors["text"], font=("Segoe UI", 10), bd=0, insertbackground="white")
            inp.config(highlightbackground=self.colors["border"], highlightthickness=1)
        inp.pack(fill="x", pady=(5, 0))
        return inp

    def update_progress(self):
        score = 0
        total = 6
        if self.dm.data["world"].get("synopsis"): score += 1
        if self.dm.data["world"].get("name"): score += 1
        if self.dm.data["world"].get("genre"): score += 1
        if self.dm.data["characters"]: score += 1
        if self.dm.data["plot"].get("act1"): score += 1
        if self.dm.data["chapters"]: score += 1
        percent = int((score / total) * 100)
        self.progress["value"] = percent
        self.prog_label.config(text=f"{percent}%")

    def start_autosave(self):
        def loop():
            while True:
                threading.Event().wait(300)
                self.dm.save_all()
                self.root.after(0, lambda: self.status_label.config(text=f"บันทึกอัตโนมัติเมื่อ {datetime.now().strftime('%H:%M:%S')}"))
        threading.Thread(target=loop, daemon=True).start()

    def build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar"], pady=25)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="🌌", font=("Segoe UI", 32), bg=self.colors["sidebar"]).pack()
        tk.Label(logo_frame, text="NEXUS GOD", font=("Segoe UI", 16, "bold"), bg=self.colors["sidebar"], fg=self.colors["accent"]).pack()
        
        self.prog_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar"], pady=10)
        self.prog_frame.pack(fill="x", padx=20)
        tk.Label(self.prog_frame, text="CREATION PROGRESS", font=("Segoe UI", 7, "bold"), bg=self.colors["sidebar"], fg=self.colors["muted"]).pack(anchor="w")
        self.progress = ttk.Progressbar(self.prog_frame, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(fill="x", pady=5)
        self.prog_label = tk.Label(self.prog_frame, text="0%", font=("Segoe UI", 8), bg=self.colors["sidebar"], fg=self.colors["accent"])
        self.prog_label.pack(anchor="e")

        self.nav_btns = {}
        nav_items = [
            ("wizard", "✨ วิถีแห่งสวรรค์ (Guided)"), ("chat", "💬 สนทนาทวยเทพ"),
            ("world", "🌍 กำเนิดโลก"), ("chars", "👤 โรงหล่อตัวละคร"),
            ("items", "⚔️ คลังไอเทม"), ("plot", "📜 โครงเรื่องสวรรค์"),
            ("editor", "📝 แก้ไขเนื้อเรื่อง"), ("memory", "🧠 ธนาคารความจำ"),
            ("review", "🔍 ตรวจสอบคัมภีร์"), ("export", "🚀 AI และส่งออก"),
            ("settings", "⚙️ ตั้งค่า")
        ]
        for key, label in nav_items:
            btn = tk.Button(self.sidebar, text=f"  {label}", font=("Segoe UI", 10), bg=self.colors["sidebar"], fg=self.colors["muted"], activebackground=self.colors["accent"], activeforeground="black", bd=0, anchor="w", padx=20, pady=10, cursor="hand2", command=lambda k=key: self.switch_tab(k))
            btn.pack(fill="x", padx=10, pady=1)
            self.nav_btns[key] = btn

        qa_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar"], pady=10)
        qa_frame.pack(fill="x", padx=10)
        tk.Button(qa_frame, text="🎲 เหตุการณ์สุ่ม", font=("Segoe UI", 8, "bold"), bg=self.colors["accent"], fg="black", bd=0, pady=8, command=self.random_event).pack(fill="x", pady=5)
        tk.Button(qa_frame, text="📂 สลับโปรเจกต์", font=("Segoe UI", 8, "bold"), bg=self.colors["muted"], fg="white", bd=0, pady=8, command=self.manage_projects).pack(fill="x", pady=5)

        # Main Container
        self.container = tk.Frame(self.root, bg=self.colors["bg"], padx=40, pady=30)
        self.container.pack(side="left", fill="both", expand=True)
        
        self.status_bar = tk.Frame(self.root, bg=self.colors["sidebar"], height=30)
        self.status_bar.pack(side="bottom", fill="x")
        self.status_label = tk.Label(self.status_bar, text="พร้อมใช้งาน", font=("Segoe UI", 8), bg=self.colors["sidebar"], fg=self.colors["muted"], padx=20)
        self.status_label.pack(side="left")

    def switch_tab(self, tab_key):
        for k, btn in self.nav_btns.items():
            btn.config(fg=self.colors["accent"] if k == tab_key else self.colors["muted"], bg=self.colors["card"] if k == tab_key else self.colors["sidebar"])
        
        for w in self.container.winfo_children(): w.destroy()
        self.current_tab = tab_key
        
        # Instantiate and build tab
        if tab_key == "world": WorldTab(self.container, self.dm, self.colors, self.build_card, self.create_input).build()
        elif tab_key == "plot": PlotTab(self.container, self.dm, self.colors, self.build_card, self.create_input).build()
        elif tab_key == "memory": MemoryTab(self.container, self.dm, self.colors, self.build_card, self.create_input).build()
        elif tab_key == "items": ItemsTab(self.container, self.dm, self.colors, self.build_card, self.create_input).build()
        elif tab_key == "settings": SettingsTab(self.container, self.dm, self.colors, self.build_card, self.create_input).build()
        elif tab_key == "export": ExportTab(self.container, self.dm, self.colors, self.build_card).build()
        elif tab_key == "review": 
            self.review_tab = ReviewTab(self.container, self.dm, self.colors, self.build_card, self.ai_service, self.get_editor_content, self.get_chapter_name, self.set_status)
            self.review_tab.build()
        elif tab_key == "chat": ChatTab(self.container, self.dm, self.colors, self.build_card, self.ai_service, self.apply_chat_update, self.set_status).build()
        elif tab_key == "chars": CharactersTab(self.container, self.dm, self.colors, self.build_card, self.create_input).build()
        elif tab_key == "editor": 
            self.editor_tab = EditorTab(self.container, self.dm, self.colors, self.build_card, self.ai_service, self.set_status, on_chapter_change_cb=self.update_last_chapter)
            self.editor_tab.build()
        elif tab_key == "wizard": WizardTab(self.container, self.dm, self.colors, self.build_card, self.ai_service, self.apply_chat_update, self.set_status, self.update_progress).build()
        
        self.update_progress()

    def set_status(self, text):
        self.status_label.config(text=text)

    def update_last_chapter(self, name):
        self.last_selected_chapter = name

    def get_editor_content(self):
        if self.current_tab == "editor":
            try:
                if hasattr(self, 'editor_tab') and hasattr(self.editor_tab, 'editor_text') and self.editor_tab.editor_text.winfo_exists():
                    return self.editor_tab.editor_text.get("1.0", tk.END).strip()
            except tk.TclError:
                pass
        
        # Fallback to data manager if editor widget is gone or we are in another tab
        chapter_name = self.get_chapter_name()
        return self.dm.data.get("chapters", {}).get(chapter_name, "")

    def get_chapter_name(self):
        if self.current_tab == "editor":
            try:
                if hasattr(self, 'editor_tab') and hasattr(self.editor_tab, 'chapter_selector') and self.editor_tab.chapter_selector.winfo_exists():
                    return self.editor_tab.chapter_selector.get()
            except tk.TclError:
                pass
        return getattr(self, 'last_selected_chapter', "ตอนที่ 1")

    def apply_chat_update(self, update):
        if "world" in update: self.dm.data["world"].update(update["world"])
        if "characters" in update:
            if isinstance(update["characters"], list):
                for char in update["characters"]: self.dm.data["characters"][char.get("name", "Unknown")] = char
            else: self.dm.data["characters"].update(update["characters"])
        if "plot" in update: self.dm.data["plot"].update(update["plot"])
        self.dm.save_all()

    def random_event(self):
        def task():
            try:
                self.root.after(0, lambda: self.set_status("AI กำลังสุ่มเหตุการณ์..."))
                prompt = "ช่วยสุ่มเหตุการณ์ที่น่าสนใจหรือจุดหักมุม (Plot Twist) ที่อาจเกิดขึ้นในเรื่องนี้"
                context = json.dumps({"world": self.dm.data["world"], "characters": self.dm.data["characters"]}, ensure_ascii=False)
                res = self.ai_service.call_ai_simple(f"Context: {context}\n\nRequest: {prompt}", "คุณคือเทพเจ้าแห่งการเล่าเรื่อง")
                self.root.after(0, lambda: messagebox.showinfo("🎲 เหตุการณ์สุ่ม", res))
                self.root.after(0, lambda: self.set_status("สุ่มเหตุการณ์เสร็จสิ้น"))
            except Exception as e:
                self.root.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))
        threading.Thread(target=task, daemon=True).start()

    def manage_projects(self):
        from nexus_god.ui.project_selector import show_project_selector
        name = show_project_selector()
        if name:
            self.switch_project(name)

    def switch_project(self, name):
        self.dm.switch_project(name)
        self.ai_service.config = self.dm.config
        self.switch_tab(self.current_tab)

def run_app():
    root = tk.Tk()
    app = NexusGodWriter(root)
    root.mainloop()
