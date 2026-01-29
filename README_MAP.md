# CSV to Map Converter

Convert GPS coordinates from CSV exports to interactive maps with inclination data visualization.

## Overview

This tool reads GPS data from CSV files (exported from the .html app) and generates beautiful, interactive maps using the Folium library. Maps can be viewed in any web browser and shared easily.

## Requirements

- Python 3.6+
- folium library

## Installation

### Install folium library

```bash
pip install folium
```

Or for a specific environment:

```bash
pip install --user folium
```

## Usage

### Basic Usage

```bash
python3 csv_to_map.py collected_data_1234567890.csv
```

This will create `gps_map.html` in the current directory.

### Specify Custom Output File

```bash
python3 csv_to_map.py collected_data_1234567890.csv my_custom_map.html
```

### With Full Paths

```bash
python3 csv_to_map.py /path/to/collected_data.csv /path/to/output_map.html
```

## Features

✅ **Interactive Map** - Zoom, pan, and explore your GPS data  
✅ **Color-Coded Markers** - Inclination angle visualized by marker color:
   - 🟢 **Green**: Low inclination (0-30°)
   - 🟠 **Orange**: Medium inclination (30-60°)
   - 🔴 **Red**: High inclination (60-90°)
   - 🟣 **Purple**: Steep/vertical (90°+)

✅ **Detailed Popups** - Click any marker to see:
   - Entry number (index)
   - Date and time
   - Exact coordinates (latitude, longitude)
   - Inclination angle with +/- sign

✅ **Track Line** - Blue line connecting all points in the order they were collected  
✅ **Tooltips** - Hover over markers to see quick information  
✅ **Responsive Design** - Works on desktop, tablet, and mobile browsers  
✅ **Layer Control** - Toggle map layers on/off for better visibility  

## Expected CSV Format

The CSV file must contain these columns (case-sensitive):

```
Index,DateTime,Latitude,Longitude,Inclination(degrees)
1,2024-01-01 12:30:45,51.5074,-0.1278,45.5
2,2024-01-01 12:31:02,51.5075,-0.1280,-12.3
...
```

- **Index**: Entry number (integer)
- **DateTime**: Date and time in format `YYYY-MM-DD HH:MM:SS`
- **Latitude**: Decimal degrees (-90 to 90)
- **Longitude**: Decimal degrees (-180 to 180)
- **Inclination(degrees)**: Angle in degrees, can be negative or positive

## Output

The script generates an interactive HTML map file that can be:
- Opened in any web browser (no server required)
- Shared with others via email or cloud storage
- Embedded in websites
- Downloaded for offline use
- Saved locally for future reference

## Workflow: Web App Integration

The typical workflow when using the web server is:

1. **Open PWA app** → `https://localhost:8444`
2. **Collect data** → GPS + inclination measurements
3. **Send to Server** → Click "Send to Server" button
4. **Server generates map** → Automatic via `csv_to_map.py`
5. **View map** → Click "View Map" button in the app

### Manual Workflow

If you prefer to generate maps manually:

1. **Export data** from measures.html as CSV
2. **Run the converter:**
   ```bash
   python3 csv_to_map.py collected_data_1704067200.csv
   ```
3. **Open the map:**
   - Open `gps_map.html` in your web browser
   - Or double-click the file in file explorer

## Example

### Sample CSV Input

```csv
Index,DateTime,Latitude,Longitude,Inclination(degrees)
1,2024-01-01 12:30:45,40.7128,-74.0060,25.5
2,2024-01-01 12:31:02,40.7130,-74.0062,-15.3
3,2024-01-01 12:31:19,40.7132,-74.0064,45.8
```

### Generate Map

```bash
python3 csv_to_map.py sample_data.csv sample_map.html
```

### View Map

Open `sample_map.html` in any web browser. You'll see:
- Three colored markers showing the three GPS points
- A blue line connecting them in order
- Popups showing details for each point
- Interactive zoom and pan controls

## Troubleshooting

### "ModuleNotFoundError: No module named 'folium'"

Install folium:
```bash
pip install folium
```

If that fails, try:
```bash
pip3 install folium
```

### "No such file or directory"

Make sure the CSV file exists in the specified location. Use the full path if the file is in a different directory:

```bash
python3 csv_to_map.py /full/path/to/collected_data.csv
```

### CSV has invalid data

The script will skip rows with invalid data and show a warning. Common issues:
- Non-numeric latitude/longitude
- Invalid datetime format (must be `YYYY-MM-DD HH:MM:SS`)
- Missing columns

Check your CSV file and ensure all rows have valid data.

### Map not showing markers

Verify your CSV file:
- Has the correct column names (case-sensitive)
- Contains valid latitude/longitude values
- Has at least one valid data row

### Map file is very large

This is normal for maps with many markers. The HTML file includes the entire map library and all data. Typical files:
- 10 points: ~500 KB
- 100 points: ~600 KB
- 1000 points: ~1-2 MB

## Performance

- Small datasets (< 100 points): Instant generation and loading
- Medium datasets (100-1000 points): 1-5 seconds generation, smooth browsing
- Large datasets (> 1000 points): May take 10+ seconds and require more browser memory

## Tips for Better Maps

1. **Collect multiple points** - More data points create a more detailed track
2. **Vary your inclination** - Collect data at different angles for better visualization
3. **Include timestamps** - The datetime helps understand the data collection sequence
4. **Verify location permissions** - Ensure GPS has a good signal for accurate coordinates

## Future Enhancements

Possible improvements to the map generator:
- Heatmap visualization of inclination values
- Statistics panel showing min/max/average inclination
- Filtering by date range or inclination angle
- Export data in other formats (GeoJSON, GPX)
- 3D visualization of inclination changes

### Map shows wrong location

This can happen if:
- GPS data is inaccurate
- Only 1-2 data points were collected
- Try collecting more data points for better accuracy

## Map Layers

The generated map includes:
- **OpenStreetMap** - Default base layer
- **Markers** - GPS coordinates with inclination data
- **Track line** - Path connecting all points
- **Layer Control** - Toggle visibility of different elements

## Inclination Color Coding

| Color | Inclination Range | Meaning |
|-------|------------------|---------|
| 🟢 Green | 0° - 30° | Low inclination (nearly horizontal) |
| 🟠 Orange | 30° - 60° | Medium inclination |
| 🔴 Red | 60° - 90° | High inclination (nearly vertical) |

## CSV Format Expected

The script expects CSV files exported from measures.html with these columns:
```
Index,DateTime,Latitude,Longitude,Inclination(degrees)
1,1/28/2026 11:45:30 PM,40.712776,-74.005974,25.50
2,1/28/2026 11:45:45 PM,40.712800,-74.005990,26.75
...
```

## Notes

- The map automatically centers on the average of all coordinates
- Initial zoom level is set to 15 (street level)
- The HTML file is self-contained and doesn't require internet for basic functionality
- Marker popups show data to 6 decimal places for latitude/longitude
- Inclination values shown to 2 decimal places

## See Also

- measures.html - The GPS data collection app
- server.py - HTTPS server to run the app
- README_SERVER.md - Server documentation
