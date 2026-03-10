import tkinter as tk
import json
import threading
from tkinter import scrolledtext, messagebox
from nexus_god.core.logging_utils import log_debug, log_info, log_error

class ChatTab:
    def __init__(self, parent, dm, colors, build_card, ai_service, apply_chat_update, set_status):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.ai_service = ai_service
        self.apply_chat_update = apply_chat_update
        self.set_status = set_status
        self.is_ai_busy = False

    def build(self):
        log_debug("Building chat content")
        card = self.build_card(self.parent, "สนทนาทวยเทพ (Divine Chat)")
        
        self.chat_display = scrolledtext.ScrolledText(card, bg=self.colors["input"], fg=self.colors["text"], font=("Segoe UI", 10), bd=0, wrap=tk.WORD)
        self.chat_display.pack(fill="both", expand=True, pady=(0, 15))
        self.chat_display.config(state="disabled")
        
        # Tags for styling
        self.chat_display.tag_config("user", foreground=self.colors["accent"], font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("ai", foreground=self.colors["success"], font=("Segoe UI", 10))

        input_f = tk.Frame(card, bg=card["bg"])
        input_f.pack(fill="x")
        
        self.chat_input = tk.Entry(input_f, bg=self.colors["input"], fg=self.colors["text"], font=("Segoe UI", 11), bd=0)
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)
        self.chat_input.bind("<Return>", lambda e: self.send_chat())
        
        tk.Button(input_f, text="ส่งสาส์น ⚡", command=self.send_chat, bg=self.colors["accent"], fg="black", font=("Segoe UI", 9, "bold"), bd=0, padx=20, pady=8).pack(side="right")

    def send_chat(self):
        msg = self.chat_input.get().strip()
        if not msg: return
        
        log_info(f"User sent chat message: {msg[:50]}...")
        self.chat_input.delete(0, tk.END)
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"คุณ: {msg}\n\n", "user")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)
        
        if self.is_ai_busy: return
        self.is_ai_busy = True
        
        def task():
            try:
                self.parent.after(0, lambda: self.set_status("AI กำลังสื่อสาร..."))
                
                # Build context
                context = f"World: {json.dumps(self.dm.data['world'], ensure_ascii=False)}\n"
                context += f"Characters: {json.dumps(list(self.dm.data['characters'].keys()), ensure_ascii=False)}\n"
                
                system = "คุณคือ Divine Architect ผู้ช่วยสร้างสรรค์นิยายที่ชาญฉลาด ให้คำแนะนำและช่วยปรับปรุงข้อมูลในโปรเจกต์"
                system += "\nหากมีการอัปเดตข้อมูล ให้ตอบกลับเป็น JSON ที่มี 'reply' และ 'update'"
                
                res_text = self.ai_service.call_ai_json(f"Context: {context}\n\nUser: {msg}", system)
                res_json = json.loads(res_text)
                
                reply = res_json.get("reply", "")
                update = res_json.get("update", {})
                
                def update_ui():
                    if update: self.apply_chat_update(update)
                    self.chat_display.config(state="normal")
                    self.chat_display.insert(tk.END, f"Divine: {reply}\n\n", "ai")
                    self.chat_display.config(state="disabled")
                    self.chat_display.see(tk.END)
                    self.is_ai_busy = False
                    self.set_status("สื่อสารเสร็จสิ้น")
                
                self.parent.after(0, update_ui)
            except Exception as e:
                log_error(f"Error in send_chat: {e}")
                self.is_ai_busy = False
                self.parent.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))

        threading.Thread(target=task, daemon=True).start()
