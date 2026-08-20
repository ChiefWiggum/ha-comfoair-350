# Environment snapshot — exported from the live HAOS machine, 2026-08-20

Everything here comes from an export taken off the running Raspberry Pi 5 on
**2026-08-20 13:07 CEST**, while the `/config` venv method was still in place.
It is the ground truth this repo's docs are written against. Credentials are
replaced by placeholders; the exported `ca350.py` and the full log are not
committed (see below).

## Serial devices actually present

```
$ ls -l /dev/serial/by-id/
usb-1a86_USB_Serial-if00-port0                     -> ../../ttyUSB0
usb-wch.cn_USB_Quad_Serial_0123456789-if00         -> ../../ttyACM0
usb-wch.cn_USB_Quad_Serial_0123456789-if02         -> ../../ttyACM1   <-- ComfoAir RS232
usb-wch.cn_USB_Quad_Serial_0123456789-if04         -> ../../ttyACM2
usb-wch.cn_USB_Quad_Serial_0123456789-if06         -> ../../ttyACM3
```

Two adapters are plugged into this machine. `usb-1a86_USB_Serial-if00-port0` is
a separate CH340 adapter and **not** the ComfoAir link — don't pick it by
accident. The ComfoAir uses the RainbowLink's RS232 channel, `…-if02`.

## Python environment of the venv (the retired method)

```
Python 3.14.7
paho-mqtt==2.1.0
pyserial==3.5
```

paho-mqtt 2.x is not optional: current `ca350.py` calls
`mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 'CA350')`, which 1.6.1 does not
have. Upstream's `src/requirements.txt` still pins 1.6.1 and is stale. The
add-on image therefore installs `paho-mqtt>=2.0,<3`.

## Bridge configuration that ran

Full file (scrubbed): [`config/config.ini.example`](../config/config.ini.example).
Values worth carrying forward:

| Key | Live value | Note |
|---|---|---|
| `SerialPort` | `…usb-wch.cn_USB_Quad_Serial_0123456789-if02` | by-id, RS232 channel |
| `RS485_protocol` | `False` | DB9 "RS232 – P.C." is true RS232 |
| `enablePcMode` | **`False`** | see below |
| `refresh_interval` | `10` | |
| Fan in/out per level | 15 / 25 / 40 / 70 | identical for supply and exhaust |
| `SetUpFanLevelsAtStart` | `True` | |
| `MQTTServer` | `127.0.0.1` | host-local; an add-on uses `core-mosquitto` |
| Device identity | `ca350` / `CA350` / Zehnder / ComfoAir 350 | drives entity names |

**`enablePcMode` was `False`, not `True`.** Earlier notes in this repo (and the
handoff) assumed `True` was needed so the CC-Luxe wall panel could stay
connected. The live setup published all values with it off, so the add-on
defaults to off too. Turn it on only if Home Assistant cannot *change* fan level
or temperature while the panel is attached — it disables the panel's control of
the bus.

**Re-verified on the add-on, 2026-08-20 13:30.** With `enable_pc_mode: false`
the dashboard card filled in completely: fan 868/860 rpm and 25 % / 25 %,
ventilation level 1, all four temperatures, comfort setpoint 20 °C, filter OK,
bypass closed, preheating off, summer mode on. The unit also accepted writes in
that state (`Changed RS232 mode to 0`, `Changed the fan levels`), and the 25 %
at level 1 is `fan_in_low` / `fan_out_low` — proof that
`setup_fan_levels_at_start` wrote 15/25/40/70 into the unit. So PC mode is not
needed on this installation, for reads or writes.

## Home Assistant side (retired)

`configuration.yaml` held exactly the `shell_command` from
[`config/configuration.yaml.snippet`](../config/configuration.yaml.snippet)
(Option A, via `ca350runner.py`), and `automations.yaml` the start automation
from [`config/automations.yaml.snippet`](../config/automations.yaml.snippet)
(`id: '1783465654554'`, HA start + 2 min delay). Both must be removed when
switching to the add-on — see `ca350_bridge/DOCS.md`.

## State of the bridge at export time: dead

`/config/ca350.log` contained **139 copies of one traceback and nothing else** —
the runner loop relaunching every 15 s into the same failure:

```
Parent process: 122
Traceback (most recent call last):
  File "/config/custom_components/ca350/ca350.py", line 24, in <module>
    import serial
  File "…/python3venv/lib/python3.14/site-packages/serial/__init__.py", line 31, in <module>
    from serial.serialposix import Serial, PosixPollSerial, VTIMESerial  # noqa
  File "…/python3venv/lib/python3.14/site-packages/serial/serialposix.py", line 77, in <module>
    import array
ImportError: Error relocating /usr/lib/python3.14/lib-dynload/array.cpython-314-aarch64-linux-musl.so:
             _PyType_AllocNoTrack: symbol not found
```

Note where the failure is: `/usr/lib/python3.14/...` — the venv's own
`site-packages` against an interpreter that lives *outside* it. That is the venv
rot of [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) #7, and the reason for the
container add-on. The full log is not committed: 1252 lines, all the same
traceback.

## The bridge script

The exported `/config/custom_components/ca350/ca350.py` is **byte-identical** to
upstream commit `dc44e4f86c3390301353d0444c544e229a18f85a`, which is the commit
pinned as `CA350_COMMIT` in [`../ca350_bridge/Dockerfile`](../ca350_bridge/Dockerfile).
So the add-on runs exactly the script that ran here. It is not vendored (see
`NOTICE.md`).
