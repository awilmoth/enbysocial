# Enby Social

A personal ad-based chat application with FastAPI backend and multiple frontends: Kivy mobile app (iOS/Android) and web interface. The application allows users to create and browse personal ads based on location, and engage in real-time chat with other users.

## Features

- User authentication and profile management
- Location-based personal ads
- Real-time messaging using WebSockets
- Cross-platform support:
  - iOS mobile app
  - Android mobile app
  - Web browser interface
- Geolocation-based distance filtering
- Profile picture upload and management
- Material Design UI across all platforms

## Project Structure

```
enbysocial/
├── backend/                 # FastAPI backend service
│   ├── app/                # Application code
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   ├── routers/       # API endpoints
│   │   └── schemas/       # Pydantic models
│   ├── migrations/        # Database migrations
│   ├── tests/            # Backend tests
│   └── README.md         # Backend documentation
│
├── frontend/              # Kivy mobile application
│   ├── screens/          # Application screens
│   ├── assets/          # Images and other assets
│   └── README.md        # Frontend documentation
│
└── web/                  # Web interface
    ├── templates/        # HTML templates
    ├── static/          # Static files
    ├── screens/         # Shared screens with mobile app
    ├── assets/          # Shared assets with mobile app
    └── README.md        # Web documentation
```

## Technology Stack

### Backend
- FastAPI: Modern, fast web framework
- PostgreSQL: Robust, open-source database
- Peewee: Simple and small ORM
- WebSockets: For real-time messaging
- JWT: For secure authentication
- Docker: For containerization

### Mobile Frontend (iOS/Android)
- Kivy: Cross-platform Python framework
- KivyMD: Material Design components
- WebSockets: For real-time messaging
- Geolocation: For distance-based features

### Web Frontend
- Flask: Web server for Kivy web app
- Kivy: UI framework (shared with mobile)
- WebAssembly: For browser compatibility
- WebSockets: For real-time messaging

## Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL
- Docker and Docker Compose
- Android Studio (for Android development)
- Xcode (for iOS development)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd enbysocial
```

2. Create and configure environment variables:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp web/.env.example web/.env
# Edit .env files with your configurations
```

3. Start all services using Docker Compose:
```bash
docker-compose up --build
```

This will start:
- Backend API at `http://localhost:8000`
- Web interface at `http://localhost:5000`
- PostgreSQL database

### Individual Component Setup

See the README.md files in each component directory for detailed setup instructions:
- [Backend Setup](backend/README.md)
- [Mobile Frontend Setup](frontend/README.md)
- [Web Frontend Setup](web/README.md)

## API Documentation

Once the backend is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Mobile Frontend Tests
```bash
cd frontend
pytest
```

### Web Frontend Tests
```bash
cd web
pytest
```

## Deployment

### Backend Deployment
The backend includes a Dockerfile and can be deployed to any container orchestration platform. See the backend README for detailed deployment instructions.

### Mobile Frontend Deployment
The mobile frontend can be built for both iOS and Android app stores. See the frontend README for detailed build and submission instructions.

### Web Frontend Deployment
The web interface can be deployed using Docker or any WSGI-compatible server. See the web README for detailed deployment options.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- Kivy team for the mobile and web development framework
- KivyMD for Material Design components
- Flask team for the web server framework
