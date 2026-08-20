# Home Assistant app (add-on): ComfoAir 350 Bridge

A Home Assistant OS app wrapping
[adorobis/hacomfoairmqtt](https://github.com/adorobis/hacomfoairmqtt): a serial
<-> MQTT bridge for **Zehnder ComfoAir 350 / 500** ventilation units, with Home
Assistant MQTT discovery.

> Since Home Assistant 2026.2, add-ons are called **apps** in the UI
> (Settings -> Apps). Nothing changed technically — this repository works the
> same way as before, and the developer docs still say "add-on".

Target setup of this repo: a **ComfoAir 350 CH L Luxe** wired to a Raspberry Pi 5
running HAOS via the DB9 "RS232 - P.C." port and a USB serial adapter. It is a
personal record of a *working* setup: the exact port, wiring, serial device,
config values, and the problems hit along the way with their fixes.

## Install in Home Assistant

1. Install the **Mosquitto broker** app and set up the **MQTT integration**.
2. Settings -> Apps -> **App Store** -> (three-dot menu) -> **Repositories**
   -> add `https://github.com/ChiefWiggum/ha-comfoair-350`.
3. Install **ComfoAir 350 Bridge** (the image is built on your machine;
   a few minutes on a Pi 5).
4. In the app's Configuration tab set `serial_port` to your adapter — prefer a
   `/dev/serial/by-id/...` path (Settings -> System -> Hardware). Leave the MQTT
   options empty; Mosquitto is auto-detected.
5. Start the app, enable **Start on boot** and **Watchdog**, and watch the log. A
   **CA350** device appears under the MQTT integration with
   `climate.ca350_climate`, `sensor.ca350_outsidetemp` and friends.

Full documentation: [`ca350_bridge/DOCS.md`](ca350_bridge/DOCS.md) (also shown in
the app's Documentation tab). Release flow:
[`docs/PUBLISHING.md`](docs/PUBLISHING.md).

> Alternative without GitHub: copy the `ca350_bridge/` folder into the `/addons`
> share of your HAOS machine (Samba app) and it appears in the store under the
> local section.

> Coming from the old `/config` venv + `shell_command` method? Remove the
> autostart automation and the `shell_command: start_ca350` block **before**
> starting the app, or the two fight over the serial port and the MQTT client id.
> See DOCS.md -> "Migrating from the /config venv method".

## The setup at a glance

| Item | Value |
|---|---|
| Unit | Zehnder ComfoAir 350 CH L **Luxe** |
| Control port used | DB9 socket labelled **"RS232 - P.C."** (connector X / X31) |
| Adapter | DFRobot RainbowLink, **RS232 channel** |
| Protocol | True RS232 (+-12 V), 9600 baud - `rs485_protocol: false` |
| USB device | WCH "USB Quad Serial" (CDC-ACM), native in HAOS |
| Serial path | `/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02` (= ttyACM1) |
| Bridge | adorobis/hacomfoairmqtt (`ca350.py`) in the add-on container |
| HA link | MQTT (Mosquitto add-on) + MQTT autodiscovery |
| Wall panel | CC-Luxe left connected; `enable_pc_mode: false` was enough to read every value |

## Repo layout

```
repository.yaml                     add-on repository manifest
LICENSE                             MIT (same as upstream hacomfoairmqtt)
ca350_bridge/                       the add-on
  config.yaml                       options, schema, uart, mqtt
  build.yaml                        base images per architecture
  Dockerfile                        own Python + pinned upstream ca350.py
  run.sh                            options -> config.ini, MQTT auto-detect, launch
  DOCS.md                           user documentation (Documentation tab)
  CHANGELOG.md
  translations/                     option labels for the HA UI (en, de)
docs/
  PUBLISHING.md                     add-on repository + release flow
  ENVIRONMENT.md                    verified snapshot of the live machine (2026-08-20)
  SETUP.md                          full board-specific setup runbook
  WIRING.md                         DB9 "RS232 - P.C." wiring + serial-device ID
  TROUBLESHOOTING.md                every issue hit, in order, with the fix
lovelace/
  comfoair-card.yaml                dashboard card examples
tools/
  serial_sniffer.py                 passive multi-port listener to find the RS232 channel
config/                             HISTORY: the old /config venv method (see below)
                                    config.ini.example is the real file, scrubbed
```

## `ca350.py` is not vendored here

The bridge script belongs to the upstream project. The add-on's Dockerfile fetches
it at build time from a **pinned commit**, so builds are reproducible; see
`CA350_COMMIT` in [`ca350_bridge/Dockerfile`](ca350_bridge/Dockerfile).

## The `config/` folder is history, not the recommended path

`config/` holds the earlier approach: `ca350.py` in a Python venv under `/config`,
started by a HA `shell_command` and an automation. It worked, but the venv borrows
the SSH add-on's Python interpreter and rots on every HAOS update
(`ImportError: ... _PyType_AllocNoTrack: symbol not found` — see
[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) #7). The add-on carries its
own Python and cannot rot. Kept for reference only.

## Credit

- Bridge: https://github.com/adorobis/hacomfoairmqtt (adorobis)
- Original Domoticz work: https://github.com/AlbertHakvoort/StorkAir-Zehnder-WHR-930-Domoticz-MQTT
- Lovelace cards: https://github.com/mweimerskirch/lovelace-hacomfoairmqtt · https://github.com/TimWeyand/lovelace-comfoair

Licensed under the [MIT license](LICENSE), same as the upstream project.
Unaffiliated with Zehnder.
