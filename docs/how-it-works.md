# How it works

The room is five Home Assistant packages in [`home-assistant/packages/`](../home-assistant/packages/).
Every automation only runs while `input_boolean.living_room_auto` is on.

```
 Room Sensor (corner)  ──┐                       ┌── lights (KAJPLATS, Thread)
   LD2410C, SHT40, lux   │   Home Assistant      ├── blind (cover)
                         ├── living_room_core ───┼── radiator (LILJEBAGGE + Better Thermostat)
 Room Panel (door)    ───┘   presence, window,   ├── vacuum (Roborock)
   C4002, SHT40, CO2,        night mode, scripts └── panel display (temperature, CO₂, price)
   knob + 4 buttons ──────── calls scripts ─────────┘
```

## Presence – `living_room_core.yaml`

`binary_sensor.living_room_occupied` is on when **either radar** sees someone. The corner
sensor covers the sofa and the room diagonally; the panel covers the door. Off is delayed
2 minutes, so a still reader on the sofa does not lose the lights.

While the vacuum is cleaning, the radars see the robot, so presence is ignored. If you
walk in during a clean, press any panel button: the robot goes home and presence works again.

## Lights – `living_room_lights.yaml`

`script.living_room_apply_lights` decides everything:

| Situation | Result |
| --- | --- |
| Room empty | Off (after 5 minutes) |
| Night mode | Floor lamp at 5 %, 2200 K; pendant off |
| Dark (below 30 lx, or sun down) or lights already on | The scene: **Everyday** pendant 80 % + floor 70 %, **Cozy** floor 50 %, **Movie** floor 12 %, **Bright** both 100 %. 4000 K by day, 2700 K after sunset; Cozy and Movie always 2200 K |
| Bright daylight | Leaves the lights alone |

Darkness is only checked while the lights are off, because they light up the sensor too.
"All off" on the panel starts a 2-minute hold so the lights don't come back on while you walk out.

## Blinds – `living_room_blinds.yaml`

Open when the sun is above −4° **and** it is after "morning starts" **and** night mode is off;
otherwise closed. Re-checked at the morning time, at dusk and dawn, at startup and when night
mode changes. A closed cellular blind is also extra insulation on winter evenings.

On hot days (panel above 24.5 °C for 15 min, room empty, sun high) the blind goes to 30 %.

A manual change from the panel stays until the next of these events.

## Heating – `living_room_heating.yaml`

`sensor.living_room_heating_target` (in core) picks the setpoint:

| Situation | Target |
| --- | --- |
| Night mode | 18 °C |
| Occupied, or occupied in the last 30 min | 21 °C |
| Empty for 30 min | 19 °C |

Better Thermostat regulates the LILJEBAGGE on the panel's temperature in the middle of the
room, not on the hot valve. When the window opens the radiator goes **off**, and back to the
target once the room has stopped cooling for 10 minutes.

## Windows – `living_room_core.yaml`

No contact sensors. `binary_sensor.living_room_window_open` is on if either:

- the Room Sensor's own ESPHome flag fires (more than 0.8 °C colder than 5 minutes ago), or
- the panel's temperature falls faster than 0.3 °C per minute (a *derivative* sensor over 2 minutes).

It stays on until the temperature has been stable for 10 minutes. Above 1000 ppm CO₂ for
10 minutes while someone is home, Home Assistant suggests airing out.

## Day and night – `living_room_core.yaml`

`input_boolean.night_mode` turns on at **23:00** or with a **long press on the all-off button**,
and off at **07:00**. Turning it on or off re-applies lights, blinds and heating straight away.

## Robot vacuum – `living_room_vacuum.yaml`

Starts `vacuum.clean_area` for the Living Room area when **all** of these hold:

- not cleaned yet today, not night mode, between 09:00 and 20:00, robot docked
- everyone has been away for 10 minutes (`zone.home` = 0), **or** "Vacuum when the room is empty"
  is on and the room has been empty for 30 minutes

It is sent back to the dock the moment someone comes home or presses a panel button. Only
a finished clean counts for the day, so an interrupted one is tried again the next time the
home is empty.

## Room Panel controls

The panel firmware calls four scripts from `living_room_core.yaml`:

| Control | Short press | Long press |
| --- | --- | --- |
| Lights | Toggle `light.living_room` | 100 % |
| Blinds | Open/close | 50 % |
| All off | `script.living_room_all_off` | `script.living_room_night` (night mode) |
| Scene | `script.living_room_scene_next` | `script.living_room_auto` (back to automatic) |
| Knob | Dims lights ±5 % or moves blinds ±10 % | Press: switch between lights and blinds |
