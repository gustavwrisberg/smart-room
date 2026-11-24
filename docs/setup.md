# Setup

From an empty Home Assistant to a working room. Install the [software](software.md) first.

## 1. Thread network

1. Plug the ZBT-2 into the Home Assistant server on its USB cable.
2. When Home Assistant finds it, choose **Thread**. It installs the OpenThread Border Router add-on.
3. Settings → Devices & services → **Thread** → make Home Assistant's network the **preferred** one.
   If you also have a DIRIGERA or an Apple/Google hub, decide now which network is yours;
   the IKEA devices can only be on one.

## 2. Matter devices (bulbs, radiator thermostat)

Do one device at a time, close to the server, and restart Home Assistant if one refuses to
join (a common tip with the KAJPLATS bulbs).

1. Settings → Devices & services → **Add device** → **Matter** → scan the QR code.
2. Rename each device and its entity:

| Device | Area | Entity id |
| --- | --- | --- |
| KAJPLATS in the ceiling pendant | Bedroom | `light.bedroom_ceiling` |
| KAJPLATS in the bedside lamp | Bedroom | `light.bedroom_bedside` |
| LILJEBAGGE on the radiator | Bedroom | `climate.bedroom_trv` |

## 3. Room Panel

The Room Panel is the only sensor in the room: presence, temperature, humidity, light and
(optionally) CO₂, plus the knob, buttons and screen.

1. Build the panel following [its repo](https://github.com/gustavwrisberg/room-panel). Decide
   on the build first ([options](shopping-list.md#room-panel-build-only-what-the-room-needs)):
   full, without the screen, without CO₂, or without both.
2. Copy `esphome/secrets.example.yaml` to `esphome/secrets.yaml` and fill it in
   (`openssl rand -base64 32` for the API key).
3. No screen fitted? In `esphome/bedroom-panel.yaml` uncomment
   `no_screen: !include options/no-screen.yaml`. No CO₂ sensor? Nothing to change.
4. Put `bedroom-panel.yaml`, the `options/` folder and `secrets.yaml` in the ESPHome
   Device Builder (or run `esphome run bedroom-panel.yaml` on your PC). The first flash
   is over USB-C, after that over Wi-Fi.
5. Adopt it in Settings → Devices & services → ESPHome and put it in the **Bedroom** area.
6. On the **Bedroom Panel** device: Configure → tick **Allow the device to perform Home
   Assistant actions**. Without it the knob and buttons do nothing.
7. Mount it at 1.4 m next to the door, where its radar sees the whole room (nothing
   metal in front of it; avoid pointing it straight at the radiator or curtains that move).

The ESPHome device name gives these entity ids, which the packages use as they are:

| Entity | From |
| --- | --- |
| `binary_sensor.bedroom_panel_presence` | C4002 radar |
| `sensor.bedroom_panel_temperature`, `sensor.bedroom_panel_humidity` | SHT40 |
| `sensor.bedroom_panel_illuminance` | BH1750 |
| `sensor.bedroom_panel_radar_presence_distance`, `..._movement_distance` | C4002 distances (in-bed detection) |
| `sensor.bedroom_panel_co2` | SCD40 (unavailable on a build without it) |
| `binary_sensor.bedroom_panel_button_*` | The four buttons |

## 4. Better Thermostat

HACS → Better Thermostat → Add integration:

| Field | Value |
| --- | --- |
| Name | `Bedroom radiator` → gives `climate.bedroom_radiator` |
| Real thermostat | `climate.bedroom_trv` |
| Temperature sensor | `sensor.bedroom_panel_temperature` |
| Window sensor | *leave empty* (the package switches the radiator off itself) |
| Calibration | Target temperature based, then let it learn for a few days |

## 5. Blinds

Whatever motor you use, rename its entity to `cover.bedroom_blinds`. 100 = open, 0 = closed.

## 6. Robot vacuum

1. Add the **Roborock** integration and sign in. Give the vacuum a fixed IP in your router.
2. Rename the entity to `vacuum.robot_vacuum`.
3. Let it map the home, then on the vacuum entity: Settings → **Map vacuum segments to
   areas** → map its bedroom segment to the **Bedroom** area (`bedroom`).
4. Install the Companion app on every phone in the household so `zone.home` counts people.

No room mapping? In `bedroom_vacuum.yaml` replace the `vacuum.clean_area` action with
`vacuum.start`.

## 7. Phones and weather

- Install the **Home Assistant Companion app** on every phone that should get the window
  warnings (it also tells the vacuum when everyone is out). Warnings go to all of them via
  `notify.notify`; for one phone only, change it to `notify.mobile_app_<phone>` in
  `script.bedroom_notify` (`bedroom_core.yaml`).
- The outdoor temperature comes from the default **Met.no** weather integration
  (`weather.forecast_home`). Have a real outdoor sensor? Point `sensor.outdoor_temperature`
  in `bedroom_core.yaml` at it.

## 8. Home Assistant packages

1. Copy `home-assistant/packages/` to `/config/packages/` (File editor or Samba add-on).
2. Add to `configuration.yaml` (see `home-assistant/configuration.example.yaml`):

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

3. Developer tools → YAML → **Check configuration**, then restart.
4. Optional: paste `home-assistant/dashboard/bedroom.yaml` into a dashboard.

## 9. Tune it

| What | Where | Start with |
| --- | --- | --- |
| Temperature offset | Better Thermostat calibration | Compare the panel with a thermometer for an hour |
| Radar | The C4002 entities in Home Assistant | Run the panel's *Radar calibrate room* switch with the room empty |
| When it counts as dark | `input_number.bedroom_dark_lux` | 30 lx |
| Comfort / eco / night temperatures | `input_number.bedroom_*_temp` | 20 / 18 / 17 °C |
| **Bed distance band** | `input_number.bedroom_bed_min_distance` / `_max_distance` | Lie in bed, roll around, and watch `sensor.bedroom_panel_radar_presence_distance`; set the band about 0.2 m either side of what you see (default 1.4–3.0 m) |
| Cold-day insulation | `input_number.bedroom_cold_day_temp`, `input_boolean.bedroom_insulate_cold_days` | Below 5 °C outside |
| Window warnings | `input_number.bedroom_window_max_minutes`, `bedroom_co2_fresh`, `bedroom_co2_high` | 15 min, 600 ppm, 1000 ppm |
| Morning and night times | `input_datetime.morning_starts`, `night_starts` | 07:00, 23:00 (the defaults are set in `bedroom_core.yaml`) |
| Window sensitivity | `-0.3` °C/min in `bedroom_core.yaml` | Open a window and watch `sensor.bedroom_temperature_change` |
| Vacuum only when away, or also when the room is empty | `input_boolean.vacuum_when_room_empty` | Off |

## Turning automation off

`input_boolean.bedroom_auto` off stops all the room's automations; a long press on the
panel's scene button turns it back on and re-applies lights, blinds and heating.
