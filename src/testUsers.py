import requests
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8890/api/auth/test-user"  # change if needed

BASE_LAT = 25.3467  # Bhilwara latitude
BASE_LON = 74.6400  # Bhilwara longitude

def random_location_near_bhilwara(radius_km=100):
    # Roughly 1° lat ≈ 111 km
    delta_lat = random.uniform(-radius_km / 111, radius_km / 111)
    delta_lon = random.uniform(-radius_km / 111, radius_km / 111)
    return round(BASE_LAT + delta_lat, 6), round(BASE_LON + delta_lon, 6)

for i in range(20):
    phone = f"+919999000{100+i}"
    lat, lon = random_location_near_bhilwara()

    payload = {
        "phone": phone,
        "profile": {
            "name": f"TestUser{i+1}",
            "dob": "1995-01-01",
            "gender": "Other",
            "about": f"Auto-generated user {i+1}",
            "photo_url": f"https://example.com/user{i+1}.jpg",
            "location": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        }
    }

    response = requests.post(API_URL, json=payload)
    print(f"[{i+1}/20] {phone} --> {response.status_code}: {response.json()}")