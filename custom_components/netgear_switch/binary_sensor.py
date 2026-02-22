"""Binary sensor platform for Netgear Managed Switch integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NetgearSwitchConfigEntry
from .entity import NetgearBinarySensorEntityDescription, NetgearSwitchEntity


def _build_port_binary_sensors(
    port_count: int,
) -> list[NetgearBinarySensorEntityDescription]:
    """Build binary sensor descriptions for each port."""
    sensors: list[NetgearBinarySensorEntityDescription] = []
    for port in range(1, port_count + 1):
        sensors.append(
            NetgearBinarySensorEntityDescription(
                key=f"port_{port}_link",
                translation_key="port_link_status",
                translation_placeholders={"port": str(port)},
                device_class=BinarySensorDeviceClass.CONNECTIVITY,
                value_fn=lambda data, p=port: data.get(f"port_{p}_status") == "on",
            )
        )
    return sensors


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetgearSwitchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors from a config entry."""
    data = entry.runtime_data
    coordinator = data.coordinator
    switch_uid = data.api.get_unique_id()
    port_count = data.api.ports

    descriptions = _build_port_binary_sensors(port_count)

    async_add_entities(
        NetgearPortBinarySensor(coordinator, description, switch_uid)
        for description in descriptions
    )


class NetgearPortBinarySensor(NetgearSwitchEntity, BinarySensorEntity):
    """Binary sensor for a Netgear switch port link status."""

    entity_description: NetgearBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return true if the port is connected."""
        return self.entity_description.value_fn(self.coordinator.data)
