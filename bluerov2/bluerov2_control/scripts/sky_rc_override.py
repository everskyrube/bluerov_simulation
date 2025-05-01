#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Joy
from mavros_msgs.msg import OverrideRCIn
from mavros_msgs.srv import CommandBool

# Define joystick axes mapping
AXIS_ROLL = 0      # Left/Right (Lateral)
AXIS_PITCH = 1     # Forward/Backward (Surge)
AXIS_THROTTLE = 3  # Up/Down (Heave)
AXIS_YAW = 2       # Rotate (Yaw)
BUTTON_ARM = 4     # Arm button
BUTTON_DISARM = 5  # Disarm button

# Default RC values
RC_NEUTRAL = 1500
RC_MIN = 1100
RC_MAX = 1900

# Publisher for RC Override
rc_pub = None

def scale_joystick(value):
    """Convert joystick (-1 to 1) to RC range (1100 to 1900)."""
    return int(max(RC_MIN, min(RC_MAX, (value + 1) * 400 + 1100)))

def joy_callback(msg):
    """Convert joystick input to MAVROS RC override messages."""
    global rc_pub

    if rc_pub is None:
        rospy.logerr("RC Publisher is not initialized!")
        return

    # Create RC override message
    rc_msg = OverrideRCIn()
    
    # Map joystick axes to RC channels
    rc_msg.channels = [
        scale_joystick(msg.axes[AXIS_ROLL]),      # Channel 1: Roll (Lateral)
        scale_joystick(msg.axes[AXIS_PITCH]),     # Channel 2: Pitch (Surge)
        scale_joystick(msg.axes[AXIS_THROTTLE]),  # Channel 3: Throttle (Heave)
        scale_joystick(msg.axes[AXIS_YAW]),       # Channel 4: Yaw (Rotation)
        RC_NEUTRAL,  # Channel 5: Unused
        RC_NEUTRAL,  # Channel 6: Unused
        RC_NEUTRAL,  # Channel 7: Camera Pan (if applicable)
        RC_NEUTRAL   # Channel 8: Lights (if applicable)
    ]

    # Arm/Disarm the vehicle based on button press
    if msg.buttons[BUTTON_ARM] == 1:
        rospy.loginfo("Arming vehicle...")
        try:
            arming_service = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
            arming_service(True)
        except rospy.ServiceException as e:
            rospy.logerr(f"Arming failed: {e}")

    if msg.buttons[BUTTON_DISARM] == 1:
        rospy.loginfo("Disarming vehicle...")
        try:
            disarm_service = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
            disarm_service(False)
        except rospy.ServiceException as e:
            rospy.logerr(f"Disarming failed: {e}")

    # Publish RC override message
    rospy.loginfo(f"Publishing RC Override: {rc_msg.channels}")
    rc_pub.publish(rc_msg)

def main():
    global rc_pub

    # Initialize ROS node
    rospy.init_node('sitl_teleop_rc_override')

    # Create RC Override Publisher
    rc_pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=10)

    # Subscribe to joystick topic
    rospy.Subscriber('/joy', Joy, joy_callback)

    rospy.loginfo("Joystick to MAVROS RC Override Node Started")
    
    rospy.spin()

if __name__ == '__main__':
    main()
