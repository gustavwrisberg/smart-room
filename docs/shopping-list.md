# Shopping list

Everything for the living room in this example. Prices are approximate (Nov 2026, EUR incl.
VAT) and change often; the same list is in [`hardware/shopping-list.csv`](../hardware/shopping-list.csv).

## Hub (once per home)

| Item | Used here | Qty | ~€ | Notes |
| --- | --- | --- | --- | --- |
| Home Assistant server | Home Assistant Green, or a used mini PC | 1 | 110 | Skip if you already run Home Assistant |
| Thread radio | Home Assistant Connect ZBT-2, Thread firmware | 1 | 45 | On the included USB cable, away from USB 3 ports and the router |

## In the room

| Item | Used here | Qty | ~€ | Connects | Notes |
| --- | --- | --- | --- | --- | --- |
| Corner sensor | [Room Sensor Lite](https://github.com/gustavwrisberg/room-sensor) | 1 | 20 | Wi-Fi, ESPHome | LD2410C radar, SHT40, BH1750. Board ≈ $22 at 5 pcs from JLCPCB + case. Use the corner mount |
| Wall panel | [Room Panel](https://github.com/gustavwrisberg/room-panel) | 1 | 67 | Wi-Fi, ESPHome | C4002 radar, SHT40, BH1750, SCD40, 2.9" e-paper, knob, 4 buttons. ≈ $78 incl. modules |
| USB charger + cable | Any 5 V 1 A | 1 | 6 | – | For the corner sensor; the panel's is in its BOM |
| Smart bulbs | IKEA KAJPLATS E27, colour and white spectrum | 2 | 12 | Matter over Thread | Mains-powered, so they also extend the Thread mesh |
| Lamps | Ceiling pendant + floor lamp (E27) | 2 | – | – | Any you like |
| Radiator thermostat | IKEA LILJEBAGGE | 1 | 15 | Matter over Thread | M30 × 1.5; check the adapter for your valve (Danfoss RA etc.) |
| Blind | IKEA HOPPVALS cellular blind, 120 × 155 cm | 1 | 45 | – | Pick the size nearest your window; it cannot be cut |
| Blind motor | Motor board on the Room Panel's J2 header (separate design) **or** a Matter/Thread blind motor | 1 | – | ESPHome / Matter | Anything that shows up as `cover.living_room_blinds` |
| Robot vacuum | Roborock with LiDAR room maps | 1 | 500 | Wi-Fi | Core integration, supports `vacuum.clean_area` |

**Total:** about **€830** with the hub and vacuum; **≈ €220** for the room alone if you already
have Home Assistant, a Thread radio and a vacuum.

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
