# Handoff brief — ComfoAir 350 → HAOS bridge

Where the project stands. Read `README.md`, `ca350_bridge/DOCS.md`,
`docs/PUBLISHING.md`, `docs/WIRING.md` and `docs/TROUBLESHOOTING.md` for detail.

## Goal
Run the adorobis/hacomfoairmqtt bridge (ca350.py) reliably on Home Assistant OS
(Raspberry Pi 5), publishing ComfoAir 350 data to HA over MQTT.

## Hardware / connection (confirmed working)
- Unit: Zehnder ComfoAir 350 CH L **Luxe**.
- Port: DB9 **"RS232 – P.C."** (connector X/X31). 3 wires: GND->pin5, TX->pin3, RX->pin2.
- Adapter: DFRobot RainbowLink, **RS232 channel**. RS232 (±12V), 9600 baud, `rs485_protocol: false`.
- USB: WCH "USB Quad Serial" (CDC-ACM), native in HAOS.
- Serial path (STABLE, use this): `/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02`
  (= ttyACM1). Verified: clean `07 f0` status frames + `07 f3` ACKs on this channel.
- Wall panel (CC-Luxe) can stay connected; `enable_pc_mode: true`.

## What works
- Serial link + wiring: confirmed good (sniffer showed valid frames).
- MQTT autodiscovery: entities appear as `ca350_*` (climate.ca350_climate,
  sensor.ca350_outsidetemp, …).

## Current state: add-on repository, image on GHCR (DONE, not yet pushed)
The `/config` venv + `shell_command` method is retired — it rotted on every HAOS
update (`_PyType_AllocNoTrack`, TROUBLESHOOTING #7). The bridge now lives in
`ca350_bridge/`, an HA add-on modelled on the `ha-optolink-splitter` repo
(`repository.yaml` + one folder per add-on, options → generated config, Supervisor
MQTT auto-detect, `uart: true`, en/de translations), plus one addition that repo
does not have: `.github/workflows/build.yaml` builds aarch64/amd64/armv7 with
`home-assistant/builder` and pushes to **GHCR**, and `config.yaml` carries
`image: ghcr.io/chiefwiggum/ca350-bridge-{arch}` so HAOS pulls instead of building
on the Pi.

The earlier hand-rolled `addon/` scaffold is gone. (It would have crashed anyway:
its generated `config.ini` lacked the `[DEVICE]` and `[HA]` sections `ca350.py`
requires, and it mapped one hardcoded device path.)

## NEXT STEPS (in order)
1. Push to `https://github.com/ChiefWiggum/ha-comfoair-350` — see
   `docs/PUBLISHING.md`.
2. The repo must be **public**: HA's Supervisor clones an add-on repository
   anonymously, so a private one cannot be added in the App Store at all.
3. After the first Actions run: **set the three GHCR packages to public** (a
   package inherits the repo's visibility at first publish), else the Supervisor
   pull fails with `unauthorized`.
4. Add the repo URL in HA (App Store → ⋮ → Repositories), install, set
   `serial_port` to the by-id `…if02` path, start.
5. **Decommission the old method** before/while starting the add-on: delete the
   "Start ca350 bridge on HA start" automation and remove the
   `shell_command: start_ca350` block from `configuration.yaml`, then `pkill -f
   ca350`. Otherwise two instances fight over the port and the hardcoded MQTT
   client id `CA350`.
6. Verify: MQTT integration → CA350 device, values refresh; then reboot once and
   confirm it comes back by itself.

## Secrets
Nothing secret is committed. MQTT credentials come from add-on options or the
Supervisor MQTT service at runtime — never from a file in this repo.
