import tkinter as tk
from tkinter import filedialog, messagebox
from nexus_god.core.logging_utils import log_debug, log_info

class ExportTab:
    def __init__(self, parent, dm, colors, build_card):
        self.parent = parent
        self.dm = dm
        self.colors = colors
        self.build_card = build_card

    def build(self):
        log_debug("Building export content")
        card = self.build_card(self.parent, "AI และส่งออก (Export & AI)")
        
        tk.Label(card, text="ส่งออกนิยายของคุณเป็นไฟล์ข้อความเพื่อนำไปใช้งานต่อ", font=("Segoe UI", 10), bg=card["bg"], fg=self.colors["muted"]).pack(pady=(0, 30))
        
        tk.Button(card, text="🚀 ส่งออกเป็นไฟล์ .txt", command=self.export_story, bg=self.colors["success"], fg="white", font=("Segoe UI", 12, "bold"), bd=0, padx=50, pady=20).pack()

    def export_story(self):
        log_info("Exporting story")
        chapters = self.dm.data.get("chapters", {})
        if not chapters:
            messagebox.showwarning("คำเตือน", "ไม่มีเนื้อหาให้ส่งออก")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path: return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"ชื่อเรื่อง: {self.dm.data['world'].get('name', 'ไม่ระบุ')}\n")
                f.write(f"แนวเรื่อง: {self.dm.data['world'].get('genre', 'ไม่ระบุ')}\n")
                f.write("="*30 + "\n\n")
                
                # Sort chapters if they are named like "ตอนที่ X"
                sorted_keys = sorted(chapters.keys())
                for key in sorted_keys:
                    f.write(f"--- {key} ---\n\n")
                    f.write(chapters[key])
                    f.write("\n\n" + "="*30 + "\n\n")
            
            messagebox.showinfo("สำเร็จ", f"ส่งออกไฟล์เรียบร้อยแล้วที่: {file_path}")
        except Exception as e:
            log_error(f"Error exporting story: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถส่งออกไฟล์ได้: {e}")
