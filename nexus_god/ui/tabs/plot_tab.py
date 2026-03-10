import tkinter as tk
from nexus_god.core.logging_utils import log_info, log_debug
from tkinter import messagebox

class PlotTab:
    def __init__(self, parent, dm, colors, build_card, create_input):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.create_input = create_input

    def build(self):
        log_debug("Building plot content")
        card = self.build_card(self.parent, "โครงเรื่องสวรรค์ (Divine Plot)")
        
        self.plot_act1 = self.create_input(card, "องก์ที่ 1: การเริ่มต้น (Act 1)", 6)
        self.plot_act2 = self.create_input(card, "องก์ที่ 2: การเผชิญหน้า (Act 2)", 6)
        self.plot_act3 = self.create_input(card, "องก์ที่ 3: บทสรุป (Act 3)", 6)
        
        # Load data
        self.plot_act1.insert("1.0", self.dm.data["plot"].get("act1", ""))
        self.plot_act2.insert("1.0", self.dm.data["plot"].get("act2", ""))
        self.plot_act3.insert("1.0", self.dm.data["plot"].get("act3", ""))
        
        tk.Button(card, text="บันทึกโครงเรื่อง 📜", command=self.save_plot_data, bg=self.colors["success"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=12).pack(fill="x", pady=20)

    def save_plot_data(self):
        log_info("Saving plot data from form")
        self.dm.data["plot"]["act1"] = self.plot_act1.get("1.0", tk.END).strip()
        self.dm.data["plot"]["act2"] = self.plot_act2.get("1.0", tk.END).strip()
        self.dm.data["plot"]["act3"] = self.plot_act3.get("1.0", tk.END).strip()
        self.dm.save_all()
        messagebox.showinfo("สำเร็จ", "บันทึกโครงเรื่องเรียบร้อยแล้ว")
