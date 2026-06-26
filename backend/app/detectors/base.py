from abc import ABC, abstractmethod
from typing import Optional, Tuple

class BaseDetector(ABC):
    """Base interface for content detectors"""
    
    @abstractmethod
    def detect(self, text: str) -> Optional[Tuple[str, bool]]:
        """
        Analyze the text and return (content_type, is_sensitive) if it matches.
        Return None if no match.
        """
        pass
