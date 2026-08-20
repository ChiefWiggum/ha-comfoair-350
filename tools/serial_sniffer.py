#!/usr/bin/env python3
"""
Passive multi-port serial sniffer — find which RainbowLink channel is the RS232
link to the ComfoAir. Opens every /dev/ttyACM* read-only and prints whichever
port receives bytes. The correct channel shows frames beginning with 07 f0.

Stop the bridge first (it holds the port):  pkill -f ca350
Run inside the venv:
  /config/custom_components/ca350/python3venv/bin/python3 tools/serial_sniffer.py
"""
import glob
import time

import serial  # pyserial

BAUD = 9600
PATTERN = "07 f0"  # ComfoAir status-frame start marker


def main():
    ports = {}
    for path in sorted(glob.glob("/dev/ttyACM*")):
        try:
            ports[path] = serial.Serial(path, BAUD, timeout=0)
            print("listening on", path)
        except Exception as exc:  # noqa: BLE001
            print("skip", path, exc)

    if not ports:
        print("no /dev/ttyACM* ports found")
        return

    print("--- waiting for data (Ctrl-C to stop) ---")
    seen = {}
    try:
        while True:
            for path, ser in ports.items():
                data = ser.read(256)
                if data:
                    seen[path] = seen.get(path, 0) + len(data)
                    hexs = data.hex(" ")
                    flag = "  <== ComfoAir frames" if PATTERN in hexs else ""
                    print(f"{path}  +{len(data)}B total={seen[path]}  {hexs}{flag}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nsummary:", seen or "no data on any port")


if __name__ == "__main__":
    main()
