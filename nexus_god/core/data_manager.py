from __future__ import annotations

import json
import threading
from pathlib import Path
from tkinter import messagebox

from .logging_utils import log_error, log_debug, log_info


class NexusDataManager:
    def __init__(self):
        log_debug("Initializing NexusDataManager")
        self.data_dir = Path("nexus_god_data")
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.config = self.load_config()

        # Current project name
        self.current_project = self.config.get("last_project", "Default_Story")
        self.project_file = self.data_dir / f"project_{self.current_project}.json"
        self.data = self.load_data()

    def load_data(self):
        log_debug(f"Loading data for project: {self.current_project}")
        default_data = {
            "world": {
                "name": "",
                "theme": "",
                "geography": "",
                "climate": "",
                "rules": "",
                "genre": "ทั่วไป",
                "culture": "",
                "sensory": "",
                "synopsis": "",
            },
            "characters": {},
            "plot": {"act1": "", "act2": "", "act3": "", "key_events": "", "ending": ""},
            "chapters": {},
            "memory": {},
            "items": {},
            "style": "มาตรฐาน",
            "chat_history": [],
            "creation_phase": "synopsis",  # phases: synopsis, planning, world, characters, story
            "project_genre": "",  # แนวเรื่องของโปรเจกต์
            "character_fields_config": [],  # Custom fields configuration for this project
            "is_new_project": True,  # Flag สำหรับโปรเจกต์ใหม่
        }

        if self.project_file.exists():
            try:
                with open(self.project_file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    # Migration + safety
                    if not isinstance(d, dict):
                        return default_data

                    if "world" not in d:
                        d["world"] = default_data["world"]
                    if "characters" not in d:
                        d["characters"] = {}
                    if "plot" not in d:
                        d["plot"] = default_data["plot"]
                    if "chapters" not in d:
                        d["chapters"] = {}
                    if "memory" not in d:
                        d["memory"] = {}
                    if "items" not in d:
                        d["items"] = {}
                    if "chat_history" not in d:
                        d["chat_history"] = []
                    if "creation_phase" not in d:
                        d["creation_phase"] = "synopsis"

                    # Safety for list vs dict
                    if isinstance(d.get("chapters"), list): d["chapters"] = {}
                    if isinstance(d.get("characters"), list): d["characters"] = {}
                    if isinstance(d.get("memory"), list): d["memory"] = {}
                    if isinstance(d.get("items"), list): d["items"] = {}
                    if "memory_bank" in d and not d.get("memory"):
                        if isinstance(d["memory_bank"], dict): d["memory"] = d["memory_bank"]
                        else: d["memory"] = {}

                    # Sub-fields migration
                    for k, v in default_data["world"].items():
                        if k not in d["world"]:
                            d["world"][k] = v

                    if "style" not in d:
                        d["style"] = "มาตรฐาน"
                    if "project_genre" not in d:
                        d["project_genre"] = ""
                    if "character_fields_config" not in d:
                        d["character_fields_config"] = []
                    if "is_new_project" not in d:
                        d["is_new_project"] = False
                    return d
            except Exception as e:
                log_error(f"Error loading project data: {e}")
                messagebox.showerror(
                    "ข้อผิดพลาด",
                    f"ไม่สามารถโหลดข้อมูลโปรเจกต์ได้: {e}\nระบบจะใช้ข้อมูลเริ่มต้นแทน",
                )

        return default_data

    def load_config(self):
        log_debug("Loading configuration")
        default_config = {
            "api_key": "",
            "model": "gemini-2.0-flash",
            "theme": "dark",
            "last_project": "Default_Story",
            "ai_provider": "gemini",
            "groq_api_key": "",
            "groq_model": "llama-3.3-70b-versatile",
            # Custom character fields system
            "default_character_fields": [
                {"key": "name", "label": "ชื่อ", "type": "text", "required": True},
                {"key": "role", "label": "บทบาท", "type": "text", "required": False},
                {"key": "personality", "label": "บุคลิกภาพ", "type": "textarea", "required": False},
                {"key": "appearance", "label": "รูปลักษณ์", "type": "textarea", "required": False},
                {"key": "powers", "label": "พลัง/ความสามารถ", "type": "textarea", "required": False},
                {"key": "relationships", "label": "ความสัมพันธ์", "type": "textarea", "required": False},
                {"key": "backstory", "label": "ปูมหลัง", "type": "textarea", "required": False},
            ],
            "custom_character_fields": [],  # User-created custom fields
        }
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    if not isinstance(c, dict):
                        return default_config
                    # Ensure all default keys exist
                    for k, v in default_config.items():
                        if k not in c:
                            c[k] = v
                    # Migrate old configs
                    if "default_character_fields" not in c:
                        c["default_character_fields"] = default_config["default_character_fields"]
                    if "custom_character_fields" not in c:
                        c["custom_character_fields"] = []
                    return c
            except Exception as e:
                log_error(f"Error loading config: {e}")
        return default_config

    def save_all(self):
        # Run saving in a background thread to prevent UI hang
        log_debug("Initiating save_all")
        try:
            data_copy = json.loads(json.dumps(self.data))  # Simple deep copy
            config_copy = json.loads(json.dumps(self.config))

            def task():
                try:
                    # Save Project Data (No indent for speed and size)
                    with open(self.project_file, "w", encoding="utf-8") as f:
                        json.dump(data_copy, f, ensure_ascii=False)

                    # Save Config
                    with open(self.config_file, "w", encoding="utf-8") as f:
                        json.dump(config_copy, f, ensure_ascii=False)

                    # Create a backup of project data
                    backup_file = self.data_dir / f"backup_{self.current_project}.json"
                    with open(backup_file, "w", encoding="utf-8") as f:
                        json.dump(data_copy, f, ensure_ascii=False)
                except Exception as e:
                    print(f"ERROR: Async Save Error: {e}")

            threading.Thread(target=task, daemon=True).start()
        except Exception as e:
            log_error(f"Error initiating async save: {e}")

    def save_config(self):
        """Alias for save_all to ensure compatibility"""
        self.save_all()

    def list_projects(self):
        try:
            return [
                f.stem.replace("project_", "") for f in self.data_dir.glob("project_*.json")
            ]
        except Exception as e:
            log_error(f"Error listing projects: {e}")
            return ["Default_Story"]

    def switch_project(self, name):
        log_info(f"Switching to project: {name}")
        try:
            self.save_all()
            self.current_project = name
            self.config["last_project"] = name
            self.project_file = self.data_dir / f"project_{name}.json"
            self.data = self.load_data()
            self.save_all()
        except Exception as e:
            log_error(f"Error switching project: {e}")
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถสลับโปรเจกต์ได้: {e}")
