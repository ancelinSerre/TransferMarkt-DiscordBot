import requests
from bs4 import BeautifulSoup

class PlayerScraper():

    base_url = "https://www.transfermarkt.fr"
    headers = {"User-Agent":"Mozilla/5.0"}

    def __init__(self, player_name):
        self._data = {}
        self.player_page_url = ""
        self._set_player_page_url(player_name)
        result = requests.get(self.player_page_url, headers=self.headers)
        self.player_page = BeautifulSoup(result.content, "html.parser")
        self.get_player_data()

    def _set_player_page_url(self, player_name):
        # Search for player page on TransferMarkt
        search_url = f"{self.base_url}/schnellsuche/ergebnis/schnellsuche?"
        payload = {"query": player_name}
        result = requests.get(search_url, params=payload, headers=self.headers)
        doc = BeautifulSoup(result.content, "html.parser")
        # Find player link to page from search results (pick the first)
        elem = doc.find("a", class_="spielprofil_tooltip")
        # Collect real player name
        self._data["player"] = elem.text
        self.player_page_url = f"{self.base_url}{elem.get('href')}"
        return

    def get_market_value(self):
        mkt_value = ""
        try:
            data = self.player_page.find("div", class_="dataMarktwert").find("a").text.split(" € ")

            mkt_value, currency = data[0].split(" ")
            last_update = data[1]
            # Parse date
            if last_update is not None:
                self.last_update = last_update.split(":")[-1][1:]
            # Parse currency
            if currency is not None:
                currency = " M€" if currency == "mio." else " K€"
            # Set market_value string
            if mkt_value is not None:
                mkt_value += currency
            else:
                mkt_value = "-"

            self._data["market_value"] = mkt_value
        except AttributeError:
            mkt_value = "-"
            self._data["market_value"] = mkt_value

        return

    def get_player_data(self):
        rows = self.player_page.find("table", class_="auflistung").findAll("tr")
        for row in rows:
            column = row.find("th").text.strip().replace(":", "")
            value = row.find("td").text.strip().replace("\xa0", " ")
            self._data[column] = value
        return

    @property
    def data(self):
        if len(self._data) <= 1:
            self.get_player_data()
        return self._data

    @property
    def market_value(self):
        if not self._data or ("market_value" not in self._data):
            self.get_market_value()
        return self._data["market_value"]

if __name__ == "__main__":
    ps = PlayerScraper("Joris Cottin")
    print(ps.data)
    print(ps.market_value)
