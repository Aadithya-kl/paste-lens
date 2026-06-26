import sys
import time
import requests
import pyperclip
import threading
import uvicorn
from app.main import app
from app.database.config import init_db, SessionLocal
from app.models.clipboard import ClipboardEntry

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

def run_tests():
    print("Waiting for server to start...")
    time.sleep(3)
    
    API_URL = "http://127.0.0.1:8001/api/v1"
    
    print("1. Clear DB...")
    db = SessionLocal()
    db.query(ClipboardEntry).delete()
    db.commit()
    db.close()
    
    # Let monitor pick up empty
    pyperclip.copy("")
    time.sleep(1)
    
    test_cases = [
        ("https://github.com", "URL", False),
        ("test@example.com", "Email", False),
        ('{"key": "value"}', "JSON", False),
        ("SELECT * FROM users;", "SQL", False),
        ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey.signature", "JWT", True),
        ("sk-12345678901234567890123456789012", "Secret", True),
        ("123e4567-e89b-12d3-a456-426614174000", "UUID", False),
        ("def my_func():\n    pass", "Code", False),
        ("# Hello World\n**bold**", "Markdown", False),
        ("Just some plain text", "Text", False),
    ]
    
    print("2. Testing detectors via clipboard monitor...")
    for content, expected_type, expected_sensitive in test_cases:
        pyperclip.copy(content)
        time.sleep(1) # wait for monitor (polls every 0.5s)
        
    print("3. Fetching history...")
    res = requests.get(f"{API_URL}/history").json()
    
    if len(res) != len(test_cases):
        print(f"ERROR: Expected {len(test_cases)} entries, got {len(res)}")
        for r in res:
            print("FOUND:", r["content"])
        sys.exit(1)
    
    for content, expected_type, expected_sensitive in test_cases:
        entry = next((e for e in res if e["content"] == content), None)
        assert entry is not None, f"Content not found: {content}"
        assert entry["content_type"] == expected_type, f"Expected {expected_type}, got {entry['content_type']} for {content}"
        assert entry["is_sensitive"] == expected_sensitive
        
    print("4. Testing deduplication...")
    pyperclip.copy("https://github.com")
    time.sleep(1.5)
    res = requests.get(f"{API_URL}/history").json()
    entry = next(e for e in res if e["content"] == "https://github.com")
    assert entry["copy_count"] == 2
    
    print("5. Testing filtering...")
    res = requests.get(f"{API_URL}/history?content_type=URL").json()
    assert len(res) == 1
    
    res = requests.get(f"{API_URL}/history?content_type=Secrets").json()
    assert len(res) == 2
    
    print("6. Testing Search...")
    res = requests.get(f"{API_URL}/history?search=SELECT").json()
    assert len(res) == 1
    assert res[0]["content_type"] == "SQL"
    
    print("7. Testing Pin & Delete...")
    to_pin = res[0]["id"]
    requests.put(f"{API_URL}/clipboard/{to_pin}/pin")
    res = requests.get(f"{API_URL}/history?is_pinned=true").json()
    assert len(res) == 1
    
    requests.delete(f"{API_URL}/clipboard/{to_pin}")
    res = requests.get(f"{API_URL}/history?search=SELECT").json()
    assert len(res) == 0
    
    print("8. Testing Clear History...")
    requests.delete(f"{API_URL}/history")
    res = requests.get(f"{API_URL}/history").json()
    assert len(res) == 0
    
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    try:
        run_tests()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
