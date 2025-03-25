import os
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.lang import Builder

# ✅ PyInstaller-safe loading of splash.kv
kv_path = os.path.join(os.path.dirname(__file__), 'splash.kv')
Builder.load_file(kv_path)

class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.go_to_home, 2.5)  # Delay of 2.5 seconds

    def go_to_home(self, dt):
        self.manager.current = "home"
