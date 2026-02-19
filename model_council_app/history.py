import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

class HistoryManager:
    @staticmethod
    def load_history():
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    @staticmethod
    def save_entry(prompt, mode, synthesis, models_used):
        history = HistoryManager.load_history()
        
        entry = {
            "id": len(history) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "mode": mode,
            "synthesis": synthesis,
            "models": models_used
        }
        
        # Prepend to keep newest first
        history.insert(0, entry)
        
        # Limit to last 50 entries
        history = history[:50]
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
