import tkinter as tk
import json
import threading
from datetime import datetime
from tkinter import ttk, scrolledtext, messagebox
from nexus_god.core.logging_utils import log_debug, log_info, log_error

class EditorTab:
    def __init__(self, parent, dm, colors, build_card, ai_service, set_status, on_chapter_change_cb=None):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card
        self.ai_service = ai_service
        self.set_status = set_status
        self.on_chapter_change_cb = on_chapter_change_cb
        self.is_ai_busy = False

    def build(self):
        log_debug("Building editor content with AI tools")
        card = self.build_card(self.parent, "แก้ไขเนื้อเรื่อง (Divine Editor)")
        
        # Toolbar
        toolbar = tk.Frame(card, bg=card["bg"])
        toolbar.pack(fill="x", pady=(0, 15))
        
        tk.Label(toolbar, text="เลือกตอน:", font=("Segoe UI", 9), bg=toolbar["bg"], fg=self.colors["text"]).pack(side="left", padx=5)
        
        # Safety check for chapters being a dict
        chapters = self.dm.data.get("chapters", {})
        if not isinstance(chapters, dict):
            chapters = {}
            self.dm.data["chapters"] = chapters
            
        self.chapter_selector = ttk.Combobox(toolbar, values=list(chapters.keys()) or ["ตอนที่ 1"])
        self.chapter_selector.pack(side="left", padx=5)
        self.chapter_selector.bind("<<ComboboxSelected>>", self.on_chapter_change)
        
        tk.Button(toolbar, text="+ เพิ่มตอน", command=self.add_chapter, bg=self.colors["sidebar"], fg=self.colors["text"], bd=0, padx=10).pack(side="left", padx=5)
        tk.Button(toolbar, text="💾 บันทึก", command=self.save_current_chapter, bg=self.colors["success"], fg="white", bd=0, padx=15).pack(side="left", padx=5)
        
        # Undo/Redo Buttons
        tk.Button(toolbar, text="↩️ เลิกทำ", command=self.undo, bg=self.colors["sidebar"], fg=self.colors["text"], bd=0, padx=10).pack(side="left", padx=2)
        tk.Button(toolbar, text="↪️ ทำซ้ำ", command=self.redo, bg=self.colors["sidebar"], fg=self.colors["text"], bd=0, padx=10).pack(side="left", padx=2)
        tk.Button(toolbar, text="🔍 ค้นหา", command=self.show_search_dialog, bg=self.colors["sidebar"], fg=self.colors["text"], bd=0, padx=10).pack(side="left", padx=2)
        
        # AI Tools Toolbar
        ai_toolbar = tk.Frame(card, bg=card["bg"])
        ai_toolbar.pack(fill="x", pady=(0, 10))
        
        tk.Label(ai_toolbar, text="AI TOOLS:", font=("Segoe UI", 8, "bold"), bg=ai_toolbar["bg"], fg=self.colors["accent"]).pack(side="left", padx=5)
        tk.Button(ai_toolbar, text="✨ เขียนต่อ", command=self.ai_continue_writing, bg=self.colors["accent"], fg="black", bd=0, padx=10, font=("Segoe UI", 8)).pack(side="left", padx=2)
        tk.Button(ai_toolbar, text="🪄 ขัดเกลา", command=self.ai_improve_text, bg=self.colors["warning"], fg="black", bd=0, padx=10, font=("Segoe UI", 8)).pack(side="left", padx=2)
        tk.Button(ai_toolbar, text="🎬 แนะนำฉาก", command=self.ai_suggest_scene, bg=self.colors["sidebar"], fg=self.colors["text"], bd=0, padx=10, font=("Segoe UI", 8)).pack(side="left", padx=2)

        # Editor with Undo enabled
        self.editor_text = scrolledtext.ScrolledText(card, bg=self.colors["input"], fg=self.colors["text"], font=("Segoe UI", 12), bd=0, wrap=tk.WORD, insertbackground="white", padx=20, pady=20, undo=True, autoseparators=True)
        self.editor_text.pack(fill="both", expand=True)
        self.editor_text.bind("<<Modified>>", self.on_text_modified)
        
        # Bind keyboard shortcuts
        self.editor_text.bind("<Control-z>", lambda e: self.undo())
        self.editor_text.bind("<Control-y>", lambda e: self.redo())
        self.editor_text.bind("<Control-Shift-Z>", lambda e: self.redo())
        self.editor_text.bind("<Control-f>", lambda e: self.show_search_dialog())
        
        # Bottom bar for stats
        self.bottom_bar = tk.Frame(card, bg=card["bg"])
        self.bottom_bar.pack(fill="x", pady=(5, 0))
        
        self.stats_label = tk.Label(self.bottom_bar, text="คำ: 0 | ตัวอักษร: 0", font=("Segoe UI", 8), bg=card["bg"], fg=self.colors["muted"])
        self.stats_label.pack(side="left")
        
        self.editor_status = tk.Label(self.bottom_bar, text="พร้อมใช้งาน", font=("Segoe UI", 8), bg=card["bg"], fg=self.colors["muted"])
        self.editor_status.pack(side="right")

        # Load first chapter
        if chapters:
            first_key = list(chapters.keys())[0]
            self.chapter_selector.set(first_key)
            if self.on_chapter_change_cb:
                self.on_chapter_change_cb(first_key)
            self.editor_text.insert("1.0", chapters.get(first_key, ""))
            self.update_stats()

    def undo(self):
        try:
            self.editor_text.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.editor_text.edit_redo()
        except tk.TclError:
            pass

    def on_chapter_change(self, event):
        name = self.chapter_selector.get()
        if self.on_chapter_change_cb:
            self.on_chapter_change_cb(name)
        log_debug(f"Chapter changed to: {name}")
        self.editor_text.delete("1.0", tk.END)
        self.editor_text.insert("1.0", self.dm.data["chapters"].get(name, ""))
        self.update_stats()

    def on_text_modified(self, event):
        if self.editor_text.edit_modified():
            self.update_stats()
            self.editor_text.edit_modified(False)

    def update_stats(self):
        content = self.editor_text.get("1.0", tk.END).strip()
        char_count = len(content)
        # Simple word count for Thai/English mix
        import re
        words = re.findall(r'\w+', content)
        word_count = len(words)
        self.stats_label.config(text=f"คำ: {word_count} | ตัวอักษร: {char_count}")

    def show_search_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("ค้นหาและแทนที่")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors["sidebar"])
        dialog.transient(self.parent)
        
        tk.Label(dialog, text="ค้นหา:", bg=self.colors["sidebar"], fg=self.colors["text"]).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        search_ent = tk.Entry(dialog, bg=self.colors["input"], fg=self.colors["text"], insertbackground="white")
        search_ent.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        tk.Label(dialog, text="แทนที่ด้วย:", bg=self.colors["sidebar"], fg=self.colors["text"]).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        replace_ent = tk.Entry(dialog, bg=self.colors["input"], fg=self.colors["text"], insertbackground="white")
        replace_ent.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        def find():
            word = search_ent.get()
            self.editor_text.tag_remove('match', '1.0', tk.END)
            if word:
                idx = '1.0'
                while True:
                    idx = self.editor_text.search(word, idx, nocase=1, stopindex=tk.END)
                    if not idx: break
                    lastidx = '%s+%dc' % (idx, len(word))
                    self.editor_text.tag_add('match', idx, lastidx)
                    idx = lastidx
                self.editor_text.tag_config('match', foreground='black', background='yellow')
        
        def replace():
            word = search_ent.get()
            repl = replace_ent.get()
            content = self.editor_text.get("1.0", tk.END)
            new_content = content.replace(word, repl)
            self.editor_text.delete("1.0", tk.END)
            self.editor_text.insert("1.0", new_content)
            self.update_stats()

        btn_f = tk.Frame(dialog, bg=self.colors["sidebar"])
        btn_f.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_f, text="ค้นหา", command=find, bg=self.colors["accent"], fg="black", bd=0, padx=10).pack(side="left", padx=5)
        tk.Button(btn_f, text="แทนที่ทั้งหมด", command=replace, bg=self.colors["warning"], fg="black", bd=0, padx=10).pack(side="left", padx=5)
        
        dialog.columnconfigure(1, weight=1)

    def add_chapter(self):
        num = len(self.dm.data["chapters"]) + 1
        name = f"ตอนที่ {num}"
        log_info(f"Adding new chapter: {name}")
        self.dm.data["chapters"][name] = ""
        self.chapter_selector["values"] = list(self.dm.data["chapters"].keys())
        self.chapter_selector.set(name)
        self.on_chapter_change(None)

    def save_current_chapter(self):
        name = self.chapter_selector.get()
        if not name: return
        log_info(f"Saving chapter: {name}")
        content = self.editor_text.get("1.0", tk.END).strip()
        self.dm.data["chapters"][name] = content
        self.dm.save_all()
        self.editor_status.config(text=f"บันทึกแล้วเมื่อ {datetime.now().strftime('%H:%M:%S')}")

    def ai_continue_writing(self):
        if self.is_ai_busy: return
        self.is_ai_busy = True
        log_info("AI Continue Writing triggered")
        
        # Get context
        content = self.editor_text.get("1.0", tk.END).strip()
        # Take last 2000 chars for context
        context_text = content[-2000:] if len(content) > 2000 else content
        
        world_info = json.dumps(self.dm.data["world"], ensure_ascii=False)
        memory_info = json.dumps(self.dm.data.get("memory", {}), ensure_ascii=False)
        
        def task():
            try:
                self.parent.after(0, lambda: self.editor_status.config(text="AI กำลังเขียนต่อ..."))
                prompt = f"ข้อมูลโลก: {world_info}\nความจำ: {memory_info}\n\nเนื้อหาล่าสุด:\n{context_text}\n\nช่วยเขียนเนื้อหาต่อจากนี้อีกประมาณ 2-3 ย่อหน้า โดยรักษาโทนเรื่องเดิม"
                
                res = self.ai_service.call_ai_simple(prompt, "คุณคือผู้ช่วยเขียนนิยายมืออาชีพ เขียนเนื้อหาที่ลื่นไหลและน่าติดตาม")
                
                def update():
                    self.editor_text.insert(tk.END, f"\n\n{res}")
                    self.editor_text.see(tk.END)
                    self.is_ai_busy = False
                    self.editor_status.config(text="เขียนต่อเสร็จสิ้น")
                    self.save_current_chapter()
                
                self.parent.after(0, update)
            except Exception as e:
                log_error(f"Error in ai_continue: {e}")
                self.is_ai_busy = False
                self.parent.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))

        threading.Thread(target=task, daemon=True).start()

    def ai_improve_text(self):
        try:
            selected = self.editor_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            messagebox.showwarning("คำเตือน", "กรุณาคลุมดำข้อความที่ต้องการขัดเกลา")
            return

        if self.is_ai_busy: return
        self.is_ai_busy = True
        log_info("AI Improve Text triggered")

        def task():
            try:
                self.parent.after(0, lambda: self.editor_status.config(text="AI กำลังขัดเกลา..."))
                prompt = f"ช่วยขัดเกลาข้อความนี้ให้สละสลวยและได้อารมณ์มากขึ้น:\n\n{selected}"
                res = self.ai_service.call_ai_simple(prompt, "คุณคือบรรณาธิการมืออาชีพที่เชี่ยวชาญการใช้ภาษาไทย")
                
                def update():
                    # Replace selection
                    start = self.editor_text.index(tk.SEL_FIRST)
                    end = self.editor_text.index(tk.SEL_LAST)
                    self.editor_text.delete(start, end)
                    self.editor_text.insert(start, res)
                    self.is_ai_busy = False
                    self.editor_status.config(text="ขัดเกลาเสร็จสิ้น")
                    self.save_current_chapter()
                
                self.parent.after(0, update)
            except Exception as e:
                log_error(f"Error in ai_improve: {e}")
                self.is_ai_busy = False
                self.parent.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))

        threading.Thread(target=task, daemon=True).start()

    def ai_suggest_scene(self):
        if self.is_ai_busy: return
        self.is_ai_busy = True
        log_info("AI Suggest Scene triggered")
        
        content = self.editor_text.get("1.0", tk.END).strip()
        context_text = content[-2000:] if len(content) > 2000 else content
        
        def task():
            try:
                self.parent.after(0, lambda: self.editor_status.config(text="AI กำลังคิดฉากต่อไป..."))
                prompt = f"จากเนื้อหาล่าสุดนี้:\n{context_text}\n\nช่วยแนะนำ 3 แนวทางที่เป็นไปได้สำหรับฉากต่อไป"
                res = self.ai_service.call_ai_simple(prompt, "คุณคือที่ปรึกษาด้านการวางโครงเรื่องนิยาย")
                
                def show():
                    messagebox.showinfo("🎬 คำแนะนำฉากต่อไป", res)
                    self.is_ai_busy = False
                    self.editor_status.config(text="แนะนำเสร็จสิ้น")
                
                self.parent.after(0, show)
            except Exception as e:
                log_error(f"Error in ai_suggest: {e}")
                self.is_ai_busy = False
                self.parent.after(0, lambda e=e: messagebox.showerror("AI Error", str(e)))

        threading.Thread(target=task, daemon=True).start()
