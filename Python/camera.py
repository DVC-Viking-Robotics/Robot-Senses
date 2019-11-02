"""
This module provides an abstraction for managing cameras.
"""

# try to use the faster C implementation of StringIO
# otherwise use the pure python implementation (builtin io module)
try:
    import cStringIO as io
except ImportError:
    import io
# pylint: disable=import-error
import picamera
# pylint: enable=import-error
import base64
import socketio
from .common import SERVER

sio = socketio.Client()

class CameraManager:
    """ This class is for abstracting the camera feed capabilities. """
    def __init__(self):
        self.camera = None

    @property
    def initialized(self):
        """ Returns true if the camera is ready to be used """
        return self.camera is not None

    def _init_pi_camera(self):
        """ Initialize the camera feed using PiCamera's implementation """
        camera = picamera.PiCamera()
        camera.resolution = (256, 144)
        camera.start_preview(fullscreen=False, window=(100, 20, 650, 480))
        # time.sleep(1)
        # camera.stop_preview()
        return camera

    def open_camera(self):
        """ Opens and initializes the camera """
        try:
            self.camera = self._init_pi_camera()
        except picamera.exc.PiCameraError as picam_error:
            self.camera = None
            raise OSError('Error: picamera is not connected!\n{}'.format(picam_error))

    def capture_image(self):
        """ Fetches an image from the camera feed and incodes it as a JPEG buffer """
        if self.initialized:
            cam_io = io.BytesIO()
            self.camera.capture(cam_io, "jpeg", use_video_port=True)
            buffer = cam_io.getvalue()
            return buffer
        else:
            raise RuntimeError('Camera manager is not initialized!')

    def close_camera(self):
        """
        Cleans up and closes the camera. Note that you cannot use the camera unless you
        re-initialize it with `open_camera()`
        """
        if self.initialized:
            self.camera.close()
        self.camera = None
# end CameraManager class

# instantiate camera using the CameraManager class for use with web sockets.
cam_mgr = CameraManager()

@sio.on('webcam-init', namespace='/camera')
def on_webcam_init():
    """Initialize the camera when the user goes to the remote control page."""
    if not cam_mgr.initialized:
        cam_mgr.open_camera()


@sio.on('webcam', namespace='/camera')
def on_webcam_request():
    """This event is to stream the webcam over websockets."""
    if cam_mgr.initialized:
        buffer = cam_mgr.capture_image()
        b64 = base64.b64encode(buffer)
        # print('webcam buffer in bytes:', len(b64))
        sio.emit('webcam-response', b64)

@sio.on('webcam-cleanup', namespace='/camera')
def on_webcam_cleanup():
    """Cleanup the camera when the user leaves the remote control page."""
    if cam_mgr.initialized:
        cam_mgr.close_camera()

if __name__ == '__main__':
    sio.connect(SERVER, namespaces=('/camera'))
