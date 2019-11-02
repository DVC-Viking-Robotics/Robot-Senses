from gps_serial import GPSserial
import socketio
from .common import SERVER

sio = socketio.Client()
GPS = GPSserial('com3', baud=9600)

@sio.on('gps', namespace='/gps')
def on_gps_request():
    """This event fired when a websocket client's response to the server about GPS coordinates."""
    # print('gps data sent')
    GPS.get_data()
    NESW = [GPS.lat, GPS.lng]
    sio.emit('gps-response', NESW)

@sio.on('disconnect', namespace='/gps')
def on_disconnect():
    """When the client is disconnected from the server. This event is for debug only as it does
    nothing with the sensor."""
    # print('connection to server lost')
    pass

if __name__ == '__main__':
    sio.connect(SERVER, namespaces=('/gps'))
