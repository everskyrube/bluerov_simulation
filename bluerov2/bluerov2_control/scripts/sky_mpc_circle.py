#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import WrenchStamped
from mavros_msgs.srv import SetMode, CommandBool
from mavros_msgs.msg import State

# Define Circle Parameters
RADIUS = 2.0  # Meters
ALTITUDE = -2.0  # Depth in meters
SPEED = 0.2  # Speed in m/s
DURATION = 30  # Time to complete the circle

class MPC_Circle:
    def __init__(self):
        rospy.init_node("mpc_circle_control", anonymous=True)
        
        # Publishers
        self.wrench_pub = rospy.Publisher("/thruster_manager/input", WrenchStamped, queue_size=10)
        
        # Services
        rospy.wait_for_service("/mavros/set_mode")
        rospy.wait_for_service("/mavros/cmd/arming")
        self.set_mode_srv = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        self.arm_srv = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        
        # Subscribe to MAVROS state to check mode
        rospy.Subscriber("/mavros/state", State, self.state_callback)
        self.current_state = None
        
        # Set mode to GUIDED
        self.set_mode_srv(custom_mode="GUIDED")
        
        # Arm the vehicle
        self.arm_srv(True)
    
    def state_callback(self, msg):
        self.current_state = msg

    def publish_wrench(self):
        rate = rospy.Rate(10)  # 10 Hz
        angle_step = (2 * math.pi) / (DURATION * 10)  # Smoother motion
        t = 0
        
        while not rospy.is_shutdown():
            if self.current_state and self.current_state.mode != "GUIDED":
                rospy.logwarn("Vehicle is not in GUIDED mode! Trying to set it.")
                self.set_mode_srv(custom_mode="GUIDED")
                rate.sleep()
                continue

            angle = t * angle_step
            wrench = WrenchStamped()
            wrench.header.stamp = rospy.Time.now()
            wrench.header.frame_id = "base_link"
            
            # Force command may only work in MANUAL mode
            # Compute force components for circular motion
            wrench.wrench.force.x = SPEED * math.cos(angle) * 5 # Forward force
            wrench.wrench.force.y = SPEED * math.sin(angle) * 5 # Side force
            wrench.wrench.force.z = 0.0  # Maintain depth
            
            # Generate yaw torque for smooth turning
            wrench.wrench.torque.z = 0.05 * math.sin(angle)  # Adjust yaw rotation
            
            rospy.loginfo(f"Publishing Wrench: Fx={wrench.wrench.force.x}, Fy={wrench.wrench.force.y}, Tz={wrench.wrench.torque.z}")
            
            self.wrench_pub.publish(wrench)
            t += 1
            rate.sleep()

if __name__ == "__main__":
    try:
        circle_control = MPC_Circle()
        circle_control.publish_wrench()
    except rospy.ROSInterruptException:
        pass