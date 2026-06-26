from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional
import datetime

from app.models.clipboard import ClipboardEntry
from app.schemas.clipboard import ClipboardEntryCreate

def get_entries(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    content_type: Optional[str] = None,
    is_pinned: Optional[bool] = None
) -> List[ClipboardEntry]:
    query = db.query(ClipboardEntry)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(ClipboardEntry.content.ilike(search_term))
        
    if content_type:
        if content_type.lower() == "secrets":
            query = query.filter(ClipboardEntry.is_sensitive == True)
        elif content_type.lower() != "all":
            query = query.filter(ClipboardEntry.content_type.ilike(content_type))
            
    if is_pinned is not None:
        query = query.filter(ClipboardEntry.is_pinned == is_pinned)
        
    return query.order_by(desc(ClipboardEntry.created_at)).offset(skip).limit(limit).all()

def add_entry(db: Session, entry: ClipboardEntryCreate) -> ClipboardEntry:
    # Check if this content already exists in history
    existing_entry = db.query(ClipboardEntry).filter(ClipboardEntry.content == entry.content).first()
    
    if existing_entry:
        # Increment copy count and bump to the top
        existing_entry.copy_count += 1
        existing_entry.created_at = datetime.datetime.utcnow()
        existing_entry.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing_entry)
        return existing_entry
        
    # If not duplicate, create new
    db_entry = ClipboardEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_entry(db: Session, entry_id: str) -> bool:
    entry = db.query(ClipboardEntry).filter(ClipboardEntry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False

def clear_history(db: Session, keep_pinned: bool = True) -> int:
    query = db.query(ClipboardEntry)
    if keep_pinned:
        query = query.filter(ClipboardEntry.is_pinned == False)
    deleted_count = query.delete()
    db.commit()
    return deleted_count

def toggle_pin(db: Session, entry_id: str) -> Optional[ClipboardEntry]:
    entry = db.query(ClipboardEntry).filter(ClipboardEntry.id == entry_id).first()
    if entry:
        entry.is_pinned = not entry.is_pinned
        db.commit()
        db.refresh(entry)
        return entry
    return None
