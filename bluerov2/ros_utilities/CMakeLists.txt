cmake_minimum_required(VERSION 3.0.2)
project(ros_utilities)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)
## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages

find_package(catkin COMPONENTS
  nodelet
  roscpp
  std_msgs
  roslaunch
  geometry_msgs
  mavros_msgs
  cv_bridge
  image_transport
  sensor_msgs
  
  genmsg
  visualization_msgs
  tf
)

find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Sophus REQUIRED)
find_package(yaml-cpp REQUIRED)

catkin_package(
    INCLUDE_DIRS include
    LIBRARIES ros_utilities

    CATKIN_DEPENDS 
    geometry_msgs 
    mavros_msgs 
    roscpp
    std_msgs
    
)

set(Sophus_LIBRARIES libSophus.so)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  ${Sophus_INCLUDE_DIRS}
)

add_library(ros_utilities
  src/ros_utilities.cpp
)

## Specify libraries to link a library or executable target against
target_link_libraries(ros_utilities
    ${catkin_LIBRARIES}
    ${OpenCV_INCLUDE_DIRS}
    ${Sophus_INCLUDE_DIRS}
    yaml-cpp
)



