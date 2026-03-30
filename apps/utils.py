import requests

def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json"
    }

    headers = {
        "User-Agent": "startup-app"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return None, None

    try:
        data = response.json()
    except:
        return None, None

    if data:
        return float(data[0]['lat']), float(data[0]['lon'])

    return None, None