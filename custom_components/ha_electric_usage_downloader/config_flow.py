from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

# Import constants or placeholders for login and usage URLs
DEFAULT_LOGIN_URL = "https://pec.smarthub.coop/Login.html"
DEFAULT_USAGE_URL = "https://pec.smarthub.coop/Usage/Usage.htm"

class ElectricUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Electric Usage Downloader."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Perform any validation if necessary
            return self.async_create_entry(title="Electric Usage Downloader", data=user_input)

        # Show the form to the user to input credentials and URLs
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("login_url", default=DEFAULT_LOGIN_URL): str,
                vol.Required("usage_url", default=DEFAULT_USAGE_URL): str,
            }),
            errors=errors,
        )
