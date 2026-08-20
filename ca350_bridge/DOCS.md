# ComfoAir 350 Bridge

Runs [adorobis/hacomfoairmqtt](https://github.com/adorobis/hacomfoairmqtt)
(`ca350.py`) as a container Home Assistant manages, publishing a Zehnder
ComfoAir 350 / 500 to Home Assistant over MQTT discovery.

The image carries its **own** Python + pyserial + paho-mqtt. That is the point:
a Python venv under `/config` borrows the SSH add-on's interpreter, which HAOS
rebuilds on updates, and the bridge then dies with
`ImportError: ... _PyType_AllocNoTrack: symbol not found`. A container cannot rot
that way, and it restarts on boot without a `shell_command` or an automation.

## Requirements

- A serial connection to the unit (see the repository's `docs/WIRING.md`).
- The **Mosquitto broker** add-on plus the **MQTT integration**. The add-on picks
  up host and credentials automatically via the Supervisor; the MQTT options are
  only needed for an external broker.

## Installation

1. Settings -> Apps (Add-ons) -> **App Store** -> three-dot menu ->
   **Repositories** -> add `https://github.com/ChiefWiggum/ha-comfoair-350`.
2. Install **ComfoAir 350 Bridge** (the image is built on your machine;
   a few minutes on a Pi 5).
3. Open **Configuration** and set `serial_port`. Prefer the stable by-id path —
   for the DFRobot RainbowLink (WCH Quad Serial) used in this project that is the
   RS232 channel:

   ```
   /dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02
   ```

   `ls -l /dev/serial/by-id/` (SSH add-on) or Settings -> System -> Hardware
   lists the candidates. Never use the bare `/dev/ttyACM1` — the four channels of
   a quad adapter can renumber across reboots.
4. Leave `rs485_protocol` **off** (the ComfoAir 350 DB9 "RS232 - P.C." port is
   true RS232) and `enable_pc_mode` **on** (hands bus control to the PC port so
   the CC-Luxe wall panel can stay connected).
5. Start the add-on, enable **Start on boot** and **Watchdog**, and watch the log.

A **CA350** device appears under Settings -> Devices & Services -> MQTT with
entities named after `device_id`: `climate.ca350_climate`,
`sensor.ca350_outsidetemp`, `sensor.ca350_supplytemp`,
`binary_sensor.ca350_filterstatus`, and so on.

## Options

| Option | Default | Meaning |
|---|---|---|
| `serial_port` | `/dev/ttyUSB0` | Serial device; use a `/dev/serial/by-id/...` path. |
| `rs485_protocol` | `false` | `true` only for an RS485 connection. |
| `enable_pc_mode` | `true` | Disables the ComfoSense / CC-Luxe bus master so the PC port can write. |
| `refresh_interval` | `10` | Seconds between polls. |
| `mqtt_broker` | *(empty)* | `host` or `host:port`. Empty = Supervisor / Mosquitto auto-detect. |
| `mqtt_user`, `mqtt_password` | *(empty)* | Empty = auto-detected Mosquitto credentials. |
| `device_id` | `ca350` | Entity prefix and discovery unique id. |
| `device_name`, `device_model` | `CA350`, `ComfoAir 350` | Shown in the device info. |
| `ha_discovery_sensors`, `ha_discovery_climate` | `true` | Publish the MQTT discovery configs. |
| `setup_fan_levels_at_start` | `true` | Write the fan percentages below into the unit at start. |
| `fan_in_*`, `fan_out_*` | 15 / 25 / 40 / 70 | Supply and exhaust fan percentage per level. |
| `debug` | `false` | Log every serial frame and MQTT message. |

### Advanced: full config.ini override

The add-on generates `config.ini` from the options and writes a copy to
`/addon_configs/<slug>/config.ini.generated`. If you place your own
**`config.ini`** into `/addon_configs/<slug>/`, it is used verbatim and every
option above is ignored (the log warns when this happens). Useful for upstream
keys the add-on does not expose yet.

## Migrating from the /config venv method

Do this **before** starting the add-on, so the two do not fight over the serial
port and the MQTT client id. `ca350.py` hardcodes the client id `CA350`, so two
instances kick each other off the broker in an endless reconnect loop:

1. Delete the automation "Start ca350 bridge on HA start".
2. Remove the `shell_command: start_ca350:` block from
   `/config/configuration.yaml` and reload the YAML configuration.
3. `pkill -f ca350` (or reboot once the add-on runs).
4. `/config/custom_components/ca350/` is no longer used — keep it as a backup or
   delete it.

## Troubleshooting

- **`Serial port ... does not exist (yet)`** in the log: the by-id path is wrong
  or the adapter is unplugged. The log then lists what `/dev/serial/by-id/`
  actually holds.
- **MQTT reconnect loop**: a second instance of the bridge is running — see the
  migration steps above.
- **`could not get serial data` / `Expected return not found`** now and then is
  normal on ComfoAir units; the bridge retries. Judge success by whether values
  refresh in Home Assistant, not by a clean log.
- **`homeassistant/sensor/ca350_[nametemp]/config`** in the log is cosmetic: the
  bridge prints the topic template before substitution. Check Developer Tools ->
  States for `sensor.ca350_outsidetemp` to confirm the real entities exist.
- **No entities at all**: confirm the MQTT integration is set up and the log
  shows a successful MQTT connection, then restart the add-on.

## Updating the bridge script

`ca350.py` is fetched at image build time from a **pinned upstream commit**
(`CA350_COMMIT` in the Dockerfile), so rebuilds are reproducible. To move to a
newer upstream version: change the hash, bump `version` in `config.yaml`, and
push — Home Assistant then offers the update and rebuilds the image.

## Credits

- Bridge: [adorobis/hacomfoairmqtt](https://github.com/adorobis/hacomfoairmqtt) (MIT).
- Original Domoticz work:
  [AlbertHakvoort/StorkAir-Zehnder-WHR-930-Domoticz-MQTT](https://github.com/AlbertHakvoort/StorkAir-Zehnder-WHR-930-Domoticz-MQTT).

This add-on is unaffiliated with Zehnder.
