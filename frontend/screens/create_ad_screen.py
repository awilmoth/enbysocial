import json
import aiohttp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from functools import partial
from plyer import gps

class CreateAdScreen(MDScreen):
    content_field = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.current_location = None
        
        # Configure GPS
        if hasattr(gps, 'configure'):
            gps.configure(
                on_location=self.on_location,
                on_status=self.on_gps_status
            )
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Clear any previous input
        if self.content_field:
            self.content_field.text = ""
        
        # Start getting location
        self.get_location()
    
    def on_leave(self):
        """Called when leaving the screen."""
        # Stop GPS
        if hasattr(gps, 'stop'):
            gps.stop()
    
    def get_location(self):
        """Start getting GPS location."""
        try:
            if hasattr(gps, 'start'):
                gps.start(minTime=1000, minDistance=1)
        except Exception as e:
            self.show_error_dialog(f"GPS Error: {str(e)}")
    
    def on_location(self, **kwargs):
        """Handle GPS location updates."""
        self.current_location = {
            'latitude': kwargs.get('lat'),
            'longitude': kwargs.get('lon')
        }
    
    def on_gps_status(self, *args, **kwargs):
        """Handle GPS status updates."""
        pass
    
    async def create_ad(self):
        """Create a new personal ad."""
        if not self.content_field.text:
            self.show_error_dialog("Please enter some content for your ad")
            return
        
        if not self.current_location:
            self.show_error_dialog("Waiting for location data. Please try again in a moment.")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                
                # First update user location
                async with session.post(
                    f"{self.app.api_url}/users/me/location",
                    headers=headers,
                    params=self.current_location
                ) as location_response:
                    if location_response.status != 200:
                        self.show_error_dialog("Failed to update location")
                        return
                
                # Then create the ad
                ad_data = {
                    "content": self.content_field.text,
                    "latitude": self.current_location['latitude'],
                    "longitude": self.current_location['longitude']
                }
                
                async with session.post(
                    f"{self.app.api_url}/personal-ads/",
                    headers=headers,
                    json=ad_data
                ) as response:
                    if response.status == 200:
                        Clock.schedule_once(self.ad_created_success)
                    else:
                        error_data = await response.json()
                        self.show_error_dialog(error_data.get("detail", "Failed to create ad"))
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    def ad_created_success(self, *args):
        """Handle successful ad creation."""
        # Show success dialog
        dialog = MDDialog(
            text="Personal ad created successfully!",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.return_to_feed(dialog)
                )
            ]
        )
        dialog.open()
    
    def return_to_feed(self, dialog):
        """Return to the personal ads feed."""
        dialog.dismiss()
        self.manager.current = 'personal_ads'
    
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
    
    def cancel_creation(self):
        """Cancel ad creation and return to feed."""
        self.manager.current = 'personal_ads'
    
    @property
    def app(self):
        """Get the app instance."""
        from kivy.app import App
        return App.get_running_app()
