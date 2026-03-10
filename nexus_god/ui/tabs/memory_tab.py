import tkinter as tk
from nexus_god.core.logging_utils import log_debug, log_info
from tkinter import messagebox, filedialog

class MemoryTab:
    def __init__(self, parent, dm, colors, build_card, create_input):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.create_input = create_input

    def build(self):
        log_debug("Building memory content")
        card = self.build_card(self.parent, "ธนาคารความจำ (Memory Bank)")
        
        tk.Label(card, text="เก็บรวบรวมข้อมูล Lore, สถานที่, และความลับของโลก เพื่อให้ AI จดจำได้แม่นยำ", font=("Segoe UI", 10), bg=card["bg"], fg=self.colors["muted"]).pack(pady=(0, 15))
        
        # Split List and Form
        split = tk.Frame(card, bg=card["bg"])
        split.pack(fill="both", expand=True)
        
        # Left: Memory List
        left = tk.Frame(split, bg=card["bg"], width=250)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)
        
        self.memory_listbox = tk.Listbox(left, bg=self.colors["input"], fg="white", bd=0, font=("Segoe UI", 10))
        self.memory_listbox.pack(fill="both", expand=True)
        self.memory_listbox.bind("<<ListboxSelect>>", self.on_memory_select)
        
        btn_f = tk.Frame(left, bg=left["bg"], pady=10)
        btn_f.pack(fill="x")
        tk.Button(btn_f, text="+ เพิ่มความจำ", command=self.add_memory, bg=self.colors["accent"], fg="black", bd=0, pady=5).pack(fill="x", pady=2)
        tk.Button(btn_f, text="- ลบความจำ", command=self.delete_memory, bg=self.colors["danger"], fg="white", bd=0, pady=5).pack(fill="x", pady=2)

        # Right: Memory Form
        self.memory_form = tk.Frame(split, bg=card["bg"])
        self.memory_form.pack(side="left", fill="both", expand=True)
        
        self.refresh_memory_list()

    def refresh_memory_list(self):
        log_debug("Refreshing memory listbox")
        self.memory_listbox.delete(0, tk.END)
        memory = self.dm.data.get("memory", {})
        for key in memory:
            self.memory_listbox.insert(tk.END, key)

    def on_memory_select(self, event):
        sel = self.memory_listbox.curselection()
        if not sel: return
        key = self.memory_listbox.get(sel[0])
        self.build_memory_form(key)

    def build_memory_form(self, key):
        for w in self.memory_form.winfo_children(): w.destroy()
        
        val = self.dm.data.get("memory", {}).get(key, "")
        
        tk.Label(self.memory_form, text=f"ความจำ: {key}", font=("Segoe UI", 12, "bold"), bg=self.memory_form["bg"], fg=self.colors["accent"]).pack(anchor="w", pady=(0, 15))
        
        self.mem_key_input = self.create_input(self.memory_form, "หัวข้อความจำ")
        self.mem_key_input.insert(0, key)
        
        self.mem_val_input = self.create_input(self.memory_form, "รายละเอียด", 10)
        self.mem_val_input.insert("1.0", val)
        
        tk.Button(self.memory_form, text="บันทึกความจำ 💾", command=lambda: self.save_memory(key), bg=self.colors["success"], fg="white", bd=0, pady=10).pack(fill="x", pady=20)

    def add_memory(self):
        key = filedialog.askstring("เพิ่มความจำ", "กรุณาใส่หัวข้อความจำ (เช่น ชื่อเมือง, ตำนาน):")
        if key:
            if "memory" not in self.dm.data: self.dm.data["memory"] = {}
            self.dm.data["memory"][key] = ""
            self.refresh_memory_list()
            self.dm.save_all()

    def delete_memory(self):
        sel = self.memory_listbox.curselection()
        if not sel: return
        key = self.memory_listbox.get(sel[0])
        if messagebox.askyesno("ยืนยัน", f"ลบความจำ '{key}'?"):
            del self.dm.data["memory"][key]
            self.refresh_memory_list()
            for w in self.memory_form.winfo_children(): w.destroy()
            self.dm.save_all()

    def save_memory(self, old_key):
        new_key = self.mem_key_input.get().strip()
        new_val = self.mem_val_input.get("1.0", tk.END).strip()
        
        if "memory" not in self.dm.data: self.dm.data["memory"] = {}
        
        if new_key != old_key:
            del self.dm.data["memory"][old_key]
        
        self.dm.data["memory"][new_key] = new_val
        self.dm.save_all()
        self.refresh_memory_list()
        messagebox.showinfo("สำเร็จ", "บันทึกความจำแล้ว")
