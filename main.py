import webview
import os
import sys
import webbrowser

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.cache import CacheManager
from logic.database import DatabaseManager
from logic.kclicker import KeyClickerLogic
from logic.clientcfg import ClientConfigManager

class KyoApi:
    def __init__(self):
        self.db = DatabaseManager()
        self.config = self.db.get_config()
        self.is_exe = getattr(sys, 'frozen', False)

        self.client_cfg = ClientConfigManager(self)
        self.cache_mgr = CacheManager(self)

        self.keyclicker = KeyClickerLogic()
        self.keyclicker.start_service()
        self.keyclickerWindow = None

    def _is_fivem_running(self):
        try:
            with os.popen('tasklist /NH /FI "IMAGENAME eq FiveM.exe"') as f:
                return "FiveM.exe" in f.read()
        except:
            return False
        

    # Path Config
    def _validate_path(self, key, path):
        rules = { "citizen_fx": "fivem.cfg", "fivem_data": "CitizenFX.ini" }
        marker_file = rules.get(key)
        if not marker_file or not path:
            return False
            
        return os.path.isfile(os.path.join(path, marker_file))

    def get_path_conf(self):
        config = self.db.get_config()
        saved_paths = config.get("paths", {})
        updated = False

        # Target pencarian default
        defaults = {
            "citizen_fx": os.path.join(os.getenv('APPDATA', ''), "CitizenFX"),
            "fivem_data": os.path.join(os.getenv('LOCALAPPDATA', ''), "FiveM", "FiveM.app")
        }

        for key in ["citizen_fx", "fivem_data"]:
            current_path = saved_paths.get(key, "")
            if current_path and not self._validate_path(key, current_path):
                saved_paths[key] = ""
                updated = True
            
            if not saved_paths.get(key):
                default_path = defaults.get(key)
                if self._validate_path(key, default_path):
                    saved_paths[key] = default_path
                    updated = True

        if updated:
            config["paths"] = saved_paths
            self.db.save_config(config)

        return saved_paths
    
    def select_path_folder(self, current_path=""):
        active_window = webview.active_window()
        if not active_window:
            return None
        
        initial_dir = current_path if current_path and os.path.exists(current_path) else os.path.expanduser("~")
        result = active_window.create_file_dialog(
            webview.FOLDER_DIALOG, 
            directory=initial_dir
        )
        
        return result[0] if result else None
    
    def save_paths(self, data):
        try:
            config = self.db.get_config()
            new_paths = {
                "citizen_fx": data.get('citizen_fx', '').strip(),
                "fivem_data": data.get('fivem_data', '').strip()
            }

            for key, path in new_paths.items():
                if path and not self._validate_path(key, path):
                    return {"status": "error", "message": f"Invalid folder! Could not find required configuration files in {key}."}

            config["paths"] = new_paths
            self.db.save_config(config)

            return {"status": "success", "message": "Configuration saved and validated!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        

    # Client Config
    def get_all_client_profiles(self):
        return self.client_cfg.get_all_profiles()

    def create_and_wipe_client(self):
        return self.client_cfg.create_and_wipe()
    
    def switch_active_profile_client(self, target_id):
        return self.client_cfg.switch_active_profile(target_id)

    def get_client_config_data(self, identifier):
        return self.client_cfg.get_config_data(identifier)

    def save_config_data_client(self, identifier, custom_binds, resource_binds):
        return self.client_cfg.save_config_data(identifier, custom_binds, resource_binds)

    def update_notes_client(self, identifier, notes):
        return self.client_cfg.update_notes(identifier, notes)
    
    def reset_client_binds(self, identifier):
        return self.client_cfg.reset_all_binds(identifier)
    
    def delete_profile_client(self, identifier):
        return self.client_cfg.delete_profile(identifier)


    # Cache Manager
    def fetch_server(self, code):
        return self.cache_mgr.fetch_single_server(code)

    def get_cached_library(self):
        return self.cache_mgr.get_library_data()
    
    def reset_cache(self, code):
        return self.cache_mgr.reset_cache(code)
    
    def remove_from_list(self, code):
        return self.cache_mgr.remove_from_list(code)
    
    def connect_server(self, code, mode, isNew):
        if self._is_fivem_running():
            return {"status": "error", "message": "FiveM is still open, please close the game first."}
        if self.is_exe and (mode == "ip" or mode == "code"):
            return {"status": "error", "message": "Direct connection is disabled in EXE version."}

        if isNew:
            if code == "localpriv":
                if not self.cache_mgr.local.get("active", False):
                    return {"status": "error", "message": "Local Server is not active."}
                
                name = self.cache_mgr.local['name']
                ip = self.cache_mgr.local['ip']
                build = self.cache_mgr.local['gameBuild']
                pools = self.cache_mgr.local.get('poolSizes', {}) # Gunakan get untuk keamanan
                max_clients = self.cache_mgr.local['max']
            else:
                temp_data = getattr(self.cache_mgr, 'temp', {})
                if code != temp_data.get('code'):
                    return { "status": "error", "message": "Code mismatch." }

                name = temp_data['name']
                ip = temp_data['ip']
                build = temp_data['gameBuild']
                pools = temp_data['poolSizes']
                max_clients = temp_data['max']
        else:
            db = self.db.get_cached()
            sInfo = db["servers"].get(code)
            if not sInfo:
                return {"status": "error", "message": "Server not found in library."}
                
            ip = sInfo['ip']
            name = sInfo['name']
            build = sInfo['gameBuild']
            pools = sInfo['poolSizes']
            max_clients = sInfo['maxClients']

        success, msg = self.cache_mgr.switch_profile(name, code, ip, max_clients, build, pools)
        if success:
            if mode in ["ip", "code"]:
                try:
                    target = ip if mode == "ip" else code
                    webbrowser.open(f"fivem://connect/{target}")
                    return {"status": "success", "message": f"Cache switched & Launching to {name}..."}
                except Exception as e:
                    return {"status": "error", "message": f"Cache ready, but failed to open FiveM: {e}"}

            return {"status": "success", "message": f"Successfully prepared cache for {name}."}
        else:
            return {"status": "error", "message": msg}
        

    # Keyboard Clicker
    def update_kclicker_conf(self, data):
        self.toggle_kclicker_window(data['enabled'])
        self.keyclicker.update_settings(data)
        return {"status": "success"}
    
    def toggle_kclicker_window(self, enabled):
        if enabled:
            if not self.keyclickerWindow:
                path = os.path.join(os.path.dirname(__file__), "gui", "kclicker-status.html")
                self.keyclickerWindow = webview.create_window('KyoStatus', url=path, width=110, height=100, frameless=True, on_top=True, easy_drag=True, background_color='#1a1a1a')
                self.keyclickerWindow.events.closed += self.on_kclicker_window_closed
        else:
            if self.keyclickerWindow:
                self.keyclickerWindow.events.closed -= self.on_kclicker_window_closed
                self.keyclickerWindow.destroy()
                self.keyclickerWindow = None

    def refresh_kclicker_window(self, is_active):
        if self.keyclickerWindow:
            state = "true" if is_active else "false"
            self.keyclickerWindow.evaluate_js(f"updateStatus({state})")

    def on_kclicker_window_closed(self):
        self.keyclickerWindow = None
        self.keyclicker.enabled = False
        self.keyclicker.makro_aktif = False

    def get_pressed_key_kclicker(self):
        from pynput import keyboard
        self.keyclickerRecorded = None

        def on_press(key):
            try:
                self.keyclickerRecorded = key.char if hasattr(key, 'char') else key.name
            except:
                self.keyclickerRecorded = str(key)
            return False 

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        return self.keyclickerRecorded
    
    def get_kclicker_history(self):
        return self.config.get("kclicker", None)


def start_app():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "gui", "base.html")

    api = KyoApi()
    webview.create_window(
        title='KyoFive Tools - Kyogo Development Team',
        url=html_path,
        js_api=api,
        width=1280,
        height=720,
        resizable=True,
        background_color='#121212'
    )

    webview.start(debug=False, gui='edge')

if __name__ == "__main__":
    start_app()