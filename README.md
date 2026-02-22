# Netgear Managed Switch for Home Assistant

[![HACS][hacs-badge]][hacs-url]
[![GitHub Release][release-badge]][release-url]
[![License][license-badge]][license-url]

A Home Assistant custom integration for **NETGEAR Plus managed switches**. Monitor port link status, traffic statistics, and connection speeds for your network switches directly in Home Assistant.

## Supported Switches

| Model | Ports | Status |
|-------|-------|--------|
| GS305E | 5 | Tested |
| GS308E | 8 | Tested |
| GS308Ev4 | 8 | Tested |

Other NETGEAR Plus switches supported by [py-netgear-plus](https://github.com/foxey/py-netgear-plus) may also work (GS105E, GS108E, GS110EMX, etc.).

## Features

- Per-port link status (connected/disconnected)
- Per-port IO speed and connection speed
- Per-port traffic RX/TX and cumulative totals (disabled by default)
- Aggregate switch traffic and speed metrics
- Switch metadata: firmware version, serial number, switch name
- Automatic session re-authentication
- Support for multiple switches

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to **Integrations**
3. Click the three-dot menu in the top right and select **Custom repositories**
4. Add `https://github.com/stormsys/ha-netgear-switch` with category **Integration**
5. Search for "Netgear Managed Switch" and click **Download**
6. Restart Home Assistant

### Manual

1. Copy the `custom_components/netgear_switch` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **Netgear Managed Switch**
3. Enter the IP address and password of your switch
4. The integration will detect the switch model and create entities

Repeat for each switch you want to monitor.

## Entities

### Binary Sensors (enabled by default)

| Entity | Description |
|--------|-------------|
| Port N Link | Whether a cable is connected and active on port N |

### Sensors (enabled by default)

| Entity | Unit | Description |
|--------|------|-------------|
| Port N IO Speed | MB/s | Combined send/receive speed |
| Port N Connection Speed | Mbps | Negotiated link speed (10/100/1000) |
| Total IO Speed | MB/s | Aggregate IO across all ports |
| Total Traffic RX | MB | Aggregate received traffic |
| Total Traffic TX | MB | Aggregate sent traffic |
| Response Time | s | Time to poll the switch |
| Switch Name | - | Configured switch name |
| Firmware Version | - | Current firmware |
| Serial Number | - | Switch serial number |

### Sensors (disabled by default)

These sensors exist but are disabled to reduce entity clutter. Enable them in the entity settings if needed.

| Entity | Unit | Description |
|--------|------|-------------|
| Port N RX Speed | MB/s | Per-port receive speed |
| Port N TX Speed | MB/s | Per-port send speed |
| Port N Traffic RX | MB | Per-port received traffic (current window) |
| Port N Traffic TX | MB | Per-port sent traffic (current window) |
| Port N Total RX | MB | Per-port cumulative received |
| Port N Total TX | MB | Per-port cumulative sent |
| Total RX Speed | MB/s | Aggregate receive speed |
| Total TX Speed | MB/s | Aggregate send speed |
| Total CRC Errors | - | Aggregate CRC errors |
| Bootloader Version | - | Switch bootloader |

## Known Limitations

- **Single session**: These switches only allow one active login session. If you open the switch web UI while HA is polling, the integration will re-authenticate automatically, but the web UI session will be dropped.
- **Polling interval**: Data updates every 30 seconds.
- **Web scraping**: The integration communicates via HTML scraping (no REST API exists for these switches). Firmware updates that change the web UI may break the integration.

## Credits

- [py-netgear-plus](https://github.com/foxey/py-netgear-plus) - Python library for NETGEAR Plus switch communication
- [ha-netgear-plus](https://github.com/ckarrie/ha-netgear-plus) - Reference HA integration

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg
[hacs-url]: https://github.com/hacs/integration
[release-badge]: https://img.shields.io/github/v/release/stormsys/ha-netgear-switch
[release-url]: https://github.com/stormsys/ha-netgear-switch/releases
[license-badge]: https://img.shields.io/github/license/stormsys/ha-netgear-switch
[license-url]: https://github.com/stormsys/ha-netgear-switch/blob/main/LICENSE
