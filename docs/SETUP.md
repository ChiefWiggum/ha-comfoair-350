# Setup runbook — ComfoAir 350 CH L Luxe on HAOS (Pi 5)

> **HISTORY.** This is the retired `/config` venv + `shell_command` method. It
> worked, then broke on every HAOS update (`TROUBLESHOOTING.md` #7). Use the
> add-on instead: `ca350_bridge/DOCS.md`. Kept because the hardware steps (1-2)
> and the verification steps (6-7) still apply, and because the machine ran
> exactly this until 2026-08-20 — see `ENVIRONMENT.md`.

## 0. Prerequisites in Home Assistant
1. Install the **Mosquitto broker** add-on; start it.
2. Add the **MQTT integration**; leave discovery enabled (prefix `homeassistant/`).
3. Create an MQTT user + a **short/simple** password (over-long passwords have blocked the bridge).
4. Install **Advanced SSH & Web Terminal** add-on with **Protection mode OFF** (needed to
   reach `/config` and build a venv).

## 1. Hardware
See `docs/WIRING.md`. Summary: RainbowLink **RS232** channel → DB9 **"RS232 – P.C."**,
GND→5, TX→3, RX→2. Set the unit to speed 1–3 (not off). No 12 V pin on this port.

## 2. Find the serial device
```bash
ls -l /dev/serial/by-id/
```
Use the `if02` path (RS232 channel here):
`/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02`

If unsure which channel is RS232, use `tools/serial_sniffer.py` and watch for `07 f0` frames.

## 3. Install the bridge
```bash
mkdir -p /config/custom_components/ca350
# ca350.py (upstream — not vendored in this repo):
curl -L -o /config/custom_components/ca350/ca350.py \
  https://raw.githubusercontent.com/adorobis/hacomfoairmqtt/master/src/ca350.py
# config + runner from this repo:
#   cp config/config.ini.example  /config/custom_components/ca350/config.ini
#   cp config/ca350runner.py      /config/custom_components/ca350/ca350runner.py

# Python venv (under /config so it survives reboots):
python3 -m venv /config/custom_components/ca350/python3venv
/config/custom_components/ca350/python3venv/bin/pip install paho-mqtt pyserial
```

## 4. Configure
Edit `/config/custom_components/ca350/config.ini` (from `config/config.ini.example`):
- `SerialPort=` the `by-id` `if02` path
- `RS485_protocol=False`
- `enablePcMode=False` (what actually ran; see `ENVIRONMENT.md`)
- `HAEnableAutoDiscoverySensors=True`, `HAEnableAutoDiscoveryClimate=True`
- MQTT server/user/password

## 5. Autostart (survives reboot)
- Add the `shell_command` block from `config/configuration.yaml.snippet` to
  `/config/configuration.yaml`. It uses `setsid … </dev/null … &` so the call returns
  immediately (avoids the 60-second `shell_command` timeout).
- Add the automation from `config/automations.yaml.snippet` (runs 2 min after HA start).
- Developer Tools → YAML → Check Configuration → Reload.

## 6. Verify
```bash
pkill -f ca350
# fire it the way boot does:
#   Developer Tools -> Actions -> shell_command.start_ca350   (should return instantly)
ps aux | grep ca350 | grep -v grep      # want ONE stable python3venv/bin/python3 ... ca350.py
cat /config/ca350.log                    # subscriptions + live values
```
Then Developer Tools → States, filter `ca350`, confirm temps/fan/filter have values.
Finally, reboot once and confirm the card fills in ~2–3 min after boot.

## 7. Dashboard
See `lovelace/comfoair-card.yaml`. Recommended card: mweimerskirch's
`custom:hacomfoairmqtt-card`.
