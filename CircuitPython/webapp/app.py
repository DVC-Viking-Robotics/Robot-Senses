"""
This script runs the flask_controller application using a development server.
"""

# pylint: disable=invalid-name,no-value-for-parameter

import click
from flask import Flask
from .routes import blueprint
from .sockets import socketio


def build_flask_app():
    """ Build and initialize the flask app. """
    app = Flask(__name__)

    app.config['DEBUG'] = True

    # Secret key used by Flask to sign cookies.
    app.config['SECRET_KEY'] = 's3cr3t'

    app.register_blueprint(blueprint)

    # Enable WebSocket integration
    socketio.init_app(app)

    return app


@click.command()
@click.option('--port', default=5555, help='The port number used to access the webapp.')
def run(port):
    """ Launch point for the web app. """
    app = build_flask_app()

    try:
        print(f'Hosting @ http://localhost:{port}')
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        socketio.stop()


if __name__ == '__main__':
    run()
