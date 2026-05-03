import os, re, shutil, requests
from datetime import datetime
from logic.database import DatabaseManager

class CacheManager:
    def __init__(self, api):
        self.db = DatabaseManager()
        self.api = api
        self.temp = {}
        self.local = {}
        self._refresh_paths()

    def _refresh_paths(self):
        paths = self.db.get_config().get("paths", {})
        self.fivem_data = paths.get("fivem_data", "")
        
        if self.fivem_data:
            data_root = os.path.join(self.fivem_data, "data")
            self.active_cache = os.path.join(data_root, "server-cache-priv")
            self.cached_dir = os.path.join(data_root, "kyofive-storage")
        else:
            self.active_cache = self.cached_dir = ""

    def _get_now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def update_server_data(self, name, code, ip, max_clients, build):
        db = self.db.get_cached()
        db["servers"][code] = { "name": name, "ip": ip, "maxClients": max_clients, "gameBuild": build, "lastConnect": self._get_now() }
        db["active_profile"] = code
        self.db.save_cached(db)

    def switch_profile(self, name, code, ip, max_clients, build="1604", pools=""):
        self._refresh_paths()
        if not self.fivem_data:
            return False, "FiveM Application Data path is not configured."

        db = self.db.get_cached()
        current_active = db.get("active_profile")

        if current_active == code:
            return True, "This server profile is already active."

        try:
            os.makedirs(self.cached_dir, exist_ok=True)

            if current_active and os.path.exists(self.active_cache):
                save_path = os.path.join(self.cached_dir, f"cache_{current_active}")
                if os.path.exists(save_path): shutil.rmtree(save_path)
                shutil.move(self.active_cache, save_path)

            load_path = os.path.join(self.cached_dir, f"cache_{code}")
            if os.path.exists(load_path):
                shutil.move(load_path, self.active_cache)
            else:
                os.makedirs(self.active_cache, exist_ok=True)

            db["active_profile"] = code
            if code != "localpriv":
                db["servers"][code] = { "name": name, "ip": ip, "maxClients": max_clients, "gameBuild": build, "poolSizes": pools, "lastConnect": self._get_now() }

            ini_path = os.path.join(self.fivem_data, "CitizenFX.ini")
            if os.path.exists(ini_path):
                with open(ini_path, 'r') as f:
                    lines = f.readlines()

                new_lines = []
                keys_to_update = {
                    "SavedBuildNumber": build,
                    "PoolSizesIncrease": pools
                }
                
                found_keys = set()
                for line in lines:
                    updated = False
                    for key, value in keys_to_update.items():
                        if line.strip().startswith(key + "="):
                            new_lines.append(f"{key}={value}\n")
                            found_keys.add(key)
                            updated = True
                            break
                    if not updated:
                        new_lines.append(line)

                for key, value in keys_to_update.items():
                    if key not in found_keys and value:
                        new_lines.append(f"{key}={value}\n")

                with open(ini_path, 'w') as f:
                    f.writelines(new_lines)
            
            self.db.save_cached(db)
            return True, f"Successfully switched to {name}"
        
        except Exception as e:
            return False, f"Switch failed: {str(e)}"

    def get_folder_size(self, code):
        db = self.db.get_cached()
        path = self.active_cache if db.get("active_profile") == code else os.path.join(self.cached_dir, f"cache_{code}")

        if not path or not os.path.exists(path): return "0 B"
        try:
            total_size = sum(f.stat().st_size for f in os.scandir(path) if f.is_file())
            if total_size >= 1024**3:
                return f"{total_size / (1024**3):.2f} GB"
            return f"{total_size / (1024**2):.1f} MB"
        except:
            return "Checking..."
        
    def check_local_server(self):
        try:
            res = requests.get("http://127.0.0.1:30120/info.json", timeout=0.5)
            if res.status_code == 200:
                data = res.json()
                p_res = requests.get("http://127.0.0.1:30120/players.json", timeout=0.5)
                count = len(p_res.json()) if p_res.status_code == 200 else 0
                
                raw_name = data.get('vars', {}).get('sv_projectName', 'LOCAL SERVER')
                clean_name = re.sub(r"\^[0-9]", "", raw_name)[:50]
                build = data.get('vars', {}).get('sv_enforceGameBuild', '1604')
                pools = data.get('vars', {}).get('sv_poolSizesIncrease', '')
                max = data['vars'].get('sv_maxClients', '48')

                db = self.db.get_cached()
                db["local_settings"] = { "name": clean_name, "gameBuild": build, "poolSizes": pools, "ip": "127.0.0.1:30120" }
                self.db.save_cached(db)

                self.local = { "active": True, "name": clean_name, "ip": "127.0.0.1:30120", "code": "localpriv", "players": f"{count}/{max}", "max": max, "gameBuild": build, "poolSizes": pools, "size": self.get_folder_size("localpriv") }
        except:
            self.local = { "active": False }

        return self.local
        
    def fetch_single_server(self, code):
        url = f"https://servers-frontend.fivem.net/api/servers/single/{code}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                resp = response.json()
                code = resp['EndPoint']

                self.temp = {
                    "code": code,
                    "name": re.sub(r"\^[0-9]", "", resp['Data'].get('hostname', 'NOT DETECTED'))[:50],
                    "ip": resp['Data'].get('connectEndPoints', ['0.0.0.0'])[0],
                    "max": resp['Data']['sv_maxclients'],
                    "icon": f"https://frontend.cfx-services.net/api/servers/icon/{code}/{resp['Data']['iconVersion']}.png",
                    "clients": resp['Data']['clients'],
                    "gameBuild": resp['Data']['vars'].get('sv_enforceGameBuild', '1604'),
                    "poolSizes": resp['Data']['vars'].get('sv_poolSizesIncrease', ''),
                    "exe_running": self.api.is_exe
                }

                return self.temp
            else:
                print(f"Server not found. Status code: {response.status_code}")
        except Exception as e:
            print(f"API Error: {e}")
        return {"error": True}

    def get_library_data(self):
        db = self.db.get_cached()
        library = [{**info, "code": code, "size": self.get_folder_size(code)} for code, info in db.get("servers", {}).items()]
        
        library.sort(key=lambda x: x.get('lastConnect', ''), reverse=True)
        return {
            "library": library,
            "active_profile": db.get("active_profile"),
            "fivem_running": self.api._is_fivem_running(),
            "local_server": self.check_local_server(),
            "exe_running": self.api.is_exe
        }
    
    def reset_cache(self, code):
        if self.api._is_fivem_running():
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}
        
        self._refresh_paths()
        if not self.fivem_data: return {"status": "error", "message": "FiveM path is not configured."}

        db = self.db.get_cached()
        path = self.active_cache if db.get("active_profile") == code else os.path.join(self.cached_dir, f"cache_{code}")

        try:
            if os.path.exists(path):
                shutil.rmtree(path)                
                if db.get("active_profile") == code: os.makedirs(self.active_cache, exist_ok=True)
                return {"status": "success", "message": f"Cache for {code} has been cleared."}
            return {"status": "error", "message": "Cache folder not found."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def remove_from_list(self, code):
        """Menghapus server dari library dan menghapus folder profilnya di storage Kyogo"""
        if self.api._is_fivem_running(): 
            return {"status": "error", "message": "FiveM is still running! Please close the game first."}
        
        db = self.db.get_cached()
        if db.get("active_profile") == code:
            return {"status": "error", "message": "Cannot remove the currently active profile."}
        
        try:
            self._refresh_paths() 
            profile_path = os.path.join(self.cached_dir, f"cache_{code}")
            
            if os.path.exists(profile_path):
                shutil.rmtree(profile_path)
            
            if "servers" in db and code in db["servers"]:
                del db["servers"][code]
                self.db.save_cached(db)
                return {"status": "success", "message": f"Server {code} successfully removed."}
            else:
                return {"status": "error", "message": "Server code not found in your library."}
                
        except Exception as e:
            return {"status": "error", "message": f"System Error: {str(e)}"}