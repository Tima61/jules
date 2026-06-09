import requests
from geopy.geocoders import Nominatim
from staticmap import StaticMap, CircleMarker, Line
import os
from bot.config import BASE_COORDS

geolocator = Nominatim(user_agent="b2b_laundry_bot")

def generate_route_map(client_address: str, telegram_id: int) -> tuple[str, float] | None:
    """
    Generates a map image with a route from BASE_COORDS to client_address.
    Returns (map_image_path, distance_in_km) or None if routing fails.
    """
    # 1. Geocode client address
    if "," in client_address and not any(c.isalpha() for c in client_address):
        # It's likely a lat,lon string from Telegram location
        try:
            parts = client_address.split(",")
            client_lat = float(parts[0])
            client_lon = float(parts[1])
        except ValueError:
            return None
    else:
        # It's a text address
        try:
            location = geolocator.geocode(client_address)
            if not location:
                return None
            client_lat = location.latitude
            client_lon = location.longitude
        except Exception:
            return None

    # 2. Get route from OSRM
    # OSRM expects coordinates in lon,lat format
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{BASE_COORDS[1]},{BASE_COORDS[0]};{client_lon},{client_lat}?overview=full&geometries=geojson"
    try:
        response = requests.get(osrm_url)
        data = response.json()
        if data.get("code") != "Ok":
            return None

        route = data["routes"][0]
        distance_km = route["distance"] / 1000.0
        geometry = route["geometry"]["coordinates"]
    except Exception:
        return None

    # 3. Draw map using staticmap
    try:
        m = StaticMap(600, 400, url_template="http://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

        # OSRM geometry is [lon, lat], staticmap also uses [lon, lat] for Line
        line = Line(geometry, 'blue', 3)
        m.add_line(line)

        # Add markers
        start_marker = CircleMarker((BASE_COORDS[1], BASE_COORDS[0]), 'green', 8)
        end_marker = CircleMarker((client_lon, client_lat), 'red', 8)
        m.add_marker(start_marker)
        m.add_marker(end_marker)

        image = m.render()
        os.makedirs("bot/assets/temp", exist_ok=True)
        img_path = f"bot/assets/temp/map_{telegram_id}.png"
        image.save(img_path)

        return img_path, distance_km
    except Exception as e:
        print(f"Map generation error: {e}")
        return None
