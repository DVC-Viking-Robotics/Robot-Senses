from gps_serial import GPSserial
import socketio
import time
from .common import SERVER, is_connected

sio = socketio.Client()
GPS = GPSserial('com3', baud=9600)

@sio.on('GPSrequest', namespace='/gps')
def on_gps_request(desired_data):
    """This event fired when a gps client's response is invoked by the server.

    :param list,tuple desired_data: A list or tuple of strings that specify the specific GPS
        related data to be returned (eg. ``['lat', 'lng']``).

    :returns: A dictionary in which the keys are the strings specified in the ``desired_data``
        parameter.
    """
    # print('gps data sent')
    GPS.get_data()
    response = {}
    if 'lat' in desired_data :
        response['lat'] = GPS.lat
    if 'lng' in desired_data:
        response['lng'] = GPS.lng
    if 'hdop' in desired_data:
        response['hdop'] = GPS.hdop
    if 'vdop' in desired_data:
        response['vdop'] = GPS.vdop
    if 'pdop' in desired_data:
        response['pdop'] = GPS.pdop
    if 'fix' in desired_data:
        response['fix'] = GPS.fix
    return response

# pylint: disable=unused-variable
@sio.on("connect", namespace="/gps")
def on_connect():
    """This event is fired when the client has connected to the server."""
    is_connected = True

@sio.on('disconnect', namespace='/gps')
def on_disconnect():
    """When the client is disconnected from the server. This event is for debug only as it does
    nothing with the sensor."""
    print('connection to server lost')
    is_connected = False
# pylint: enable=unused-variable

def send_gps_pos():
    """This function will "emit" the latest GPS position's latitude & longitude in a `dict`
    form."""
    sio.emit('gps', data={'lat': GPS.lat, 'lng': GPS.lng}, namespace='/gps')

if __name__ == '__main__':
    sio.connect(SERVER, namespaces=('/gps'))
    while is_connected:
        GPS.get_data()
        send_gps_pos()
        time.sleep(1)
