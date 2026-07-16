"""Address geocoding via OpenStreetMap Nominatim."""

import requests


def get_coordinates(address: str):
    """Resolve an address to (latitude, longitude) or (None, None)."""
    if not address:
        return None, None

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "AutoServiceMarketplace/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None, None

    data = response.json()
    if not data:
        return None, None
    return float(data[0]["lat"]), float(data[0]["lon"])
