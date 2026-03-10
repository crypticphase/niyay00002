"""Project Selection Screen - เลือก/สร้าง/ลบโปรเจกต์ก่อนเข้าโปรแกรม"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from nexus_god.core.data_manager import NexusDataManager
from nexus_god.core.logging_utils import log_error, log_debug, log_info


class ProjectSelector:
    """หน้าจอเลือกโปรเจกต์"""
    
    def __init__(self, root):
        log_debug("Initializing ProjectSelector")
        self.root = root
        self.root.title("🌌 NEXUS GOD WRITER - เลือกโปรเจกต์")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        self.root.configure(bg="#0f172a")
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.selected_project = None
        self.dm = NexusDataManager()
        
        self.build_ui()
    
    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0f172a", pady=40)
        header.pack(fill="x")
        
        tk.Label(header, text="🌌", font=("Segoe UI", 48), bg="#0f172a", fg="#38bdf8").pack()
        tk.Label(header, text="NEXUS GOD WRITER", font=("Segoe UI", 24, "bold"), 
                bg="#0f172a", fg="#38bdf8").pack(pady=5)
        tk.Label(header, text="เลือกโปรเจกต์ของคุณ", font=("Segoe UI", 12), 
                bg="#0f172a", fg="#94a3b8").pack()
        
        # Main content
        content = tk.Frame(self.root, bg="#0f172a", padx=40, pady=20)
        content.pack(fill="both", expand=True)
        
        # Project list frame
        list_frame = tk.Frame(content, bg="#1e293b", padx=20, pady=20)
        list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        tk.Label(list_frame, text="โปรเจกต์ที่มีอยู่", font=("Segoe UI", 14, "bold"), 
                bg="#1e293b", fg="#38bdf8").pack(anchor="w", pady=(0, 15))
        
        # Listbox with scrollbar
        list_container = tk.Frame(list_frame, bg="#1e293b")
        list_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.project_listbox = tk.Listbox(
            list_container,
            bg="#0f172a",
            fg="#f8fafc",
            selectbackground="#38bdf8",
            selectforeground="black",
            font=("Segoe UI", 11),
            bd=0,
            yscrollcommand=scrollbar.set,
            height=12
        )
        self.project_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.project_listbox.yview)
        
        # Load projects
        self.refresh_project_list()
        
        # Buttons
        btn_frame = tk.Frame(content, bg="#0f172a")
        btn_frame.pack(fill="x")
        
        tk.Button(
            btn_frame,
            text="➕ สร้างโปรเจกต์ใหม่",
            font=("Segoe UI", 11, "bold"),
            bg="#10b981",
            fg="white",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.create_new_project
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="📂 เปิดโปรเจกต์",
            font=("Segoe UI", 11, "bold"),
            bg="#38bdf8",
            fg="black",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.open_project
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ ลบโปรเจกต์",
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444",
            fg="white",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.delete_project
        ).pack(side="left", padx=5)
        
        # Bind double-click to open
        self.project_listbox.bind("<Double-Button-1>", lambda e: self.open_project())
    
    def refresh_project_list(self):
        """รีเฟรชรายการโปรเจกต์"""
        log_debug("Refreshing project listbox from data directory")
        self.project_listbox.delete(0, tk.END)
        projects = self.dm.list_projects()
        if projects:
            log_info(f"Found {len(projects)} projects")
            for project in projects:
                self.project_listbox.insert(tk.END, f"  {project}")
        else:
            log_info("No projects found")
            self.project_listbox.insert(tk.END, "  (ยังไม่มีโปรเจกต์)")
    
    def create_new_project(self):
        """สร้างโปรเจกต์ใหม่"""
        log_debug("Opening create new project dialog")
        dialog = tk.Toplevel(self.root)
        dialog.title("สร้างโปรเจกต์ใหม่")
        dialog.geometry("500x200")
        dialog.configure(bg="#1e293b")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"500x200+{x}+{y}")
        
        tk.Label(dialog, text="ชื่อโปรเจกต์", font=("Segoe UI", 12, "bold"), 
                bg="#1e293b", fg="#38bdf8").pack(pady=20)
        
        name_entry = tk.Entry(dialog, bg="#0f172a", fg="#f8fafc", 
                             font=("Segoe UI", 11), bd=0, insertbackground="white")
        name_entry.pack(fill="x", padx=40, pady=10, ipady=8)
        name_entry.focus()
        
        def on_create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อโปรเจกต์")
                return
            
            # Check if project exists
            if name in self.dm.list_projects():
                messagebox.showwarning("คำเตือน", f"โปรเจกต์ '{name}' มีอยู่แล้ว")
                return
            
            try:
                self.dm.switch_project(name)
                self.selected_project = name
                dialog.destroy()
                self.root.quit()  # Exit selector, return to main
            except Exception as e:
                log_error(f"Error creating project: {e}")
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถสร้างโปรเจกต์ได้: {e}")
        
        btn_frame = tk.Frame(dialog, bg="#1e293b")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="สร้าง", command=on_create, 
                bg="#10b981", fg="white", bd=0, padx=20, pady=8,
                font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="ยกเลิก", command=dialog.destroy,
                bg="#64748b", fg="white", bd=0, padx=20, pady=8,
                font=("Segoe UI", 10)).pack(side="left", padx=5)
        
        name_entry.bind("<Return>", lambda e: on_create())
    
    def open_project(self):
        """เปิดโปรเจกต์ที่เลือก"""
        selection = self.project_listbox.curselection()
        if not selection:
            log_debug("No project selected to open")
            messagebox.showwarning("คำเตือน", "กรุณาเลือกโปรเจกต์")
            return
        
        project_name = self.project_listbox.get(selection[0]).strip()
        log_info(f"Opening project: {project_name}")
        if project_name == "(ยังไม่มีโปรเจกต์)":
            return
        
        try:
            self.dm.switch_project(project_name)
            self.selected_project = project_name
            self.root.quit()  # Exit selector, return to main
        except Exception as e:
            log_error(f"Error opening project: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเปิดโปรเจกต์ได้: {e}")
    
    def delete_project(self):
        """ลบโปรเจกต์ที่เลือก"""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกโปรเจกต์ที่ต้องการลบ")
            return
        
        project_name = self.project_listbox.get(selection[0]).strip()
        if project_name == "(ยังไม่มีโปรเจกต์)":
            return
        
        if not messagebox.askyesno("ยืนยันการลบ", 
                                   f"คุณต้องการลบโปรเจกต์ '{project_name}' ใช่หรือไม่?\n\n⚠️ การกระทำนี้ไม่สามารถยกเลิกได้!"):
            return
        
        try:
            project_file = self.dm.data_dir / f"project_{project_name}.json"
            if project_file.exists():
                project_file.unlink()
            
            # Also delete backup
            backup_file = self.dm.data_dir / f"backup_{project_name}.json"
            if backup_file.exists():
                backup_file.unlink()
            
            messagebox.showinfo("สำเร็จ", f"ลบโปรเจกต์ '{project_name}' เรียบร้อยแล้ว")
            self.refresh_project_list()
        except Exception as e:
            log_error(f"Error deleting project: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถลบโปรเจกต์ได้: {e}")
    
    def run(self):
        """รัน selector และคืนค่าโปรเจกต์ที่เลือก"""
        self.root.mainloop()
        return self.selected_project


def show_project_selector() -> str | None:
    """แสดงหน้าจอเลือกโปรเจกต์และคืนค่าโปรเจกต์ที่เลือก"""
    root = tk.Tk()
    selector = ProjectSelector(root)
    selected = selector.run()
    root.destroy()
    return selected
