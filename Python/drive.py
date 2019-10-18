import board
from drivetrain import Tank, BiMotor
from .sockets import sio

D_TRAIN = Tank([BiMotor(board.D17, board.D18), BiMotor(board.D22, board.D13)])

@sio.on('remoteOut')
def handle_remoteOut(args):
    """This event gets fired when the client sends data to the server about remote controls
    (via remote control page) specific to the robot's drivetrain.

    :param list args: The list of motor inputs received from the remote control page.

    """
    print('remote =', repr(args))
    D_TRAIN.go([args[0] * 655.35, args[1] * 655.35])
