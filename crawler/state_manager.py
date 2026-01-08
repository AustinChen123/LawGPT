import json
import os
import hashlib
from typing import Dict

STATE_FILE = "data/crawler_state.json"

class StateManager:
    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_hash(self, key: str) -> str:
        return self.state.get(key, {}).get("hash")

    def update_state(self, key: str, content: str):
        """
        Updates the state with the new hash of the content.
        Returns True if content has changed (or is new), False otherwise.
        """
        new_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        old_hash = self.get_hash(key)
        
        if new_hash != old_hash:
            self.state[key] = {
                "hash": new_hash,
                "last_updated": os.path.getmtime(self.state_file) if os.path.exists(self.state_file) else 0
            }
            self._save_state()
            return True # Changed
        return False # Unchanged
