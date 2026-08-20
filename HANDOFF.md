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

## Current state: add-on repository, built on HAOS (pushed)
The `/config` venv + `shell_command` method is retired — it rotted on every HAOS
update (`_PyType_AllocNoTrack`, TROUBLESHOOTING #7). The bridge now lives in
`ca350_bridge/`, an HA add-on modelled on the `ha-optolink-splitter` repo:
`repository.yaml` + one folder per add-on, options -> generated `config.ini`,
Supervisor MQTT auto-detect, `uart: true`, en/de translations, and the image
built on the HAOS machine from the add-on's Dockerfile (no registry, no CI).
Pushed to https://github.com/ChiefWiggum/ha-comfoair-350 (public).

Architectures: aarch64 + amd64. No armv7 — Home Assistant dropped it in 2025.12.

The earlier hand-rolled `addon/` scaffold is gone. (It would have crashed anyway:
its generated `config.ini` lacked the `[DEVICE]` and `[HA]` sections `ca350.py`
requires, and it mapped one hardcoded device path.)

## NEXT STEPS (in order)
1. Add the repo in HA: App Store -> ⋮ -> Repositories ->
   `https://github.com/ChiefWiggum/ha-comfoair-350`, then install (builds on the
   Pi, a few minutes).
2. Set `serial_port` to the by-id `…if02` path; leave MQTT options empty
   (Mosquitto is auto-detected); `rs485_protocol` off, `enable_pc_mode` on.
3. **Decommission the old method** before/while starting the add-on: delete the
   "Start ca350 bridge on HA start" automation and remove the
   `shell_command: start_ca350` block from `configuration.yaml`, then `pkill -f
   ca350`. Otherwise two instances fight over the port and the hardcoded MQTT
   client id `CA350`.
4. Verify: MQTT integration -> CA350 device, values refresh; then reboot once and
   confirm it comes back by itself.
5. Untested so far: the image has never been built (no Docker here, no CI). First
   install is the first real build — watch the add-on's build log.

## Secrets
Nothing secret is committed. MQTT credentials come from add-on options or the
Supervisor MQTT service at runtime — never from a file in this repo.
