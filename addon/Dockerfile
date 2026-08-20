ARG BUILD_FROM
FROM ${BUILD_FROM}

# Python + serial/mqtt libs baked into THIS image — never borrows HAOS's interpreter,
# so it cannot rot on reboot/update the way a /config venv does.
RUN apk add --no-cache python3 py3-pip \
    && pip3 install --break-system-packages --no-cache-dir paho-mqtt pyserial

# Fetch the upstream bridge script at build time (not vendored in this repo).
ADD https://raw.githubusercontent.com/adorobis/hacomfoairmqtt/master/src/ca350.py /app/ca350.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
