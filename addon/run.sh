#!/usr/bin/with-contenv bashio
set -e

CONFIG_DIR=/app
CONFIG_FILE="${CONFIG_DIR}/config.ini"

SERIAL_PORT="$(bashio::config 'serial_port')"
RS485="$(bashio::config 'rs485_protocol')"
PCMODE="$(bashio::config 'enable_pc_mode')"
REFRESH="$(bashio::config 'refresh_interval')"
MQTT_SERVER="$(bashio::config 'mqtt_server')"
MQTT_PORT="$(bashio::config 'mqtt_port')"
MQTT_USER="$(bashio::config 'mqtt_user')"
MQTT_PASS="$(bashio::config 'mqtt_password')"
DEBUG="$(bashio::config 'debug')"

# python booleans want Capitalized True/False
cap() { case "$1" in true) echo True;; false) echo False;; *) echo "$1";; esac; }

cat > "${CONFIG_FILE}" <<INI
[DEFAULT]
SerialPort=${SERIAL_PORT}
RS485_protocol=$(cap "${RS485}")
enablePcMode=$(cap "${PCMODE}")
refresh_interval=${REFRESH}
debug=$(cap "${DEBUG}")

[MQTT]
MQTTServer=${MQTT_SERVER}
MQTTPort=${MQTT_PORT}
MQTTKeepalive=45
MQTTUser=${MQTT_USER}
MQTTPassword=${MQTT_PASS}
HAEnableAutoDiscoverySensors=True
HAEnableAutoDiscoveryClimate=True
INI

bashio::log.info "Starting ComfoAir 350 bridge on ${SERIAL_PORT}"
cd "${CONFIG_DIR}"
exec python3 ca350.py
