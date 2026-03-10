import tkinter as tk
import json
import threading
from tkinter import messagebox
from nexus_god.core.logging_utils import log_debug, log_info, log_error

class WizardTab:
    def __init__(self, parent, dm, colors, build_card, ai_service, apply_chat_update, set_status, update_progress):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.ai_service = ai_service
        self.apply_chat_update = apply_chat_update
        self.set_status = set_status
        self.update_progress = update_progress
        self.is_ai_busy = False

    def build(self):
        log_debug("Building wizard content")
        card = self.build_card(self.parent, "วิถีแห่งการสรรค์สร้าง (The Divine Path)")
        
        tk.Label(card, text="ระบบนำทางอัจฉริยะที่จะช่วยคุณสร้างโลกและเนื้อเรื่องทีละขั้นตอน", font=("Segoe UI", 10), bg=card["bg"], fg=self.colors["muted"]).pack(pady=(0, 20))
        
        self.wizard_msg = tk.Label(card, text="กำลังโหลดขั้นตอน...", font=("Segoe UI", 11, "italic"), bg=card["bg"], fg=self.colors["text"], wraplength=600)
        self.wizard_msg.pack(pady=20)
        
        btn_f = tk.Frame(card, bg=card["bg"])
        btn_f.pack(fill="x", pady=20)
        
        self.wiz_next_btn = tk.Button(btn_f, text="เริ่มขั้นตอนต่อไป ➔", command=self.next_wizard_step, bg=self.colors["accent"], fg="black", font=("Segoe UI", 10, "bold"), bd=0, padx=30, pady=12)
        self.wiz_next_btn.pack()
        
        self.refresh_wizard()

    def refresh_wizard(self):
        phase = self.dm.data.get("creation_phase", "synopsis")
        log_debug(f"Refreshing wizard for phase: {phase}")
        
        messages = {
            "synopsis": "ขั้นตอนที่ 1: กำหนดแก่นเรื่องและเรื่องย่อ (Synopsis)",
            "planning": "ขั้นตอนที่ 2: วางโครงสร้างเหตุการณ์สำคัญ (Plot Planning)",
            "world": "ขั้นตอนที่ 3: สร้างรายละเอียดของโลกและกฎเกณฑ์ (World Building)",
            "characters": "ขั้นตอนที่ 4: ออกแบบตัวละครและบทบาท (Character Design)",
            "story": "ขั้นตอนที่ 5: เริ่มต้นเขียนเนื้อเรื่องบทแรก (Writing)"
        }
        self.wizard_msg.config(text=messages.get(phase, "ขั้นตอนการสร้างสรรค์"))
        self.update_progress()

    def next_wizard_step(self):
        phase = self.dm.data.get("creation_phase", "synopsis")
        log_info(f"Requesting AI to generate wizard {phase}")
        
        if self.is_ai_busy: return
        self.is_ai_busy = True
        
        def task():
            try:
                self.parent.after(0, lambda: self.set_status(f"AI กำลังช่วยออกแบบ {phase}..."))
                
                context = f"Genre: {self.dm.data.get('project_genre', 'ทั่วไป')}\n"
                context += f"World: {json.dumps(self.dm.data['world'], ensure_ascii=False)}\n"
                
                prompts = {
                    "synopsis": "ช่วยร่างเรื่องย่อ (Synopsis) ที่น่าตื่นเต้นสำหรับนิยายเรื่องนี้",
                    "planning": "ช่วยวางโครงเรื่อง 3 องก์ (Act 1, 2, 3) และจุดหักมุมที่น่าสนใจ",
                    "world": "ช่วยขยายรายละเอียดของโลก กฎพลัง และสถานที่สำคัญ",
                    "characters": "ช่วยออกแบบตัวละครหลัก 3 ตัว พร้อมบุคลิกและปูมหลัง",
                    "story": "ช่วยร่างโครงสร้างของตอนที่ 1 และประโยคเปิดเรื่องที่ทรงพลัง"
                }
                
                system = "คุณคือ Divine Architect ให้ตอบกลับเป็น JSON Object ที่มี 'reply' (คำบรรยาย) และ 'update' (ข้อมูลที่จะอัปเดตในโปรเจกต์)"
                
                res_text = self.ai_service.call_ai_json(f"Context: {context}\n\nRequest: {prompts.get(phase)}", system)
                res_json = json.loads(res_text)
                
                def update_ui():
                    reply = res_json.get("reply", "AI ได้เตรียมข้อมูลให้คุณแล้ว")
                    update = res_json.get("update", {})
                    
                    if update:
                        log_info(f"Applying wizard {phase} update")
                        self.apply_chat_update(update)
                    
                    messagebox.showinfo("Divine Guidance", reply)
                    
                    # Move to next phase
                    phases = ["synopsis", "planning", "world", "characters", "story"]
                    try:
                        curr_idx = phases.index(phase)
                        if curr_idx < len(phases) - 1:
                            self.dm.data["creation_phase"] = phases[curr_idx + 1]
                        else:
                            messagebox.showinfo("ยินดีด้วย", "คุณได้เตรียมข้อมูลพื้นฐานครบถ้วนแล้ว! เริ่มเขียนนิยายได้เลย")
                    except ValueError:
                        self.dm.data["creation_phase"] = "synopsis"
                    
                    self.dm.save_all()
                    self.refresh_wizard()
                    self.is_ai_busy = False
                    self.set_status("นำทางเสร็จสิ้น")
                
                self.parent.after(0, update_ui)
            except Exception as e:
                log_error(f"Error in wizard: {e}")
                self.is_ai_busy = False
                self.parent.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))

        threading.Thread(target=task, daemon=True).start()
