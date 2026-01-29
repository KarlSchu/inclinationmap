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
import math
import argparse

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


def create_map(data, output_file="gps_map.html", mode="cluster", base_offset=0.00001):
    """
    Create an interactive map with GPS coordinates and inclination data
    mode: "spread" or "cluster"
    base_offset: offset in degrees for spreading markers when in "spread" mode
    0.00001 degrees is approx 1.1 meters
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

    # Choose behavior: clustered or spread
    if mode == "cluster":
        marker_cluster = plugins.MarkerCluster(
            options={
                "spiderfyOnMaxZoom": True,
                "showCoverageOnHover": False,
                "removeOutsideVisibleBounds": False,
            }
        ).add_to(m)

        for entry in data:
            latitude = entry["latitude"]
            longitude = entry["longitude"]
            inclination = entry["inclination"]
            index = entry["index"]
            datetime = entry["datetime"]

            inclination_sign = "+" if inclination >= 0 else ""
            popup_text = f"""
            <b>Entry #{index}</b><br>
            <b>DateTime:</b> {datetime}<br>
            <b>Latitude:</b> {latitude:.6f}<br>
            <b>Longitude:</b> {longitude:.6f}<br>
            <b>Inclination:</b> {inclination_sign}{inclination:.2f}°
            """

            abs_inclination = abs(inclination)
            if abs_inclination < 0.5:
                color = "green"
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
    else:
        # Spread markers that are very close to each other by applying
        # a small deterministic offset so points remain individually clickable
        groups = {}
        for entry in data:
            key = (round(entry["latitude"], 5), round(entry["longitude"], 5))
            groups.setdefault(key, []).append(entry)

        for key, entries in groups.items():
            n = len(entries)
            for i, entry in enumerate(entries):
                orig_lat = entry["latitude"]
                orig_lon = entry["longitude"]
                latitude = orig_lat
                longitude = orig_lon

                if n > 1:
                    angle = 2 * math.pi * i / n
                    radius = base_offset * (1 + (i // 8))
                    latitude = orig_lat + math.cos(angle) * radius
                    longitude = orig_lon + math.sin(angle) * radius

                inclination = entry["inclination"]
                index = entry["index"]
                datetime = entry["datetime"]

                inclination_sign = "+" if inclination >= 0 else ""
                popup_text = f"""
                <b>Entry #{index}</b><br>
                <b>DateTime:</b> {datetime}<br>
                <b>Latitude:</b> {orig_lat:.6f}<br>
                <b>Longitude:</b> {orig_lon:.6f}<br>
                <b>Inclination:</b> {inclination_sign}{inclination:.2f}°
                """

                abs_inclination = abs(inclination)
                if abs_inclination < 0.5:
                    color = "green"
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
                ).add_to(m)

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
    parser = argparse.ArgumentParser(description="Convert CSV/JSON data to an interactive map")
    parser.add_argument("in_file", nargs="?", help="Input CSV or JSON file (if omitted, uses latest collected_data_*.csv)")
    parser.add_argument("output_file", nargs="?", help="Output HTML file (default: created_maps/gps_map.html)")
    parser.add_argument("--mode", choices=["spread", "cluster"], default="spread", help="Display mode for markers: spread or cluster (default: spread)")
    parser.add_argument("--offset", type=float, default=0.00002, help="Base offset in degrees when using spread mode (default: 0.00002)")
    args = parser.parse_args()

    in_file = args.in_file
    if not in_file:
        csv_files = list(Path(".").glob("collected_data_*.csv"))
        if csv_files:
            in_file = sorted(csv_files, reverse=True)[0]
            print(f"No file specified. Using most recent: {in_file}")
        else:
            parser.print_help()
            sys.exit(1)

    output_file = args.output_file if args.output_file else os.path.join(DIR_CREATED_FILES, "gps_map.html")

    # If input is JSON, convert to CSV first
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
    else:
        csv_file = in_file

    print(f"Reading CSV file: {csv_file}")

    # Read CSV file
    data = read_csv_file(csv_file)
    if data is None:
        sys.exit(1)

    print(f"Loaded {len(data)} data entries.")

    # Create map with chosen mode and offset
    if create_map(data, output_file, mode=args.mode, base_offset=args.offset):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
