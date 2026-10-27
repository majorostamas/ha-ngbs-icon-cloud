# NGBS iCON (cloud) for Home Assistant

Control NGBS iCON underfloor heating/cooling controllers from Home Assistant, through the NGBS cloud, the same service the official **NGBS iCON** mobile app uses. If the app works for you, this integration will too, whether or not Home Assistant is on the same network as the controller.

> Unofficial. Not affiliated with or endorsed by NGBS. It uses the same cloud API as the mobile app, which may change without notice.

## What you get

For each controller on your account:

| Entity | What it does |
|---|---|
| Heating/cooling (select) | Switches the whole system between heating and cooling. Only shown if your controller allows switching. |
| Water temperature, Outside temperature (sensors) | Only shown if the sensors are installed. |
| Online (binary sensor) | Whether the controller is connected to the cloud. |

For each room (thermostat):

| Entity | What it does |
|---|---|
| Thermostat card (climate) | Current temperature and humidity, target temperature (within the room's allowed range), comfort/ECO preset, heating/idle state. |
| Temperature, Humidity, Dew point, Target temperature (sensors) | For history graphs and automations. |
| Valve (binary sensor) | Whether the room's valve is open. |
| ECO mode (switch) | ECO on/off for the room. |
| Parental lock (switch) | Locks the thermostat's buttons. |

Devices and rooms take the names set in the NGBS app. Data refreshes every 30 seconds.

## Installation

### With HACS (recommended)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=majorostamas&repository=ha-ngbs-icon-cloud&category=integration)

Click the button above, or add it by hand:

1. In Home Assistant open **HACS**, then the three-dot menu (top right), then **Custom repositories**.
2. Add `https://github.com/majorostamas/ha-ngbs-icon-cloud` with type **Integration**.
3. Search HACS for **NGBS iCON (cloud)**, open it and click **Download**.
4. Restart Home Assistant.

### Manually

1. Download this repository (green **Code** button → **Download ZIP**).
2. Copy the `custom_components/ngbs_icon_cloud` folder into the `custom_components` folder of your Home Assistant configuration directory (the one containing `configuration.yaml`). Create `custom_components` if it doesn't exist. The Samba share, File editor or SSH add-ons all work for this.
3. Restart Home Assistant.

## Setup

[![Open your Home Assistant instance and start setting up the integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ngbs_icon_cloud)

1. Go to **Settings → Devices & services → Add integration** (or click the button above).
2. Search for **NGBS iCON (cloud)**.
3. Enter the email and password you use in the NGBS iCON app.

Home Assistant stores the credentials in its own configuration storage. You never put them in a file. If the password changes, Home Assistant shows a notification asking you to log in again.

## Good to know

- **Changes take a few seconds.** A change shows immediately in Home Assistant, then is confirmed from the cloud about 3 seconds later.
- **Switching between heating and cooling pauses the system.** After a changeover the pump and valves stay off for a few minutes. This is the controller's normal changeover delay.
- **Target temperatures are limited** to the range configured for each room on the controller.

## Troubleshooting

Turn on debug logging by adding this to `configuration.yaml` and restarting:

```yaml
logger:
  logs:
    custom_components.ngbs_icon_cloud: debug
```
