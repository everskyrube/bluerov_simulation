import rospy
from mavros_msgs.msg import OverrideRCIn

# Define RC PWM range
RC_MIN = 1100
RC_MAX = 1900
RC_NEUTRAL = 1500

class ThrusterController:
    def __init__(self):
        rospy.init_node('thruster_controller', anonymous=True)
        self.thruster_pub = rospy.Publisher('/mavros/rc/override', OverrideRCIn, queue_size=10)
        rospy.sleep(1)
        rospy.loginfo("Thruster Controller Initialized with 6 Thrusters")

    def send_thruster_commands(self, thruster_values):
        rc_msg = OverrideRCIn()

        # Map the 6-thruster configuration
        rc_msg.channels[0] = thruster_values[0]  # Thruster 1
        rc_msg.channels[1] = thruster_values[1]  # Thruster 2
        rc_msg.channels[2] = thruster_values[2]  # Thruster 3
        rc_msg.channels[3] = thruster_values[3]  # Thruster 4
        rc_msg.channels[4] = thruster_values[4]  # Thruster 5
        rc_msg.channels[5] = thruster_values[5]  # Thruster 6
        
        # Disable other channels (7 and 8 are unused in 6-thruster config)
        rc_msg.channels[6] = RC_NEUTRAL  
        rc_msg.channels[7] = RC_NEUTRAL  

        # Publish thruster values
        self.thruster_pub.publish(rc_msg)

        # Print sent values
        rospy.loginfo(f"Sent Thruster Commands: {thruster_values}")

if __name__ == '__main__':
    controller = ThrusterController()
    rate = rospy.Rate(10)  # 10 Hz
    
    while not rospy.is_shutdown():
        # Example thruster commands (Neutral + small changes for testing)
        thrusters = [1500, 1550, 1450, 1500, 1550, 1450]  # Example PWM values
        controller.send_thruster_commands(thrusters)
        rate.sleep()
