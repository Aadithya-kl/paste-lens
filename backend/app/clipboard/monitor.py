import asyncio
import os
import pyperclip
import logging
from app.database.config import SessionLocal
from app.detectors import analyze_content
from app.schemas.clipboard import ClipboardEntryCreate
from app.services.clipboard_service import add_entry

logger = logging.getLogger(__name__)

async def start_clipboard_monitor():
    poll_interval = int(os.environ.get("POLL_INTERVAL", "500")) / 1000.0
    last_paste = ""
    
    logger.info(f"Starting clipboard monitor (polling every {poll_interval}s)")
    
    while True:
        try:
            current_paste = pyperclip.paste()
            
            # Skip empty or identical
            if current_paste and current_paste != last_paste:
                last_paste = current_paste
                
                # Analyze content
                content_type, is_sensitive = analyze_content(current_paste)
                
                # Create entry
                entry = ClipboardEntryCreate(
                    content=current_paste,
                    content_type=content_type,
                    is_sensitive=is_sensitive
                )
                
                # Save to DB
                db = SessionLocal()
                try:
                    add_entry(db, entry)
                finally:
                    db.close()
                    
        except Exception as e:
            logger.error(f"Error in clipboard monitor: {e}")
            
        await asyncio.sleep(poll_interval)
