#!/usr/bin/env python3
import rospy
from mavros_msgs.msg import OverrideRCIn
import time

# Constants
RC_NEUTRAL = 1500
FORWARD_PWM = 1700
BACKWARD_PWM = 1300
CHANNEL_SURGE = 4  # Forward/Backward

# Trajectory parameters
PERIOD = 2.0  # seconds
DURATION = 60.0  # total script duration in seconds

def send_pwm(pwm_value):
    rc_msg = OverrideRCIn()
    rc_msg.channels = [RC_NEUTRAL] * 8
    rc_msg.channels[CHANNEL_SURGE] = pwm_value
    pub.publish(rc_msg)

def run_trajectory():
    rospy.init_node('trajectory_override_sender')
    global pub
    pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=10)
    rospy.loginfo("Trajectory override script started.")

    rate = rospy.Rate(10)
    t_start = rospy.Time.now().to_sec()

    forward = True
    phase_start = t_start

    while not rospy.is_shutdown():
        t_now = rospy.Time.now().to_sec()
        elapsed = t_now - phase_start

        # Switch direction after PERIOD seconds
        if elapsed > PERIOD:
            forward = not forward
            phase_start = t_now

        pwm = FORWARD_PWM if forward else BACKWARD_PWM
        send_pwm(pwm)

        # Exit after DURATION seconds
        if t_now - t_start > DURATION:
            break

        rate.sleep()

    # Reset to neutral
    send_pwm(RC_NEUTRAL)
    rospy.loginfo("Trajectory override script ended.")

if __name__ == '__main__':
    try:
        run_trajectory()
    except rospy.ROSInterruptException:
        pass
