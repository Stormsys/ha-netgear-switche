"""Base entity classes for Netgear Managed Switch integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NetgearSwitchCoordinator


@dataclass(frozen=True, kw_only=True)
class NetgearSensorEntityDescription(SensorEntityDescription):
    """Describes a Netgear switch sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType]


@dataclass(frozen=True, kw_only=True)
class NetgearBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Netgear switch binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None]


class NetgearSwitchEntity(CoordinatorEntity[NetgearSwitchCoordinator]):
    """Base entity for Netgear switch integration."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NetgearSwitchCoordinator,
        description: SensorEntityDescription | BinarySensorEntityDescription,
        switch_uid: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{switch_uid}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, switch_uid)},
        )
