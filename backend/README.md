# Enby Social Backend

This is the backend service for Enby Social, a personal ad-based chat application. It's built using FastAPI and PostgreSQL, following a microservice architecture.

## Features

- User authentication and authorization
- Personal ads management with geolocation support
- Real-time messaging using WebSockets
- Distance-based search functionality
- Profile management with image upload support

## Tech Stack

- FastAPI: Modern, fast web framework for building APIs
- PostgreSQL: Robust, open-source database
- Peewee: Simple and small ORM
- WebSockets: For real-time messaging
- JWT: For secure authentication
- Docker: For containerization and easy deployment

## Prerequisites

- Docker and Docker Compose
- Python 3.11 or higher (for local development)
- PostgreSQL (for local development without Docker)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd enbysocial/backend
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py      # Configuration settings
│   │   └── security.py    # Security utilities
│   ├── models/
│   │   └── user.py        # Database models
│   ├── routers/
│   │   ├── user.py        # User endpoints
│   │   ├── personal_ads.py # Personal ads endpoints
│   │   └── messages.py    # Messaging endpoints
│   ├── schemas/
│   │   └── user.py        # Pydantic models
│   ├── database.py        # Database configuration
│   └── main.py           # Application entry point
├── tests/                # Test files
├── .env.example         # Example environment variables
├── docker-compose.yml   # Docker compose configuration
├── Dockerfile          # Docker configuration
└── requirements.txt    # Python dependencies
```

## API Endpoints

### Authentication
- POST `/users/register` - Register new user
- POST `/users/token` - Login and get access token

### Users
- GET `/users/me` - Get current user profile
- PUT `/users/me` - Update user profile
- POST `/users/me/location` - Update user location

### Personal Ads
- POST `/personal-ads` - Create new personal ad
- GET `/personal-ads` - Get personal ads (with optional distance filter)
- GET `/personal-ads/{ad_id}` - Get specific personal ad
- PUT `/personal-ads/{ad_id}` - Update personal ad
- DELETE `/personal-ads/{ad_id}` - Delete personal ad
- GET `/personal-ads/user/{user_id}` - Get user's personal ads

### Messages
- WebSocket `/messages/ws/{token}` - Real-time messaging connection
- POST `/messages` - Send message
- GET `/messages` - Get conversation messages
- PUT `/messages/{message_id}/read` - Mark message as read
- GET `/messages/unread` - Get unread messages

## Testing

Run tests using pytest:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
