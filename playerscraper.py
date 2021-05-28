import locale
from datetime import datetime

import requests
from lxml import etree, html

class PlayerScraper():

    base_url = "https://www.transfermarkt.fr"
    headers = {"User-Agent":"Mozilla/5.0"}

    def __init__(self, player_name):
        # Set locale to parse date
        locale.setlocale(category=locale.LC_ALL, locale="French")
        self._data = {}
        self.player_page_url = ""
        self._set_player_page_url(player_name)
        result = requests.get(self.player_page_url, headers=self.headers)
        self.player_page = etree.ElementTree(html.fromstring(result.content))
        self.get_player_data()

    def _set_player_page_url(self, player_name):
        # Search for player page on TransferMarkt
        search_url = f"{self.base_url}/schnellsuche/ergebnis/schnellsuche?"
        payload = {"query": player_name}
        result = requests.get(search_url, params=payload, headers=self.headers)
        doc = etree.ElementTree(html.fromstring(result.content))
        # Find player link to page from search results (pick the first)
        elem = doc.xpath("//a[@class='spielprofil_tooltip']")[0]
        # Collect real player name
        self._data["player"] = elem.text
        self.player_page_url = f"{self.base_url}{elem.get('href')}"
        return

    def get_market_value(self):
        mkt_value = self.player_page.xpath("//div[@class='dataMarktwert']/a/text()")[0]
        currency = self.player_page.xpath("//div[@class='dataMarktwert']/a/span[@class='waehrung']/text()")[0]
        last_update = self.player_page.xpath("//div[@class='dataMarktwert']/a/p/text()")[0]
        # Parse date
        if last_update is not None:
            try:
                self.last_update = datetime.strptime(last_update.split(":")[-1][1:], "%d %B %Y").date()
            except:
                self.last_update = datetime.strptime(last_update.split(":")[-1][1:], "%d %b %Y").date()
        # Parse currency
        if currency is not None:
            currency = "M€" if currency == "mio. €" else "K€"
        # Set market_value string
        if mkt_value is not None:
            mkt_value += currency
        else:
            mkt_value = "Not found"

        self._data["market_value"] = mkt_value
        return

    def get_player_data(self):
        table = self.player_page.xpath("//table[@class='auflistung']")[0]
        rows = iter(table)
        for row in rows:
            column = row.xpath("th/text()")[0].strip().replace(":", "")
            value = row.xpath("td/*/text()")

            if not value:
                value = " ".join(row.xpath("td/text()"))
            else:
                value = " ".join(value)

            value = value.strip().replace("\xa0", "")
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
    ps = PlayerScraper("olivier giroud")
    print(ps.data)
    print(ps.market_value)
