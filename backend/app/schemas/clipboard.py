from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class ClipboardEntryBase(BaseModel):
    content: str
    content_type: str
    is_sensitive: bool = False
    is_pinned: bool = False
    copy_count: int = 1
    entry_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[Union[List[str], str, dict]] = None
    summary: Optional[str] = None
    embedding: Optional[str] = None

class ClipboardEntryCreate(ClipboardEntryBase):
    pass

class ClipboardEntryResponse(ClipboardEntryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
