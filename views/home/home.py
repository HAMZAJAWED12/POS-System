import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivymd.app import MDApp

from database.db import get_total_products, get_total_orders, get_total_revenue

# ✅ Load KV file using absolute path for PyInstaller compatibility
kv_path = os.path.join(os.path.dirname(__file__), 'home.kv')
Builder.load_file(kv_path)


class HomeScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.add_background)
        self.update_dashboard_stats()

    def add_background(self, *args):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source="assets/bg-gradient.jpg", size=Window.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name

    def update_dashboard_stats(self):
        self.ids.total_products.text = f"📦 Total Products: {get_total_products()}"
        self.ids.total_orders.text = f"🧾 Orders Placed: {get_total_orders()}"
        self.ids.total_revenue.text = f"💰 Total Revenue: ${get_total_revenue():.2f}"

    def toggle_theme(self, switch_instance, value):
        if value:
            MDApp.get_running_app().theme_cls.theme_style = "Dark"
        else:
            MDApp.get_running_app().theme_cls.theme_style = "Light"
