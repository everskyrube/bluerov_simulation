#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import TwistStamped
from mavros_msgs.srv import SetMode, CommandBool
from mavros_msgs.msg import OverrideRCIn

# Define Circle Parameters
RADIUS = 2.0  # Meters
CENTER_X = 0.0
CENTER_Y = 0.0
ALTITUDE = -1.0  # Depth in meters
SPEED = 0.5  # Speed in m/s
DURATION = 20  # Duration to complete the circle in seconds
ADJUSTMENT_FACTOR = 0.8  # Reduce drift due to water turbulence

class CircularTrajectory:
    def __init__(self):
        rospy.init_node("circular_trajectory_node", anonymous=True)
        
        # Publishers
        self.vel_pub = rospy.Publisher("/mavros/setpoint_velocity/cmd_vel", TwistStamped, queue_size=10)
        
        # Joystick Input Subscriber
        rospy.Subscriber("/mavros/rc/override", OverrideRCIn, self.joystick_callback)
        self.joystick_active = False  # Flag to check if joystick is moving
        
        # Services
        rospy.wait_for_service("/mavros/set_mode")
        rospy.wait_for_service("/mavros/cmd/arming")
        self.set_mode_srv = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        self.arm_srv = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        
        # Set mode to GUIDED
        self.set_mode_srv(custom_mode="GUIDED")
        
        # Arm the vehicle
        self.arm_srv(True)
    
    def joystick_callback(self, msg):
        # If any of the joystick channels are outside the neutral range, assume manual control
        RC_NEUTRAL = 1500
        if any(abs(ch - RC_NEUTRAL) > 100 for ch in msg.channels[:4]):
            self.joystick_active = True
        else:
            self.joystick_active = False

    def publish_waypoints(self):
        rate = rospy.Rate(10)  # 10 Hz
        angle_step = (2 * math.pi) / (DURATION * 10)  # Adjust for smooth motion
        t = 0
        
        while not rospy.is_shutdown():
            if self.joystick_active:
                rospy.loginfo("Joystick input detected, pausing trajectory execution")
                rate.sleep()
                continue  # Skip trajectory when joystick is used

            angle = t * angle_step
            twist = TwistStamped()
            twist.header.stamp = rospy.Time.now()
            twist.twist.linear.x = SPEED * math.cos(angle) * ADJUSTMENT_FACTOR  # Adjusted X velocity
            twist.twist.linear.y = SPEED * math.sin(angle) * ADJUSTMENT_FACTOR  # Adjusted Y velocity
            twist.twist.linear.z = 0.0  # Maintain depth
            
            rospy.loginfo(f"Publishing Twist: linear_x={twist.twist.linear.x}, linear_y={twist.twist.linear.y}, linear_z={twist.twist.linear.z}")

            self.vel_pub.publish(twist)
            t += 1
            rate.sleep()

if __name__ == "__main__":
    try:
        traj = CircularTrajectory()
        traj.publish_waypoints()
    except rospy.ROSInterruptException:
        pass
