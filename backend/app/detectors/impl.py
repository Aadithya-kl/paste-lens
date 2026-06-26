import re
import json
from .base import BaseDetector
from typing import Optional, Tuple

class URLDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        if re.match(r'^https?://[^\s]+$', text.strip()):
            return ("URL", False)
        return None

class EmailDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', text.strip()):
            return ("Email", False)
        return None

class JSONDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        text_strip = text.strip()
        if (text_strip.startswith('{') and text_strip.endswith('}')) or (text_strip.startswith('[') and text_strip.endswith(']')):
            try:
                json.loads(text_strip)
                return ("JSON", False)
            except ValueError:
                pass
        return None

class SQLDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        sql_keywords = r'^(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b'
        if re.match(sql_keywords, text.strip(), re.IGNORECASE):
            return ("SQL", False)
        return None

class JWTDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        if re.match(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$', text.strip()):
            return ("JWT", True)
        return None

class APIKeyDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        if re.match(r'^(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36,})$', text.strip()):
            return ("Secret", True)
        return None
        
class UUIDDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        if re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', text.strip()):
            return ("UUID", False)
        return None

class CodeDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        lines = text.split('\n')
        if any(re.search(r'(function\s+\w+|def\s+\w+|class\s+\w+|import\s+\w+|const\s+\w+\s*=)', line) for line in lines):
            return ("Code", False)
        return None

class MarkdownDetector(BaseDetector):
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        if re.search(r'(^#+\s)|(\*\*.*?\*\*)|(`.*?`)', text, re.MULTILINE):
            return ("Markdown", False)
        return None
