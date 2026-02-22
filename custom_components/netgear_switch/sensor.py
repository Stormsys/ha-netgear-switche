"""Sensor platform for Netgear Managed Switch integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import NetgearSwitchConfigEntry
from .entity import NetgearSensorEntityDescription, NetgearSwitchEntity

# Unit string for data rate (not in homeassistant.const)
UNIT_MEGABYTES_PER_SECOND = "MB/s"
UNIT_MEGABITS_PER_SECOND = "Mbps"

# --- Device-level diagnostic sensors (always the same) ---

DEVICE_SENSORS: list[NetgearSensorEntityDescription] = [
    NetgearSensorEntityDescription(
        key="switch_name",
        translation_key="switch_name",
        icon="mdi:swap-horizontal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("switch_name"),
    ),
    NetgearSensorEntityDescription(
        key="switch_firmware",
        translation_key="switch_firmware",
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("switch_firmware"),
    ),
    NetgearSensorEntityDescription(
        key="switch_serial_number",
        translation_key="switch_serial_number",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("switch_serial_number"),
    ),
    NetgearSensorEntityDescription(
        key="switch_bootloader",
        translation_key="switch_bootloader",
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("switch_bootloader"),
    ),
    NetgearSensorEntityDescription(
        key="response_time",
        translation_key="response_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("response_time_s"),
    ),
]

# --- Aggregate sensors ---

AGGREGATE_SENSORS: list[NetgearSensorEntityDescription] = [
    NetgearSensorEntityDescription(
        key="sum_speed_io",
        translation_key="sum_speed_io",
        icon="mdi:swap-horizontal",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_MEGABYTES_PER_SECOND,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("sum_port_speed_io"),
    ),
    NetgearSensorEntityDescription(
        key="sum_traffic_rx",
        translation_key="sum_traffic_rx",
        icon="mdi:download",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("sum_port_traffic_rx"),
    ),
    NetgearSensorEntityDescription(
        key="sum_traffic_tx",
        translation_key="sum_traffic_tx",
        icon="mdi:upload",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("sum_port_traffic_tx"),
    ),
    NetgearSensorEntityDescription(
        key="sum_speed_rx",
        translation_key="sum_speed_rx",
        icon="mdi:download",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_MEGABYTES_PER_SECOND,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("sum_port_speed_rx"),
    ),
    NetgearSensorEntityDescription(
        key="sum_speed_tx",
        translation_key="sum_speed_tx",
        icon="mdi:upload",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_MEGABYTES_PER_SECOND,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("sum_port_speed_tx"),
    ),
    NetgearSensorEntityDescription(
        key="sum_crc_errors",
        translation_key="sum_crc_errors",
        icon="mdi:alert-circle-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("sum_port_crc_errors"),
    ),
]


def _build_port_sensors(port_count: int) -> list[NetgearSensorEntityDescription]:
    """Build sensor descriptions for each port."""
    sensors: list[NetgearSensorEntityDescription] = []
    for port in range(1, port_count + 1):
        # --- Enabled by default ---
        sensors.extend(
            [
                NetgearSensorEntityDescription(
                    key=f"port_{port}_connection_speed",
                    translation_key="port_connection_speed",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:ethernet",
                    native_unit_of_measurement=UNIT_MEGABITS_PER_SECOND,
                    entity_category=EntityCategory.DIAGNOSTIC,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_connection_speed"
                    ),
                ),
                NetgearSensorEntityDescription(
                    key=f"port_{port}_speed_io",
                    translation_key="port_speed_io",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:swap-horizontal",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UNIT_MEGABYTES_PER_SECOND,
                    suggested_display_precision=2,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_speed_io_mbytes"
                    ),
                ),
            ]
        )
        # --- Disabled by default ---
        sensors.extend(
            [
                NetgearSensorEntityDescription(
                    key=f"port_{port}_speed_rx",
                    translation_key="port_speed_rx",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:download",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UNIT_MEGABYTES_PER_SECOND,
                    suggested_display_precision=2,
                    entity_registry_enabled_default=False,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_speed_rx_mbytes"
                    ),
                ),
                NetgearSensorEntityDescription(
                    key=f"port_{port}_speed_tx",
                    translation_key="port_speed_tx",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:upload",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UNIT_MEGABYTES_PER_SECOND,
                    suggested_display_precision=2,
                    entity_registry_enabled_default=False,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_speed_tx_mbytes"
                    ),
                ),
                NetgearSensorEntityDescription(
                    key=f"port_{port}_traffic_rx",
                    translation_key="port_traffic_rx",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:download",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfInformation.MEGABYTES,
                    suggested_display_precision=2,
                    entity_registry_enabled_default=False,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_traffic_rx_mbytes"
                    ),
                ),
                NetgearSensorEntityDescription(
                    key=f"port_{port}_traffic_tx",
                    translation_key="port_traffic_tx",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:upload",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfInformation.MEGABYTES,
                    suggested_display_precision=2,
                    entity_registry_enabled_default=False,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_traffic_tx_mbytes"
                    ),
                ),
                NetgearSensorEntityDescription(
                    key=f"port_{port}_sum_rx",
                    translation_key="port_sum_rx",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:download",
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    native_unit_of_measurement=UnitOfInformation.MEGABYTES,
                    suggested_display_precision=2,
                    entity_registry_enabled_default=False,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_sum_rx_mbytes"
                    ),
                ),
                NetgearSensorEntityDescription(
                    key=f"port_{port}_sum_tx",
                    translation_key="port_sum_tx",
                    translation_placeholders={"port": str(port)},
                    icon="mdi:upload",
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    native_unit_of_measurement=UnitOfInformation.MEGABYTES,
                    suggested_display_precision=2,
                    entity_registry_enabled_default=False,
                    value_fn=lambda data, p=port: data.get(
                        f"port_{p}_sum_tx_mbytes"
                    ),
                ),
            ]
        )
    return sensors


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetgearSwitchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    data = entry.runtime_data
    coordinator = data.coordinator
    switch_uid = data.api.get_unique_id()
    port_count = data.api.ports

    entities: list[NetgearSwitchSensor] = []

    # Device-level diagnostic sensors
    for description in DEVICE_SENSORS:
        entities.append(NetgearSwitchSensor(coordinator, description, switch_uid))

    # Per-port sensors
    port_descriptions = _build_port_sensors(port_count)
    for description in port_descriptions:
        entities.append(NetgearSwitchSensor(coordinator, description, switch_uid))

    # Aggregate sensors
    for description in AGGREGATE_SENSORS:
        entities.append(NetgearSwitchSensor(coordinator, description, switch_uid))

    async_add_entities(entities)


class NetgearSwitchSensor(NetgearSwitchEntity, SensorEntity):
    """Sensor entity for a Netgear switch."""

    entity_description: NetgearSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
