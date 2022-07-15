import json
from logging.config import dictConfig

from flask import Flask, Response, jsonify, request

from prometheus_client import (CollectorRegistry, CONTENT_TYPE_LATEST,
                               Counter, Info, generate_latest, multiprocess)

from simple_settings import settings

from werkzeug.middleware.dispatcher import DispatcherMiddleware


dictConfig(settings.LOGGING)


def make_wsgi_app():
    def prometheus_app(environ, start_response):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        status = '200 OK'
        response_headers = [
            ('Content-type', CONTENT_TYPE_LATEST),
            ('Content-Length', str(len(data)))
        ]
        start_response(status, response_headers)
        return iter([data])

    return prometheus_app


app = Flask(__name__)
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})


info = Info('webhook_counter', 'Description of info')
info.info({'version': settings.VERSION})

metrics = {
    'total': Counter(
        'webhook_notifications_total',
        'Total number of received HTTP notifications.',
    ),
    'error_total': Counter(
        'webhook_notifications_error_total',
        'Total number of received invalid (non-JSON) HTTP notifications.',
    ),
    'unpacked_total': Counter(
        'webhook_notifications_unpacked_total',
        'Total number of received alerts (unpacked HTTP notifications).',
        ['receiver', 'status'],
    ),
    'by_type': Counter(
        'webhook_notifications_types',
        'Total number of received alerts by receiver and type.',
        ['receiver', 'alertname', 'status'],
    ),
}


@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'version': settings.VERSION,
    })


@app.route('/hook', methods=['POST'])
def webhook_receiver():

    try:
        data = json.loads(request.data)
    except ValueError:
        metrics['error_total'].inc()
        msg = 'Invalid request data: {}.'.format(request.data)
        app.logger.error(msg)
        return Response(json.dumps({'error': msg}),
                        status=400,
                        mimetype='application/json')

    metrics['total'].inc()
    app.logger.debug('Received requests: {}'.format(data))

    receiver = data['receiver']

    for alert in data['alerts']:
        status = alert['status']
        metrics['unpacked_total'].labels(
            receiver,
            status).inc()
        metrics['by_type'].labels(
            receiver,
            alert['labels']['alertname'],
            status).inc()

    app.logger.debug('Successful counter update')
    return jsonify({'result': 'OK'})


if __name__ == '__main__':
    app.run()
