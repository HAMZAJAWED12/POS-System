import os
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from kivy.lang import Builder

from database.db import get_all_orders, regenerate_invoice, print_invoice

# ✅ Load KV file using safe path for PyInstaller
kv_path = os.path.join(os.path.dirname(__file__), 'orderhistory.kv')
Builder.load_file(kv_path)


class OrderHistoryScreen(Screen):
    def on_enter(self):
        self.load_orders()

    def load_orders(self):
        self.ids.order_list.clear_widgets()
        orders = get_all_orders()

        if not orders:
            self.ids.order_list.add_widget(MDLabel(
                text="No orders found.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for order_id, timestamp, total in orders:
            self.ids.order_list.add_widget(OrderRow(order_id, timestamp, total))


class OrderRow(MDBoxLayout):
    def __init__(self, order_id, timestamp, total, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(10)
        self.padding = dp(5)
        self.size_hint_y = None
        self.height = dp(50)

        self.add_widget(MDLabel(
            text=f"Order #{order_id}",
            size_hint_x=0.3,
            halign="left"
        ))
        self.add_widget(MDLabel(
            text=timestamp,
            size_hint_x=0.4,
            halign="center"
        ))
        self.add_widget(MDLabel(
            text=f"${total:.2f}",
            size_hint_x=0.2,
            halign="right"
        ))

        print_btn = MDIconButton(
            icon="file-pdf-box",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 1, 1)
        )
        print_btn.bind(on_press=lambda _: (regenerate_invoice(order_id), print_invoice(order_id)))
        self.add_widget(print_btn)
