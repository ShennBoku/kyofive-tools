import os
import json

class DatabaseManager:
    def __init__(self):
        # Path dasar penyimpanan
        self.appdata = os.getenv('LOCALAPPDATA')
        self.storage_dir = os.path.join(self.appdata, "FiveM", "FiveM.app", "data", "kyofive-storage")
        
        # Nama file database
        self.db_cached = os.path.join(self.storage_dir, "cached.json") # Server Library
        self.db_config = os.path.join(self.storage_dir, "config.json") # Tool Settings (Clicker, dll)

        # Pastikan folder storage ada
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        # Inisialisasi file jika belum ada
        self._ensure_file(self.db_cached, {"active_profile": None, "servers": {}})
        self._ensure_file(self.db_config, {
            "app": {"auto_refresh": True},
            "kclicker": {"trigger": "INSERT", "spam": "E", "delay": "40"}
        })

    def _ensure_file(self, path, default_data):
        if not os.path.exists(path):
            self.save_json(path, default_data)

    def load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_json(self, path, data):
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def get_config(self): return self.load_json(self.db_config)
    def save_config(self, data): self.save_json(self.db_config, data)

    def get_cached(self): return self.load_json(self.db_cached)
    def save_cached(self, data): self.save_json(self.db_cached, data)
