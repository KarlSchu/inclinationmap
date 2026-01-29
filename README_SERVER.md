# GPS & Phone Inclination Logger - HTTPS Server

## Overview

A full-featured HTTPS web server that delivers the GPS & Phone Inclination Logger as a Progressive Web App (PWA). The server:

- Serves the PWA with offline support via service worker
- Collects GPS coordinates and phone inclination data
- Generates interactive maps from collected data
- Stores received data as JSON and CSV files
- Supports multiple requests with automatic map generation

## Features

✅ **Progressive Web App (PWA)** - Installable on mobile devices  
✅ **Offline Support** - App works without internet connection  
✅ **HTTPS with Self-Signed Certificates** - Secure local development  
✅ **REST API** - `/data_collector` endpoint for data submission  
✅ **Automatic Map Generation** - Creates interactive maps from received data  
✅ **CORS Support** - Cross-origin requests enabled  
✅ **Smart Caching** - Long-term cache for static assets, fresh content for HTML  

## Requirements

- Python 3.6+
- OpenSSL (for certificate generation)
- folium (for map generation): `pip install folium`
- Linux, macOS, or Windows

## Installation

### Install Python dependencies

```bash
pip install folium
```

### Install OpenSSL (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openssl
```

**macOS:**
```bash
brew install openssl
```

**Windows:**
Download from https://slproweb.com/products/Win32OpenSSL.html or use Chocolatey:
```bash
choco install openssl
```

## Running the Server

### Start the Server

```bash
python3 server.py
```

The server will:
1. Generate or load SSL certificates (stored as `cert.pem` and `key.pem`)
2. Start listening on `https://localhost:8444`
3. Serve the PWA application
4. Accept data submissions at `/data_collector`

### Output Example

```
============================================================
HTTPS Web Server Started
============================================================
📁 Serving: measures.html
🔒 Server: https://localhost:8444
📱 Mobile: https://<your-ip>:8444
🔐 Certificate: cert.pem

✓ Server running. Press Ctrl+C to stop.
============================================================
```

## Accessing the App

### Desktop Browser

1. Open: `https://localhost:8444` (or `https://localhost:8444/measures.html`)
2. Accept the security warning (normal for self-signed certificates)
3. Click "Advanced" → "Proceed to localhost"

### Mobile Device (Android/iOS)

1. Find your computer's local IP:
   - Linux/macOS: `ifconfig | grep inet`
   - Windows: `ipconfig`

2. Open browser and visit:
   - `https://<your-computer-ip>:8444`
   - Example: `https://192.168.1.100:8444`

3. Accept security warning

4. Grant location and device orientation permissions when prompted

5. On iOS/Android, use the browser's "Add to Home Screen" option to install as PWA

## API Endpoints

### GET `/`
Serves the main PWA application (`measures.html`)

### GET `/measures.html`, `/manifest.json`, `/sw.js`, `/styles.css`, `/icon.svg`
Serves PWA assets with long-term caching

### GET `/created_maps/map_*.html`
Serves generated interactive maps

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

The server will:
1. Save the JSON data to `received/received_data_<timestamp>.json`
2. Convert to CSV at `received/received_data_<timestamp>.csv`
3. Generate an interactive map at `created_maps/map_<timestamp>.html`
4. Return the map URL to the client

## File Structure

```
coordinates_and_inclination/
├── server.py                  # HTTPS server (main)
├── measures.html             # PWA application
├── styles.css                 # Application styles
├── manifest.json              # PWA manifest
├── sw.js                      # Service worker for offline support
├── icon.svg                   # App icon
├── csv_to_map.py             # Map generator script
├── cert.pem                   # Generated SSL certificate
├── key.pem                    # Generated SSL private key
├── received/                  # Received data storage
│   ├── received_data_*.json   # Raw JSON submissions
│   └── received_data_*.csv    # Converted CSV files
├── created_maps/              # Generated maps
│   └── map_*.html            # Interactive folium maps
└── README files               # Documentation
```

## Workflow

1. **User opens app** → Browser loads PWA from server
2. **User collects data** → GPS coordinates and inclination measured locally
3. **User clicks "Send to Server"** → Data POSTed to `/data_collector`
4. **Server processes** → Data saved as JSON/CSV, map generated
5. **User clicks "View Map"** → Opens interactive map in new tab

## Security Notes

⚠️ **Important:** This server uses a self-signed certificate. It is suitable for:
- Local development and testing
- Testing on private networks
- Demonstration purposes

**For production use:**
- Use a proper SSL certificate from a Certificate Authority
- Deploy to a hosting service with built-in HTTPS support
- Implement authentication and rate limiting
- Validate and sanitize all incoming data

## Troubleshooting

### "Port already in use" error

Edit `server.py` and change the `PORT` variable (line 16), then restart.

### "Permission denied" on port 8444

Use a port above 1024. Edit `server.py` to use a different port.

### "openssl not found"

Install OpenSSL (see Installation section above).

### Certificate warning in browser

This is **expected** with self-signed certificates. Click "Advanced" and proceed.

### Map not generating

1. Ensure `folium` is installed: `pip install folium`
2. Check server logs for CSV conversion errors
3. Verify `csv_to_map.py` is in the same directory

### CORS errors when accessing from mobile

CORS headers are already configured in the server. If issues persist, verify the server is accessible at the correct IP and port.

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.
- The connection is still encrypted
- Accept the certificate to proceed

## File Structure

```
coordinates_and_inclination/
├── measures.html          # Main app (served by server)
├── server.py              # HTTPS server script
├── run_server.sh          # Bash startup script
├── cert.pem               # SSL certificate (auto-generated)
├── key.pem                # SSL private key (auto-generated)
└── README_SERVER.md       # This file
```

## Features

- ✅ Self-signed HTTPS certificate (auto-generated)
- ✅ Works with Android Chrome
- ✅ CORS headers enabled
- ✅ No external dependencies (uses Python standard library)
- ✅ Easy to use
- ✅ Suitable for development and testing

## Next Steps

1. Run the server: `python3 server.py`
2. Open in browser: `https://localhost:8443`
3. Grant permissions when prompted
4. Start collecting GPS and inclination data

Enjoy! 🎉
