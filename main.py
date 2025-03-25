from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from views.home.home import HomeScreen
from views.products.products import ProductScreen
from views.cart.cart import CartScreen
from views.orderhistory.orderhistory import OrderHistoryScreen
from views.splash.splash import SplashScreen
from database.db import create_tables
from views.analytics.analytics import AnalyticsScreen

class POSApp(MDApp):
    def build(self):
        create_tables()
        sm = ScreenManager()

        # ✅ Add splash first
        sm.add_widget(SplashScreen(name='splash'))

        # ✅ Add other screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AnalyticsScreen(name="analytics"))
        sm.add_widget(ProductScreen(name='products'))
        sm.add_widget(CartScreen(name='cart'))
        sm.add_widget(OrderHistoryScreen(name='orderhistory'))

        # ✅ Start from splash screen
        sm.current = "splash"

        return sm

if __name__ == "__main__":
    POSApp().run()
