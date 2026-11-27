from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    sensor_node = Node(
        package='water_monitoring',
        executable='sensor_node',
        name='sensor_node',
        output='screen'
    )

    gps_node = Node(
        package='water_monitoring',
        executable='gps_node',
        name='gps_node',
        output='screen'
    )

    monitor_node = Node(
        package='water_monitoring',
        executable='monitor_node',
        name='monitor_node',
        output='screen'
    )

    calibration_server = Node(
        package='water_monitoring',
        executable='calibration_server',
        name='calibration_server',
        output='screen'
    )

    sampling_action_server = Node(
        package='water_monitoring',
        executable='sampling_action_server',
        name='sampling_action_server',
        output='screen'
    )

    return LaunchDescription([
        sensor_node,
        gps_node,
        monitor_node,
        calibration_server,
        sampling_action_server
    ])
