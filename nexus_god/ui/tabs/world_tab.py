import tkinter as tk
from nexus_god.core.logging_utils import log_info, log_debug
from tkinter import messagebox

class WorldTab:
    def __init__(self, parent, dm, colors, build_card, create_input):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.create_input = create_input

    def build(self):
        log_debug("Building world content")
        card = self.build_card(self.parent, "กำเนิดโลก (World Genesis)")
        
        self.world_name = self.create_input(card, "ชื่อโลก / ชื่อเรื่อง")
        self.world_genre = self.create_input(card, "แนวเรื่อง (Genre)")
        self.world_theme = self.create_input(card, "ธีมหลัก (Theme)")
        self.world_rules = self.create_input(card, "กฎของโลก / ระบบพลัง", 6)
        self.world_desc = self.create_input(card, "รายละเอียดเพิ่มเติม", 8)
        
        # Load data
        self.world_name.insert(0, self.dm.data["world"].get("name", ""))
        self.world_genre.insert(0, self.dm.data["world"].get("genre", ""))
        self.world_theme.insert(0, self.dm.data["world"].get("theme", ""))
        self.world_rules.insert("1.0", self.dm.data["world"].get("rules", ""))
        self.world_desc.insert("1.0", self.dm.data["world"].get("description", ""))
        
        tk.Button(card, text="บันทึกข้อมูลโลก 💾", command=self.save_world_data, bg=self.colors["success"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=12).pack(fill="x", pady=20)

    def save_world_data(self):
        log_info("Saving world data from form")
        self.dm.data["world"]["name"] = self.world_name.get()
        self.dm.data["world"]["genre"] = self.world_genre.get()
        self.dm.data["world"]["theme"] = self.world_theme.get()
        self.dm.data["world"]["rules"] = self.world_rules.get("1.0", tk.END).strip()
        self.dm.data["world"]["description"] = self.world_desc.get("1.0", tk.END).strip()
        self.dm.save_all()
        messagebox.showinfo("สำเร็จ", "บันทึกข้อมูลโลกเรียบร้อยแล้ว")
