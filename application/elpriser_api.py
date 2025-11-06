import requests
from datetime import datetime

class ElpriserAPI:
    BASE_URL = "https://www.elprisetjustnu.se/api/v1/prices"

    def __init__(self, year=None, month=None, day=None, prisklass="SE3"):
        """
        Initialiserar API-klassen med datum och prisområde.
        Om inget datum anges används dagens datum.
        Prisområden: SE1, SE2, SE3, SE4
        """
        today = datetime.today()

        def _to_int(val, default):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        y = _to_int(year, today.year)
        m = _to_int(month, today.month)
        d = _to_int(day, today.day)

        # store as strings formatted for the API path
        self.year = str(y)
        self.month = f"{m:02d}"
        self.day = f"{d:02d}"
        self.prisklass = prisklass.upper()
        if self.prisklass not in ["SE1", "SE2", "SE3", "SE4"]:
            raise ValueError("Ogiltig prisklass. Välj SE1, SE2, SE3 eller SE4.")

    def get_url(self):
        """Bygger URL för API-anrop"""
        return f"{self.BASE_URL}/{self.year}/{self.month}-{self.day}_{self.prisklass}.json"

    def fetch_prices(self):
        """Hämtar elpriser från API och returnerar som JSON"""
        url = self.get_url()
        try:
            response = requests.get(url)
            response.raise_for_status()  # ger ett fel om status != 200
            return response.json()
        except requests.RequestException as e:
            print(f"Fel vid hämtning av data: {e}")
            return None

# --- Exempel på användning ---
if __name__ == "__main__":
    api = ElpriserAPI(year=2025, month=10, day=27, prisklass="SE3")
    priser = api.fetch_prices()
    if priser:
        print(priser)