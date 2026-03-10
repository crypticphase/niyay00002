import tkinter as tk
import threading
from tkinter import scrolledtext, messagebox
from nexus_god.core.logging_utils import log_debug, log_error

class ReviewTab:
    def __init__(self, parent, dm, colors, build_card, ai_service, get_editor_content, get_chapter_name, set_status):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.ai_service = ai_service
        self.get_editor_content = get_editor_content
        self.get_chapter_name = get_chapter_name
        self.set_status = set_status
        self.is_ai_busy = False

    def build(self):
        log_debug("Building review content")
        card = self.build_card(self.parent, "ตรวจสอบคัมภีร์ (Divine Review)")
        
        tk.Label(card, text="ให้ AI ช่วยตรวจสอบความสมเหตุสมผล, โทนเรื่อง, และคำผิดในตอนปัจจุบัน", font=("Segoe UI", 10), bg=card["bg"], fg=self.colors["muted"]).pack(pady=(0, 20))
        
        btn_f = tk.Frame(card, bg=card["bg"])
        btn_f.pack(fill="x", pady=10)
        
        tk.Button(btn_f, text="🔍 ตรวจสอบตอนปัจจุบัน", command=self.ai_review_chapter, bg=self.colors["accent"], fg="black", font=("Segoe UI", 10, "bold"), bd=0, padx=30, pady=12).pack()
        
        self.review_display = scrolledtext.ScrolledText(card, bg=self.colors["input"], fg=self.colors["text"], font=("Segoe UI", 10), bd=0, wrap=tk.WORD)
        self.review_display.pack(fill="both", expand=True, pady=20)
        self.review_display.config(state="disabled")

    def ai_review_chapter(self):
        name = self.get_chapter_name()
        content = self.get_editor_content()
        if not content:
            messagebox.showwarning("คำเตือน", "ไม่มีเนื้อหาให้ตรวจสอบ")
            return
            
        if self.is_ai_busy: return
        self.is_ai_busy = True
        
        def task():
            try:
                self.parent.after(0, lambda: self.set_status("AI กำลังตรวจสอบ..."))
                prompt = f"ช่วยตรวจสอบเนื้อหานิยายตอน '{name}' นี้:\n\n{content}\n\nโดยให้คำแนะนำในหัวข้อ:\n1. ความสมเหตุสมผลของเนื้อเรื่อง\n2. โทนและการใช้ภาษา\n3. คำผิดหรือจุดที่ควรแก้ไข"
                res = self.ai_service.call_ai_simple(prompt, "คุณคือบรรณาธิการนิยายมืออาชีพ")
                
                def update():
                    self.review_display.config(state="normal")
                    self.review_display.delete("1.0", tk.END)
                    self.review_display.insert("1.0", res)
                    self.review_display.config(state="disabled")
                    self.is_ai_busy = False
                    self.set_status("ตรวจสอบเสร็จสิ้น")
                
                self.parent.after(0, update)
            except Exception as e:
                log_error(f"Error in ai_review: {e}")
                self.is_ai_busy = False
                self.parent.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))

        threading.Thread(target=task, daemon=True).start()
