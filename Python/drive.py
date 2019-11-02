import board
from drivetrain import Tank, BiMotor
import socketio
from .common import SERVER

sio = socketio.Client()
D_TRAIN = Tank([BiMotor(board.D17, board.D18), BiMotor(board.D22, board.D13)])

@sio.on('remoteOut', namespace='/drivetrain')
def on_remote_out(args):
    """This event gets fired when the client sends data to the server about remote controls
    (via remote control page) specific to the robot's drivetrain.

    :param list args: The list of motor inputs received from the remote control page.
    """
    # print('remote =', repr(args))
    D_TRAIN.go([args[0] * 655.35, args[1] * 655.35])

@sio.on('disconnect', namespace='/drivetrain')
def on_disconnect():
    """When the client is disconnected from the server. This event essentially stops all motion
    in the drivetrain."""
    # print('connection to server lost')
    D_TRAIN.go([0, 0])

if __name__ == '__main__':
    sio.connect(SERVER, namespaces=('/drivetrain'))
