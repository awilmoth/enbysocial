import json
import aiohttp
import asyncio
import websockets
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, DictProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget
from datetime import datetime
from functools import partial

class ChatListItem(TwoLineAvatarListItem):
    def __init__(self, user_data, last_message, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_data['id']
        self.text = user_data['username']
        self.secondary_text = last_message['content'] if last_message else "No messages yet"
        
        # Add profile picture
        profile_pic = user_data.get('profile_picture', 'assets/default_profile.png')
        self.add_widget(ImageLeftWidget(source=profile_pic))

class MessagesScreen(MDScreen):
    chat_list = ObjectProperty(None)
    chat_input = ObjectProperty(None)
    messages_list = ObjectProperty(None)
    active_chat = DictProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.ws = None
        self.chats = {}  # Store chat history
        Clock.schedule_interval(self.check_websocket, 5)  # Check WebSocket connection every 5 seconds
    
    def on_enter(self):
        """Called when the screen is entered."""
        self.load_chats()
        self.connect_websocket()
    
    def on_leave(self):
        """Called when leaving the screen."""
        self.disconnect_websocket()
    
    async def load_chats(self):
        """Load user's chats."""
        if not self.app.access_token:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                
                # Get unread messages to identify active chats
                async with session.get(
                    f"{self.app.api_url}/messages/unread",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        unread_messages = await response.json()
                        # Process unread messages to get unique users
                        chat_users = set()
                        for msg in unread_messages:
                            chat_users.add(msg['sender_id'])
                        
                        # Load chat history for each user
                        for user_id in chat_users:
                            await self.load_chat_history(user_id)
                        
                        Clock.schedule_once(self.update_chat_list)
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    async def load_chat_history(self, other_user_id):
        """Load chat history with specific user."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                
                # Get user info
                async with session.get(
                    f"{self.app.api_url}/users/{other_user_id}",
                    headers=headers
                ) as user_response:
                    if user_response.status == 200:
                        user_data = await user_response.json()
                        
                        # Get messages
                        async with session.get(
                            f"{self.app.api_url}/messages/",
                            headers=headers,
                            params={"other_user_id": other_user_id}
                        ) as messages_response:
                            if messages_response.status == 200:
                                messages = await messages_response.json()
                                self.chats[other_user_id] = {
                                    "user": user_data,
                                    "messages": messages
                                }
        except Exception as e:
            self.show_error_dialog(f"Error loading chat history: {str(e)}")
    
    def update_chat_list(self, *args):
        """Update the chat list UI."""
        self.chat_list.clear_widgets()
        for user_id, chat_data in self.chats.items():
            last_message = chat_data["messages"][-1] if chat_data["messages"] else None
            item = ChatListItem(
                chat_data["user"],
                last_message,
                on_release=lambda x, uid=user_id: self.open_chat(uid)
            )
            self.chat_list.add_widget(item)
    
    def open_chat(self, user_id):
        """Open chat with specific user."""
        if user_id in self.chats:
            self.active_chat = self.chats[user_id]
            self.update_messages_list()
    
    def update_messages_list(self, *args):
        """Update the messages list UI."""
        if not self.active_chat:
            return
            
        self.messages_list.clear_widgets()
        for message in self.active_chat["messages"]:
            is_own = message["sender_id"] == self.app.current_user["id"]
            self.add_message_to_list(message, is_own)
    
    def add_message_to_list(self, message, is_own):
        """Add a message to the messages list."""
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        
        card = MDCard(
            orientation="vertical",
            size_hint_x=0.8,
            padding=dp(10),
            spacing=dp(5),
            pos_hint={"right": 0.98} if is_own else {"x": 0.02}
        )
        
        content = MDLabel(
            text=message["content"],
            theme_text_color="Primary"
        )
        card.add_widget(content)
        
        timestamp = MDLabel(
            text=self.format_time(message["created_at"]),
            theme_text_color="Secondary",
            font_style="Caption"
        )
        card.add_widget(timestamp)
        
        self.messages_list.add_widget(card)
    
    async def send_message(self):
        """Send a message to the active chat."""
        if not self.active_chat or not self.chat_input.text:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.app.access_token}"}
                data = {
                    "content": self.chat_input.text,
                    "receiver_id": self.active_chat["user"]["id"]
                }
                
                async with session.post(
                    f"{self.app.api_url}/messages/",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        message = await response.json()
                        self.active_chat["messages"].append(message)
                        Clock.schedule_once(lambda x: self.add_message_to_list(message, True))
                        self.chat_input.text = ""
                    else:
                        error_data = await response.json()
                        self.show_error_dialog(error_data.get("detail", "Failed to send message"))
        except Exception as e:
            self.show_error_dialog(f"Connection error: {str(e)}")
    
    async def connect_websocket(self):
        """Connect to WebSocket for real-time messages."""
        if not self.app.access_token or self.ws:
            return
        
        try:
            self.ws = await websockets.connect(
                f"ws://{self.app.api_url.replace('http://', '')}/messages/ws/{self.app.access_token}"
            )
            asyncio.create_task(self.listen_websocket())
        except Exception as e:
            self.show_error_dialog(f"WebSocket connection error: {str(e)}")
    
    async def listen_websocket(self):
        """Listen for WebSocket messages."""
        try:
            while True:
                message = await self.ws.recv()
                data = json.loads(message)
                if data["type"] == "new_message":
                    sender_id = data["sender_id"]
                    if sender_id not in self.chats:
                        await self.load_chat_history(sender_id)
                    elif self.active_chat and sender_id == self.active_chat["user"]["id"]:
                        self.active_chat["messages"].append(data)
                        Clock.schedule_once(lambda x: self.add_message_to_list(data, False))
        except websockets.exceptions.ConnectionClosed:
            self.ws = None
        except Exception as e:
            self.show_error_dialog(f"WebSocket error: {str(e)}")
            self.ws = None
    
    def disconnect_websocket(self):
        """Disconnect WebSocket."""
        if self.ws:
            asyncio.create_task(self.ws.close())
            self.ws = None
    
    def check_websocket(self, dt):
        """Check WebSocket connection and reconnect if necessary."""
        if not self.ws and self.app.access_token:
            asyncio.create_task(self.connect_websocket())
    
    def format_time(self, timestamp):
        """Format timestamp to readable time."""
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%I:%M %p")
    
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
