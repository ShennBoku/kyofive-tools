import os
import re
import json
import uuid
import shutil
from logic.database import DatabaseManager

class ClientConfigManager:
    def __init__(self, api):
        self.db = DatabaseManager()
        self.api = api
        self.cfg_file = os.path.join(self.db.storage_dir, "client-config.json")
        self._refresh_paths()
        self._ensure_db()

    def _refresh_paths(self):
        paths = self.db.get_config().get("paths", {})
        self.citizen_fx = paths.get("citizen_fx", "")
        self.temp_dir = os.path.join(self.citizen_fx, "temp") if self.citizen_fx else ""

    def _ensure_db(self):
        if not os.path.exists(self.cfg_file):
            initial_id = f"cfg_{uuid.uuid4().hex[:8]}"
            self._save_client_db({
                "active_profile": initial_id,
                "profiles": {
                    initial_id: "Original Config"
                }
            })

    def _load_client_db(self):
        try:
            if not os.path.exists(self.cfg_file): return {"active_profile": None, "profiles": {}}
            with open(self.cfg_file, "r") as f:
                return json.load(f)
        except:
            return {"active_profile": None, "profiles": {}}

    def _save_client_db(self, data):
        try:
            with open(self.cfg_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving client-config database: {e}")

    def create_and_wipe(self):
        if self.api._is_fivem_running():
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}

        self._refresh_paths()
        main_cfg = os.path.join(self.citizen_fx, "fivem.cfg")
        
        if not os.path.exists(main_cfg):
            return {"status": "error", "message": "Original fivem.cfg not found in Roaming folder!"}

        try:
            db = self._load_client_db()
            old_id = db.get("active_profile")
            new_id = f"cfg_{uuid.uuid4().hex[:8]}"

            os.makedirs(self.temp_dir, exist_ok=True)
            backup_path = os.path.join(self.temp_dir, f"{old_id}.cfg")
            shutil.copy2(main_cfg, backup_path)

            with open(main_cfg, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            clean_lines = [l for l in lines if not l.strip().lower().startswith(("bind ", "rbind "))]

            with open(main_cfg, "w", encoding="utf-8") as f:
                f.writelines(clean_lines)

            db["profiles"][new_id] = "New Clean Configuration"
            db["active_profile"] = new_id
            self._save_client_db(db)

            return {"status": "success", "identifier": new_id}
        except Exception as e:
            return {"status": "error", "message": f"Failed to swap config: {str(e)}"}

    def switch_active_profile(self, target_id):
        if self.api._is_fivem_running():
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}

        self._refresh_paths()
        db = self._load_client_db()
        current_id = db.get("active_profile")
        
        if target_id == current_id: return {"status": "success"}

        main_cfg = os.path.join(self.citizen_fx, "fivem.cfg")
        target_cfg = os.path.join(self.temp_dir, f"{target_id}.cfg")

        try:
            shutil.copy2(main_cfg, os.path.join(self.temp_dir, f"{current_id}.cfg"))
            if os.path.exists(target_cfg):
                shutil.copy2(target_cfg, main_cfg)
            
            db["active_profile"] = target_id
            self._save_client_db(db)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": f"Switch failed: {str(e)}"}

    def get_config_data(self, identifier):
        self._refresh_paths()
        db = self._load_client_db()
        active_id = db.get("active_profile")
        
        main_cfg = os.path.join(self.citizen_fx, "fivem.cfg")
        temp_cfg = os.path.join(self.temp_dir, f"{identifier}.cfg")

        if identifier == active_id:
            target_file = main_cfg
        else:
            target_file = temp_cfg

        if not os.path.exists(target_file):
            if identifier == active_id:
                return {"status": "error", "message": "Main fivem.cfg not found. Check Path Config!"}
            else:
                if os.path.exists(main_cfg):
                    target_file = main_cfg
                else:
                    return {"status": "error", "message": "Configuration file not found in any location."}

        custom_binds, resource_binds = [], []
        try:
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    c_m = re.match(r'^bind\s+(\w+)\s+"?([\w\d_]+)"?\s+"(.+)"', line, re.I)
                    if c_m:
                        custom_binds.append({"device": c_m.group(1), "key": c_m.group(2), "command": c_m.group(3)})
                        continue

                    r_m = re.match(r'^rbind\s+([\w\d_-]+)\s+(\w+)\s+"?([\w\d_]+)"?\s+"(.+)"', line, re.I)
                    if r_m:
                        resource_binds.append({
                            "resource": r_m.group(1), "device": r_m.group(2), 
                            "key": r_m.group(3), "command": r_m.group(4)
                        })
            
            return {"status": "success", "customBinds": custom_binds, "resourceBinds": resource_binds}
        except Exception as e:
            return {"status": "error", "message": f"Read Error: {str(e)}"}

    def save_config_data(self, identifier, custom_binds, resource_binds):
        if self.api._is_fivem_running():
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}

        self._refresh_paths()
        db = self._load_client_db()
        
        target_file = os.path.join(self.citizen_fx, "fivem.cfg") if identifier == db.get("active_profile") else os.path.join(self.temp_dir, f"{identifier}.cfg")

        if not os.path.exists(target_file):
            return {"status": "error", "message": "Target file missing."}

        try:
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            new_lines = [l for l in lines if not l.strip().lower().startswith(("bind ", "rbind "))]

            insert_index = -1
            for i, line in enumerate(new_lines):
                if line.strip().lower() == "unbindall":
                    insert_index = i + 1
                    break

            generated_binds = []
            for b in custom_binds:
                generated_binds.append(f'bind {b["device"]} "{b["key"]}" "{b["command"]}"\n')
            for rb in resource_binds:
                generated_binds.append(f'rbind {rb["resource"]} {rb["device"]} "{rb["key"]}" "{rb["command"]}"\n')

            if insert_index != -1:
                new_lines[insert_index:insert_index] = generated_binds
            else:
                new_lines.extend(generated_binds)

            with open(target_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_notes(self, identifier, notes):
        db = self._load_client_db()
        if identifier in db["profiles"]:
            db["profiles"][identifier] = notes
            self._save_client_db(db)
            return {"status": "success"}
        return {"status": "error", "message": "Profile not found."}
    
    def reset_all_binds(self, identifier):
        if self.api._is_fivem_running():
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}

        self._refresh_paths()
        db = self._load_client_db()
        
        if identifier == db.get("active_profile"):
            target_file = os.path.join(self.citizen_fx, "fivem.cfg")
        else:
            target_file = os.path.join(self.temp_dir, f"{identifier}.cfg")

        if not os.path.exists(target_file):
            return {"status": "error", "message": "File not found."}

        try:
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            clean_lines = [l for l in lines if not l.strip().lower().startswith(("bind ", "rbind "))]
            with open(target_file, "w", encoding="utf-8") as f:
                f.writelines(clean_lines)

            return {"status": "success", "message": "All bindings have been cleared."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def delete_profile(self, identifier):
        if self.api._is_fivem_running():
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}

        self._refresh_paths()
        db = self._load_client_db()
        main_cfg = os.path.join(self.citizen_fx, "fivem.cfg")
        
        if identifier not in db["profiles"]:
            return {"status": "error", "message": "Profile not found."}
            
        try:
            if os.path.exists(main_cfg):
                os.remove(main_cfg)
            
            del db["profiles"][identifier]
            
            remaining_ids = list(db["profiles"].keys())
            if not remaining_ids:
                db["active_profile"] = None
                self._save_client_db(db)
                return {"status": "success", "next_id": None}

            new_active_id = remaining_ids[-1]
            target_temp_file = os.path.join(self.temp_dir, f"{new_active_id}.cfg")

            if os.path.exists(target_temp_file):
                shutil.copy2(target_temp_file, main_cfg)

            db["active_profile"] = new_active_id
            self._save_client_db(db)
                
            return {"status": "success", "next_id": new_active_id}
            
        except Exception as e:
            return {"status": "error", "message": f"Delete & Recovery failed: {str(e)}"}

    def get_all_profiles(self):
        return self._load_client_db()