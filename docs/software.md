# Software

Everything the room needs, in the order you install it. All of it is free and runs locally;
only the Roborock needs its cloud once for sign-in and as a fallback.

| # | Software | What it does here | Where |
| --- | --- | --- | --- |
| 1 | **Home Assistant OS** | Runs everything. 2026.3 or newer (needed for `vacuum.clean_area`) | Preinstalled on the Green; [installation](https://www.home-assistant.io/installation/) for a mini PC |
| 2 | **OpenThread Border Router** add-on | Turns the ZBT-2 into a Thread border router | Installed automatically when you plug in the ZBT-2 and pick *Thread* |
| 3 | **Matter Server** add-on + **Matter** integration | Commissions and controls the IKEA bulbs and the LILJEBAGGE | Settings → Devices & services → Add → Matter |
| 4 | **Thread** integration | Shows the Thread network; set Home Assistant's network as preferred | Settings → Devices & services → Thread |
| 5 | **ESPHome Device Builder** add-on + **ESPHome** integration | Builds and flashes the Room Panel firmware; brings it into HA | Add-on store |
| 6 | **HACS** | Community store for the next two | [hacs.xyz](https://hacs.xyz) |
| 7 | **Better Thermostat** (HACS) | Wraps the LILJEBAGGE so it regulates on the panel's room temperature | HACS → Integrations |
| 8 | **Energi Data Service** (HACS) | Hourly Danish spot price incl. tariffs, shown on the panel's e-paper | HACS → Integrations |
| 9 | **Roborock** integration (core) | The robot vacuum, room maps, `vacuum.clean_area` | Settings → Devices & services → Roborock |
| 10 | **Home Assistant Companion app** (phones) | Puts people in `zone.home`, so the vacuum knows when the home is empty | App store / Play store |
| 11 | **IKEA Home smart** app (optional) | Firmware updates for the IKEA devices, if you also have a DIRIGERA | Only needed with a DIRIGERA |

Built into Home Assistant and used by the packages (nothing to install): template,
derivative, light group, input helpers, timer, sun, script, automation.

## Room Panel firmware

[`esphome/living-room-panel.yaml`](../esphome/living-room-panel.yaml) pulls the firmware
straight from [room-panel/firmware/living-room-panel.yaml](https://github.com/gustavwrisberg/room-panel/blob/main/firmware/living-room-panel.yaml)
as an ESPHome remote package (it uses DFRobot's `dfrobot_c4002` external component), so
only the room-specific names live here. For a panel without the screen, include
[`esphome/options/no-screen.yaml`](../esphome/options/no-screen.yaml) (one line to uncomment).

The full and the no-screen builds both validate with ESPHome 2026.11 (`esphome config`).

## Only for the 3D model

| Software | For |
| --- | --- |
| Python 3.11+ with `manifold3d trimesh numpy` | `models/build_room.py` |
| Blender / any glTF viewer | Opening `room.glb` and the part GLBs |
| A slicer (PrusaSlicer, Bambu Studio, Cura) | Printing the Room Panel case from its repo |
