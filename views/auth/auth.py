from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_file("views/auth/auth.kv")

class LoginScreen(Screen):
    def do_login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        print(f"Logging in with: {username}, {password}")

class SignupScreen(Screen):
    pass
