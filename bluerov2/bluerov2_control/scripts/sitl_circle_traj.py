#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import TwistStamped
from mavros_msgs.srv import SetMode, CommandBool

# Define Circle Parameters
RADIUS = 2.0  # Meters
CENTER_X = 0.0
CENTER_Y = 0.0
ALTITUDE = -1.0  # Depth in meters
SPEED = 0.2  # Speed in m/s
DURATION = 30  # Duration to complete the circle in seconds

class CircularTrajectory:
    def __init__(self):
        rospy.init_node("circular_trajectory_node", anonymous=True)
        
        # Publishers
        self.vel_pub = rospy.Publisher("/mavros/setpoint_velocity/cmd_vel", TwistStamped, queue_size=10)
        
        # Services
        rospy.wait_for_service("/mavros/set_mode")
        rospy.wait_for_service("/mavros/cmd/arming")
        self.set_mode_srv = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        self.arm_srv = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        
        # Set mode to GUIDED
        self.set_mode_srv(custom_mode="GUIDED")
        
        # Arm the vehicle
        self.arm_srv(True)

    def publish_waypoints(self):
        rate = rospy.Rate(10)  # 10 Hz
        angle_step = (2 * math.pi) / (DURATION * 10)  # Adjust for smooth motion
        t = 0
        
        while not rospy.is_shutdown():
            angle = t * angle_step
            twist = TwistStamped()
            twist.header.stamp = rospy.Time.now()
            twist.twist.linear.x = SPEED * math.cos(angle)  # X velocity
            twist.twist.linear.y = SPEED * math.sin(angle)  # Y velocity
            twist.twist.linear.z = 0.0  # Maintain depth
            
            self.vel_pub.publish(twist)
            t += 1
            rate.sleep()

if __name__ == "__main__":
    try:
        traj = CircularTrajectory()
        traj.publish_waypoints()
    except rospy.ROSInterruptException:
        pass
