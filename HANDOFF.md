# Handoff brief — ComfoAir 350 → HAOS bridge (for Claude Code)

Context for continuing this project in Claude Code. Read `README.md`, `docs/WIRING.md`,
`docs/TROUBLESHOOTING.md`, and `addon/` first — this file is just the "where we are / what's next".

## Goal
Run the adorobis/hacomfoairmqtt bridge (ca350.py) reliably on Home Assistant OS (Raspberry
Pi 5), publishing ComfoAir 350 data to HA over MQTT.

## Hardware / connection (confirmed working)
- Unit: Zehnder ComfoAir 350 CH L **Luxe**.
- Port: DB9 **"RS232 – P.C."** (connector X/X31). 3 wires: GND->pin5, TX->pin3, RX->pin2.
- Adapter: DFRobot RainbowLink, **RS232 channel**. RS232 (±12V), 9600 baud. RS485_protocol=False.
- USB: WCH "USB Quad Serial" (CDC-ACM), native in HAOS.
- Serial path (STABLE, use this): `/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02`
  (= ttyACM1). Verified: clean `07 f0` status frames + `07 f3` ACKs on this channel.
- Wall panel (CC-Luxe) can stay connected; set enablePcMode=True.

## What works
- Serial link + wiring: confirmed good (sniffer showed valid frames).
- MQTT autodiscovery: entities appear as `ca350_*` (climate.ca350_climate, sensor.ca350_outsidetemp, etc.).

## What kept breaking (see docs/TROUBLESHOOTING.md for details)
1. Duplicate ca350.py processes -> MQTT reconnect loop (same client id).
2. venv not active -> ModuleNotFoundError paho.
3. ca350runner.py used `source && python3` -> /bin/sh has no `source`, failed on boot.
4. HA `shell_command` killed the long-running process at 60s -> fixed with `setsid ... </dev/null ... &`.
5. `ca350_[nametemp]` placeholder -> possibly old ca350.py; diagnose via States.
6. Empty Lovelace card -> entity-name mismatch / wrong card (use mweimerskirch's).
7. **RECURRING BLOCKER: `ImportError: _PyType_AllocNoTrack: symbol not found`.** The `/config`
   venv borrows the SSH add-on's Python; HAOS rebuilds that interpreter on reboot/update, so
   the venv rots. Rebuild fixes it only until next reboot. Root cause = architecture.

## Decision: move to a container-based add-on
Stop using the `/config` venv + `shell_command`. Run the bridge as a container with its OWN
Python (cannot rot). A first-pass local add-on scaffold is in `addon/` (config.yaml, Dockerfile,
run.sh).

## NEXT STEP for Claude Code
The user already maintains a **custom Docker image for another HAOS app on GitHub, with build
actions/CI**. Preferred plan:
- Fold this bridge into that existing image/repo pattern (multi-arch build via GitHub Actions,
  published to GHCR), rather than the hand-rolled local add-on.
- Model on the upstream container `ghcr.io/revog/hacomfoairmqtt` (env-var driven config:
  SERIAL_PORT, RS485_PROTOCOL, ENABLE_PC_MODE, MQTT_*, HA_ENABLE_AUTO_DISCOVERY_*).
- Then install on HAOS either as a local add-on referencing the GHCR image, or via the user's
  existing add-on repo.
- Device mapping into the container must use the by-id `...if02` path above.
- After cutover: delete the "Start ca350 bridge on HA start" automation and remove the
  `shell_command: start_ca350` block from configuration.yaml so nothing fights over the port/MQTT id.

## Secrets
User states MQTT passwords are not secret for their setup, but keep them out of any PUBLIC repo
(use add-on options / GH Actions secrets / .env, not committed config.ini).
