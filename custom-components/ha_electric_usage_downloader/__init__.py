import logging
import aiohttp
from bs4 import BeautifulSoup
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ha-electric-usage-downloader from a config entry."""

    # Get credentials and URLs from config entry
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    login_url = entry.data["login_url"]
    usage_url = entry.data["usage_url"]

    session = async_get_clientsession(hass)  # Get aiohttp session from Home Assistant
    api = ElectricUsageAPI(session, username, password, login_url, usage_url)

    # Create and set up the data coordinator
    coordinator = ElectricUsageCoordinator(hass, api)
    await coordinator.async_refresh()  # Perform an initial fetch of data

    # Store the coordinator in Home Assistant's global data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the platform (e.g., sensors)
    hass.config_entries.async_setup_platforms(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ha-electric-usage-downloader."""
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.api.session.close()  # Clean up the session

    # Unload the sensor platform
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

class ElectricUsageAPI:
    """Class to handle communication with the PEC SmartHub portal."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str, login_url: str, usage_url: str):
        """Initialize the API client."""
        self.session = session
        self.username = username
        self.password = password
        self.login_url = login_url
        self.usage_url = usage_url
        self.cookies = None  # Store cookies after login

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
                self.cookies = response.cookies  # Store cookies for authenticated requests
            else:
                _LOGGER.error("Failed to log in to PEC SmartHub: %s", response.status)
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

            # Parse the HTML response
            html_content = await response.text()
            soup = BeautifulSoup(html_content, "html.parser")

            # Use the working version from the repo to parse the usage data
            usage_data = self._parse_usage_data(soup)
            return usage_data

    def _parse_usage_data(self, soup):
        """Parse the electric usage data from the HTML soup."""
        # Reuse the parsing logic from the original repo
        usage_value = soup.find("td", class_="highcharts-tooltip").get_text()  # Modify based on actual HTML
        return {"usage": float(usage_value)}

class ElectricUsageCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching electric usage data from the PEC SmartHub API."""

    def __init__(self, hass: HomeAssistant, api: ElectricUsageAPI):
        """Initialize the coordinator."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name="Electric Usage Coordinator",
            update_interval=SCAN_INTERVAL
        )

    async def _async_update_data(self):
        """Fetch data from the PEC SmartHub API."""
        # Log in to the API before fetching data
        await self.api.login()
        # Fetch the electric usage data
        data = await self.api.get_usage_data()
        return data
