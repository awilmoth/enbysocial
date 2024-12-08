import json
import aiohttp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from functools import partial

class RegisterScreen(MDScreen):
    username_field = ObjectProperty(None)
    email_field = ObjectProperty(None)
    password_field = ObjectProperty(None)
    confirm_password_field = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Clear any previous input
        if self.username_field:
            self.username_field.text = ""
        if self.email_field:
            self.email_field.text = ""
        if self.password_field:
            self.password_field.text = ""
        if self.confirm_password_field:
            self.confirm_password_field.text = ""
    
    def validate_input(self):
        """Validate user input."""
        if not all([
            self.username_field.text,
            self.email_field.text,
            self.password_field.text,
            self.confirm_password_field.text
        ]):
            self.show_error_dialog("Please fill in all fields")
            return False
        
        if self.password_field.text != self.confirm_password_field.text:
            self.show_error_dialog("Passwords do not match")
            return False
        
        if len(self.password_field.text) < 8:
            self.show_error_dialog("Password must be at least 8 characters long")
            return False
        
        if '@' not in self.email_field.text:
            self.show_error_dialog("Please enter a valid email address")
            return False
        
        return True
    
    async def register(self):
        """Handle registration process."""
        if not self.validate_input():
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.app.api_url}/users/register",
                    json={
                        "username": self.username_field.text,
                        "email": self.email_field.text,
                        "password": self.password_field.text
                    }
                ) as response:
                    if response.status == 200:
                        # Registration successful, now login
                        async with session.post(
                            f"{self.app.api_url}/users/token",
                            data={
                                "username": self.username_field.text,
                                "password": self.password_field.text
                            }
                        ) as login_response:
                            if login_response.status == 200:
                                login_data = await login_response.json()
                                # Get user data
                                headers = {"Authorization": f"Bearer {login_data['access_token']}"}
                                async with session.get(
                                    f"{self.app.api_url}/users/me",
                                    headers=headers
                                ) as user_response:
                                    if user_response.status == 200:
                                        user_data = await user_response.json()
                                        Clock.schedule_once(
                                            partial(self.registration_success, login_data['access_token'], user_data)
                                        )
                                    else:
                                        self.show_error_dialog("Failed to get user data")
                            else:
                                self.show_error_dialog("Registration successful but login failed")
                    else:
                        error_data = await response.json()
                        self.show_error_dialog(error_data.get("detail", "Registration failed"))
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    def registration_success(self, access_token, user_data, *args):
        """Handle successful registration."""
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
    
    def go_to_login(self):
        """Navigate to login screen."""
        self.manager.current = 'login'
    
    @property
    def app(self):
        """Get the app instance."""
        from kivy.app import App
        return App.get_running_app()
