import os, re, json, shutil, requests
from datetime import datetime

class CacheManager:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.fivem_data = os.path.join(self.appdata, "FiveM", "FiveM.app", "data")
        self.active_cache = os.path.join(self.fivem_data, "server-cache-priv")
        self.storage_dir = os.path.join(self.fivem_data, "kyofive-storage")
        self.db_file = os.path.join(self.storage_dir, "cached.json")

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        if not os.path.exists(self.db_file):
            self.save_db({"active_profile": None, "servers": {}})


    # --- DATABASE ---
    def load_db(self):
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except:
            return {"active_profile": None, "servers": {}}

    def save_db(self, data):
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    def update_server_data(self, name, code, ip, max_clients, build):
        db = self.load_db()
        db["servers"][code] = {
            "name": name,
            "ip": ip,
            "maxClients": max_clients,
            "gameBuild": build,
            "lastConnect": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        db["active_profile"] = code
        self.save_db(db)

    def switch_profile(self, name, code, ip, max_clients, build="1604"):
        db = self.load_db()
        current_active = db.get("active_profile")

        if current_active is None:
            db["active_profile"] = code
            db["servers"][code] = {
                "name": name,
                "ip": ip,
                "maxClients": max_clients,
                "gameBuild": build,
                "lastConnect": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.save_db(db)            
            return True, f"First profile set: {name}"

        if current_active == code:
            return True, "The server is active."

        try:
            if os.path.exists(self.active_cache):
                save_path = os.path.join(self.storage_dir, f"cache_{current_active}")
                if os.path.exists(save_path): shutil.rmtree(save_path)
                shutil.move(self.active_cache, save_path)

            load_path = os.path.join(self.storage_dir, f"cache_{code}")
            if os.path.exists(load_path):
                shutil.move(load_path, self.active_cache)
            else:
                os.makedirs(self.active_cache)

            db["active_profile"] = code
            if code != "localpriv":
                db["servers"][code] = {
                    "name": name,
                    "ip": ip,
                    "maxClients": max_clients,
                    "gameBuild": build,
                    "lastConnect": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            self.save_db(db)

            return True, f"Switched to {name} (Build {build})"
        except Exception as e:
            return False, f"Gagal: {str(e)}"
        

    # --- CHECKER ---
    def is_fivem_running(self):
        try:
            # Menjalankan perintah tasklist untuk mencari FiveM
            output = os.popen('tasklist /FI "IMAGENAME eq FiveM.exe"').read()
            return "FiveM.exe" in output
        except:
            return False

    def get_folder_size(self, code):
        db = self.load_db()
        if db.get("active_profile") == code:
            path = self.active_cache
        else:
            path = os.path.join(self.storage_dir, f"cache_{code}")

        if not os.path.exists(path): return "0 B"
        try:
            total_size = sum(f.stat().st_size for f in os.scandir(path) if f.is_file())
            gb = total_size / (1024**3)
            return f"{gb:.2f} GB" if gb >= 0.1 else f"{total_size / (1024**2):.1f} MB"
        except:
            return "Checking..."
        
    def check_local_server(self):
        try:
            response = requests.get("http://127.0.0.1:30120/info.json", timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                
                players_res = requests.get("http://127.0.0.1:30120/players.json", timeout=0.5)
                player_count = len(players_res.json()) if players_res.status_code == 200 else 0
                
                raw_name = data.get('vars', {}).get('sv_projectName', 'LOCAL DEVELOPMENT SERVER')
                clean_name = re.sub(r"\^[0-9]", "", raw_name)[:50]
                max_clients = data.get('vars', {}).get('sv_maxClients', '48')
                gameBuild = data.get('vars', {}).get('sv_enforceGameBuild', '1604')

                db = self.load_db()
                db["local_settings"] = { "name": clean_name, "gameBuild": gameBuild, "ip": "127.0.0.1:30120" }
                self.save_db(db)

                return {
                    "active": True,
                    "name": f"{clean_name}",
                    "ip": "127.0.0.1:30120",
                    "code": "localpriv",
                    "players": f"{player_count}/{max_clients}",
                    "gameBuild": gameBuild,
                    "size": self.get_folder_size("localpriv")
                }
        except:
            pass

        return {"active": False}
        
    def fetch_single_server(self, code):
        url = f"https://servers-frontend.fivem.net/api/servers/single/{code}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Server not found. Status code: {response.status_code}")
        except Exception as e:
            print(f"API Error: {e}")
        return {"error": True}
    

    # --- ACTION ---
    def get_library_data(self):
        db = self.load_db()
        library = []
        is_running = self.is_fivem_running()

        for code, info in db["servers"].items():
            # Clone info agar tidak merusak DB asli saat ditambah field 'size'
            item = info.copy()
            item["code"] = code
            item["size"] = self.get_folder_size(code)
            library.append(item)
        
        # Urutkan berdasarkan koneksi terakhir (terbaru di atas)
        library.sort(key=lambda x: x['lastConnect'], reverse=True)
        return {
            "library": library,
            "active_profile": db.get("active_profile"),
            "fivem_running": is_running,
            "local_server": self.check_local_server()
        }
    
    def reset_cache(self, code):
        if self.is_fivem_running():
            return {"status": "error", "message": "FiveM is still open! Close the game first."}

        db = self.load_db()
        if db.get("active_profile") == code:
            path = self.active_cache
        else:
            path = os.path.join(self.storage_dir, f"cache_{code}")

        try:
            if os.path.exists(path):
                shutil.rmtree(path)                
                if db.get("active_profile") == code:
                    os.makedirs(self.active_cache)
                    
                return {"status": "success", "message": f"{code} cache cleared successfully."}
            else:
                return {"status": "error", "message": "Cache folder not found."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
    def remove_from_list(self, code):
        if self.is_fivem_running():
            return {"status": "error", "message": "FiveM is still open! Close the game first."}
        
        db = self.load_db()
        if db.get("active_profile") == code:
            return {"status": "error", "message": "Cannot delete active server."}
        
        path = os.path.join(self.storage_dir, f"cache_{code}")
        try:
            if os.path.exists(path):
                shutil.rmtree(path)

                if code in db["servers"]:
                    del db["servers"][code]
                    self.save_db(db)

                return {"status": "success", "message": f"The {code} cache was successfully removed from the library."}
            else:
                return {"status": "error", "message": "Cache folder not found."}
        except Exception as e:
            return {"status": "error", "message": str(e)}