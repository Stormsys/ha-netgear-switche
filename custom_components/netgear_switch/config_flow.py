"""Config flow for Netgear Managed Switch integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD

from .const import DEFAULT_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


def _try_connect(host: str, password: str) -> dict[str, Any]:
    """Try to connect to the switch and return info.

    This runs in the executor since py-netgear-plus uses blocking I/O.
    Returns dict with model_name and unique_id on success.
    Raises CannotConnect or InvalidAuth on failure.
    """
    from py_netgear_plus import (
        LoginFailedError,
        NetgearSwitchConnector,
        PageFetcherConnectionError,
        SwitchModelNotDetectedError,
    )

    _LOGGER.debug("Attempting to connect to switch at %s", host)

    try:
        api = NetgearSwitchConnector(host=host, password=password)
    except Exception:
        _LOGGER.exception("Failed to create connector for %s", host)
        raise CannotConnect

    try:
        detected_model = api.autodetect_model()
        _LOGGER.debug(
            "Detected model: %s (%d ports)",
            detected_model.MODEL_NAME,
            api.ports,
        )
    except SwitchModelNotDetectedError:
        _LOGGER.error("Could not detect switch model at %s", host)
        raise CannotConnect
    except PageFetcherConnectionError:
        _LOGGER.error("Connection failed to %s", host)
        raise CannotConnect
    except Exception:
        _LOGGER.exception("Unexpected error detecting model at %s", host)
        raise CannotConnect

    # Attempt login, retrying once with a fresh login page on soft failure.
    # A retry helps when the cached login page has a stale 'rand' token or
    # when a concurrent session (e.g. the switch web UI) caused rejection.
    login_ok = False
    for attempt in range(2):
        try:
            login_ok = api.get_login_cookie()
            _LOGGER.debug(
                "Login result for %s (attempt %d): %s", host, attempt + 1, login_ok
            )
        except LoginFailedError as err:
            _LOGGER.error("Login rejected by %s: %s", host, err)
            raise InvalidAuth
        except PageFetcherConnectionError:
            _LOGGER.error("Connection lost during login to %s", host)
            raise CannotConnect
        except Exception:
            _LOGGER.exception("Unexpected error during login to %s", host)
            raise CannotConnect

        if login_ok:
            break

        if attempt == 0:
            _LOGGER.debug(
                "Login failed for %s, retrying with fresh login page", host
            )

    if not login_ok:
        _LOGGER.error(
            "Login failed for %s (check password — avoid non-ASCII special "
            "characters if possible)",
            host,
        )
        raise InvalidAuth

    unique_id = api.get_unique_id()
    model_name = api.switch_model.MODEL_NAME

    # Clean up the session
    try:
        api.delete_login_cookie()
    except Exception:
        _LOGGER.debug("Failed to logout during config flow, ignoring")

    return {
        "unique_id": unique_id,
        "model_name": model_name,
    }


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""


class NetgearSwitchConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Netgear Managed Switch."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await self.hass.async_add_executor_job(
                    _try_connect,
                    user_input[CONF_HOST],
                    user_input[CONF_PASSWORD],
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception in config flow")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                title = f"{info['model_name']} ({user_input[CONF_HOST]})"
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
