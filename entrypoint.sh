#!/bin/ash

export SIMPLE_SETTINGS=${SIMPLE_SETTINGS:-webhook_counter.settings}
export PROMETHEUS_MULTIPROC_DIR=/opt/webhookcounter

WORKERS=${WH_COUNTER_WORKERS:-4}
BUFFER=${WH_COUNTER_BUFFER_SIZE:-32768}
PORT=${WH_COUNTER_APP_PORT:-5000}
LISTEN_QUEUE=${WH_COUNTER_LISTEN_QUEUE:-100}
LOGPATH=/var/log/webhookcounter.log

touch $LOGPATH
mkdir -p $PROMETHEUS_MULTIPROC_DIR
chown -R 1000:1000 $LOGPATH $PROMETHEUS_MULTIPROC_DIR

uwsgi -p ${WORKERS} \
    --uid 1000 \
    --gid 1000 \
    --http 0.0.0.0:${PORT} \
    --wsgi-file webhook_counter/server.py \
    --callable app_dispatch \
    --buffer-size=${BUFFER} \
    --listen=${LISTEN_QUEUE} \
    --max-worker-lifetime 300 \
    --master \
    --req-logger=file:/var/log/webhookcounter.log
