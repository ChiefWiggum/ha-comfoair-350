# Troubleshooting log

Every issue hit during this integration, in the order it appeared, with the fix. Useful
both as a history and as a checklist if the setup breaks after an update.

## 1. MQTT reconnect loop (subscribe → disconnect → reconnect → repeat)

**Symptom:** log spams "Successfull subscribed …" then "Unexpected disconnection from MQTT,
trying to reconnect", over and over, seconds apart.

**Cause:** two MQTT clients using the same client ID — almost always **two copies of
`ca350.py` running at once** (e.g. a hand-started one plus the autostarted one). The broker
kicks the older session each time the newer connects; they fight forever.

**Fix:** ensure a single instance.
```bash
ps aux | grep ca350 | grep -v grep
pkill -f ca350        # then start exactly one
```

## 2. ModuleNotFoundError: No module named 'paho'

**Symptom:** running `python3 ca350.py` after a reboot throws `ModuleNotFoundError: paho`.

**Cause:** the shell was not in the venv, so system `python3` ran (no paho installed there).

**Fix:** use the venv — either activate it, or call its python by absolute path:
```bash
/config/custom_components/ca350/python3venv/bin/python3 /config/custom_components/ca350/ca350.py
```

## 3. Autostart runner used `source && python3` (didn't work on boot)

**Symptom:** bridge worked when started by hand, but never came up on boot.

**Cause:** `ca350runner.py` launched the script with
`os.system('source .../activate && python3 ...')`. `os.system` runs via `/bin/sh`, which has
no `source` builtin, so activation silently failed and the script ran without paho (see #2).

**Fix:** call the venv python by absolute path in `ca350runner.py` — no `source` needed.
See `config/ca350runner.py`.

## 4. shell_command timed out after 60 seconds (the big one)

**Symptom:** automation trace shows
`Error: Timed out running command: 'python3 .../ca350runner.py &', after: 60 seconds`.
Nothing runs after boot; Lovelace card empty.

**Cause:** HA's `shell_command` waits for the command to *finish* and kills it at 60 s. The
runner (and the bridge) loop forever, so it never returns; the trailing `&` alone doesn't
detach it because `shell_command` keeps the pipe open.

**Fix:** make the command return immediately and fully detach, using `setsid` + closing
stdio. See `config/configuration.yaml.snippet`. After editing: Developer Tools → YAML →
Check Configuration → Reload; then run `shell_command.start_ca350` and confirm it returns
instantly and leaves a process alive.

## 5. `ca350_[nametemp]` placeholder in autodiscovery topic

**Symptom:** log shows `homeassistant/sensor/ca350_[nametemp]/config` with a literal
`[nametemp]` instead of real temp-sensor names.

**Cause:** either the log simply prints the template before substitution (cosmetic), or an
outdated `ca350.py` that doesn't substitute per-sensor names.

**Diagnose:** Developer Tools → States, filter `ca350`. If `sensor.ca350_outsidetemp`,
`_supplytemp`, `_returntemp`, `_exhausttemp` exist with values → cosmetic, ignore it. If
they're missing → update the script.

**Fix (if broken):**
```bash
cd /config/custom_components/ca350
cp ca350.py ca350.py.bak
curl -L -o ca350.py https://raw.githubusercontent.com/adorobis/hacomfoairmqtt/master/src/ca350.py
```
Also confirm `HAEnableAutoDiscoverySensors=True` in `config.ini`.

## 6. Empty Lovelace card

**Symptom:** card renders but shows no data.

**Causes & fixes, in order:**
1. **No data at all** — check `ps aux | grep ca350`; if nothing is running, it's a bridge
   problem (see #1–#4), not the card.
2. **Resource not loaded / cache** — hard-refresh (Ctrl-Shift-R); verify the card's `.js`
   is registered under Settings → Dashboards → Resources.
3. **Entity-name mismatch** — the cards bind to hard-coded IDs like
   `sensor.ca350_outsidetemp`, `climate.ca350_climate`. If your entities are named
   differently, the card finds nothing. Confirm names in Developer Tools → States.
4. **Which card** — TimWeyand's fork is reported to render empty even when installed right;
   mweimerskirch's (`custom:hacomfoairmqtt-card`) is the reliable one.

## Golden rules

- Judge success by whether **values refresh in HA**, not by a clean log.
- Occasional `could not get serial data` / `Expected return not found` is **normal** on
  ComfoAir units — the serial implementation is flaky and the bridge retries.
  Measured on the add-on's first run (2026-08-20): the log carried these warnings for
  `get_fan_status`, `get_ventilation_status`, `get_bypass_status`, `get_filter_weeks`,
  `get_filter_hours`, `get_preheating_status`, `get_ewt` and `get_analog_sensor` — and
  every one of those entities was still populated in the dashboard, because the next poll
  succeeded. A whole class of reads warning repeatedly does **not** mean the datapoint is
  missing, and it is **not** a reason to enable PC mode.
- Always use the **`by-id` serial path**, never the bare `ttyACMx`.
- Keep the venv under **`/config`** (persists across reboots); never rely on packages
  installed into the add-on's system python (wiped on restart).

## 7. Recurring ImportError: _PyType_AllocNoTrack: symbol not found (venv rot)

**Symptom:** after a reboot, `/config/ca350.log` loops:
`ImportError: Error relocating /usr/lib/python3.14/.../array...musl.so: _PyType_AllocNoTrack:
symbol not found`. Card empty. Rebuilding the venv fixes it — until the next reboot.

The log exported on 2026-08-20 was **1252 lines: 139 copies of this one traceback and
nothing else**, the runner relaunching every 15 s into the same import failure. Note the
path in the error — `/usr/lib/python3.14/lib-dynload/...` — the venv's packages loading
against an interpreter that lives outside the venv. Full excerpt and the environment it
ran in: `docs/ENVIRONMENT.md`.

**Cause:** the venv lives in `/config` (persistent) but borrows the SSH add-on's Python
interpreter and C-extensions, which live inside that add-on's container. When HAOS rebuilds
the add-on (updates/reboots), those musl binaries change and the `/config` venv points at a
mismatched interpreter. This is architectural, not a one-off — the venv-on-borrowed-Python
approach is not stable on HAOS.

**Durable fix:** stop using a `/config` venv + `shell_command`. Run the bridge as an
**add-on** (a container HA manages, carrying its own Python + pyserial + paho-mqtt). See
`ca350_bridge/` in this repo, installable as an add-on repository - it maps the serial
device via `uart: true`, restarts on boot, and cannot rot because it doesn't borrow HAOS's
interpreter. After installing the add-on, remove the old automation and the `shell_command`
block so they don't fight over the port / MQTT client id (see
`ca350_bridge/DOCS.md` -> "Migrating from the /config venv method").
