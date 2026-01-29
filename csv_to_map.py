#!/usr/bin/env python3
"""
Convert GPS coordinates from CSV export to interactive Google Map
Reads CSV files exported from measures.html and creates a map with inclination data

use it with python 3.12
"""

from datetime import datetime
from pathlib import Path
import csv
import csv
import json
import os
import pathlib
import sys

try:
    import folium
    from folium import plugins
except ImportError:
    print("Error: folium library not found.")
    print("Install it with: pip install folium")
    sys.exit(1)

HTML_FILE_SHOW_MAP = "map.html"
DIR_RECEIVED_FILES = "received_data"
DIR_CREATED_FILES = "created_maps"


def read_csv_file(filepath):
    """
    Read CSV file and return list of data entries
    Expected columns: Index, DateTime, Latitude, Longitude, Inclination(degrees)
    """
    data = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    data.append(
                        {
                            "index": int(row["Index"]),
                            "datetime": row["DateTime"],
                            "latitude": float(row["Latitude"]),
                            "longitude": float(row["Longitude"]),
                            "inclination": float(row["Inclination(degrees)"]),
                        }
                    )
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping row due to invalid data: {e}")
                    continue

        if not data:
            print("Error: No valid data found in CSV file.")
            return None

        return data

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def create_map(data, output_file="gps_map.html"):
    """
    Create an interactive map with GPS coordinates and inclination data
    """
    if not data or len(data) == 0:
        print("Error: No data to plot.")
        return False

    # Calculate center of map (average of all coordinates)
    avg_latitude = sum(d["latitude"] for d in data) / len(data)
    avg_longitude = sum(d["longitude"] for d in data) / len(data)

    # Create map centered at average location
    m = folium.Map(
        location=[avg_latitude, avg_longitude], zoom_start=30, tiles="OpenStreetMap"
    )

    # Use a MarkerCluster with spiderfy enabled so overlapping markers can be expanded
    marker_cluster = plugins.MarkerCluster(
        options={
            "spiderfyOnMaxZoom": True,
            "showCoverageOnHover": False,
            "removeOutsideVisibleBounds": False,
        }
    ).add_to(m)

    # Add markers for each data point into the cluster
    for entry in data:
        latitude = entry["latitude"]
        longitude = entry["longitude"]
        inclination = entry["inclination"]
        index = entry["index"]
        datetime = entry["datetime"]

        # Create popup with detailed information
        # Format inclination as +/- from 0
        inclination_sign = "+" if inclination >= 0 else ""
        popup_text = f"""
        <b>Entry #{index}</b><br>
        <b>DateTime:</b> {datetime}<br>
        <b>Latitude:</b> {latitude:.6f}<br>
        <b>Longitude:</b> {longitude:.6f}<br>
        <b>Inclination:</b> {inclination_sign}{inclination:.2f}°
        """

        # Color code based on inclination angle
        abs_inclination = abs(inclination)
        if abs_inclination < 0.5:
            color = "green"  # Near zero
        elif inclination < -0.5:
            color = "orange"
        else:
            color = "blue"
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"#{index}: {inclination_sign}{inclination:.2f}°",
            icon=folium.Icon(color=color, icon="info-sign"),
            prefix="fa",
        ).add_to(marker_cluster)

    # Add a line connecting all points in order
    coordinates = [[d["latitude"], d["longitude"]] for d in data]
    folium.PolyLine(
        coordinates, color="blue", weight=2, opacity=0.7, popup="GPS Track"
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save map
    try:
        m.save(output_file)

        # Add favicon to generated map
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Add favicon link in the <head> section
            favicon_link = (
                '<link rel="icon" type="image/svg+xml" href="../icon.svg">\n    '
            )
            if "<head>" in html_content and favicon_link not in html_content:
                html_content = html_content.replace(
                    "<head>", "<head>\n    " + favicon_link
                )
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
        except Exception as e:
            print(f"Warning: Could not add favicon to map: {e}")

        print(f"✓ Map created successfully: {output_file}")
        print(f"  Total points: {len(data)}")
        print(f"  Center: ({avg_latitude:.6f}, {avg_longitude:.6f})")
        print(f"  Open {output_file} in your web browser to view the map.")
        return True
    except Exception as e:
        print(f"Error saving map: {e}")
        return False


def convert_json_to_csv(json_file, csv_file):
    print(f"Convertoing Json {{json_file}} to CSV file: {csv_file}")
    try:
        data = json.load(open(json_file, "r", encoding="utf-8"))
        if data:
            with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=[
                        "Index",
                        "DateTime",
                        "Latitude",
                        "Longitude",
                        "Inclination(degrees)",
                    ],
                )
                writer.writeheader()
                for row in data.get("data", []):
                    writer.writerow(
                        {
                            "Index": row.get("index", ""),
                            "DateTime": row.get("dateTime", ""),
                            "Latitude": row.get("latitude", ""),
                            "Longitude": row.get("longitude", ""),
                            "Inclination(degrees)": row.get("inclination", ""),
                        }
                    )
            print(f"Generated CSV: {csv_file}")

    except Exception as e:
        print(f"Error converting json to csv: {e}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        # Try to find the most recent CSV file
        csv_files = list(Path(".").glob("collected_data_*.csv"))
        if csv_files:
            in_file = sorted(csv_files, reverse=True)[0]
            print(f"No file specified. Using most recent: {in_file}")
        else:
            print("Usage: python3 csv_to_map.py <csv_file> [output_file.html]")
            print("\nExample:")
            print("  python3 csv_to_map.py collected_data_1234567890.csv")
            print("  python3 csv_to_map.py collected_data_1234567890.csv my_map.html")
            print(
                "\nThe script reads CSV files exported from measures.html and creates"
            )
            print("an interactive map showing GPS coordinates with inclination data.")
            sys.exit(1)
    else:
        in_file = sys.argv[1]

    # Get output file name
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = os.path.join(DIR_CREATED_FILES, "gps_map.html")

    if pathlib.Path(in_file).suffix.lower() == ".json":
        json_file = in_file
        csv_file = os.path.splitext(in_file)[0] + ".csv"
        index = 0
        while pathlib.Path(csv_file).exists():
            if index == 0:
                csv_file = f"{os.path.splitext(csv_file)[0]}_{index:03d}.csv"
            else:
                csv_file = f"{os.path.splitext(csv_file)[0][:-4]}_{index:03d}.csv"
            index += 1
        convert_json_to_csv(json_file, csv_file)

    print(f"Reading CSV file: {csv_file}")

    # Read CSV file
    data = read_csv_file(csv_file)
    if data is None:
        sys.exit(1)

    print(f"Loaded {len(data)} data entries.")

    # Create map
    if create_map(data, output_file):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
