#!/usr/bin/env python
import sys
sys.path.insert(0, 'D:\\ai_\\LLM_evaluation\\backend')

try:
    print("Attempting to import app.main...")
    from app.main import app
    print("Main imported successfully")
except Exception as e:
    import traceback
    print("Error occurred:")
    traceback.print_exc()
    sys.exit(1)
