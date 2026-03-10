from __future__ import annotations
import json
import os
from nexus_god.ai.providers import Groq, genai, HAS_GENAI, HAS_GROQ
from nexus_god.core.logging_utils import log_debug, log_error

class AIService:
    def __init__(self, config):
        self.config = config

    def call_ai_simple(self, prompt, system):
        log_debug(f"Calling AI simple: {prompt[:50]}...")
        provider = self.config.get("ai_provider", "gemini")
        if provider == "gemini":
            api_key = self.config.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("กรุณาระบุ Gemini API Key ในหน้าตั้งค่า หรือตั้งค่า Environment Variable 'GEMINI_API_KEY'")
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model=self.config.get("model", "gemini-2.0-flash"),
                contents=prompt,
                config={"system_instruction": system}
            )
            return resp.text
        else:
            api_key = self.config.get("groq_api_key")
            if not api_key:
                raise ValueError("กรุณาระบุ Groq API Key ในหน้าตั้งค่า")
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model=self.config.get("groq_model", "llama-3.3-70b-versatile"),
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            )
            return resp.choices[0].message.content

    def call_ai_json(self, prompt, system):
        log_debug(f"Calling AI JSON: {prompt[:50]}...")
        provider = self.config.get("ai_provider", "gemini")
        
        if "JSON" not in system:
            system += "\nตอบกลับเป็น JSON เท่านั้น"

        if provider == "gemini":
            api_key = self.config.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("กรุณาระบุ Gemini API Key ในหน้าตั้งค่า หรือตั้งค่า Environment Variable 'GEMINI_API_KEY'")
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model=self.config.get("model", "gemini-2.0-flash"),
                contents=prompt,
                config={
                    "system_instruction": system,
                    "response_mime_type": "application/json"
                }
            )
            return resp.text
        else:
            api_key = self.config.get("groq_api_key")
            if not api_key:
                raise ValueError("กรุณาระบุ Groq API Key ในหน้าตั้งค่า")
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model=self.config.get("groq_model", "llama-3.3-70b-versatile"),
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content
