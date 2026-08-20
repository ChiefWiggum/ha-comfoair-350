# ComfoAir 350 CH L Luxe → Home Assistant (HAOS on Raspberry Pi 5)

Documentation and configuration for integrating a **Zehnder ComfoAir 350 CH L Luxe**
ventilation unit into **Home Assistant OS** running on a **Raspberry Pi 5**, using the
[adorobis/hacomfoairmqtt](https://github.com/adorobis/hacomfoairmqtt) serial↔MQTT bridge
and a **DFRobot RainbowLink** USB→serial converter (RS232 channel).

This repo is a personal record of a *working* setup: the exact port, wiring, serial
device, config values, and — importantly — the problems hit along the way and their fixes.

## The setup at a glance

| Item | Value |
|---|---|
| Unit | Zehnder ComfoAir 350 CH L **Luxe** |
| Control port used | DB9 socket labelled **"RS232 – P.C."** (connector X / X31) |
| Adapter | DFRobot RainbowLink, **RS232 channel** |
| Protocol | True RS232 (±12 V), 9600 baud — `RS485_protocol=False` |
| USB device | WCH "USB Quad Serial" (CDC-ACM), native in HAOS |
| Serial path | `/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02` (= ttyACM1) |
| Bridge | adorobis/hacomfoairmqtt (`ca350.py`) in a venv under `/config` |
| HA link | MQTT (Mosquitto add-on) + MQTT autodiscovery |
| Wall panel | CC-Luxe left connected; `enablePcMode=True` hands the bus to the PC port |

## Repo layout

```
comfoair350-haos/
├── README.md                         this file
├── docs/
│   ├── SETUP.md                      full board-specific setup runbook
│   ├── WIRING.md                     DB9 "RS232 – P.C." wiring + serial-device ID
│   └── TROUBLESHOOTING.md            every issue hit, in order, with the fix
├── config/
│   ├── config.ini.example           hacomfoairmqtt config (placeholders, no secrets)
│   ├── ca350runner.py               supervisor loop (fixed: absolute venv python)
│   ├── configuration.yaml.snippet   HA shell_command (setsid, returns immediately)
│   └── automations.yaml.snippet     HA-start automation
├── lovelace/
│   └── comfoair-card.yaml           dashboard card examples
└── tools/
    └── serial_sniffer.py            passive multi-port listener to find the RS232 channel
```

## Important: ca350.py is NOT included

The bridge script `ca350.py` belongs to the upstream project and is not vendored here.
Pull it fresh into `/config/custom_components/ca350/`:

```bash
curl -L -o /config/custom_components/ca350/ca350.py \
  https://raw.githubusercontent.com/adorobis/hacomfoairmqtt/master/src/ca350.py
```

See `docs/SETUP.md` for the full installation, including the Python venv.

## Credit

- Bridge: https://github.com/adorobis/hacomfoairmqtt (adorobis)
- Original Domoticz work: https://github.com/AlbertHakvoort/StorkAir-Zehnder-WHR-930-Domoticz-MQTT
- Lovelace cards: https://github.com/mweimerskirch/lovelace-hacomfoairmqtt · https://github.com/TimWeyand/lovelace-comfoair

## Recommended: run as a local add-on

The `shell_command` + `/config` venv method proved fragile on HAOS (the venv rots on
reboot — see docs/TROUBLESHOOTING.md #7). The **durable** setup is the local add-on in
`addon/`, which runs the bridge as a container HA manages. Prefer that; the `config/` venv
files are kept for reference/history.
