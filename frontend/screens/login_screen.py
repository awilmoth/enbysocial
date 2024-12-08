import json
import aiohttp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from functools import partial

class LoginScreen(MDScreen):
    username_field = ObjectProperty(None)
    password_field = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        
    def on_enter(self):
        """Called when the screen is entered."""
        # Clear any previous input
        if self.username_field:
            self.username_field.text = ""
        if self.password_field:
            self.password_field.text = ""
    
    async def login(self):
        """Handle login process."""
        username = self.username_field.text
        password = self.password_field.text
        
        if not username or not password:
            self.show_error_dialog("Please fill in all fields")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.app.api_url}/users/token",
                    data={
                        "username": username,
                        "password": password
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Get user data
                        headers = {"Authorization": f"Bearer {data['access_token']}"}
                        async with session.get(
                            f"{self.app.api_url}/users/me",
                            headers=headers
                        ) as user_response:
                            if user_response.status == 200:
                                user_data = await user_response.json()
                                Clock.schedule_once(
                                    partial(self.login_success, data['access_token'], user_data)
                                )
                            else:
                                self.show_error_dialog("Failed to get user data")
                    else:
                        error_data = await response.json()
                        self.show_error_dialog(error_data.get("detail", "Login failed"))
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    def login_success(self, access_token, user_data, *args):
        """Handle successful login."""
        self.app.login_success(access_token, user_data)
    
    def show_error_dialog(self, text):
        """Show error dialog."""
        if not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog.text = text
        self.dialog.open()
    
    def go_to_register(self):
        """Navigate to registration screen."""
        self.manager.current = 'register'
    
    @property
    def app(self):
        """Get the app instance."""
        from kivy.app import App
        return App.get_running_app()
