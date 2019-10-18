from gps_serial import GPSserial
from .sockets import sio

GPS = GPSserial('com3', baud=9600)

@sio.on('gps')
def handle_gps_request():
    """This event fired when a websocket client's response to the server about GPS coordinates."""
    # print('gps data sent')
    GPS.get_data()
    NESW = [GPS.lat, GPS.lng]
    sio.emit('gps-response', NESW)

