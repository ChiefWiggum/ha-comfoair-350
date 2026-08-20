# ComfoAir 350 Bridge — local HAOS add-on

Runs the adorobis/hacomfoairmqtt bridge as a **container Home Assistant manages**, instead
of a `/config` venv. This is the durable fix for the recurring
`ImportError: ... _PyType_AllocNoTrack: symbol not found` crash: that happens because a venv
in `/config` borrows the SSH add-on's Python, which HAOS rebuilds on updates/reboots. This
add-on carries its **own** Python + pyserial baked into the image, so it can't rot, and it
restarts automatically on boot.

## Install

1. Enable **Advanced Mode** on your HA user profile (needed to see local add-ons).
2. Copy this `addon/` folder to HAOS at **`/addons/ca350_bridge/`** so you have:
   ```
   /addons/ca350_bridge/config.yaml
   /addons/ca350_bridge/Dockerfile
   /addons/ca350_bridge/run.sh
   ```
   (Use the Samba or File editor add-on to create `/addons/ca350_bridge/` and drop the files in.)
3. **Settings → Add-ons → Add-on Store → ⋮ (top right) → Check for updates.**
4. Scroll to **Local add-ons → "ComfoAir 350 Bridge" → Install** (first build takes a few minutes).
5. Open the **Configuration** tab, set `mqtt_user` / `mqtt_password` (and confirm `serial_port`
   is your `by-id` `...if02` path), **Save**.
6. **Info** tab → enable **Start on boot** and **Watchdog** → **Start**.
7. Watch the **Log** tab — you should see "Starting ComfoAir 350 bridge …" then subscriptions
   and live values.

## Before you install — decommission the old venv method

So the two don't fight over the serial port and the MQTT client id:

- Delete the autostart automation "Start ca350 bridge on HA start".
- Remove the `shell_command: start_ca350:` block from `/config/configuration.yaml`.
- `pkill -f ca350` (or just reboot after the add-on is running).
- You can keep `/config/custom_components/ca350/` as a backup, or delete it — the add-on
  doesn't use it.

## Notes

- `serial_port` in the Configuration tab must match the device mapped in `config.yaml`
  (`devices:`). If your by-id path differs, edit BOTH.
- `mqtt_server: core-mosquitto` is the hostname of the Mosquitto add-on from inside another
  add-on — use that rather than an IP.
- The upstream `ca350.py` is fetched at image build time (see Dockerfile), not stored here.
