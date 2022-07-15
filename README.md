# webhook-counter

Counting Prometheus Alertmanager notifications

Docker image: https://hub.docker.com/r/mkobus/webhook-counter

## Build your own

```
$ docker build -t webhook-counter .
```

## How to use it?

Run webhook-counter:

```
$ docker run -d \
  -it \
  -p 8888:5000 \
  --name webhook-counter
  docker.io/mkobus/webhook-counter:latest
8986bf6308106b5f5e5788519d38774c2c32453c36cf2c627e6547d7683928e4
```

Configure Prometheus Alertmanager to send notifications to webhook-counter:

```
route:
  receiver: default
  group_by:
  - alertname
  routes:
  - receiver: webhook-counter
    continue: true
receivers:
- name: default
- name: webhook-counter
  webhook_configs:
  - send_resolved: true
    url: http://localhost:8888/hook
```

Curl webhook-counter metrics endpoint to see the results:

```
$ curl http://localhost:8888/metrics
# HELP webhook_notifications_total Multiprocess metric
# TYPE webhook_notifications_total counter
webhook_notifications_total 1.0
# HELP webhook_notifications_error_total Multiprocess metric
# TYPE webhook_notifications_error_total counter
webhook_notifications_error_total 0.0
# HELP webhook_notifications_unpacked_total Multiprocess metric
# TYPE webhook_notifications_unpacked_total counter
webhook_notifications_unpacked_total{receiver="webhook-counter",status="firing"} 1.0
# HELP webhook_notifications_types_total Multiprocess metric
# TYPE webhook_notifications_types_total counter
webhook_notifications_types_total{alertname="ApacheServiceDown",receiver="webhook-counter",status="firing"} 1.0
```
