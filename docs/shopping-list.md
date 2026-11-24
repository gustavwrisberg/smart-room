# Shopping list

Everything for the bedroom in this example. Prices are approximate (Nov 2026, EUR incl.
VAT) and change often; the same list is in [`hardware/shopping-list.csv`](../hardware/shopping-list.csv).

## Hub (once per home)

| Item | Used here | Qty | ~€ | Notes |
| --- | --- | --- | --- | --- |
| Home Assistant server | Home Assistant Green, or a used mini PC | 1 | 110 | Skip if you already run Home Assistant |
| Thread radio | Home Assistant Connect ZBT-2, Thread firmware | 1 | 45 | On the included USB cable, away from USB 3 ports and the router |

## In the room

| Item | Used here | Qty | ~€ | Connects | Notes |
| --- | --- | --- | --- | --- | --- |
| Room device | [Room Panel](https://github.com/gustavwrisberg/room-panel), full build | 1 | 67 | Wi-Fi, ESPHome | The only sensor in the room: C4002 radar, SHT40, BH1750, SCD40, 2.9" e-paper, knob, 4 buttons. ≈ $78 incl. USB charger. Cheaper builds below |
| Smart bulbs | IKEA KAJPLATS E27, colour and white spectrum | 2 | 12 | Matter over Thread | Mains-powered, so they also extend the Thread mesh |
| Lamps | Ceiling pendant + bedside lamp (E27) | 2 | – | – | Any you like |
| Radiator thermostat | IKEA LILJEBAGGE | 1 | 15 | Matter over Thread | M30 × 1.5; check the adapter for your valve (Danfoss RA etc.) |
| Blind | IKEA HOPPVALS cellular blind, 120 × 155 cm | 1 | 45 | – | Pick the size nearest your window; it cannot be cut |
| Blind motor | Motor board on the Room Panel's J2 header (separate design) **or** a Matter/Thread blind motor | 1 | – | ESPHome / Matter | Anything that shows up as `cover.bedroom_blinds` |
| Robot vacuum | Roborock with LiDAR room maps | 1 | 500 | Wi-Fi | Core integration, supports `vacuum.clean_area` |

**Total:** about **€805** with the hub and vacuum; **≈ €150** for the room alone if you already
have Home Assistant, a Thread radio and a vacuum.

## Room Panel: build only what the room needs

One Room Panel per room does everything. The same PCB and case work with fewer parts:
leave a module off and the rest keeps working.

| Build | Leave out | What you lose | ~€ per panel | Firmware |
| --- | --- | --- | --- | --- |
| **Full** (this example) | – | – | 67 | `esphome/bedroom-panel.yaml` as is |
| **No screen** | Waveshare 2.9" e-paper, its cable and J3 | The status/control display. Knob and buttons still work | 49 | Uncomment `no_screen` in the yaml |
| **No CO₂** | SCD40/SCD41 breakout and its wires on J4 | CO₂ reading and the "air out" hint | 49 | Nothing to change; CO₂ shows as unavailable |
| **Presence + climate only** | Both of the above | Both of the above | 32 | Uncomment `no_screen` |

Every build keeps what the automations need: radar presence, temperature (heating, window
detection), light level (lights), and the knob and buttons. A bedroom or hallway usually
does fine with the cheapest build; keep CO₂ in rooms where people sit for hours.

Prices from the room-panel BOM (Nov 2026: display ≈ $21, CO₂ breakout ≈ $20).

## Optional, whole home

| Item | Used here | Notes |
| --- | --- | --- |
| Smart meter reader | DIY ESP32 HAN-port reader (Kamstrup/Aidon) | Energy dashboard; ask your grid company for the key |
| Smart plugs | IKEA GRILLPLATS | Energy metering per appliance; also Thread routers |
| Large e-ink display | Seeed reTerminal E1001 | Whole-home status, TBD |

## Not used on purpose

- **Door/window contact sensors (e.g. IKEA MYGGBETT):** windows are detected from the
  temperature drop instead, so there is nothing to stick on the window frame.
- **Mains-wired devices:** everything is plug-in or battery. In Denmark fixed electrical
  installation work needs an authorised electrician.
