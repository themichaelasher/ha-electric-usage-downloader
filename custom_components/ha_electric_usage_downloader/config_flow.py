import logging
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

# Setup logging
_LOGGER = logging.getLogger(__name__)

# Default URLs for login and usage
DEFAULT_LOGIN_URL = "https://pec.smarthub.coop/Login.html"
DEFAULT_USAGE_URL = "https://pec.smarthub.coop/Usage/Usage.htm"

class ElectricUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Electric Usage Downloader."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step of user input."""
        errors = {}

        if user_input is not None:
            # Validate user input if necessary, you can add more checks here
            if not user_input["username"] or not user_input["password"]:
                errors["base"] = "invalid_credentials"
                _LOGGER.error("Invalid credentials provided.")

            if not errors:
                # If no errors, create the config entry
                _LOGGER.info("Creating config entry for Electric Usage Downloader.")
                return self.async_create_entry(title="Electric Usage Downloader", data=user_input)

        # If there were errors or this is the first time, show the form again
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
