# GPS & Phone Inclination Logger

A complete Progressive Web App (PWA) for collecting GPS coordinates and phone inclination data,  
with automatic interactive map generation. Works offline and can be installed on mobile devices.

## 📱 Features

- **Progressive Web App (PWA)** - Install directly on mobile devices
- **Offline Support** - Works without internet connection
- **GPS Data Collection** - Captures latitude and longitude
- **Phone Inclination** - Measures device tilt angle
- **Local Storage** - Data persists across page reloads
- **Export to CSV** - Download collected data as CSV files
- **Interactive Maps** - Automatic generation of beautiful, zoomable maps with marker clustering
- **HTTPS Server** - Secure local development with self-signed certificates
- **REST API** - Submit data to server for processing
- **Responsive Design** - Works on all modern devices
- **Debug Mode** - Performance timing diagnostics (use `?debug` query parameter)

## 🚀 Quick Start
### 1. Install Dependencies

```bash
pip install folium
```

or

```bash
apt install python3-folium
```

### 2. Start the Server

```bash
python3 server.py
```

### 3. Open the App

Open your browser and visit:
```
https://localhost:8444
```

**Note:** You'll see a security warning (normal for self-signed certificates). Click "Advanced" and proceed.

### 4. On Mobile

Find your computer's IP address and visit from your phone:
```
https://<your-computer-ip>:8444
```

Example: `https://192.168.1.100:8444`

## 📖 Documentation

- [Server Documentation](README_SERVER.md) - Detailed server setup, API, and troubleshooting
- [Map Generator Documentation](README_MAP.md) - How maps are created and customized

## 🔄 Workflow

1. **Open App** → Browser loads PWA from server
2. **Request Permissions** → Grant location and sensor access
3. **Collect Data** → Click "Collect Data" to capture GPS + inclination
4. **Export or Send** → 
   - Click "Export as CSV" to download locally
   - Click "Send to Server" to upload and generate a map
5. **View Map** → Click "View Map" to see the interactive map in a new tab

### Debug Mode

For performance diagnostics and troubleshooting:
```
https://localhost:8444/measures.html?debug
```

This displays a collapsible debug panel (top-right) showing:
- Geolocation wait time
- LocalStorage save duration
- Table update time
- Total collect cycle time

Panel state is remembered in localStorage.

## 📂 Project Structure

```
coordinates_and_inclination/
├── 📄 measures.html          # PWA application (main UI)
├── 🎨 styles.css              # Application styling
├── 🔧 server.py               # HTTPS server
├── 🗺️  csv_to_map.py          # Map generator script
│
├── 📦 PWA Assets
│   ├── manifest.json          # PWA metadata
│   ├── sw.js                  # Service worker (offline support)
│   └── icon.svg               # App icon
│
├── 📚 Documentation
│   ├── README.md              # This file
│   ├── README_SERVER.md       # Server guide
│   └── README_MAP.md          # Map generator guide
│
├── 🔒 Certificates (auto-generated)
│   ├── cert.pem               # SSL certificate
│   └── key.pem                # Private key
│
└── 📦 Data Storage
    ├── received_data/         # Submitted data
    │   └── data_*.json
    │   └── data_*.csv
    │
    └── created_maps/          # Generated maps
        └── map_*.html
```

## 🛠️ System Requirements

- **Python 3.6+**
- **OpenSSL** (for certificate generation)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Mobile device** with GPS (Android 5+, iOS 13+)

### Required Python Packages

```bash
pip install folium
```

## 💾 Data Storage

### Client-Side
- Collected data is saved to browser's localStorage
- Data persists across page reloads and offline sessions
- Manually clear with the "Clear Data" button

### Server-Side
When you send data to the server, it's stored as:
- **JSON**: `received_data/received_data_<timestamp>.json` (raw submission)
- **CSV**: `received_data/data_<timestamp>.csv` (converted format)
- **HTML Map**: `created_maps/map_<timestamp>.html` (interactive folium map)

## 🗺️ Map Generation

Maps are automatically generated from submitted data using the folium library. Features include:

