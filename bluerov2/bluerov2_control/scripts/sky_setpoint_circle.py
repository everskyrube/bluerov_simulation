#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import SetMode, CommandBool
from mavros_msgs.msg import OverrideRCIn

# Define Circle Parameters
RADIUS = 2.0  # Meters
CENTER_X = 0.0
CENTER_Y = 0.0
ALTITUDE = -1.0  # Depth in meters
POINTS = 36  # Number of waypoints for smoother motion

class CircularTrajectory:
    def __init__(self):
        rospy.init_node("circular_trajectory_node", anonymous=True)
        
        # Publishers
        self.pose_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
        
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
        rate = rospy.Rate(1)  # 1 Hz for smooth movement
        angle_step = (2 * math.pi) / POINTS
        
        while not rospy.is_shutdown():
            for i in range(POINTS):
                if self.joystick_active:
                    rospy.loginfo("Joystick input detected, pausing trajectory execution")
                    rate.sleep()
                    continue
                
                angle = i * angle_step
                pose = PoseStamped()
                pose.header.stamp = rospy.Time.now()
                pose.header.frame_id = "map"
                pose.pose.position.x = CENTER_X + RADIUS * math.cos(angle)
                pose.pose.position.y = CENTER_Y + RADIUS * math.sin(angle)
                pose.pose.position.z = ALTITUDE  # Maintain depth
                
                rospy.loginfo(f"Publishing Pose: x={pose.pose.position.x}, y={pose.pose.position.y}, z={pose.pose.position.z}")
                
                self.pose_pub.publish(pose)
                rate.sleep()

if __name__ == "__main__":
    try:
        traj = CircularTrajectory()
        traj.publish_waypoints()
    except rospy.ROSInterruptException:
        pass
