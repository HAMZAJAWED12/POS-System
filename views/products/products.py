import os
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivy.lang import Builder
from kivy.metrics import dp
from database.db import add_product, get_products, update_product, delete_product, add_to_cart

# ✅ Load KV using absolute path (for PyInstaller compatibility)
kv_path = os.path.join(os.path.dirname(__file__), 'products.kv')
Builder.load_file(kv_path)


class ProductScreen(Screen):
    def on_enter(self):
        self.load_products()

    def load_products(self):
        """Loads products into the UI"""
        products = get_products()
        self.ids.product_list.clear_widgets()

        for product in products:
            product_id, name, price, stock = product
            self.ids.product_list.add_widget(ProductRow(product_id, name, price, stock, self))

    def add_new_product(self):
        """Adds a new product to the database"""
        name = self.ids.product_name.text
        price = self.ids.product_price.text
        stock = self.ids.product_stock.text

        if name and price and stock:
            add_product(name, float(price), int(stock))
            self.ids.product_name.text = ""
            self.ids.product_price.text = ""
            self.ids.product_stock.text = ""

            self.ids.status_label.text = "Product added successfully!"
            self.load_products()

    def edit_product(self, product_id, name, price, stock):
        """Fill the text fields with product details for editing"""
        self.ids.product_name.text = name
        self.ids.product_price.text = str(price)
        self.ids.product_stock.text = str(stock)

        self.ids.add_product_button.text = "Update Product"
        self.ids.add_product_button.unbind(on_press=self.add_new_product)
        self.ids.add_product_button.bind(on_press=lambda _: self.update_existing_product(product_id))

    def update_existing_product(self, product_id):
        """Update the product details in the database"""
        name = self.ids.product_name.text
        price = self.ids.product_price.text
        stock = self.ids.product_stock.text

        if name and price and stock:
            update_product(product_id, name, float(price), int(stock))

            self.ids.product_name.text = ""
            self.ids.product_price.text = ""
            self.ids.product_stock.text = ""

            self.ids.add_product_button.text = "Add Product"
            self.ids.add_product_button.unbind(on_press=self.update_existing_product)
            self.ids.add_product_button.bind(on_press=self.add_new_product)

            self.load_products()

    def add_product_to_cart(self, product_row):
        """Extract product details from row and add to cart"""
        product_id = product_row.product_id
        name = product_row.name
        price = product_row.price

        if not product_id or not name or not price:
            print("❌ Missing product details")
            return

        try:
            add_to_cart(product_id, name, float(price))
            print(f"✅ {name} added to cart!")
        except Exception as e:
            print(f"❌ Error adding to cart: {e}")


class ProductRow(MDBoxLayout):
    """Represents a single product row in the list"""

    def __init__(self, product_id, name, price, stock, product_screen, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(10)
        self.padding = dp(5)
        self.size_hint_y = None
        self.height = dp(40)

        self.product_screen = product_screen
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

        # Product details
        self.add_widget(MDLabel(text=name, size_hint_x=0.3, halign="left", bold=True))
        self.add_widget(MDLabel(text=f"${price}", size_hint_x=0.2, halign="center"))
        self.add_widget(MDLabel(text=f"Stock: {stock}", size_hint_x=0.2, halign="right"))

        # Edit button
        edit_button = MDIconButton(icon="pencil", size_hint_x=0.1, theme_text_color="Custom", text_color=(0, 0.5, 1, 1))
        edit_button.bind(on_press=self.edit_product)
        self.add_widget(edit_button)

        # Delete button
        delete_button = MDIconButton(icon="delete", size_hint_x=0.1, theme_text_color="Custom", text_color=(1, 0, 0, 1))
        delete_button.bind(on_press=self.delete_product)
        self.add_widget(delete_button)

        # ✅ Fixed Add to Cart button
        cart_button = MDIconButton(icon="cart-plus", size_hint_x=0.1, theme_text_color="Custom", text_color=(0, 0.6, 0, 1))
        cart_button.bind(on_press=self.add_to_cart)
        self.add_widget(cart_button)

    def edit_product(self, instance):
        """Calls the edit function in ProductScreen"""
        self.product_screen.edit_product(self.product_id, self.name, self.price, self.stock)

    def delete_product(self, instance):
        """Deletes the product"""
        delete_product(self.product_id)
        self.parent.remove_widget(self)

    def add_to_cart(self, instance):
        """Calls the add to cart function from ProductScreen"""
        self.product_screen.add_product_to_cart(self)
