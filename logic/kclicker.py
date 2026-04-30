import threading, time
from pynput.keyboard import Controller, Listener, Key
from logic.database import DatabaseManager

class KeyClickerLogic:
    def __init__(self, api):
        self.api = api
        self.keyboard = Controller()
        self.db = DatabaseManager()

        config = self.db.get_config().get("kclicker", {})
        self.enabled = False
        self.makro_aktif = False
        self.berjalan = True
        
        self.trigger_key = config.get("trigger", "F6").lower()
        self.spam_key = config.get("spam", "E").lower()
        self.delay = float(config.get("delay", 100)) / 1000.0

    def start_service(self):
        threading.Thread(target=self.fungsi_makro, daemon=True).start()
        threading.Thread(target=self.listen, daemon=True).start()

    def fungsi_makro(self):
        while self.berjalan:
            if self.enabled and self.makro_aktif:
                try:
                    self.keyboard.press(self.spam_key)
                    time.sleep(0.03) 
                    self.keyboard.release(self.spam_key)
                    
                    time_to_sleep = self.delay - 0.03
                    time.sleep(max(0.01, time_to_sleep))
                except:
                    self.makro_aktif = False
            else:
                time.sleep(0.1)

    def on_press(self, key):
        if not self.enabled: return
        try:
            current_key = key.char if hasattr(key, 'char') else key.name
            if current_key == self.trigger_key:
                self.makro_aktif = not self.makro_aktif
        except:
            pass

    def listen(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def update_settings(self, data):
        self.enabled = data['enabled']
        self.trigger_key = data['trigger'].lower()
        self.spam_key = data['spam'].lower()
        self.delay = float(data['delay']) / 1000.0

        config = self.db.get_config()
        config["kclicker"] = {
            "trigger": data['trigger'],
            "spam": data['spam'],
            "delay": data['delay']
        }
        self.db.save_config(config)
        
        if not self.enabled:
            self.makro_aktif = False