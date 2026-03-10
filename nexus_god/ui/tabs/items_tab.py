import tkinter as tk
from nexus_god.core.logging_utils import log_debug, log_info
from tkinter import messagebox, filedialog

class ItemsTab:
    def __init__(self, parent, dm, colors, build_card, create_input):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.create_input = create_input

    def build(self):
        log_debug("Building item content")
        card = self.build_card(self.parent, "คลังไอเทมและสิ่งประดิษฐ์ (Divine Armory)")
        
        tk.Label(card, text="จัดการอาวุธ ชุดเกราะ ยา และไอเทมสำคัญในเรื่อง", font=("Segoe UI", 10), bg=card["bg"], fg=self.colors["muted"]).pack(pady=(0, 15))
        
        split = tk.Frame(card, bg=card["bg"])
        split.pack(fill="both", expand=True)
        
        left = tk.Frame(split, bg=card["bg"], width=250)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)
        
        self.item_listbox = tk.Listbox(left, bg=self.colors["input"], fg="white", bd=0, font=("Segoe UI", 10))
        self.item_listbox.pack(fill="both", expand=True)
        self.item_listbox.bind("<<ListboxSelect>>", self.on_item_select)
        
        btn_f = tk.Frame(left, bg=left["bg"], pady=10)
        btn_f.pack(fill="x")
        tk.Button(btn_f, text="+ เพิ่มไอเทม", command=self.add_item, bg=self.colors["accent"], fg="black", bd=0, pady=5).pack(fill="x", pady=2)
        tk.Button(btn_f, text="- ลบไอเทม", command=self.delete_item, bg=self.colors["danger"], fg="white", bd=0, pady=5).pack(fill="x", pady=2)

        self.item_form = tk.Frame(split, bg=card["bg"])
        self.item_form.pack(side="left", fill="both", expand=True)
        
        self.refresh_item_list()

    def refresh_item_list(self):
        log_debug("Refreshing item listbox")
        self.item_listbox.delete(0, tk.END)
        items = self.dm.data.get("items", {})
        for name in items:
            self.item_listbox.insert(tk.END, name)

    def on_item_select(self, event):
        sel = self.item_listbox.curselection()
        if not sel: return
        name = self.item_listbox.get(sel[0])
        self.build_item_form(name)

    def build_item_form(self, name):
        for w in self.item_form.winfo_children(): w.destroy()
        
        data = self.dm.data.get("items", {}).get(name, {})
        
        tk.Label(self.item_form, text=f"ไอเทม: {name}", font=("Segoe UI", 12, "bold"), bg=self.item_form["bg"], fg=self.colors["accent"]).pack(anchor="w", pady=(0, 15))
        
        self.item_name_input = self.create_input(self.item_form, "ชื่อไอเทม")
        self.item_name_input.insert(0, name)
        
        self.item_desc_input = self.create_input(self.item_form, "รายละเอียด/ความสามารถ", 10)
        self.item_desc_input.insert("1.0", data.get("description", ""))
        
        tk.Button(self.item_form, text="บันทึกไอเทม 💾", command=lambda: self.save_item(name), bg=self.colors["success"], fg="white", bd=0, pady=10).pack(fill="x", pady=20)

    def add_item(self):
        name = filedialog.askstring("เพิ่มไอเทม", "กรุณาใส่ชื่อไอเทม:")
        if name:
            if "items" not in self.dm.data: self.dm.data["items"] = {}
            self.dm.data["items"][name] = {"description": ""}
            self.refresh_item_list()
            self.dm.save_all()

    def delete_item(self):
        sel = self.item_listbox.curselection()
        if not sel: return
        name = self.item_listbox.get(sel[0])
        if messagebox.askyesno("ยืนยัน", f"ลบไอเทม '{name}'?"):
            del self.dm.data["items"][name]
            self.refresh_item_list()
            for w in self.item_form.winfo_children(): w.destroy()
            self.dm.save_all()

    def save_item(self, old_name):
        new_name = self.item_name_input.get().strip()
        new_desc = self.item_desc_input.get("1.0", tk.END).strip()
        
        if "items" not in self.dm.data: self.dm.data["items"] = {}
        
        if new_name != old_name:
            del self.dm.data["items"][old_name]
        
        self.dm.data["items"][new_name] = {"description": new_desc}
        self.dm.save_all()
        self.refresh_item_list()
        messagebox.showinfo("สำเร็จ", "บันทึกไอเทมแล้ว")
