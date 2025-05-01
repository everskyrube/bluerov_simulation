#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Joy
from mavros_msgs.msg import OverrideRCIn

class SITLTeleop(object):
    """Class to handle gazebo teleop"""

    def __init__(self):
        super(SITLTeleop, self).__init__()

        self.pwms = [1500,1500,1500,1500,1500,1500,1500,1100]
        self.dirs = [-1.0,1.0,-1.0,1.0,1.0,1.0]
        self.pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=10)
        rospy.Subscriber('/joy', Joy, self.joy_callback)

    def joy_callback(self, msg):
        gains = msg.axes
        self.pwms = [int(max(1100, min(1900, round(sgn * gain * (1900 - 1100) + 1500)))) for sgn, gain in zip(self.dirs, gains)]

    def run(self):
        """ Run Gazebo Teleop """
        hz = rospy.Rate(5)
        while not rospy.is_shutdown():
            try:
                msg = OverrideRCIn()
                msg.channels = [int(1500), int(1500), int(self.pwms[3]), int(self.pwms[2]), int(self.pwms[1]), int(self.pwms[0]), int(1500), int(1100)]
                self.pub.publish(msg)
            except Exception as error:
                rospy.logerr('{}: rc error {}'.format(rospy.get_name(), error))

if __name__ == "__main__":
    try:
        rospy.init_node('sitl_teleop')
    except rospy.ROSInterruptException as error:
        rospy.logerr('{} pubs error with ROS {}'.format(rospy.get_name(), error))
        exit(1)

    sitl_teleop = SITLTeleop()
    sitl_teleop.run()
