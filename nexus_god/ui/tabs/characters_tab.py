import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from nexus_god.core.logging_utils import log_debug, log_info

class CharactersTab:
    def __init__(self, parent, dm, colors, build_card, create_input):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.create_input = create_input
        self.char_inputs = {}

    def build(self):
        log_debug("Building character content")
        card = self.build_card(self.parent, "โรงหล่อตัวละคร (Character Foundry)")
        
        # List and Form Split
        split = tk.Frame(card, bg=card["bg"])
        split.pack(fill="both", expand=True)
        
        # Left: Character List
        left = tk.Frame(split, bg=card["bg"], width=250)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)
        
        self.char_listbox = tk.Listbox(left, bg=self.colors["input"], fg="white", bd=0, font=("Segoe UI", 10))
        self.char_listbox.pack(fill="both", expand=True)
        self.char_listbox.bind("<<ListboxSelect>>", self.on_char_select)
        
        btn_f = tk.Frame(left, bg=left["bg"], pady=10)
        btn_f.pack(fill="x")
        tk.Button(btn_f, text="+ เพิ่มตัวละคร", command=self.add_character, bg=self.colors["accent"], fg="black", bd=0, pady=5).pack(fill="x", pady=2)
        tk.Button(btn_f, text="- ลบตัวละคร", command=self.delete_character, bg=self.colors["danger"], fg="white", bd=0, pady=5).pack(fill="x", pady=2)
        tk.Button(btn_f, text="⚙️ จัดการฟิลด์", command=self.manage_custom_fields, bg=self.colors["muted"], fg="white", bd=0, pady=5).pack(fill="x", pady=2)

        # Right: Character Form
        self.char_form_container = tk.Frame(split, bg=card["bg"])
        self.char_form_container.pack(side="left", fill="both", expand=True)
        
        self.refresh_char_list()

    def refresh_char_list(self):
        log_debug("Refreshing character listbox")
        self.char_listbox.delete(0, tk.END)
        for name in self.dm.data["characters"]:
            self.char_listbox.insert(tk.END, name)

    def on_char_select(self, event):
        sel = self.char_listbox.curselection()
        if not sel: return
        name = self.char_listbox.get(sel[0])
        self.build_char_form(name)

    def build_char_form(self, char_name):
        for w in self.char_form_container.winfo_children(): w.destroy()
        self.char_inputs = {}
        
        char_data = self.dm.data["characters"].get(char_name, {})
        
        header = tk.Frame(self.char_form_container, bg=self.char_form_container["bg"])
        header.pack(fill="x", pady=(0, 15))
        tk.Label(header, text=f"ตัวละคร: {char_name}", font=("Segoe UI", 14, "bold"), bg=header["bg"], fg=self.colors["accent"]).pack(side="left")
        
        # Scrollable area for fields
        canvas = tk.Canvas(self.char_form_container, bg=self.char_form_container["bg"], bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.char_form_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.char_form_container["bg"])
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=500)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Fields from config
        fields = self.dm.config.get("default_character_fields", []) + self.dm.config.get("custom_character_fields", [])
        
        for f in fields:
            label = f["label"]
            key = f["key"]
            val = char_data.get(label, char_data.get(key, ""))
            
            if f["type"] == "text":
                inp = self.create_input(scroll_frame, label)
                inp.insert(0, val)
            else:
                inp = self.create_input(scroll_frame, label, 5)
                inp.insert("1.0", val)
            self.char_inputs[label] = inp

        tk.Button(scroll_frame, text="บันทึกข้อมูลตัวละคร 💾", command=lambda: self.save_char_data(char_name), bg=self.colors["success"], fg="white", bd=0, pady=10).pack(fill="x", pady=20)

    def add_character(self):
        name = filedialog.askstring("เพิ่มตัวละคร", "กรุณาใส่ชื่อตัวละคร:")
        if name:
            self.dm.data["characters"][name] = {"ชื่อ": name}
            self.refresh_char_list()
            self.dm.save_all()

    def delete_character(self):
        sel = self.char_listbox.curselection()
        if not sel: return
        name = self.char_listbox.get(sel[0])
        if messagebox.askyesno("ยืนยัน", f"ลบตัวละคร '{name}'?"):
            del self.dm.data["characters"][name]
            self.refresh_char_list()
            for w in self.char_form_container.winfo_children(): w.destroy()
            self.dm.save_all()

    def save_char_data(self, old_name):
        new_data = {}
        for field, inp in self.char_inputs.items():
            if hasattr(inp, "get") and not isinstance(inp, scrolledtext.ScrolledText):
                new_data[field] = inp.get()
            else:
                new_data[field] = inp.get("1.0", tk.END).strip()
        
        new_name = new_data.get("ชื่อ", old_name)
        if new_name != old_name:
            log_info(f"Renaming character from {old_name} to {new_name}")
            del self.dm.data["characters"][old_name]
        
        self.dm.data["characters"][new_name] = new_data
        self.dm.save_all()
        self.refresh_char_list()
        messagebox.showinfo("สำเร็จ", f"บันทึกข้อมูล '{new_name}' เรียบร้อยแล้ว")

    def manage_custom_fields(self):
        log_debug("Opening custom fields manager")
        from nexus_god.ui.custom_fields_manager import CustomFieldsManager
        CustomFieldsManager(self.parent, self.dm, on_update=lambda: self.build())
