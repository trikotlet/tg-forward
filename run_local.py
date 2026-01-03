#!/usr/bin/env python3
"""
Скрипт для локального запуска бота без Docker (для тестирования)
"""
# #region agent log - hypothesis J: run_local script start
import json
import sys
import os
import time

def debug_log(hypothesis_id, message, data=None):
    log_entry = {
        "sessionId": "debug-session",
        "runId": "fourth-run",
        "hypothesisId": hypothesis_id,
        "location": "run_local.py",
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000)
    }
    try:
        log_path = "/Users/romansokolov/Cursor/002 VibeCoding Tg bot/.cursor/debug.log"
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"✅ Debug log written: {message}")
    except Exception as e:
        print(f"❌ Failed to write debug log: {e}")

debug_log("J", "run_local.py script started", {
    "python_version": sys.version,
    "current_dir": os.getcwd(),
    "script_path": __file__
})
# #endregion

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

debug_log("I", "Path updated, importing main")

try:
    # Импортируем и запускаем main
    from main import main
    debug_log("I", "main imported successfully")

    import asyncio

    if __name__ == '__main__':
        debug_log("I", "Starting asyncio main")
        asyncio.run(main())
except Exception as e:
    debug_log("I", "Error in run_local.py", {"error": str(e)})
    print(f"❌ Ошибка в run_local.py: {e}")
    import traceback
    traceback.print_exc()
# #endregion
