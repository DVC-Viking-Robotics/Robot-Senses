import socketio
import click
import eventlet
from .navigation import Navigator

sio = socketio.Server(logger=False, engineio_logger=False, async_mode='eventlet')
curr_dtrain_cmd = None
curr_gps_pos = {} # A dict of GPS coordinates. {latitude, longitude}
curr_gps_dops = {} # A dict including dilutions of percision. {horizontal, vertical, positional}
curr_imu_data = {} # A dict of interia measurements. {accel, gyro, mag}
curr_imu_hypr = {} # A dict of calulated orientations. {heading, yaw, pitch, roll}
NAV = Navigator()

@sio.on('WaypointList')
def build_wapypoints(waypoints, clear):
    """Builds a list of waypoints based on the order they were created on
    the 'automode.html' page

    :param list waypoints: A list of GPS latitude & longitude pairs for the robot to
        travel to in sequence. Each waypoint must be in the form
        ``{'lat': float_x, 'lng': float_y}``.
    :param bool clear: A flag that will clear the existing list of GPS waypoints before appending
        to it.
    """
    if clear:
        NAV.clear()
    print('received waypoints')
    for point in waypoints:
        NAV.insert(point)
    NAV.printWP()

# pylint: disable=unused-variable
@sio.on('connect', namespace='/drivetrain')
def drivetrain_connect(sid):
    """This event fired when a drivetrain output client establishes a connection to the server"""
    print('drivetrain client connected with session id', sid)
    dtrain_cmd = [0, 0]
    if sio.emit('remoteOut', data=curr_dtrain_cmd, namespace='/drivetrain'):
        print('drivetrain command sent successfully!')

@sio.on('connect', namespace='/gps')
def gps_connect(sid):
    """This event fired when a gps sensor client establishes a connection to the server"""
    print('GPS client connected with session id', sid)
    sio.emit('GPSrequest', data=('lat', 'lng'), namespace='/gps', callback=on_gps)

@sio.on('connect', namespace='/imu')
def imu_connect(sid):
    """This event fired when a IMU sensor client establishes a connection to the server"""
    print('IMU client connected with session id', sid)
    sio.emit('DoFrequest', data=('heading', 'yaw', 'pitch', 'roll'), namespace='/imu', callback=on_imu)

@sio.on('gps', namespace='/gps')
def on_gps(sid, data):
    """This event is fired when GPS data is received by the client

    :param dict data: A dictionary of GPS data in which the keys descibe the specific GPS
        attribute(s) that is received. Currently only supporting ``lat``, ``lng``, ``hdop``,
        ``vdop``, & ``pdop``. See the GPS_Serial library for more information on these attributes.
    """
    if 'lat' in data.keys() and 'lng' in data.keys:
        curr_gps_pos = {'lat': data['lat'], 'lng': data['lng']}
    if 'hdop' in data.keys():
        curr_gps_dops['hdop'] = data['hdop']
    if 'vdop' in data.keys:
        curr_gps_dops['vdop'] = data['vdop']
    if 'pdop' in data.keys():
        curr_gps_dops['pdop'] = data['pdop']

@sio.on('imu', namespace='/imu')
def on_imu(sid, data):
    """This event is fired when IMU data is received by the client

    :param dict data: A dictionary of GPS data in which the keys descibe the specific GPS
        attribute(s) that is received. Currently only supporting ``lat``, ``lng``, ``hdop``,
        ``vdop``, & ``pdop``. See the GPS_Serial library for more information on these attributes.
    """
    if 'accel' in data.keys() and 'gyro' in data.keys and 'mag' in data.keys:
        curr_imu_data = {'accel': data['accel'], 'gyro': data['gyro'], 'mag': data['mag']}
    elif 'heading' in data.keys() and 'yaw' in data.keys and 'pitch' in data.keys() and 'roll' in data.keys():
        curr_imu_hypr = {'heading': data['heading'],
                         'yaw': data['yaw'],
                         'pitch': data['pitch'],
                         'roll': data['roll']}
# pylint: enable=unused-variable

@click.command()
@click.option('--port', default=5555, help='The port number used to access the socket server.')
def run(port):
    """Launch point for the socket server."""
    app = socketio.WSGIApp(sio)
    sock = eventlet.listen(('0.0.0.0', port))
    # NOTE This function runs forever until KeyboardInterupt
    eventlet.wsgi.server(sock, app)

if __name__ == '__main__':
    # avoid pylint error about not specifying the `port` param when
    # the `click.option` does so using its `default` parameter.
    # pylint: disable=no-value-for-parameter
    run()
