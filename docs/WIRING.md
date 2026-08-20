# Wiring & serial device

## Port: DB9 "RS232 – P.C." (connector X / X31)

The ComfoAir 350 Luxe control board exposes several connectors. The one used here is the
**DB9 socket silk-screened "RS232 – P.C."** at the bottom of the board. It is a standard
PC serial port and is the correct, safe choice:

- It only uses pins **2, 3, 5** — there is **no 12 V pin** to worry about (unlike the RJ45
  RS232 port, whose pin 1 carries ~12 V and can destroy an adapter/unit if mis-wired).
- It is separate from **X6 "RS232 – KFB"** (the line to the CC-Luxe wall panel) and from
  **X5** (RJ45). Because the PC port is independent, the wall panel can stay connected;
  `enablePcMode=True` in the bridge hands bus control to the PC port.

Leave these alone: **X5** (RJ45), **X6** (RS232-KFB), **X7** (sensor / 0-10 V / 12 V strip).

## Wiring (3 wires only)

The board's DB9 is **female**, so a **male DB9** breakout is needed (a screw-terminal DB9
shell). Wire the RainbowLink **RS232 channel** to it:

| RainbowLink RS232 terminal | -> | DB9 "RS232 – P.C." pin |
|---|---|---|
| GND | -> | pin 5 |
| TX  | -> | pin 3 |
| RX  | -> | pin 2 |

If no data appears, swap the two data lines (**pin 2 <-> pin 3**); GND always stays on pin 5.
RX/TX swaps are harmless. In this build the mapping above worked as-is (no swap needed).

Alternative to the RainbowLink: a plain USB-to-RS232 **male-DB9 FTDI/CP2102 cable** plugs
straight into this port with no wiring at all, and is natively supported by HAOS.

## Confirmed link

A passive sniff of all serial channels (see `tools/serial_sniffer.py`) showed clean
ComfoAir protocol frames beginning with `07 f0` (status) and `07 f3` (ACK) on the RS232
channel, proving the wiring direction is correct and the link is bidirectional.

## Serial device identification

The RainbowLink enumerates as a WCH "USB Quad Serial" in **CDC-ACM** mode — natively
supported by HAOS, no extra driver needed. All four channels appear:

```
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0             -> ttyUSB0   <-- other adapter, NOT the ComfoAir
/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if00 -> ttyACM0
/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if02 -> ttyACM1   <-- RS232 channel
/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if04 -> ttyACM2
/dev/serial/by-id/usb-wch.cn_USB_Quad_Serial_0123456789-if06 -> ttyACM3
```

(Verbatim from the machine, 2026-08-20 — see `docs/ENVIRONMENT.md`. The
`usb-1a86_…` entry is a separate CH340 adapter on the same Pi; picking it by
mistake gives a silent, dataless link.)

**Always use the `by-id` path, not the bare `/dev/ttyACM1`.** The four channels can renumber
across reboots, but the `by-id` (`if02`) path always tracks the same physical RS232 channel.

Find it yourself with:

```bash
ls -l /dev/serial/by-id/
```
