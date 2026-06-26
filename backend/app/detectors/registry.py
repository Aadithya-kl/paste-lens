from typing import Tuple
from .base import BaseDetector
from .impl import (
    URLDetector, EmailDetector, JSONDetector, SQLDetector, 
    JWTDetector, APIKeyDetector, UUIDDetector, CodeDetector, MarkdownDetector
)

# Order matters: more specific/sensitive first
DETECTORS = [
    JWTDetector(),
    APIKeyDetector(),
    URLDetector(),
    EmailDetector(),
    JSONDetector(),
    SQLDetector(),
    UUIDDetector(),
    CodeDetector(),
    MarkdownDetector(),
]

def analyze_content(text: str) -> Tuple[str, bool]:
    """
    Run text through all detectors.
    Returns (content_type, is_sensitive).
    Defaults to ('Text', False).
    """
    if not text or not text.strip():
        return ("Text", False)
        
    for detector in DETECTORS:
        result = detector.detect(text)
        if result:
            return result
    return ("Text", False)
