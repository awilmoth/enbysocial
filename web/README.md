# Enby Social Web Interface

A web-based version of the Enby Social application using Kivy for web browsers. This implementation provides the same functionality as the mobile app but runs in a web browser.

## Features

- Identical UI/UX to the mobile app using Kivy
- Real-time messaging with WebSocket support
- Location-based personal ads
- Profile management with image upload
- Material Design components
- Responsive design for different screen sizes

## Prerequisites

- Python 3.11 or higher
- Flask
- Kivy and KivyMD
- Docker and Docker Compose (for containerized deployment)

## Local Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

4. Run the development server:
```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

## Docker Deployment

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

2. Access the web interface at `http://localhost:5000`

## Project Structure

```
web/
├── app.py              # Main Flask application
├── templates/         # HTML templates
│   └── index.html    # Main template for Kivy web app
├── static/           # Static files
├── assets/          # Shared assets with mobile app
├── screens/         # Shared screens with mobile app
├── Dockerfile       # Docker configuration
└── requirements.txt # Python dependencies
```

## Browser Compatibility

The web interface has been tested and works on:
- Google Chrome (recommended)
- Firefox
- Safari
- Edge

## Performance Considerations

The web interface uses WebAssembly for optimal performance. However, some features might perform differently compared to the native mobile app:

- Camera access requires browser permissions
- Location services use browser geolocation API
- File uploads are handled through browser file picker
- Touch events are emulated for desktop browsers

## Development Notes

### Shared Code with Mobile App
The web interface shares the same Kivy screens and KV language files with the mobile app, ensuring consistent behavior across platforms. Any changes to the shared files will affect both mobile and web versions.

### WebSocket Implementation
Real-time messaging is implemented using browser WebSocket API, which connects to the same backend WebSocket endpoint as the mobile app.

### Browser-Specific Features
Some features are implemented differently for the web:
- File selection uses HTML5 file input
- Geolocation uses browser's geolocation API
- Touch events are mapped to mouse events where necessary

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing

Run tests using pytest:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
