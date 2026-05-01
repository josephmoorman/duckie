#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState
from duckietown_msgs.msg import AprilTagDetectionArray

class Target_Follower:
    def __init__(self):
        
        # Initialize ROS node
        rospy.init_node('target_follower_node', anonymous=True)

        # Shutdown safety
        rospy.on_shutdown(self.clean_shutdown)
        
        # Publisher and Subscriber using robot name deakinbot
        self.cmd_vel_pub = rospy.Publisher('/deakinbot/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/deakinbot/apriltag_detector_node/detections', AprilTagDetectionArray, self.tag_callback, queue_size=1)

        rospy.spin()

    # Callback for AprilTag detections
    def tag_callback(self, msg):
        self.move_robot(msg.detections)
 
    # Shutdown function
    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    # Stop robot completely
    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    # Main movement logic
    def move_robot(self, detections):

        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0   # No forward/backward movement required

        # =========================================
        # FEATURE 1: SEEK AN OBJECT
        # =========================================
        if len(detections) == 0:
            rospy.loginfo("No AprilTag detected - seeking object")
            cmd_msg.omega = 0.3   # slow in-place rotation
            self.cmd_vel_pub.publish(cmd_msg)
            return

        # =========================================
        # FEATURE 2: LOOK AT THE OBJECT
        # =========================================
        x = detections[0].transform.translation.x
        y = detections[0].transform.translation.y
        z = detections[0].transform.translation.z

        rospy.loginfo("AprilTag position x,y,z: %f %f %f", x, y, z)

        # Keep object centered using x value
        if abs(x) < 0.02:
            cmd_msg.omega = 0.0
            rospy.loginfo("Object centered - holding position")

        elif x > 0.02:
            cmd_msg.omega = -0.4
            rospy.loginfo("Object offset detected - rotating toward target")

        else:
            cmd_msg.omega = 0.4
            rospy.loginfo("Object offset detected - rotating toward target")

        self.cmd_vel_pub.publish(cmd_msg)

if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass
