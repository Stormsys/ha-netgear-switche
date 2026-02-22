"""The Netgear Managed Switch integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, TypeAlias

from py_netgear_plus import (
    LoginFailedError,
    NetgearSwitchConnector,
    NotLoggedInError,
    PageFetcherConnectionError,
    SwitchModelNotDetectedError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, MANUFACTURER, PLATFORMS
from .coordinator import NetgearSwitchCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class NetgearSwitchData:
    """Runtime data for a Netgear switch config entry."""

    api: NetgearSwitchConnector
    coordinator: NetgearSwitchCoordinator


NetgearSwitchConfigEntry: TypeAlias = ConfigEntry[NetgearSwitchData]


async def async_setup_entry(
    hass: HomeAssistant, entry: NetgearSwitchConfigEntry
) -> bool:
    """Set up Netgear Managed Switch from a config entry."""
    host = entry.data[CONF_HOST]
    password = entry.data[CONF_PASSWORD]

    api = NetgearSwitchConnector(host=host, password=password)

    # Detect model (blocking I/O)
    try:
        await hass.async_add_executor_job(api.autodetect_model)
    except (SwitchModelNotDetectedError, PageFetcherConnectionError) as err:
        raise ConfigEntryNotReady(
            f"Cannot connect to switch at {host}: {err}"
        ) from err

    _LOGGER.debug(
        "Detected %s with %d ports at %s",
        api.switch_model.MODEL_NAME,
        api.ports,
        host,
    )

    # Authenticate (blocking I/O).
    # Retry once with a fresh login page if the first attempt fails, because
    # the cached page from autodetect_model() may carry a stale 'rand' CSRF
    # token (e.g. another session loaded the switch UI in the meantime).
    logged_in = False
    for attempt in range(2):
        try:
            logged_in = await hass.async_add_executor_job(api.get_login_cookie)
        except PageFetcherConnectionError as err:
            raise ConfigEntryNotReady(
                f"Connection failed during login to {host}: {err}"
            ) from err
        except (LoginFailedError, NotLoggedInError) as err:
            if attempt == 0:
                _LOGGER.debug(
                    "Login attempt 1 failed for %s, retrying with fresh page",
                    host,
                )
                try:
                    api._page_fetcher.clear_login_page_response()
                except AttributeError:
                    pass
                continue
            raise ConfigEntryAuthFailed(
                f"Authentication failed for {host}: {err}"
            ) from err

        if logged_in:
            break

        if attempt == 0:
            _LOGGER.debug(
                "Login returned False for %s, retrying with fresh page", host
            )
            try:
                api._page_fetcher.clear_login_page_response()
            except AttributeError:
                pass

    if not logged_in:
        raise ConfigEntryAuthFailed(f"Login failed for {host}")

    # Create coordinator and do first refresh
    coordinator = NetgearSwitchCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, api.get_unique_id())},
        name=coordinator.data.get("switch_name", f"Netgear {api.switch_model.MODEL_NAME}"),
        manufacturer=MANUFACTURER,
        model=api.switch_model.MODEL_NAME,
        sw_version=coordinator.data.get("switch_firmware"),
        configuration_url=f"http://{host}",
    )

    # Store runtime data
    entry.runtime_data = NetgearSwitchData(api=api, coordinator=coordinator)

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: NetgearSwitchConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        try:
            await hass.async_add_executor_job(
                entry.runtime_data.api.delete_login_cookie
            )
        except Exception:
            _LOGGER.debug("Failed to logout from switch during unload, ignoring")

    return unload_ok
