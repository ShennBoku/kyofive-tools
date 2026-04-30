import webview
import os
import sys
import ctypes

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.cache import CacheManager
from logic.database import DatabaseManager
from logic.kclicker import KeyClickerLogic

class KyoApi:
    def __init__(self):
        self.db = DatabaseManager()
        self.fivem_exe = os.path.join(os.getenv('LOCALAPPDATA'), "FiveM", "FiveM.exe")
        self.cache_mgr = CacheManager()

        self.keyclicker = KeyClickerLogic(self)
        self.keyclicker.start_service()
        self.keyclickerWindow = None

    # Cache Manager
    def fetch_server(self, code):
        return self.cache_mgr.fetch_single_server(code)

    def get_cached_library(self):
        return self.cache_mgr.get_library_data()
    
    def reset_cache(self, code):
        return self.cache_mgr.reset_cache(code)
    
    def remove_from_list(self, code):
        return self.cache_mgr.remove_from_list(code)
    
    def connect_server(self, serv, isNew):
        if self.cache_mgr.is_fivem_running():
            return {"status": "error", "message": "FiveM is still open! Please close the game first."}

        if isNew:
            name = serv['name']
            code = serv['code']
            ip = serv['ip']
            build = serv['build']
            max_clients = serv['clients']
        else:
            db = self.cache_mgr.load_db()
            code = serv['code']
            sInfo = db["servers"].get(serv['code'])
            ip = sInfo['ip']
            name = sInfo['name']
            build = sInfo['gameBuild']
            max_clients = sInfo['maxClients']

        success, msg = self.cache_mgr.switch_profile(name, code, ip, max_clients, build)
        if success:
            try:
                # os.startfile(f"fivem://connect/{ip}")
                ctypes.windll.shell32.ShellExecuteW(None, "open", f"fivem://connect/{ip}", None, None, 1)
                return {"status": "success", "message": "Launching..."}
            except Exception as e:
                return {"status": "error", "message": f"Failed to Open FiveM: {e}"}
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
        return self.db.get_config().get("kclicker", None)


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