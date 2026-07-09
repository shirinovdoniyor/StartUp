import requests
import requests


def get_coordinates(address):
    """
    Address -> (latitude, longitude)
    OpenStreetMap Nominatim orqali.
    """

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "ServisProject/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None, None

    return (
        float(data[0]["lat"]),
        float(data[0]["lon"]),
    )