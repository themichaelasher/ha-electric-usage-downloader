import aiohttp
from bs4 import BeautifulSoup
import logging

_LOGGER = logging.getLogger(__name__)

class ElectricUsageAPI:
    """Handles communication with the PEC SmartHub portal."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str, login_url: str, usage_url: str):
        """Initialize the API client."""
        self.session = session
        self.username = username
        self.password = password
        self.login_url = login_url
        self.usage_url = usage_url
        self.cookies = None

    async def login(self):
        """Log in to the PEC SmartHub and retrieve session cookies."""
        payload = {
            "UserName": self.username,
            "Password": self.password
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        async with self.session.post(self.login_url, data=payload, headers=headers) as response:
            if response.status == 200:
                _LOGGER.debug("Successfully logged in to PEC SmartHub")
                self.cookies = response.cookies
            else:
                _LOGGER.error(f"Failed to log in to PEC SmartHub: {response.status}")
                raise Exception("Login failed")

    async def get_usage_data(self):
        """Fetch electric usage data by scraping the PEC SmartHub portal."""
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        async with self.session.get(self.usage_url, cookies=self.cookies, headers=headers) as response:
            if response.status != 200:
                _LOGGER.error(f"Failed to fetch usage data: {response.status}")
                return None

            html_content = await response.text()
            soup = BeautifulSoup(html_content, "html.parser")

            # Parse the usage data
            usage_data = self._parse_usage_data(soup)
            return usage_data

    def _parse_usage_data(self, soup):
        """Parse the electric usage data from the HTML soup."""
        usage_value = soup.find("td", class_="highcharts-tooltip").get_text()
        return {"usage": float(usage_value)}
