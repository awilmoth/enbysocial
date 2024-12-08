import os
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from kivy.config import Config

# Configure Kivy for web
Config.set('kivy', 'desktop', 1)
Config.set('graphics', 'width', 900)
Config.set('graphics', 'height', 600)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', 0)

from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.clock import Clock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock GPS for web environment
class MockGPS:
    def configure(self, *args, **kwargs):
        pass
    
    def start(self, *args, **kwargs):
        pass
    
    def stop(self, *args, **kwargs):
        pass

# Import screens with GPS mock if needed
try:
    from plyer import gps
except ImportError:
    gps = MockGPS()

from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.profile_screen import ProfileScreen
from screens.personal_ads_screen import PersonalAdsScreen
from screens.messages_screen import MessagesScreen
from screens.create_ad_screen import CreateAdScreen

class EnbySocialWebApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = os.getenv('API_URL', 'http://localhost:8000')
        self.access_token = None
        self.current_user = None
        self.screens = {}
        self.socketio = None

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

    def login_success(self, access_token, user_data):
        """Handle successful login."""
        self.access_token = access_token
        self.current_user = user_data
        self.root.current = 'personal_ads'
        if self.socketio:
            self.socketio.emit('user_login', {'token': access_token})
    
    def logout(self):
        """Handle logout."""
        if self.socketio:
            self.socketio.emit('user_logout')
        self.access_token = None
        self.current_user = None
        self.root.current = 'login'

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")

# Create Kivy app instance
kivy_app = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    # Forward message to appropriate handler in Kivy app
    if kivy_app and kivy_app.current_user:
        kivy_app.screens['messages'].handle_message(data)

def start_kivy_app():
    global kivy_app
    if kivy_app is None:
        kivy_app = EnbySocialWebApp()
        kivy_app.socketio = socketio
        # Load KV files
        for kv_file in os.listdir('screens'):
            if kv_file.endswith('.kv'):
                Builder.load_file(os.path.join('screens', kv_file))
        kivy_app.run()

if __name__ == '__main__':
    # Start Kivy app in a separate thread
    from threading import Thread
    kivy_thread = Thread(target=start_kivy_app)
    kivy_thread.daemon = True
    kivy_thread.start()
    
    # Start Flask-SocketIO app
    socketio.run(app, 
                host='0.0.0.0', 
                port=int(os.getenv('PORT', 5000)), 
                debug=os.getenv('DEBUG', 'True').lower() == 'true',
                use_reloader=False)
