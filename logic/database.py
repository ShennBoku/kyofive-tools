import os
import json

class DatabaseManager:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.storage_dir = os.path.join(self.appdata, "Kyogo Development", "kyofive-tools")
        
        self.db_config = os.path.join(self.storage_dir, "config.json")
        self.db_cached = os.path.join(self.storage_dir, "cached.json")

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        self._init_storage()

    def _init_storage(self):        
        self._ensure_file(self.db_cached, {
            "active_profile": None, 
            "servers": {}
        })
        
        self._ensure_file(self.db_config, {
            "app": {"auto_refresh": True},
            "kclicker": {"trigger": "INSERT", "spam": "E", "delay": "40"},
            "paths": {
                "citizen_fx": "",
                "fivem_data": ""
            }
        })

    def _ensure_file(self, path, default_data):
        if not os.path.exists(path):
            self.save_json(path, default_data)

    def load_json(self, path):
        try:
            if not os.path.exists(path): return {}
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def save_json(self, path, data):
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    # Getters & Setters
    def get_config(self): return self.load_json(self.db_config)
    def save_config(self, data): self.save_json(self.db_config, data)
    def get_cached(self): return self.load_json(self.db_cached)
    def save_cached(self, data): self.save_json(self.db_cached, data)