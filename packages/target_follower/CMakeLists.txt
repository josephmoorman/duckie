cmake_minimum_required(VERSION 2.8.3)
project(target_follower)
find_package(catkin REQUIRED COMPONENTS
  std_msgs
  rospy
  roscpp
)
catkin_package()