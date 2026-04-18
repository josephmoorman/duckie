#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class Drive_Square:
    def __init__(self):
        # Initialize message
        self.cmd_msg = Twist2DStamped()

        # Prevent multiple runs
        self.running = False

        # Initialize ROS node
        rospy.init_node('drive_square_node', anonymous=True)

        # Publishers and Subscribers (NO hardcoded robot name)
        self.pub = rospy.Publisher('car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('fsm_node/mode', FSMState, self.fsm_callback, queue_size=1)

    # FSM callback
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.running = False
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING" and not self.running:
            self.running = True
            rospy.sleep(1)  # small delay
            self.move_robot()

    # Stop robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    # Keep node alive
    def run(self):
        rospy.spin()

    # Square movement
    def move_robot(self):

        rospy.loginfo("Starting square motion")

        for i in range(4):

            # Move forward
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.3
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Forward")
            rospy.sleep(6)   # 🔧 adjust for distance

            self.stop_robot()
            rospy.sleep(0.5)

            # Turn 90 degrees
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = 4.0
            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Turning")
            rospy.sleep(1.5)   # 🔧 adjust for 90° turn

            self.stop_robot()
            rospy.sleep(0.5)

        rospy.loginfo("Square complete")
        self.stop_robot()


if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
