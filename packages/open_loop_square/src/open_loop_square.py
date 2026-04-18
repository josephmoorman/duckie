#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState

class Drive_Square:
    def __init__(self):
        #Initialize global class variables
        self.cmd_msg = Twist2DStamped()
        self.running = False

        #Initialize ROS node
        rospy.init_node('drive_square_node', anonymous=True)

        #Initialize Pub/Subs
        self.pub = rospy.Publisher('car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('fsm_node/mode', FSMState, self.fsm_callback, queue_size=1)

    # Robot only moves when lane following is selected on the duckiebot joystick app
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)
        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.running = False
            self.stop_robot()
        elif msg.state == "LANE_FOLLOWING" and not self.running:
            self.running = True
            rospy.sleep(1) # Wait for a sec for the node to be ready
            self.move_robot()

    # Sends zero velocities to stop the robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    # Spin forever but listen to message callbacks
    def run(self):
        rospy.spin() # keeps node from exiting until node has shutdown

    # Publishes a velocity command for a set duration at 10Hz
    def publish_for_duration(self, v, omega, duration):
        rate = rospy.Rate(10)  # 10Hz
        end_time = rospy.Time.now() + rospy.Duration(duration)
        while rospy.Time.now() < end_time:
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = v
            self.cmd_msg.omega = omega
            self.pub.publish(self.cmd_msg)
            rate.sleep()

    # Robot drives in a square and then stops
    def move_robot(self):
        rospy.loginfo("Starting square motion")

        for i in range(4):
            # Move forward
            rospy.loginfo("Forward!")
            self.publish_for_duration(v=0.3, omega=0.0, duration=3.4)  # 🔧 adjust duration for ~1m
            self.stop_robot()
            rospy.sleep(0.5)

            # Turn 90 degrees in place
            rospy.loginfo("Turning!")
            self.publish_for_duration(v=0.0, omega=4.0, duration=0.88)  # 🔧 adjust duration for 90°
            self.stop_robot()
            rospy.sleep(0.5)

        rospy.loginfo("Square complete")
        self.stop_robot()
        self.running = False

if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
