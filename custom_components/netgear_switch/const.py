"""Constants for the Netgear Managed Switch integration."""

from homeassistant.const import Platform

DOMAIN = "netgear_switch"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_HOST = "192.168.0.239"
MANUFACTURER = "NETGEAR"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]
