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
- Always use the **`by-id` serial path**, never the bare `ttyACMx`.
- Keep the venv under **`/config`** (persists across reboots); never rely on packages
  installed into the add-on's system python (wiped on restart).
