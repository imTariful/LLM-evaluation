
import uvicorn
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.join(os.getcwd(), "backend"))
    try:
        print("Starting uvicorn...")
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="debug")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
