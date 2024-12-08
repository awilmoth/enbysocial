import json
import aiohttp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, NumericProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList
from kivy.metrics import dp
from datetime import datetime
from functools import partial
from geopy.distance import geodesic

class PersonalAdCard(MDCard):
    def __init__(self, ad_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(15)
        self.spacing = dp(10)
        self.elevation = 1
        self.radius = [dp(10)]
        
        # Add content
        from kivymd.uix.label import MDLabel
        
        # Username and time
        header = MDLabel(
            text=f"{ad_data['username']} • {self.format_time(ad_data['created_at'])}",
            theme_text_color="Secondary",
            font_style="Caption"
        )
        self.add_widget(header)
        
        # Content
        content = MDLabel(
            text=ad_data['content'],
            theme_text_color="Primary"
        )
        self.add_widget(content)
        
        # Distance
        if 'distance' in ad_data:
            distance = MDLabel(
                text=f"{ad_data['distance']:.1f} miles away",
                theme_text_color="Secondary",
                font_style="Caption"
            )
            self.add_widget(distance)
    
    def format_time(self, timestamp):
        """Format timestamp to relative time."""
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"

class PersonalAdsScreen(MDScreen):
    ads_list = ObjectProperty(None)
    distance_filter = NumericProperty(50)  # Default 50 miles
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        Clock.schedule_interval(self.refresh_ads, 60)  # Refresh every minute
    
    def on_enter(self):
        """Called when the screen is entered."""
        self.refresh_ads()
    
    async def refresh_ads(self, *args):
        """Fetch and display personal ads."""
        if not self.app.access_token:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                params = {"distance": self.distance_filter} if self.distance_filter else {}
                
                async with session.get(
                    f"{self.app.api_url}/personal-ads/",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        ads = await response.json()
                        Clock.schedule_once(partial(self.display_ads, ads))
                    else:
                        self.show_error_dialog("Failed to fetch personal ads")
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    def display_ads(self, ads, *args):
        """Display the fetched ads."""
        self.ads_list.clear_widgets()
        for ad in ads:
            # Calculate distance if coordinates are available
            if (self.app.current_user.get('latitude') and 
                self.app.current_user.get('longitude') and
                ad.get('latitude') and ad.get('longitude')):
                user_coords = (self.app.current_user['latitude'], self.app.current_user['longitude'])
                ad_coords = (ad['latitude'], ad['longitude'])
                ad['distance'] = geodesic(user_coords, ad_coords).miles
            
            card = PersonalAdCard(ad)
            self.ads_list.add_widget(card)
    
    def update_distance_filter(self, value):
        """Update distance filter and refresh ads."""
        self.distance_filter = value
        self.refresh_ads()
    
    def create_new_ad(self):
        """Navigate to create ad screen."""
        self.manager.current = 'create_ad'
    
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
    
    @property
    def app(self):
        """Get the app instance."""
        from kivy.app import App
        return App.get_running_app()
