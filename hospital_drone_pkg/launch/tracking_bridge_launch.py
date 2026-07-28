from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Clock
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='clock_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
            output='screen',
        ),
        # IMU Bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='imu_bridge',
            arguments=[
                '/world/finalproject1/model/x500_0/link/base_link/sensor/imu_sensor/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'
            ],
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),

        # GPS Bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='gps_bridge',
            arguments=[
                '/world/finalproject1/model/x500_0/link/base_link/sensor/navsat_sensor/navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat'
            ],
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
        # Pose (already working)
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='pose_bridge',
            arguments=[
                '/world/finalproject1/dynamic_pose/info@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
            ],
            output='screen',
        ),

        # Camera (keep if needed)
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='camera_bridge',
            arguments=[
                '/world/finalproject1/model/x500_0/link/camera_link/sensor/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
                '/world/finalproject1/model/x500_0/link/camera_link/sensor/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            ],
            output='screen',
        ),

        # Your drone tracker
        Node(
            package='hospital_drone_pkg',
            executable='drone_tracker',
            name='drone_tracker',
            output='screen',
        ),
    ])
