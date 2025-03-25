import os
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivy.lang import Builder
from kivy.metrics import dp

from database.db import get_cart_items, remove_from_cart, update_cart_quantity, clear_cart, save_order

# ✅ PyInstaller-safe KV loading
kv_path = os.path.join(os.path.dirname(__file__), 'cart.kv')
Builder.load_file(kv_path)


class CartScreen(Screen):
    """Cart screen where users can view and manage cart items with better UI"""

    def on_enter(self):
        """Load cart items when entering the cart screen"""
        self.load_cart_items()

    def load_cart_items(self):
        """Load and display cart items dynamically from the database"""
        self.ids.cart_list.clear_widgets()
        cart_items = get_cart_items()
        total_price = 0  

        if not cart_items:
            self.ids.cart_list.add_widget(MDLabel(
                text="Your cart is empty",
                halign="center",
                size_hint_y=None,
                height=dp(40),
                theme_text_color="Secondary"
            ))
        else:
            for product_id, name, price, quantity in cart_items:
                total_price += price * quantity
                self.ids.cart_list.add_widget(CartRow(product_id, name, price, quantity, self))

        # ✅ Update total price with better styling
        self.ids.total_price.text = f"[b]Total: ${total_price:.2f}[/b]"

    def increase_quantity(self, product_id):
        """Increase product quantity in cart"""
        update_cart_quantity(product_id, increase=True)
        self.load_cart_items()

    def decrease_quantity(self, product_id):
        """Decrease product quantity in cart"""
        update_cart_quantity(product_id, increase=False)
        self.load_cart_items()

    def remove_item(self, product_id):
        """Remove an item from the cart"""
        remove_from_cart(product_id)
        self.load_cart_items()

    def clear_cart(self):
        """Clear all items from the cart"""
        clear_cart()
        self.load_cart_items()

    def checkout(self):
        """Complete checkout process: Save order and generate invoice"""
        order_id = save_order()  # ✅ Save order in the database
        if order_id:
            print(f"✅ Order {order_id} completed! Invoice generated.")
            self.clear_cart()  # Clear cart after successful order
        else:
            print("❌ Checkout failed: No items in cart.")


class CartRow(MDBoxLayout):
    """Represents a single cart item with better spacing and alignment"""

    def __init__(self, product_id, name, price, quantity, cart_screen, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(15)
        self.padding = [dp(10), dp(5)]
        self.size_hint_y = None
        self.height = dp(50)

        self.cart_screen = cart_screen
        self.product_id = product_id

        self.add_widget(MDLabel(
            text=f"[b]{name}[/b]", 
            size_hint_x=0.3, 
            halign="left", 
            markup=True
        ))

        self.add_widget(MDLabel(
            text=f"[b]${price:.2f}[/b]", 
            size_hint_x=0.2, 
            halign="center", 
            markup=True
        ))

        self.quantity_label = MDLabel(
            text=f"[b]Qty: {quantity}[/b]", 
            size_hint_x=0.2, 
            halign="right", 
            markup=True
        )
        self.add_widget(self.quantity_label)

        increase_btn = MDIconButton(
            icon="plus", 
            size_hint_x=0.1, 
            theme_text_color="Custom", 
            text_color=(0, 0.5, 1, 1)
        )
        increase_btn.bind(on_press=lambda _: self.update_quantity(True))
        self.add_widget(increase_btn)

        decrease_btn = MDIconButton(
            icon="minus", 
            size_hint_x=0.1, 
            theme_text_color="Custom", 
            text_color=(1, 0.5, 0, 1)
        )
        decrease_btn.bind(on_press=lambda _: self.update_quantity(False))
        self.add_widget(decrease_btn)

        delete_btn = MDIconButton(
            icon="delete", 
            size_hint_x=0.1, 
            theme_text_color="Custom", 
            text_color=(1, 0, 0, 1)
        )
        delete_btn.bind(on_press=lambda _: self.remove_item())
        self.add_widget(delete_btn)

    def update_quantity(self, increase):
        """Increase or decrease item quantity"""
        update_cart_quantity(self.product_id, increase)
        self.cart_screen.load_cart_items()

    def remove_item(self):
        """Remove item from cart"""
        remove_from_cart(self.product_id)
        self.cart_screen.load_cart_items()
