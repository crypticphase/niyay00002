import tkinter as tk
from tkinter import ttk, messagebox
from nexus_god.core.logging_utils import log_debug, log_info

class SettingsTab:
    def __init__(self, parent, dm, colors, build_card, create_input):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.create_input = create_input

    def build(self):
        log_debug("Building settings content")
        card = self.build_card(self.parent, "ตั้งค่า (Settings)")
        
        self.set_theme = self.create_input(card, "ธีม (dark/light)")
        self.set_theme.insert(0, self.dm.config.get("theme", "dark"))
        
        tk.Label(card, text="AI Provider:", font=("Segoe UI", 9, "bold"), bg=card["bg"], fg=self.colors["accent"]).pack(anchor="w", pady=(10, 5))
        self.set_provider = ttk.Combobox(card, values=["gemini", "groq"])
        self.set_provider.pack(fill="x", pady=(0, 10))
        self.set_provider.set(self.dm.config.get("ai_provider", "gemini"))

        self.set_api = self.create_input(card, "Gemini API Key")
        self.set_api.insert(0, self.dm.config.get("api_key", ""))
        
        self.set_groq_api = self.create_input(card, "Groq API Key")
        self.set_groq_api.insert(0, self.dm.config.get("groq_api_key", ""))
        
        tk.Button(card, text="บันทึกการตั้งค่า ⚙️", command=self.save_settings, bg=self.colors["success"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=12).pack(fill="x", pady=20)

    def save_settings(self):
        log_info("Saving settings from form")
        theme = self.set_theme.get().strip()
        api_key = self.set_api.get().strip()
        groq_api_key = self.set_groq_api.get().strip()
        provider = self.set_provider.get().strip()
        
        self.dm.config["theme"] = theme
        self.dm.config["api_key"] = api_key
        self.dm.config["groq_api_key"] = groq_api_key
        self.dm.config["ai_provider"] = provider
        self.dm.save_all()
        
        messagebox.showinfo("สำเร็จ", "บันทึกการตั้งค่าแล้ว (กรุณารีสตาร์ทโปรแกรมเพื่อเปลี่ยนธีม)")
