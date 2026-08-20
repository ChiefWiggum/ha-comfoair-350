# Changelog

## 1.0.0

Initial release.

- Wraps [adorobis/hacomfoairmqtt](https://github.com/adorobis/hacomfoairmqtt)
  (pinned commit `dc44e4f`) with `config.ini` generated from the add-on options;
  Mosquitto broker auto-detection via the Supervisor MQTT service.
- Own Python 3 + pyserial + paho-mqtt 2.x inside the image — the durable fix for
  the recurring `_PyType_AllocNoTrack` venv rot of the `/config` venv method
  (see `docs/TROUBLESHOOTING.md` #7).
- Multi-arch image (aarch64, amd64) built by GitHub Actions and published
  to GHCR, so installing pulls an image instead of building one on the Pi.
- All four upstream config sections are exposed as options: serial port /
  protocol / PC mode, per-level supply and exhaust fan percentages, MQTT, and the
  discovery device identity (`device_id`, `device_name`, `device_model`).
- Escape hatch: a `config.ini` in `/addon_configs/<slug>/` overrides the
  generated one; the generated file is written there as `config.ini.generated`.
- Startup check logs the contents of `/dev/serial/by-id/` when the configured
  serial port is missing.
- Replaces the hand-rolled local add-on scaffold that used to live in `addon/`,
  which mapped a hardcoded device path and wrote an incomplete `config.ini`
  (missing the `[DEVICE]` and `[HA]` sections that `ca350.py` requires, so it
  would have crashed with a `KeyError` on start).
