#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg_andino_gz = get_package_share_directory('andino_gz')

    ros_bridge_arg = DeclareLaunchArgument(
        'ros_bridge', default_value='false', description = 'Run ROS bridge node.')
    rviz_arg = DeclareLaunchArgument('rviz', default_value='false', description='Start RViz.')
    world_name_arg = DeclareLaunchArgument('world_name', default_value='depot.sdf', description='Name of the world to load.')

    world_name = LaunchConfiguration('world_name')
    world_path = PathJoinSubstitution([pkg_andino_gz, 'worlds', world_name])

    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': world_path}.items(),
    )

    # Spawn the robot and the Robot State Publisher node.
    spawn_robot_and_rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_andino_gz, 'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={
            'entity': 'andino',
            'initial_pose_x': '0',
            'initial_pose_y': '0',
            'initial_pose_z': '0.1',
            'initial_pose_yaw': '0',
            'robot_description_topic': '/robot_description',
            'use_sim_time': 'true',
        }.items(),
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_andino_gz, 'rviz', 'andino_gz.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # Run ros_gz bridge
    ros_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_andino_gz, 'launch', 'gz_ros_bridge.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('ros_bridge'))
    )

    return LaunchDescription(
        [
            # Arguments and Nodes
            ros_bridge_arg,
            rviz_arg,
            world_name_arg,
            gazebo,
            ros_bridge,
            spawn_robot_and_rsp,
            rviz,
        ]
    )
