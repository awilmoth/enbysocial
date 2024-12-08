import os
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.utils import platform
from kivy.clock import Clock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import screens
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.profile_screen import ProfileScreen
from screens.personal_ads_screen import PersonalAdsScreen
from screens.messages_screen import MessagesScreen
from screens.create_ad_screen import CreateAdScreen

# Set window size for desktop development
if platform not in ('android', 'ios'):
    Window.size = (400, 800)

class EnbySocialApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize variables
        self.api_url = os.getenv('API_URL', 'http://localhost:8000')
        self.access_token = None
        self.current_user = None
        self.screens = {}
        
    def build(self):
        # Set theme colors
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        # Create screen manager
        from kivy.uix.screenmanager import ScreenManager, NoTransition
        sm = ScreenManager(transition=NoTransition())
        
        # Create and add screens
        self.screens['login'] = LoginScreen(name='login')
        self.screens['register'] = RegisterScreen(name='register')
        self.screens['profile'] = ProfileScreen(name='profile')
        self.screens['personal_ads'] = PersonalAdsScreen(name='personal_ads')
        self.screens['messages'] = MessagesScreen(name='messages')
        self.screens['create_ad'] = CreateAdScreen(name='create_ad')
        
        # Add screens to screen manager
        for screen in self.screens.values():
            sm.add_widget(screen)
        
        return sm
    
    def on_start(self):
        """Called when the application starts."""
        # Check for stored credentials
        self.check_stored_credentials()
        
        # Request necessary permissions on Android
        if platform == 'android':
            self.request_android_permissions()
    
    def check_stored_credentials(self):
        """Check for stored login credentials."""
        # TODO: Implement secure credential storage and retrieval
        pass
    
    def request_android_permissions(self):
        """Request necessary permissions on Android."""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            permissions = [
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA
            ]
            request_permissions(permissions)
    
    def login_success(self, access_token, user_data):
        """Handle successful login."""
        self.access_token = access_token
        self.current_user = user_data
        self.root.current = 'personal_ads'
    
    def logout(self):
        """Handle logout."""
        self.access_token = None
        self.current_user = None
        self.root.current = 'login'
    
    def show_error_dialog(self, text):
        """Show error dialog."""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        dialog = MDDialog(
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

if __name__ == '__main__':
    EnbySocialApp().run()
