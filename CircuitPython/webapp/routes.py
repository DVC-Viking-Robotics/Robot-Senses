""" A collection of Flask routes """
# pylint: disable=invalid-name

import os
from flask import Blueprint, render_template
from .sockets import socketio

blueprint = Blueprint('blueprint', __name__)

@blueprint.route("/shutdown_server")
@login_required
def shutdown_server():
    """ Shutdowns the webapp. """
    socketio.stop()


@blueprint.route("/restart")
@login_required
def restart():
    """ Restarts the robot (Only applicable if webserver runs off rasp pi) """
    os.system('sudo reboot')


@blueprint.route("/shutdown_robot")
@login_required
def shutdown_robot():
    """ Shutsdown the robot (Only applicable if webserver runs off rasp pi) """
    os.system('sudo shutdown -h now')
