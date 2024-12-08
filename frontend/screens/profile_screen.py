import json
import aiohttp
import os
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivy.utils import platform
from functools import partial
from PIL import Image
from io import BytesIO
import base64

class ProfileScreen(MDScreen):
    username_field = ObjectProperty(None)
    email_field = ObjectProperty(None)
    profile_image = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_profile_picture,
            preview=True,
        )
    
    def on_enter(self):
        """Called when the screen is entered."""
        self.load_user_data()
    
    def load_user_data(self):
        """Load user data into fields."""
        if not self.app.current_user:
            return
        
        self.username_field.text = self.app.current_user.get('username', '')
        self.email_field.text = self.app.current_user.get('email', '')
        
        # Load profile picture if exists
        if self.app.current_user.get('profile_picture'):
            self.profile_image.source = self.app.current_user['profile_picture']
    
    def open_file_manager(self):
        """Open file manager to select profile picture."""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE])
        
        # Set initial path
        initial_path = '/' if platform == 'android' else os.path.expanduser('~')
        self.file_manager.show(initial_path)
    
    def exit_file_manager(self, *args):
        """Close file manager."""
        self.file_manager.close()
    
    def select_profile_picture(self, path):
        """Handle profile picture selection."""
        try:
            # Close file manager
            self.file_manager.close()
            
            # Process and upload image
            self.process_and_upload_image(path)
        except Exception as e:
            self.show_error_dialog(f"Error selecting image: {str(e)}")
    
    def process_and_upload_image(self, path):
        """Process and upload the selected image."""
        try:
            # Open and resize image
            with Image.open(path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize maintaining aspect ratio
                max_size = (800, 800)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save to bytes
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Convert to base64
                img_base64 = base64.b64encode(img_byte_arr).decode()
                
                # Upload image
                self.upload_profile_picture(img_base64)
        except Exception as e:
            self.show_error_dialog(f"Error processing image: {str(e)}")
    
    async def upload_profile_picture(self, img_base64):
        """Upload profile picture to server."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                data = {"profile_picture": f"data:image/jpeg;base64,{img_base64}"}
                
                async with session.put(
                    f"{self.app.api_url}/users/me",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.app.current_user = user_data
                        self.load_user_data()
                    else:
                        error_data = await response.json()
                        self.show_error_dialog(error_data.get("detail", "Failed to upload image"))
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    async def update_profile(self):
        """Update user profile information."""
        if not self.username_field.text or not self.email_field.text:
            self.show_error_dialog("Please fill in all fields")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                data = {
                    "username": self.username_field.text,
                    "email": self.email_field.text
                }
                
                async with session.put(
                    f"{self.app.api_url}/users/me",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.app.current_user = user_data
                        self.show_success_dialog("Profile updated successfully")
                    else:
                        error_data = await response.json()
                        self.show_error_dialog(error_data.get("detail", "Failed to update profile"))
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    def logout(self):
        """Handle logout."""
        self.app.logout()
    
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
    
    def show_success_dialog(self, text):
        """Show success dialog."""
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
    
    @property
    def app(self):
        """Get the app instance."""
        from kivy.app import App
        return App.get_running_app()
