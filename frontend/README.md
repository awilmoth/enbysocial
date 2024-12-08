# Enby Social Mobile App

The mobile frontend for Enby Social, built with Kivy and KivyMD. This application provides a modern, native-feeling interface for both iOS and Android platforms.

## Features

- Material Design UI components
- Real-time messaging with WebSocket support
- Location-based personal ads
- Profile management with image upload
- Cross-platform compatibility (iOS and Android)

## Prerequisites

- Python 3.11 or higher
- Kivy and KivyMD
- Xcode (for iOS builds)
- Android Studio (for Android builds)
- Java Development Kit (JDK)
- Buildozer (for Android packaging)

## Setup Development Environment

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the App

### Desktop Development
```bash
python main.py
```

### iOS Development

1. Install additional iOS dependencies:
```bash
pip install kivy-ios
```

2. Create Xcode project:
```bash
toolchain build python3 kivy
```

3. Build the app:
```bash
toolchain create Enby Social /path/to/frontend
```

4. Open the Xcode project and run on simulator or device

### Android Development

1. Install Buildozer:
```bash
pip install buildozer
```

2. Initialize Buildozer:
```bash
buildozer init
```

3. Edit buildozer.spec with appropriate settings

4. Build the app:
```bash
buildozer android debug deploy run
```

## Project Structure

```
frontend/
├── main.py              # Application entry point
├── screens/            # Screen implementations
│   ├── login_screen.py
│   ├── login_screen.kv
│   ├── register_screen.py
│   ├── register_screen.kv
│   ├── personal_ads_screen.py
│   ├── personal_ads_screen.kv
│   ├── create_ad_screen.py
│   ├── create_ad_screen.kv
│   ├── messages_screen.py
│   ├── messages_screen.kv
│   ├── profile_screen.py
│   └── profile_screen.kv
├── assets/             # Images and other assets
├── requirements.txt    # Python dependencies
└── .env.example       # Example environment variables
```

## Building for Production

### iOS App Store

1. Configure certificates and provisioning profiles in Apple Developer Portal

2. Update Info.plist with required permissions:
- NSLocationWhenInUseUsageDescription
- NSCameraUsageDescription
- NSPhotoLibraryUsageDescription

3. Build for release:
```bash
toolchain create "Enby Social" /path/to/frontend --release
```

4. Archive and upload through Xcode

### Google Play Store

1. Create a keystore for signing:
```bash
keytool -genkey -v -keystore enbysocial.keystore -alias enbysocial -keyalg RSA -keysize 2048 -validity 10000
```

2. Update buildozer.spec with keystore information

3. Build release APK:
```bash
buildozer android release
```

4. Sign the APK:
```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore enbysocial.keystore bin/enbysocial-release-unsigned.apk enbysocial
```

5. Optimize with zipalign:
```bash
zipalign -v 4 bin/enbysocial-release-unsigned.apk bin/enbysocial-release.apk
```

## Required Permissions

### Android
- INTERNET
- ACCESS_FINE_LOCATION
- ACCESS_COARSE_LOCATION
- CAMERA
- READ_EXTERNAL_STORAGE
- WRITE_EXTERNAL_STORAGE

### iOS
- Location Services
- Camera
- Photo Library

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
