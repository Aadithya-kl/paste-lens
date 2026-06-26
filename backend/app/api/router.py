from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.config import get_db
from app.schemas.clipboard import ClipboardEntryResponse, ClipboardEntryCreate
from app.services import clipboard_service

api_router = APIRouter()

@api_router.get("/history", response_model=List[ClipboardEntryResponse])
def get_history(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000), 
    search: Optional[str] = None,
    content_type: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return clipboard_service.get_entries(db, skip, limit, search, content_type, is_pinned)

@api_router.post("/clipboard", response_model=ClipboardEntryResponse)
def add_clipboard_entry(entry: ClipboardEntryCreate, db: Session = Depends(get_db)):
    return clipboard_service.add_entry(db, entry)

@api_router.delete("/clipboard/{entry_id}")
def delete_entry(entry_id: str, db: Session = Depends(get_db)):
    success = clipboard_service.delete_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "success"}

@api_router.delete("/history")
def clear_history(keep_pinned: bool = True, db: Session = Depends(get_db)):
    count = clipboard_service.clear_history(db, keep_pinned)
    return {"deleted": count}

@api_router.put("/clipboard/{entry_id}/pin", response_model=ClipboardEntryResponse)
def toggle_pin(entry_id: str, db: Session = Depends(get_db)):
    entry = clipboard_service.toggle_pin(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry
