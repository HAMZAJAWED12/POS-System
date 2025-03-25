import os
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.metrics import dp
import matplotlib.pyplot as plt
from database.db import get_sales_data

# ✅ PyInstaller-friendly KV loading
kv_path = os.path.join(os.path.dirname(__file__), 'analytics.kv')
Builder.load_file(kv_path)


class AnalyticsScreen(Screen):
    def on_enter(self):
        self.plot_sales_per_day()
        self.plot_top_products()

    def plot_sales_per_day(self):
        self.ids.bar_chart_box.clear_widgets()

        data = get_sales_data(group_by='date')
        if not data:
            return

        labels = [item[0] for item in data]
        values = [item[1] for item in data]

        plt.figure(figsize=(6, 4))
        plt.bar(labels, values, color='skyblue')
        plt.title("Sales Per Day")
        plt.xlabel("Date")
        plt.ylabel("Total Sales")
        plt.tight_layout()
        plt.xticks(rotation=45)
        bar_chart_file = "bar_chart.png"
        plt.savefig(bar_chart_file)
        plt.close()

        self.ids.bar_chart_box.add_widget(
            Image(source=bar_chart_file, size_hint=(1, None), height=dp(200))
        )

    def plot_top_products(self):
        self.ids.pie_chart_box.clear_widgets()

        data = get_sales_data(group_by='product')
        if not data:
            return

        labels = [item[0] for item in data]
        values = [item[1] for item in data]

        plt.figure(figsize=(5, 5))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Top Products Sold")
        plt.tight_layout()
        pie_chart_file = "pie_chart.png"
        plt.savefig(pie_chart_file)
        plt.close()

        self.ids.pie_chart_box.add_widget(
            Image(source=pie_chart_file, size_hint=(1, None), height=dp(250))
        )
