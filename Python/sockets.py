"""A collection of websocket routes"""
# pylint: disable=invalid-name

import socketio
import click
import eventlet

sio = socketio.Server(logger=False, engineio_logger=False, async_mode='eventlet')

@sio.on('connect')
def handle_connect():
    """This event fired when a websocket client establishes a connection to the server"""
    print('websocket Client connected!')

@click.command()
@click.option('--port', default=5555, help='The port number used to access the socket server.')
def run(port):
    """ Launch point for the socket server. """
    app = socketio.WSGIApp(sio)
    sock = eventlet.listen(('0.0.0.0', port))
    # NOTE This function runs forever until KeyboardInterupt
    eventlet.wsgi.server(sock, app)

if __name__ == '__main__':
    # avoid pylint error about not specifying the `port` param when
    # the `click.option` does so using its `default` parameter.
    # pylint: disable=no-value-for-parameter
    run()
