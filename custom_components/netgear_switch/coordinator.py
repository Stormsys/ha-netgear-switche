"""DataUpdateCoordinator for Netgear Managed Switch."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from py_netgear_plus import (
    NetgearSwitchConnector,
    NotLoggedInError,
    PageFetcherConnectionError,
)

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NetgearSwitchCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage fetching data from a Netgear switch."""

    def __init__(self, hass: HomeAssistant, api: NetgearSwitchConnector) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self._lock = asyncio.Lock()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the switch."""
        async with self._lock:
            try:
                data = await self.hass.async_add_executor_job(
                    self.api.get_switch_infos
                )
            except NotLoggedInError:
                _LOGGER.debug("Session expired, re-authenticating")
                try:
                    logged_in = await self.hass.async_add_executor_job(
                        self.api.get_login_cookie
                    )
                except PageFetcherConnectionError as err:
                    raise UpdateFailed(
                        f"Connection failed during re-auth: {err}"
                    ) from err

                if not logged_in:
                    raise ConfigEntryAuthFailed("Re-authentication failed")

                try:
                    data = await self.hass.async_add_executor_job(
                        self.api.get_switch_infos
                    )
                except Exception as err:
                    raise UpdateFailed(
                        f"Failed after re-auth: {err}"
                    ) from err
            except PageFetcherConnectionError as err:
                raise UpdateFailed(f"Connection error: {err}") from err
            except Exception as err:
                raise UpdateFailed(f"Unexpected error: {err}") from err

        _LOGGER.debug("Switch data updated: %d keys", len(data))
        return data
