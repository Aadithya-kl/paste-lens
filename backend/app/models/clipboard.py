import uuid
import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, JSON
from app.database.config import Base

class ClipboardEntry(Base):
    __tablename__ = "clipboard_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    content = Column(Text, nullable=False)
    content_type = Column(String, index=True, nullable=False)
    is_sensitive = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False, index=True)
    copy_count = Column(Integer, default=1)
    
    entry_metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    embedding = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
