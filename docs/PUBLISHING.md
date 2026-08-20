# Publishing: GitHub repo + multi-arch image on GHCR

This repo is now a **Home Assistant add-on repository** in the same shape as
[`ha-optolink-splitter`](https://github.com/ChiefWiggum/ha-optolink-splitter)
(`repository.yaml` at the root, one folder per add-on), with one addition: the
image is **not** built on the Pi. GitHub Actions builds it for three
architectures and pushes it to GHCR, and `config.yaml` points Home Assistant at
that image.

```
repository.yaml                     add-on repository manifest (name, url, maintainer)
LICENSE                             MIT (same as upstream hacomfoairmqtt)
ca350_bridge/
  config.yaml                       manifest: options, schema, uart, mqtt, image:
  build.yaml                        per-arch base images + OCI labels
  Dockerfile                        own Python + pinned upstream ca350.py
  run.sh                            options -> config.ini, MQTT auto-detect, launch
  DOCS.md                           shown in the add-on Documentation tab
  CHANGELOG.md
  translations/{en,de}.yaml          option labels in the HA UI
.github/workflows/build.yaml        lint + multi-arch build + push to GHCR
```

## Assumptions baked into the files

| Thing | Value | Where to change it |
|---|---|---|
| GitHub repo | `ChiefWiggum/ha-comfoair-350` | `repository.yaml`, `ca350_bridge/config.yaml` (`url`), `ca350_bridge/build.yaml` (label), `DOCS.md` |
| Image name | `ghcr.io/chiefwiggum/ca350-bridge-{arch}` | `ca350_bridge/config.yaml` (`image`), `.github/workflows/build.yaml` (`IMAGE_NAME`) |
| Add-on slug | `ca350_bridge` | folder name + `slug` in `config.yaml` |

GHCR image names must be lowercase, hence `chiefwiggum`. The workflow lowercases
`github.repository_owner` itself, so a fork publishes under its own owner without
edits; only the `image:` line in `config.yaml` is hardcoded.

## One-time setup

1. Push to the repo (`ChiefWiggum/ha-comfoair-350`):

   ```bash
   git remote add origin https://github.com/ChiefWiggum/ha-comfoair-350.git
   git push -u origin main
   ```

   The repo has to be **public**. Home Assistant's Supervisor clones an add-on
   repository anonymously, so a private one cannot be added in the App Store —
   it fails with a clone error, before any image is involved.

2. Watch **Actions -> Build and publish add-on image**. Three jobs
   (aarch64, amd64, armv7) each push `ca350-bridge-<arch>:1.0.0` and `:latest`.
   The workflow needs no secrets — it uses the built-in `GITHUB_TOKEN` with
   `packages: write`.

3. **Make the packages public.** A new GHCR package inherits the repository's
   visibility at first publish, and the Supervisor pulls anonymously, so an
   install would otherwise fail with `unauthorized`. Package visibility is set
   per package and can be public even if the repo were not.
   For each of the three packages: profile -> **Packages** ->
   `ca350-bridge-aarch64` -> **Package settings** -> **Change visibility** ->
   **Public**. While there, **Connect repository** links the package to the repo
   (the `org.opencontainers.image.source` label in `build.yaml` does this
   automatically on most pushes).

4. In Home Assistant: Settings -> Apps -> **App Store** -> three-dot menu ->
   **Repositories** -> add `https://github.com/ChiefWiggum/ha-comfoair-350`.
   **ComfoAir 350 Bridge** appears and installs by pulling the image.

## Releasing a new version

The Supervisor compares the `version` in `config.yaml` with the installed one, and
the image tag *is* that version — so the two must move together:

1. Change what you need (options, `run.sh`, or `CA350_COMMIT` in the Dockerfile
   to follow upstream).
2. Bump `version` in `ca350_bridge/config.yaml`.
3. Add a `CHANGELOG.md` entry (shown in the update dialog).
4. Commit and push to `main`. The workflow builds and pushes the new tag; Home
   Assistant offers the update within an hour, or immediately after
   **App Store -> three-dot menu -> Check for updates**.

Pull requests build all three architectures with `--test` and push nothing, so a
broken Dockerfile is caught before it reaches GHCR.

The workflow's `lint` job (`frenck/action-addon-linter`) gates the build: if it
flags `config.yaml`, nothing is published. It also emits warnings for the missing
`icon.png` / `logo.png` — warnings do not fail the run. Drop the `needs: lint`
line if you ever want a build to go out despite a lint failure.

## Local build instead of GHCR

To test a change on the Pi without going through GitHub, copy the `ca350_bridge/`
folder into the HAOS `/addons` share (Samba add-on) **and delete the `image:`
line** from the copy's `config.yaml`. Without that line the Supervisor builds the
image locally from the Dockerfile — the same code path the `ha-optolink-splitter`
add-on uses for all of its installs.

## Secrets

Nothing secret is committed: MQTT credentials come from the add-on options or the
Supervisor MQTT service at runtime, never from a file in this repo. The workflow
uses only `GITHUB_TOKEN`.
