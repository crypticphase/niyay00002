"""Project Setup Screen - กำหนดแนวเรื่องและตัวละครหลักสำหรับโปรเจกต์ใหม่"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from nexus_god.core.data_manager import NexusDataManager
from nexus_god.core.logging_utils import log_error, log_debug, log_info


class ProjectSetup:
    """หน้าจอ Setup สำหรับโปรเจกต์ใหม่"""
    
    def __init__(self, window, data_manager: NexusDataManager):
        log_debug("Initializing ProjectSetup")
        self.window = window
        self.dm = data_manager
        self.window.title("🌌 NEXUS GOD WRITER - ตั้งค่าโปรเจกต์ใหม่")
        self.window.geometry("900x700")
        self.window.minsize(700, 600)
        self.window.configure(bg="#0f172a")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        if isinstance(self.window, tk.Toplevel):
            self.window.transient(self.window.master)
            self.window.grab_set()

        self.setup_complete = False
        self.build_ui()
    
    def build_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#0f172a", pady=30)
        header.pack(fill="x")
        
        tk.Label(header, text="🌌", font=("Segoe UI", 40), bg="#0f172a", fg="#38bdf8").pack()
        tk.Label(header, text="ตั้งค่าโปรเจกต์ใหม่", font=("Segoe UI", 20, "bold"), 
                bg="#0f172a", fg="#38bdf8").pack(pady=5)
        tk.Label(header, text="กำหนดแนวเรื่องและตัวละครหลัก", font=("Segoe UI", 11), 
                bg="#0f172a", fg="#94a3b8").pack()
        
        # Main content
        content = tk.Frame(self.window, bg="#0f172a", padx=50, pady=30)
        content.pack(fill="both", expand=True)
        
        # Genre section
        genre_frame = tk.Frame(content, bg="#1e293b", padx=25, pady=20)
        genre_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(genre_frame, text="📚 แนวเรื่อง (Genre) *", 
                font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#38bdf8").pack(anchor="w", pady=(0, 10))
        
        self.genre_entry = tk.Entry(genre_frame, bg="#0f172a", fg="#f8fafc", 
                                    font=("Segoe UI", 11), bd=0, insertbackground="white")
        self.genre_entry.pack(fill="x", ipady=10)
        self.genre_entry.insert(0, self.dm.data.get("project_genre", ""))
        
        tk.Label(genre_frame, text="เช่น: แฟนตาซี, ไซไฟ, โรแมนติก, แอ็คชั่น, ฯลฯ", 
                font=("Segoe UI", 9), bg="#1e293b", fg="#64748b").pack(anchor="w", pady=(5, 0))
        
        # Main character section
        char_frame = tk.Frame(content, bg="#1e293b", padx=25, pady=20)
        char_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        tk.Label(char_frame, text="👤 ตัวละครหลัก (Main Character) *", 
                font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#38bdf8").pack(anchor="w", pady=(0, 15))
        
        # Character name
        name_frame = tk.Frame(char_frame, bg="#1e293b")
        name_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(name_frame, text="ชื่อตัวละคร:", font=("Segoe UI", 10), 
                bg="#1e293b", fg="#f8fafc", width=15, anchor="w").pack(side="left")
        
        self.char_name_entry = tk.Entry(name_frame, bg="#0f172a", fg="#f8fafc", 
                                       font=("Segoe UI", 11), bd=0, insertbackground="white")
        self.char_name_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(10, 0))
        
        # Character role
        role_frame = tk.Frame(char_frame, bg="#1e293b")
        role_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(role_frame, text="บทบาท:", font=("Segoe UI", 10), 
                bg="#1e293b", fg="#f8fafc", width=15, anchor="w").pack(side="left")
        
        self.char_role_entry = tk.Entry(role_frame, bg="#0f172a", fg="#f8fafc", 
                                       font=("Segoe UI", 11), bd=0, insertbackground="white")
        self.char_role_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(10, 0))
        self.char_role_entry.insert(0, "ตัวละครหลัก")
        
        # Character description
        desc_frame = tk.Frame(char_frame, bg="#1e293b")
        desc_frame.pack(fill="both", expand=True)
        
        tk.Label(desc_frame, text="คำอธิบาย:", font=("Segoe UI", 10), 
                bg="#1e293b", fg="#f8fafc", anchor="nw").pack(anchor="nw", pady=(0, 5))
        
        self.char_desc_text = scrolledtext.ScrolledText(
            desc_frame,
            bg="#0f172a",
            fg="#f8fafc",
            font=("Segoe UI", 10),
            bd=0,
            height=5,
            wrap=tk.WORD,
            insertbackground="white"
        )
        self.char_desc_text.pack(fill="both", expand=True)
        
        tk.Label(char_frame, text="💡 คุณสามารถเพิ่มตัวละครอื่นๆ และปรับแต่งฟิลด์ได้ภายหลัง", 
                font=("Segoe UI", 9), bg="#1e293b", fg="#64748b").pack(anchor="w", pady=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(content, bg="#0f172a")
        btn_frame.pack(fill="x")
        
        tk.Button(
            btn_frame,
            text="✅ เริ่มต้นโปรเจกต์",
            font=("Segoe UI", 12, "bold"),
            bg="#10b981",
            fg="white",
            bd=0,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.complete_setup
        ).pack(side="right", padx=5)
        
        tk.Button(
            btn_frame,
            text="⏭️ ข้าม (ใช้ค่าเริ่มต้น)",
            font=("Segoe UI", 11),
            bg="#64748b",
            fg="white",
            bd=0,
            padx=30,
            pady=15,
            cursor="hand2",
            command=self.skip_setup
        ).pack(side="right", padx=5)
    
    def complete_setup(self):
        """บันทึกการตั้งค่าและเสร็จสิ้น"""
        log_info("Completing project setup with user input")
        genre = self.genre_entry.get().strip()
        char_name = self.char_name_entry.get().strip()
        
        if not genre:
            log_debug("Setup validation failed: Genre is missing")
            messagebox.showwarning("คำเตือน", "กรุณาระบุแนวเรื่อง")
            self.genre_entry.focus()
            return
        
        if not char_name:
            log_debug("Setup validation failed: Main character name is missing")
            messagebox.showwarning("คำเตือน", "กรุณาระบุชื่อตัวละครหลัก")
            self.char_name_entry.focus()
            return
        
        try:
            log_info(f"Setting up project with genre: {genre} and main character: {char_name}")
            # บันทึกแนวเรื่อง
            self.dm.data["project_genre"] = genre
            self.dm.data["world"]["genre"] = genre
            
            # สร้างตัวละครหลัก
            main_char = {
                "name": char_name,
                "role": self.char_role_entry.get().strip() or "ตัวละครหลัก",
                "personality": "",
                "appearance": "",
                "powers": "",
                "relationships": "",
                "backstory": self.char_desc_text.get("1.0", tk.END).strip(),
                "is_main": True  # Mark as main character
            }
            
            # ถ้ายังไม่มีตัวละคร ให้เพิ่มตัวละครหลัก
            if not self.dm.data.get("characters") or isinstance(self.dm.data["characters"], list):
                log_debug("Initializing characters dict with main character")
                self.dm.data["characters"] = {char_name: main_char}
            else:
                # ถ้ามีตัวละครอยู่แล้ว ให้ตรวจสอบว่ามีตัวละครหลักหรือไม่
                has_main = any(c.get("is_main", False) for c in self.dm.data["characters"].values())
                if not has_main:
                    log_debug("Adding main character to characters dict")
                    self.dm.data["characters"][char_name] = main_char
            
            # Mark setup as complete
            self.dm.data["is_new_project"] = False
            self.dm.save_all()
            log_info("Project setup completed successfully")
            
            self.setup_complete = True
            if isinstance(self.window, tk.Tk):
                self.window.quit()
            else:
                self.window.destroy()
        except Exception as e:
            log_error(f"Error completing setup: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถบันทึกการตั้งค่าได้: {e}")
    
    def skip_setup(self):
        """ข้ามการตั้งค่า (ใช้ค่าเริ่มต้น)"""
        log_info("Skipping project setup, using defaults")
        try:
            # Set default genre if not set
            if not self.dm.data.get("project_genre"):
                self.dm.data["project_genre"] = "ทั่วไป"
                self.dm.data["world"]["genre"] = "ทั่วไป"
            
            # Mark setup as complete
            self.dm.data["is_new_project"] = False
            self.dm.save_all()
            
            self.setup_complete = True
            if isinstance(self.window, tk.Tk):
                self.window.quit()
            else:
                self.window.destroy()
        except Exception as e:
            log_error(f"Error skipping setup: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {e}")
    
    def run(self):
        """รัน setup screen"""
        if isinstance(self.window, tk.Tk):
            self.window.mainloop()
        else:
            self.window.wait_window()
        return self.setup_complete


def show_project_setup(data_manager: NexusDataManager, parent=None) -> bool:
    """แสดงหน้าจอ Setup และคืนค่า True ถ้าสำเร็จ"""
    if parent:
        window = tk.Toplevel(parent)
    else:
        window = tk.Tk()
        
    setup = ProjectSetup(window, data_manager)
    completed = setup.run()
    
    if isinstance(window, tk.Tk):
        window.destroy()
    return completed