- **Color-coded markers** by inclination angle
  - 🟢 Green: 0-30° (gentle angle)
  - 🟠 Orange: 30-60° (medium angle)
  - 🔴 Red: 60-90° (steep angle)
  
- **Track line** showing the path of data collection
- **Interactive popups** with detailed information
- **Zoom and pan** controls
- **Layer toggles** for different map types

See [README_MAP.md](README_MAP.md) for more details.

## 🔐 Security Notes

⚠️ **Self-Signed Certificates**: The server uses self-signed SSL certificates suitable for:
- Local development and testing
- Private network use
- Demonstrations

**For production:**
- Use certificates from a Certificate Authority
- Deploy to a hosting service with proper HTTPS
- Implement authentication and rate limiting

See [README_SERVER.md](README_SERVER.md) for more information.

## 🐛 Troubleshooting

### Common Issues

**"Port already in use"**
- Edit `server.py` line 16 to change `PORT` to a different value
- Example: `PORT = 8445`

**"openssl not found"**
- Install OpenSSL:
  - Ubuntu/Debian: `sudo apt-get install openssl`
  - macOS: `brew install openssl`
  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html

**"folium not found"**
- Install folium: `pip install folium`

**GPS not working on mobile**
- Ensure HTTPS is used (not HTTP)
- Grant location permission in browser settings
- Device must have GPS capability

**Map not generating**
- Check server logs for errors
- Verify `folium` is installed
- Ensure CSV data is valid

See [README_SERVER.md](README_SERVER.md) and [README_MAP.md](README_MAP.md) for more troubleshooting.

## 📱 Installing as PWA

### On Android
1. Open the app in Chrome
2. Tap the three-dot menu
3. Select "Install app" or "Add to Home screen"

### On iOS
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"

## 🔗 API Endpoints

### GET `/`
Returns the PWA application

### POST `/data_collector`
Accepts GPS data and generates a map

**Request:**

```json
{
  "timestamp": 1704067200000,
  "data": [
    {
      "index": 1,
      "dateTime": "2024-01-01 12:30:45",
      "latitude": 51.5074,
      "longitude": -0.1278,
      "inclination": 45.5
    }
  ]
}
```

**Response:**

```json
{
  "status": "ok",
  "received": "received/received_data_1704067200.json",
  "map": "/created_maps/map_1704067200.html"
}
```

See [README_SERVER.md](README_SERVER.md) for complete API documentation.

## 📊 Data Format

### CSV Export Format

```
Index,DateTime,Latitude,Longitude,Inclination(degrees)
1,2024-01-01 12:30:45,40.7128,-74.0060,25.5
2,2024-01-01 12:31:02,40.7130,-74.0062,-15.3
3,2024-01-01 12:31:19,40.7132,-74.0064,45.8
```

- **Index**: Sequential entry number
- **DateTime**: Collection time (YYYY-MM-DD HH:MM:SS)
- **Latitude**: Decimal degrees (-90 to 90)
- **Longitude**: Decimal degrees (-180 to 180)
- **Inclination(degrees)**: Tilt angle, positive or negative

## 🚀 Performance

- **Data Collection**: Instant, no network required
- **CSV Export**: Immediate browser download
- **Map Generation**: 1-5 seconds for typical datasets
- **Map Display**: Smooth interaction with 100+ points
- **App Load**: < 1 second on high-speed connection

## 📞 Support

For issues, check the detailed documentation:
- [Server Setup & API](README_SERVER.md)
- [Map Generation](README_MAP.md)

## 📄 License

This project is open source. Feel free to use and modify for your needs.

## 🎯 Use Cases

- **Field Research**: Collect GPS and inclination data in the field
- **Construction**: Track building angles and measurements
- **Geological Surveys**: Log terrain inclination data
- **Mobile Apps**: Test PWA capabilities
- **Education**: Learn about web apps and data visualization
- **Rehabilitation**: Track patient movement and angle data

## 🔮 Future Enhancements

Potential improvements:
- User authentication
- Data synchronization across devices
- Batch data processing
- Advanced analytics and filtering
- Real-time data streaming
- Multiple user support
- Database backend integration
