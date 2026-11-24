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
| KAJPLATS in the ceiling pendant | Living Room | `light.living_room_pendant` |
| KAJPLATS in the floor lamp | Living Room | `light.living_room_floor_lamp` |
| LILJEBAGGE on the radiator | Living Room | `climate.living_room_trv` |

## 3. Room Sensor and Room Panel

1. Build both devices following their repos.
2. Copy `esphome/secrets.example.yaml` to `esphome/secrets.yaml` and fill it in
   (`openssl rand -base64 32` for the API key).
3. Put `living-room-sensor.yaml`, `living-room-panel.yaml` and `secrets.yaml` in the ESPHome
   Device Builder (or run `esphome run living-room-sensor.yaml` on your PC). The first flash
   is over USB-C, after that over Wi-Fi.
4. Adopt both in Settings → Devices & services → ESPHome and put them in the **Living Room**
   area.
5. On the **Living Room Panel** device: Configure → tick **Allow the device to perform Home
   Assistant actions**. Without it the knob and buttons do nothing.
6. Mount: the sensor in a corner at about 2.1 m on its 45° corner mount, the panel at
   1.4 m next to the door.

The ESPHome device names give these entity ids, which the packages use as they are:

| Entity | From |
| --- | --- |
| `binary_sensor.living_room_sensor_presence` | Room Sensor (LD2410C) |
| `binary_sensor.living_room_sensor_window_open_temperature_drop` | Room Sensor (temperature drop in ESPHome) |
| `sensor.living_room_sensor_illuminance` | Room Sensor (BH1750) |
| `binary_sensor.living_room_panel_presence` | Room Panel (C4002) |
| `sensor.living_room_panel_temperature`, `sensor.living_room_panel_co2` | Room Panel (SHT40, SCD40) |
| `binary_sensor.living_room_panel_button_*` | Room Panel buttons |

## 4. Better Thermostat

HACS → Better Thermostat → Add integration:

| Field | Value |
| --- | --- |
| Name | `Living room radiator` → gives `climate.living_room_radiator` |
| Real thermostat | `climate.living_room_trv` |
| Temperature sensor | `sensor.living_room_panel_temperature` |
| Window sensor | *leave empty* (the package switches the radiator off itself) |
| Calibration | Target temperature based, then let it learn for a few days |

## 5. Blinds

Whatever motor you use, rename its entity to `cover.living_room_blinds`. 100 = open, 0 = closed.

## 6. Robot vacuum

1. Add the **Roborock** integration and sign in. Give the vacuum a fixed IP in your router.
2. Rename the entity to `vacuum.robot_vacuum`.
3. Let it map the home, then on the vacuum entity: Settings → **Map vacuum segments to
   areas** → map its living-room segment to the **Living Room** area (`living_room`).
4. Install the Companion app on every phone in the household so `zone.home` counts people.

No room mapping? In `living_room_vacuum.yaml` replace the `vacuum.clean_area` action with
`vacuum.start`.

## 7. Home Assistant packages

1. Copy `home-assistant/packages/` to `/config/packages/` (File editor or Samba add-on).
2. Add to `configuration.yaml` (see `home-assistant/configuration.example.yaml`):

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

3. Developer tools → YAML → **Check configuration**, then restart.
4. Optional: paste `home-assistant/dashboard/living_room.yaml` into a dashboard.

## 8. Tune it

| What | Where | Start with |
| --- | --- | --- |
| Temperature offset of each device | `temp_offset` in the ESPHome yaml / Better Thermostat calibration | Compare with a thermometer for an hour |
| Radar gates and timeouts | The LD2410 and C4002 entities in Home Assistant | Run the panel's *Radar calibrate room* switch with the room empty |
| When it counts as dark | `input_number.living_room_dark_lux` | 30 lx |
| Comfort / eco / night temperatures | `input_number.living_room_*_temp` | 21 / 19 / 18 °C |
| Morning and night times | `input_datetime.morning_starts`, `night_starts` | 07:00, 23:00 (the defaults are set in `living_room_core.yaml`) |
| Window sensitivity | `-0.3` °C/min in `living_room_core.yaml` | Open a window and watch `sensor.living_room_temperature_change` |
| Vacuum only when away, or also when the room is empty | `input_boolean.vacuum_when_room_empty` | Off |

## Turning automation off

`input_boolean.living_room_auto` off stops all the room's automations; a long press on the
panel's scene button turns it back on and re-applies lights, blinds and heating.
