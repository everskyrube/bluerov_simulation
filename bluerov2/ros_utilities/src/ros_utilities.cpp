#include "ros_utilities/ros_utilities.h"

RosUtilities::RosUtilities() {

}

Eigen::Vector3d RosUtilities::q2rpy(const Eigen::Quaterniond& q)
{
    tfScalar yaw, pitch, roll;
    tf::Quaternion q_tf;
    q_tf.setW(q.w());
    q_tf.setX(q.x());
    q_tf.setY(q.y());
    q_tf.setZ(q.z());

    tf::Matrix3x3 mat(q_tf);
    mat.getEulerYPR(yaw, pitch, roll);

    return Eigen::Vector3d(roll, pitch, yaw);
}

Eigen::Quaterniond RosUtilities::rpy2q(const Eigen::Vector3d& rpy)
{
    Eigen::AngleAxisd rollAngle(rpy(0), Eigen::Vector3d::UnitX());
    Eigen::AngleAxisd pitchAngle(rpy(1), Eigen::Vector3d::UnitY());
    Eigen::AngleAxisd yawAngle(rpy(2), Eigen::Vector3d::UnitZ());

    Eigen::Quaterniond q = yawAngle * pitchAngle * rollAngle;

    return q;
}

Eigen::Vector3d RosUtilities::q_rotate_vector(
    const Eigen::Quaterniond& q, 
    const Eigen::Vector3d& v
)
{
    return q * v;
}

nav_msgs::Odometry RosUtilities::SE3_to_odommsg(
    const Sophus::SE3d& pose_on_SE3,
    const Sophus::Vector6d& velo,
    const std_msgs::Header& msgHeader
)
{
    nav_msgs::Odometry returnOdomMsg;
    returnOdomMsg.header = msgHeader;

    // pose
    returnOdomMsg.pose.pose.position.x = pose_on_SE3.translation().x();
    returnOdomMsg.pose.pose.position.y = pose_on_SE3.translation().y();
    returnOdomMsg.pose.pose.position.z = pose_on_SE3.translation().z();

    returnOdomMsg.pose.pose.orientation.w = pose_on_SE3.unit_quaternion().w();
    returnOdomMsg.pose.pose.orientation.x = pose_on_SE3.unit_quaternion().x();
    returnOdomMsg.pose.pose.orientation.y = pose_on_SE3.unit_quaternion().y();
    returnOdomMsg.pose.pose.orientation.z = pose_on_SE3.unit_quaternion().z();

    // twist
    returnOdomMsg.twist.twist.linear.x = velo(0);
    returnOdomMsg.twist.twist.linear.y = velo(1);
    returnOdomMsg.twist.twist.linear.z = velo(2);

    returnOdomMsg.twist.twist.angular.x = velo(3);
    returnOdomMsg.twist.twist.angular.y = velo(4);
    returnOdomMsg.twist.twist.angular.z = velo(5);

    return returnOdomMsg;
}

geometry_msgs::PoseStamped RosUtilities::SE3_to_posemsg(
    const Sophus::SE3d& pose_on_SE3,
    const std_msgs::Header& msgHeader
)
{
    geometry_msgs::PoseStamped returnPoseMsg;
    returnPoseMsg.header = msgHeader;

    returnPoseMsg.pose.position.x = pose_on_SE3.translation().x();
    returnPoseMsg.pose.position.y = pose_on_SE3.translation().y();
    returnPoseMsg.pose.position.z = pose_on_SE3.translation().z();

    returnPoseMsg.pose.orientation.w = pose_on_SE3.unit_quaternion().w();
    returnPoseMsg.pose.orientation.x = pose_on_SE3.unit_quaternion().x();
    returnPoseMsg.pose.orientation.y = pose_on_SE3.unit_quaternion().y();
    returnPoseMsg.pose.orientation.z = pose_on_SE3.unit_quaternion().z();

    return returnPoseMsg;
}

Sophus::SE3d RosUtilities::posemsg_to_SE3(
    const geometry_msgs::Pose& pose
)
{
    return Sophus::SE3d(
        Eigen::Quaterniond(
            pose.orientation.w,
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z  
        ).normalized().toRotationMatrix(),
        Eigen::Translation3d(
            pose.position.x,
            pose.position.y,
            pose.position.z
        ).translation()
    );
}

Sophus::Vector6d RosUtilities::twistmsg_to_velo(
    const geometry_msgs::Twist& twist
)
{
    return (
        Sophus::Vector6d() << 
        twist.linear.x,
        twist.linear.y, 
        twist.linear.z, 
        twist.angular.x, 
        twist.angular.y, 
        twist.angular.z
    ).finished();
}

Sophus::Matrix3d RosUtilities::Jacobi3dR(const Sophus::SE3d& pose)
{
    
    Eigen::Vector3d rpy = q2rpy(pose.unit_quaternion());
    double phi = rpy(0);
    double theta = rpy(1);
    double psi = rpy(2);

    return (
        Sophus::Matrix3d() <<
            1, sin(psi)*sin(theta)/cos(theta), cos(phi)*sin(theta)/cos(theta),
            0, cos(phi), sin(phi),
            0, sin(phi)/cos(theta), cos(phi)/cos(theta)
    ).finished();
}

Sophus::Vector6d RosUtilities::imumsg_to_accl(const sensor_msgs::Imu& imu)
{
    return(
        Sophus::Vector6d() <<
            imu.linear_acceleration.x,
            imu.linear_acceleration.y,
            imu.linear_acceleration.z,
            imu.angular_velocity.x,
            imu.angular_velocity.y,
            imu.angular_velocity.z
    ).finished();
}

void RosUtilities::write_yaml(
    const Eigen::Vector3d& input_data_, 
    const std::string& yaml_filename_,
    const std::string& param_name_
) 
{
    YAML::Node yaml_config =  YAML::LoadFile(yaml_filename_);

    for(int i = 0; i < 3; i++)
        yaml_config[param_name_][i] = input_data_(i);
    

    std::ofstream yaml_of(yaml_filename_);
    yaml_of << yaml_config;

    yaml_of.close();
}