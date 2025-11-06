import requests
# application/user_handler.py, ta user by ip koppla till din UUID returnera elområde crosscheck elpris i generella området. 
def get_location_and_elarea(user_ip=None):
    """ Get geolocation and electricity area based on IP address."""

    url = f"https://ipwho.is/{user_ip}" if user_ip else "https://ipwho.is/"
    resp = requests.get(url)
    data = resp.json()

    if not data.get("success"):
        raise ValueError(f"Lookup failed: {data.get('message')}")

    lat, lon = data["latitude"], data["longitude"]

    if lat >= 64.5:
        elarea = "SE1"
    elif lat >= 62:
        elarea = "SE2"
    elif lat >= 57:
        elarea = "SE3"
    else:
        elarea = "SE4"

    return {
        "ip": data["ip"],
        "country": data["country"],
        "city": data["city"],
        "latitude": lat,
        "longitude": lon,
        "elarea": elarea
    }

