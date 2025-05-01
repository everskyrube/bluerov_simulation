#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Joy
from mavros_msgs.msg import OverrideRCIn
import subprocess
import time

SCRIPT_PATH = "/root/catkin_ws/src/bluerov2/bluerov2_control/scripts/traj_control.py"
script_process = None

# Define joystick axes mapping
AXIS_ROLL = 0   # Left/Right Left axis 1 is roll now
#AXIS_PITCH = 1  # Forward/Backward axis 0 nothing 
AXIS_SURGE = 1
AXIS_THROTTLE = 4  # Up/Down axis 3 up down correct
AXIS_YAW = 3    # Changed axis 6 on the left to YAW

## Button

BUTTON_ARM = 4   # Arm button L1
BUTTON_DISARM = 5  # Disarm button R1
BUTTON_TRAJECTORY_TOGGLE = 0  # Button X to toggle trajectory (PS4 joystick)
prev_button_state = 0

# Default RC values
RC_NEUTRAL = 1500
RC_MIN = 1100
RC_MAX = 1900

def scale_joystick(value):
    """Convert joystick (-1 to 1) to RC range (1100 to 1900)"""
    return int(max(RC_MIN, min(RC_MAX, (value + 1) * 400 + 1100)))
    #return int((value + 1) * 400 + 1100)

def joy_callback(msg):
    global script_process, prev_button_state

    """Convert joystick input to MAVROS RC override messages"""
    rc_msg = OverrideRCIn()
    
    
    # Map joystick axes to RC channels
    #rc_msg.channels[0] = scale_joystick(msg.axes[AXIS_ROLL])      # Roll
    rc_msg.channels[0] = RC_NEUTRAL
    rc_msg.channels[1] = scale_joystick(msg.axes[AXIS_ROLL])    
    rc_msg.channels[2] = scale_joystick(msg.axes[AXIS_THROTTLE])  # Throttle
    rc_msg.channels[3] = scale_joystick(msg.axes[AXIS_YAW])       # Yaw
    rc_msg.channels[4] = scale_joystick(msg.axes[AXIS_SURGE])   # Unused
    rc_msg.channels[5] = RC_NEUTRAL   # Unused
    rc_msg.channels[6] = RC_NEUTRAL
    rc_msg.channels[7] = RC_NEUTRAL

    current_state = msg.buttons[BUTTON_TRAJECTORY_TOGGLE]

    if current_state == 1 and prev_button_state == 0:
        # Rising edge: toggle trajectory script
        if script_process is None or script_process.poll() is not None:
            rospy.loginfo("Starting external trajectory script...")
            script_process = subprocess.Popen(['python3', SCRIPT_PATH])
        else:
            rospy.loginfo("Stopping external trajectory script...")
            script_process.terminate()
            script_process = None

    prev_button_state = current_state

    # Arm/Disarm the vehicle
    if msg.buttons[BUTTON_ARM] == 1:
        rospy.loginfo("Arming vehicle...")
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            arming_service = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
            arming_service(True)
        except rospy.ServiceException as e:
            rospy.logerr(f"Arming failed: {e}")

    if msg.buttons[BUTTON_DISARM] == 1:
        rospy.loginfo("Disarming vehicle...")
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            disarm_service = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
            disarm_service(False)
        except rospy.ServiceException as e:
            rospy.logerr(f"Disarming failed: {e}")

    # Publish RC override
    rc_pub.publish(rc_msg)

if __name__ == '__main__':
    rospy.init_node('joy_to_mavros')
    rc_pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=10)
    rospy.Subscriber('/joy', Joy, joy_callback)
    rospy.loginfo("Joystick to MAVROS RC Override Node Started")
    rospy.spin()
