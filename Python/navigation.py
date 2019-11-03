import math
import time

class Navigator:
    """A class to manage the navigation from current GPS position to another. The GPS positions
    are designated using an internal list of `dict` type waypoints. Each waypoint must be in the
    form ``{'lat': float_x, 'lng': float_y}``."""
    def __init__(self):
        self.waypoints = [] #: A FIFO queue of GPS waypoints to travel to. Order is not sorted.

    # override [] operators to return the waypoints queue
    def __getitem__(self, key):
        return self.waypoints[key]

    def __setitem__(self, key, val):
        raise RuntimeWarning(
            'GPSnav.waypoints can not be directly set!! Use .insert() & .pop() accordingly!!')

    def insert(self, wp=None, index=-1):
        """This function inserts an item to the `waypoints` list.

        :param dict wp: The GPS waypoint to be added. This must be in the form
            ``{'lat': float_x, 'lng': float_y}``.
        :param int index: The position for the item to be inserted. Defaults to the last position.
        """
        if index < 0 or index > len(self.waypoints):
            # insert @ end of list if index is out of bounds
            self.waypoints.append(wp)
        else:  # insert @ specified index
            self.waypoints.insert(index, wp)

    def pop(self, index=-1):
        """This function removes an item from the `waypoints` list.

        :param int index: The position of the item to be removed. Defaults to the last position.
        """
        if index >= len(self.waypoints) or index < -1:
            return None  # do nothing if out of bounds
        else:
            return self.waypoints.pop(index)

    def clear(self):
        """This function will empty the `waypoints` list."""
        self.waypoints.clear()

    @property
    def len(self):
        """returns the length of the `waypoints` list."""
        return len(self.waypoints)

    def printWP(self):
        """A debugging function that will print all items in the `waypoints` list"""
        for i in range(len(self.waypoints)):
            print('\t', i + 1,
                  'lat =', self.waypoints[i]['lat'],
                  'lng =', self.waypoints[i]['lng'])

    def get_new_heading(self, current_pos, base=0):
        """This function will determine a new desired heading based on the `waypoints` list

        :param dict current_pos: The current GPS position must be in the form
            ``{'lat': float_x, 'lng': float_y}``.
        """
        if not self.waypoints:
            print("No GPS waypoints created.")
            return 0
        else:  # calc slope between 2 points and return as heading
            y2 = float(self.waypoints[base]['lat'])
            x2 = float(self.waypoints[base]['lng'])
            y1 = float(current_pos['lat'])
            x1 = float(current_pos['lng'])

            # y1 = float(self.waypoints[base]['lat'])
            # x1 = float(self.waypoints[base]['lng'])
            heading = math.degrees(math.atan2((y2 - y1), (x2 - x1)))
            if(heading < 0):
                heading += 360
            return heading

    def align_heading(self, new_heading, d_train_socket, curr_heading):
        """This function will orient the robot so that it is facing a new course heading
        :param float new_heading: The new heading must be in the form of a `float` ranging
            [0, 360].
        :param float curr_heading: The current heading must be in the form of a `float` ranging
            [0, 360]. This should be a reference variable so that it's updated values are handled
            accordingly without having to initiate an event to fetch the value updates.
        :param socketio.Server d_train_socket: The websocket server instance to be used to output
            drivetrain commands. Any websocket events involving the Drivetrain data will use the
            namspace "/drivetrain".
        """
        if d_train_socket.emit('remoteOut', data=[0, 0], namespace='/drivetrain'):
            print('stopped motion in drivetrain')
        print("current robot heading: ")
        print(curr_heading)

        dTcw = new_heading - curr_heading
        dTccw = curr_heading - new_heading

        correctionAngle = 0

        # correction angle based on how the mag3110 is mounted. edit value until 0 aligns robot with true north.
        curr_heading += correctionAngle

        print("current robot heading: ")
        print(curr_heading)

        dTcw = new_heading - curr_heading
        dTccw = curr_heading - new_heading
        if (dTcw < 0):
            dTcw += 360

        if (dTccw < 0):
            dTccw += 360

        if (dTcw < dTccw):
            if d_train_socket.emit('remoteOut', data=[15, 0], namespace='/drivetrain'):
                print("turning clockwise")
        else:
            if d_train_socket.emit('remoteOut', data=[-15, 0], namespace='/drivetrain'):
                print("turning counterclockwise")

        while abs(curr_heading - new_heading) > 6.5:
            # hold steady until new heading is acheived w/in 2 degrees
            print("Current Heading:", curr_heading)
        if d_train_socket.emit('remoteOut', data=[0, 0], namespace='/drivetrain'):
            print("Heading", new_heading, "reached within +/- 6.5 degrees")

    def drivetoWaypoint(self, curr_gps_pos, hdop, pdop, d_train_socket, curr_heading):
        """ WIP! this function needs updated since this class is undergoing new maintainance """
        # retrieve the current position of the robot
        # just making sure that the coordinates are getting stored properly
        print("current lat: ", curr_gps_pos['lat'])
        print("current lng: ", curr_gps_pos['lng'])
        print("----------------")
        print("target lat: ", self.waypoints[0]['lat'])
        print("target lng: ", self.waypoints[0]['lng'])

        # calculated the heading between current position and target coordinate (waypoint[0]['lat/lng'])
        new_heading = self.get_new_heading(curr_gps_pos)
        print("Destination heading:", new_heading)
        # turn the robot toward destination
        self.align_heading(new_heading, d_train_socket, curr_heading)
        # current position of the robot is stored in self.waypoints[base]['lat'] & self.waypoints[base]['lng']
