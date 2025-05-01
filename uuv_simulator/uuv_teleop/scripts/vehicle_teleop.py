#!/usr/bin/env python
from __future__ import print_function
import os
import rospy
import numpy as np
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist, Accel, Vector3
from sensor_msgs.msg import Joy


class VehicleTeleop:
    def __init__(self):
        # Load joystick axis mapping
        self._axes = dict(x=4, y=3, z=1,
                          roll=2, pitch=5, yaw=0,
                          xfast=-1, yfast=-1, zfast=-1,
                          rollfast=-1, pitchfast=-1, yawfast=-1)
        
        # Load joystick gain settings
        self._axes_gain = dict(x=3, y=3, z=0.5,
                               roll=0.5, pitch=0.5, yaw=0.5,
                               xfast=6, yfast=6, zfast=1,
                               rollfast=2, pitchfast=2, yawfast=2)

        # Adding Ascend and Descend Buttons
        self._ascend_button = 2   # Button 6 for ascending
        self._descend_button = 0  # Button 7 for descending
        self._depth_gain = 0.5    # Adjust this value for speed

        if rospy.has_param('~mapping'):
            mapping = rospy.get_param('~mapping')
            for tag in self._axes:
                if tag in mapping:
                    if 'axis' in mapping[tag]:
                        self._axes[tag] = mapping[tag]['axis']
                    if 'gain' in mapping[tag]:
                        self._axes_gain[tag] = mapping[tag]['gain']

        self._deadzone = 0.5
        if rospy.has_param('~deadzone'):
            self._deadzone = float(rospy.get_param('~deadzone'))

        self._deadman_button = -1
        if rospy.has_param('~deadman_button'):
            self._deadman_button = int(rospy.get_param('~deadman_button'))

        self._home_button = 7
        if rospy.has_param('~home_button'):
            self._home_button = int(rospy.get_param('~home_button'))

        self._msg_type = 'twist'
        if rospy.has_param('~type'):
            self._msg_type = rospy.get_param('~type')

        if self._msg_type == 'twist':
            self._output_pub = rospy.Publisher('output', Twist, queue_size=1)
        else:
            self._output_pub = rospy.Publisher('output', Accel, queue_size=1)

        self._home_pressed_pub = rospy.Publisher(
            'home_pressed', Bool, queue_size=1)

        self._joy_sub = rospy.Subscriber('joy', Joy, self._joy_callback)

        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            rate.sleep()

    def _parse_joy(self, joy=None):
        if self._msg_type == 'twist':
            cmd = Twist()
        else:
            cmd = Accel()

        if joy is not None:
            l = Vector3(0, 0, 0)

            if self._axes['x'] > -1 and abs(joy.axes[self._axes['x']]) > self._deadzone:
                l.x += self._axes_gain['x'] * joy.axes[self._axes['x']]

            if self._axes['y'] > -1 and abs(joy.axes[self._axes['y']]) > self._deadzone:
                l.y += self._axes_gain['y'] * joy.axes[self._axes['y']]

            if self._axes['z'] > -1 and abs(joy.axes[self._axes['z']]) > self._deadzone:
                l.z += self._axes_gain['z'] * joy.axes[self._axes['z']]

            # NEW: Ascend & Descend using Buttons
            if joy.buttons[self._ascend_button] == 1:
                rospy.loginfo("Ascending...")
                l.z -= self._depth_gain  # Move up

            if joy.buttons[self._descend_button] == 1:
                rospy.loginfo("Descending...")
                l.z += self._depth_gain  # Move down

            a = Vector3(0, 0, 0)

            if self._axes['roll'] > -1 and abs(joy.axes[self._axes['roll']]) > self._deadzone:
                a.x += self._axes_gain['roll'] * joy.axes[self._axes['roll']]

            if self._axes['pitch'] > -1 and abs(joy.axes[self._axes['pitch']]) > self._deadzone:
                a.y += self._axes_gain['pitch'] * joy.axes[self._axes['pitch']]

            if self._axes['yaw'] > -1 and abs(joy.axes[self._axes['yaw']]) > self._deadzone:
                a.z += self._axes_gain['yaw'] * joy.axes[self._axes['yaw']]

            cmd.linear = l
            cmd.angular = a

        else:
            cmd.linear = Vector3(0, 0, 0)
            cmd.angular = Vector3(0, 0, 0)

        return cmd

    def _joy_callback(self, joy):
        try:
            if self._deadman_button != -1:
                if joy.buttons[self._deadman_button] == 1:
                    cmd = self._parse_joy(joy)
                else:
                    cmd = self._parse_joy()
            else:
                cmd = self._parse_joy(joy)

            self._output_pub.publish(cmd)
            self._home_pressed_pub.publish(
                Bool(bool(joy.buttons[self._home_button])))

        except Exception as e:
            rospy.logerr("Error parsing joystick input: {}".format(e))


if __name__ == '__main__':
    node_name = os.path.splitext(os.path.basename(__file__))[0]
    rospy.init_node(node_name)
    rospy.loginfo("Starting [{}] node".format(node_name))

    teleop = VehicleTeleop()

    rospy.spin()
    rospy.loginfo("Shutting down [{}] node".format(node_name))
