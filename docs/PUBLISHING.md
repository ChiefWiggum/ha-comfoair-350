# Publishing: the add-on repository

This repo is a **Home Assistant add-on repository**, same shape as
[`ha-optolink-splitter`](https://github.com/ChiefWiggum/ha-optolink-splitter):
`repository.yaml` at the root, one folder per add-on. The Supervisor clones the
repo and **builds the image on the HAOS machine** from the add-on's `Dockerfile`
and `build.yaml` — no registry, no CI, nothing to publish beyond a `git push`.

```
repository.yaml                     add-on repository manifest (name, url, maintainer)
LICENSE                             MIT (same as upstream hacomfoairmqtt)
ca350_bridge/
  config.yaml                       manifest: options, schema, uart, mqtt
  build.yaml                        base image per architecture
  Dockerfile                        own Python + pinned upstream ca350.py
  run.sh                            options -> config.ini, MQTT auto-detect, launch
  DOCS.md                           shown in the add-on Documentation tab
  CHANGELOG.md
  translations/{en,de}.yaml          option labels in the HA UI
```

Architectures: **aarch64** (Pi 5) and **amd64**. armv7 is deliberately absent —
Home Assistant dropped it in 2025.12, and the add-on linter flags it.

## One-time setup

1. Push to `ChiefWiggum/ha-comfoair-350`:

   ```bash
   git push -u origin main
   ```

   The repo has to be **public**: the Supervisor clones an add-on repository
   anonymously, so a private one cannot be added in the App Store at all.

2. In Home Assistant: Settings -> Apps -> **App Store** -> three-dot menu ->
   **Repositories** -> add `https://github.com/ChiefWiggum/ha-comfoair-350`.
   **ComfoAir 350 Bridge** appears; installing builds the image on the Pi (a few
   minutes, mostly `apk add python3` plus two pip wheels).

## Releasing a new version

The Supervisor compares the `version` in `config.yaml` with the installed one, so
that field is what triggers an update:

1. Change what you need (options, `run.sh`, or `CA350_COMMIT` in the Dockerfile to
   follow upstream).
2. Bump `version` in `ca350_bridge/config.yaml`.
3. Add a `CHANGELOG.md` entry — it is shown in the update dialog.
4. Commit and push to `main`. Home Assistant offers the update within an hour, or
   immediately after **App Store -> three-dot menu -> Check for updates**.

Updating rebuilds the image, which re-runs the `ADD` of `ca350.py` at the pinned
commit — so an unchanged `CA350_COMMIT` really does give the same script back.

## Local copy instead of the GitHub repo

To try a change without pushing, copy the `ca350_bridge/` folder into the HAOS
`/addons` share (Samba app). It shows up in the store under the local section and
builds from exactly the same files.

## Checking changes before you push

There is no CI, so a `config.yaml` typo surfaces as a failed install. Cheap local
checks:

```bash
bash -n ca350_bridge/run.sh
```

```bash
python -c "import yaml,sys; [yaml.safe_load(open(f,encoding='utf-8')) for f in sys.argv[1:]]" ca350_bridge/config.yaml ca350_bridge/build.yaml ca350_bridge/translations/en.yaml ca350_bridge/translations/de.yaml repository.yaml
```

The keys under `options` and `schema` in `config.yaml` and both translation files
have to agree, or the UI shows raw key names.

Two rules the Home Assistant add-on linter enforced on this add-on, worth
remembering when editing `config.yaml`: a key set to its default value is
rejected (`boot: auto` is the default, so it must be omitted), and `armv7` is no
longer a valid architecture. Both also apply to the `ha-optolink-splitter`
add-on, which predates those rules.

## Secrets

Nothing secret is committed. MQTT credentials come from the add-on options or the
Supervisor MQTT service at runtime, never from a file in this repo.
