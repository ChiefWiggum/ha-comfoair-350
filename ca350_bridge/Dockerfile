ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:3.21
FROM ${BUILD_FROM}

# Pinned upstream commit of adorobis/hacomfoairmqtt (master).
# To update: change the hash, bump 'version' in config.yaml, then rebuild the
# add-on in Home Assistant.
ARG CA350_COMMIT=dc44e4f86c3390301353d0444c544e229a18f85a

# Own Python inside the image: it cannot rot the way a /config venv does
# (see docs/TROUBLESHOOTING.md #7). ca350.py on master needs paho-mqtt 2.x
# (it uses mqtt.CallbackAPIVersion.VERSION2) even though the upstream
# requirements.txt still pins 1.6.1.
RUN apk add --no-cache python3 py3-pip \
    && pip3 install --no-cache-dir --break-system-packages \
        "pyserial>=3.5" \
        "paho-mqtt>=2.0,<3"

# The bridge script is fetched at build time, never vendored in this repo.
# ca350.py reads config.ini from its OWN directory, so run.sh writes it here.
ADD https://raw.githubusercontent.com/adorobis/hacomfoairmqtt/${CA350_COMMIT}/src/ca350.py /opt/hacomfoairmqtt/ca350.py

COPY run.sh /run.sh
RUN chmod a+x /run.sh && chmod a+r /opt/hacomfoairmqtt/ca350.py

CMD [ "/run.sh" ]
