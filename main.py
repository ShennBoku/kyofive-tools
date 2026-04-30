import webview
import os
import sys
import ctypes

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.cache import CacheManager
# from logic.clicker import ClickerLogic # Aktifkan jika file sudah ada

class KyoApi:
    def __init__(self):
        self.fivem_exe = os.path.join(os.getenv('LOCALAPPDATA'), "FiveM", "FiveM.exe")
        self.cache_mgr = CacheManager()

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