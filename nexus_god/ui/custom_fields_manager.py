"""Custom Fields Manager - จัดการฟิลด์สำหรับตัวละคร"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from nexus_god.core.data_manager import NexusDataManager
from nexus_god.core.logging_utils import log_error, log_debug, log_info


class CustomFieldsManager:
    """หน้าจอจัดการ Custom Fields"""
    
    def __init__(self, parent, data_manager: NexusDataManager, on_update=None):
        log_debug("Initializing CustomFieldsManager")
        self.parent = parent
        self.dm = data_manager
        self.on_update = on_update
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ จัดการ Custom Fields สำหรับตัวละคร")
        self.dialog.geometry("700x600")
        self.dialog.minsize(600, 500)
        self.dialog.configure(bg="#0f172a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"700x600+{x}+{y}")
        
        self.fields_changed = False
        self.build_ui()
    
    def build_ui(self):
        # Header
        header = tk.Frame(self.dialog, bg="#0f172a", pady=20)
        header.pack(fill="x")
        
        tk.Label(header, text="⚙️ จัดการ Custom Fields", font=("Segoe UI", 18, "bold"), 
                bg="#0f172a", fg="#38bdf8").pack()
        tk.Label(header, text="เพิ่ม/ลบ/แก้ไขฟิลด์สำหรับตัวละคร", font=("Segoe UI", 10), 
                bg="#0f172a", fg="#94a3b8").pack(pady=5)
        
        # Main content
        content = tk.Frame(self.dialog, bg="#0f172a", padx=30, pady=20)
        content.pack(fill="both", expand=True)
        
        # Current fields section
        fields_frame = tk.Frame(content, bg="#1e293b", padx=20, pady=15)
        fields_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        tk.Label(fields_frame, text="ฟิลด์ที่ใช้งานอยู่", font=("Segoe UI", 12, "bold"), 
                bg="#1e293b", fg="#38bdf8").pack(anchor="w", pady=(0, 10))
        
        # Fields list with scrollbar
        list_container = tk.Frame(fields_frame, bg="#1e293b")
        list_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.fields_listbox = tk.Listbox(
            list_container,
            bg="#0f172a",
            fg="#f8fafc",
            selectbackground="#38bdf8",
            selectforeground="black",
            font=("Segoe UI", 10),
            bd=0,
            yscrollcommand=scrollbar.set,
            height=12
        )
        self.fields_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.fields_listbox.yview)
        
        self.refresh_fields_list()
        
        # Buttons for fields management
        fields_btn_frame = tk.Frame(fields_frame, bg="#1e293b")
        fields_btn_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(fields_btn_frame, text="➕ เพิ่มฟิลด์", command=self.add_field,
                bg="#10b981", fg="white", bd=0, padx=15, pady=8,
                font=("Segoe UI", 9, "bold")).pack(side="left", padx=2)
        
        tk.Button(fields_btn_frame, text="✏️ แก้ไข", command=self.edit_field,
                bg="#38bdf8", fg="black", bd=0, padx=15, pady=8,
                font=("Segoe UI", 9)).pack(side="left", padx=2)
        
        tk.Button(fields_btn_frame, text="🗑️ ลบ", command=self.remove_field,
                bg="#ef4444", fg="white", bd=0, padx=15, pady=8,
                font=("Segoe UI", 9)).pack(side="left", padx=2)
        
        tk.Button(fields_btn_frame, text="📥 เพิ่มจาก Template", command=self.add_from_template,
                bg="#f59e0b", fg="black", bd=0, padx=15, pady=8,
                font=("Segoe UI", 9)).pack(side="left", padx=2)
        
        # Bottom buttons
        btn_frame = tk.Frame(content, bg="#0f172a")
        btn_frame.pack(fill="x")
        
        tk.Button(btn_frame, text="✅ บันทึก", command=self.save_fields,
                bg="#10b981", fg="white", bd=0, padx=30, pady=12,
                font=("Segoe UI", 11, "bold"), cursor="hand2").pack(side="right", padx=5)
        
        tk.Button(btn_frame, text="ยกเลิก", command=self.dialog.destroy,
                bg="#64748b", fg="white", bd=0, padx=30, pady=12,
                font=("Segoe UI", 11), cursor="hand2").pack(side="right", padx=5)
    
    def get_current_fields(self):
        """ดึงฟิลด์ที่ใช้งานอยู่ (จาก project config หรือ default)"""
        project_fields = self.dm.data.get("character_fields_config", [])
        if project_fields:
            return project_fields.copy()
        
        # ใช้ default fields
        default_fields = self.dm.config.get("default_character_fields", [])
        return default_fields.copy()
    
    def refresh_fields_list(self):
        """รีเฟรชรายการฟิลด์"""
        log_debug("Refreshing custom fields listbox")
        self.fields_listbox.delete(0, tk.END)
        fields = self.get_current_fields()
        log_info(f"Found {len(fields)} fields in current configuration")
        
        for field in fields:
            required = " *" if field.get("required", False) else ""
            field_type = field.get("type", "text")
            label = f"{field.get('label', field.get('key', ''))} ({field_type}){required}"
            self.fields_listbox.insert(tk.END, f"  {label}")
    
    def add_field(self):
        """เพิ่มฟิลด์ใหม่"""
        log_debug("Adding new custom field")
        self.show_field_dialog()
    
    def edit_field(self):
        """แก้ไขฟิลด์ที่เลือก"""
        selection = self.fields_listbox.curselection()
        if not selection:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกฟิลด์ที่ต้องการแก้ไข")
            return
        
        idx = selection[0]
        fields = self.get_current_fields()
        if idx >= len(fields):
            return
        
        self.show_field_dialog(fields[idx], idx)
    
    def remove_field(self):
        """ลบฟิลด์ที่เลือก"""
        selection = self.fields_listbox.curselection()
        if not selection:
            log_debug("No field selected to remove")
            messagebox.showwarning("คำเตือน", "กรุณาเลือกฟิลด์ที่ต้องการลบ")
            return
        
        idx = selection[0]
        fields = self.get_current_fields()
        if idx >= len(fields):
            return
        
        field = fields[idx]
        log_info(f"Removing field: {field.get('key')}")
        if field.get("required", False):
            messagebox.showwarning("คำเตือน", "ไม่สามารถลบฟิลด์ที่จำเป็นได้")
            return
        
        if not messagebox.askyesno("ยืนยัน", f"คุณต้องการลบฟิลด์ '{field.get('label', '')}' ใช่หรือไม่?"):
            return
        
        # Remove from current config
        if not self.dm.data.get("character_fields_config"):
            self.dm.data["character_fields_config"] = self.get_current_fields()
        
        self.dm.data["character_fields_config"].pop(idx)
        self.fields_changed = True
        self.refresh_fields_list()
    
    def add_from_template(self):
        """เพิ่มฟิลด์จาก template (custom fields ที่บันทึกไว้)"""
        custom_fields = self.dm.config.get("custom_character_fields", [])
        if not custom_fields:
            messagebox.showinfo("ข้อมูล", "ยังไม่มี Custom Fields ที่บันทึกไว้")
            return
        
        dialog = tk.Toplevel(self.dialog)
        dialog.title("เลือกฟิลด์จาก Template")
        dialog.geometry("500x400")
        dialog.configure(bg="#1e293b")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        tk.Label(dialog, text="เลือกฟิลด์ที่ต้องการเพิ่ม", font=("Segoe UI", 12, "bold"),
                bg="#1e293b", fg="#38bdf8").pack(pady=20)
        
        list_frame = tk.Frame(dialog, bg="#1e293b")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        template_listbox = tk.Listbox(list_frame, bg="#0f172a", fg="#f8fafc",
                                     font=("Segoe UI", 10), bd=0, yscrollcommand=scrollbar.set)
        template_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=template_listbox.yview)
        
        for field in custom_fields:
            label = f"{field.get('label', '')} ({field.get('type', 'text')})"
            template_listbox.insert(tk.END, f"  {label}")
        
        def on_add():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("คำเตือน", "กรุณาเลือกฟิลด์")
                return
            
            selected_field = custom_fields[selection[0]].copy()
            
            # Add to current config
            if not self.dm.data.get("character_fields_config"):
                self.dm.data["character_fields_config"] = self.get_current_fields()
            
            self.dm.data["character_fields_config"].append(selected_field)
            self.fields_changed = True
            self.refresh_fields_list()
            dialog.destroy()
            messagebox.showinfo("สำเร็จ", f"เพิ่มฟิลด์ '{selected_field.get('label', '')}' เรียบร้อยแล้ว")
        
        btn_frame = tk.Frame(dialog, bg="#1e293b")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="เพิ่ม", command=on_add, bg="#10b981", fg="white",
                bd=0, padx=20, pady=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="ยกเลิก", command=dialog.destroy, bg="#64748b", fg="white",
                bd=0, padx=20, pady=8).pack(side="left", padx=5)
    
    def show_field_dialog(self, field_data=None, edit_index=None):
        """แสดง dialog สำหรับเพิ่ม/แก้ไขฟิลด์"""
        is_edit = field_data is not None
        
        dialog = tk.Toplevel(self.dialog)
        dialog.title("แก้ไขฟิลด์" if is_edit else "เพิ่มฟิลด์ใหม่")
        dialog.geometry("500x350")
        dialog.configure(bg="#1e293b")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        tk.Label(dialog, text="เพิ่มฟิลด์ใหม่" if not is_edit else "แก้ไขฟิลด์",
                font=("Segoe UI", 14, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=20)
        
        # Field key (read-only if editing)
        key_frame = tk.Frame(dialog, bg="#1e293b")
        key_frame.pack(fill="x", padx=30, pady=10)
        tk.Label(key_frame, text="Key (ภาษาอังกฤษ):", font=("Segoe UI", 10),
                bg="#1e293b", fg="#f8fafc", width=20, anchor="w").pack(side="left")
        key_entry = tk.Entry(key_frame, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 10), bd=0)
        key_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(10, 0))
        if is_edit:
            key_entry.insert(0, field_data.get("key", ""))
            key_entry.config(state="readonly")
        
        # Field label
        label_frame = tk.Frame(dialog, bg="#1e293b")
        label_frame.pack(fill="x", padx=30, pady=10)
        tk.Label(label_frame, text="Label (ชื่อแสดง):", font=("Segoe UI", 10),
                bg="#1e293b", fg="#f8fafc", width=20, anchor="w").pack(side="left")
        label_entry = tk.Entry(label_frame, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 10), bd=0)
        label_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(10, 0))
        if is_edit:
            label_entry.insert(0, field_data.get("label", ""))
        
        # Field type
        type_frame = tk.Frame(dialog, bg="#1e293b")
        type_frame.pack(fill="x", padx=30, pady=10)
        tk.Label(type_frame, text="ประเภท:", font=("Segoe UI", 10),
                bg="#1e293b", fg="#f8fafc", width=20, anchor="w").pack(side="left")
        type_var = tk.StringVar(value=field_data.get("type", "text") if is_edit else "text")
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, state="readonly",
                                 values=["text", "textarea"], font=("Segoe UI", 10))
        type_combo.pack(side="left", fill="x", expand=True, ipady=6, padx=(10, 0))
        
        # Required checkbox
        required_var = tk.BooleanVar(value=field_data.get("required", False) if is_edit else False)
        required_frame = tk.Frame(dialog, bg="#1e293b")
        required_frame.pack(fill="x", padx=30, pady=10)
        tk.Checkbutton(required_frame, text="ฟิลด์จำเป็น (Required)", variable=required_var,
                      bg="#1e293b", fg="#f8fafc", selectcolor="#0f172a",
                      font=("Segoe UI", 10)).pack(anchor="w")
        
        def on_save():
            key = key_entry.get().strip()
            label = label_entry.get().strip()
            field_type = type_var.get()
            
            if not key:
                messagebox.showwarning("คำเตือน", "กรุณาใส่ Key")
                return
            if not label:
                messagebox.showwarning("คำเตือน", "กรุณาใส่ Label")
                return
            
            # Check if key already exists (if not editing)
            if not is_edit:
                fields = self.get_current_fields()
                if any(f.get("key") == key for f in fields):
                    messagebox.showwarning("คำเตือน", f"Key '{key}' มีอยู่แล้ว")
                    return
            
            field = {
                "key": key,
                "label": label,
                "type": field_type,
                "required": required_var.get()
            }
            
            # Update or add field
            if not self.dm.data.get("character_fields_config"):
                self.dm.data["character_fields_config"] = self.get_current_fields()
            
            if is_edit:
                self.dm.data["character_fields_config"][edit_index] = field
            else:
                self.dm.data["character_fields_config"].append(field)
            
            # Save to custom fields if new
            if not is_edit:
                custom_fields = self.dm.config.get("custom_character_fields", [])
                if not any(f.get("key") == key for f in custom_fields):
                    custom_fields.append(field.copy())
                    self.dm.config["custom_character_fields"] = custom_fields
            
            self.fields_changed = True
            self.refresh_fields_list()
            if self.on_update:
                self.on_update()
            dialog.destroy()
            messagebox.showinfo("สำเร็จ", f"{'แก้ไข' if is_edit else 'เพิ่ม'}ฟิลด์เรียบร้อยแล้ว")
        
        btn_frame = tk.Frame(dialog, bg="#1e293b")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="บันทึก", command=on_save, bg="#10b981", fg="white",
                bd=0, padx=20, pady=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="ยกเลิก", command=dialog.destroy, bg="#64748b", fg="white",
                bd=0, padx=20, pady=8).pack(side="left", padx=5)
    
    def save_fields(self):
        """บันทึกการเปลี่ยนแปลง"""
        log_info("Saving custom fields changes")
        try:
            self.dm.save_all()
            messagebox.showinfo("สำเร็จ", "บันทึกการตั้งค่าฟิลด์เรียบร้อยแล้ว")
            self.dialog.destroy()
        except Exception as e:
            log_error(f"Error saving fields: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถบันทึกได้: {e}")
