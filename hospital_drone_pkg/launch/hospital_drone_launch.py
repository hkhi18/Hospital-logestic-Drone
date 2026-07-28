from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

        Node(
            package='hospital_drone_pkg',
            executable='check_arm_service',
            name='check_arm_service',
            output='screen',
        ),
        Node(
            package='hospital_drone_pkg',
            executable='check_arm_client',
            name='check_arm_client',
            output='screen',
        ),
        Node(
            package='hospital_drone_pkg',
            executable='drone_sim',
            name='drone_sim',
            output='screen',
            parameters=[{'mission': 'helipad1_to_helipad2'}],
        ),
        Node(
            package='hospital_drone_pkg',
            executable='drone_monitor',
            name='drone_monitor',
            output='screen',
        ),
        Node(
            package='hospital_drone_pkg',
            executable='distance_sensor',
            name='distance_sensor',
            output='screen',
        ),
        Node(
            package='hospital_drone_pkg',
            executable='distance_monitor',
            name='distance_monitor',
            output='screen',
        ),
        Node(
            package='hospital_drone_pkg',
            executable='px4_bridge',
            name='px4_bridge',
            output='screen',
        ),
        Node(
    package='hospital_drone_pkg',
    executable='mavsdk_node',
    name='mavsdk_node',
    output='screen',
),
Node(
    package='hospital_drone_pkg',
    executable='mission_node',
    name='mission_node',
    output='screen',
),
Node(
    package='hospital_drone_pkg',
    executable='camera_safety_node',
    name='camera_safety_node',
    output='screen',
),
    ])
