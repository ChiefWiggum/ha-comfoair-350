#!/usr/bin/env python3
# Supervisor for ca350.py: relaunches the bridge every 15s if it exits.
#
# Fix vs. the original: call the venv's python by ABSOLUTE PATH instead of
# `source .../activate && python3 ...`. os.system() runs via /bin/sh, which has
# no `source` builtin, so activation silently failed on boot and the script ran
# without paho-mqtt. The absolute path always resolves to the venv interpreter.
import os
import time

pid = os.fork()

if pid > 0:
    print("Parent process:", os.getpid())
else:
    while True:
        print("Run ca350.py")
        os.system('/config/custom_components/ca350/python3venv/bin/python3 '
                  '/config/custom_components/ca350/ca350.py')
        time.sleep(15)
