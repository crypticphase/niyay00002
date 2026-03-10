from __future__ import annotations

# Keep this module side-effect free (no logging configuration or messageboxes).
# The UI layer can decide how/when to report missing optional dependencies.

try:
    from google import genai  # type: ignore

    HAS_GENAI = True
except ImportError:
    genai = None  # type: ignore
    HAS_GENAI = False

try:
    from groq import Groq  # type: ignore

    HAS_GROQ = True
except ImportError:
    Groq = None  # type: ignore
    HAS_GROQ = False
