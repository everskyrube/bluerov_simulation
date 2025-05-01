#!/usr/bin/env python3
import rospy
from mavros_msgs.msg import OverrideRCIn

    # rc_msg.channels[0] = RC_NEUTRAL
    # rc_msg.channels[1] = scale_joystick(msg.axes[AXIS_ROLL])    # roll
    # rc_msg.channels[2] = scale_joystick(msg.axes[AXIS_THROTTLE])  # throttle, UP/DOWN
    # rc_msg.channels[3] = scale_joystick(msg.axes[AXIS_YAW])       # yaw
    # rc_msg.channels[4] = scale_joystick(msg.axes[AXIS_SURGE])   # SURGE, Forward / Backward
    # rc_msg.channels[5] = RC_NEUTRAL   # Unused
    # rc_msg.channels[6] = RC_NEUTRAL
    # rc_msg.channels[7] = RC_NEUTRAL

def send_rc_override(roll=1500, throttle=1500, yaw=1500, surge=1500):
    rospy.init_node('rc_override_control', anonymous=True)
    pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=10)
    rate = rospy.Rate(10)

    RC_NEUTRAL = 1500

    msg = OverrideRCIn()
    msg.channels = [RC_NEUTRAL, roll, throttle, yaw, surge, RC_NEUTRAL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    rospy.loginfo(f"Sending RC Override: {msg.channels}")
    while not rospy.is_shutdown():
        pub.publish(msg)
        rate.sleep()

if __name__ == "__main__":
    send_rc_override(surge=1600)  # Moves forward