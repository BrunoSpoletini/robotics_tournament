"""
Semana 06 — launch de localización con filtro de partículas.

Reemplaza las seis terminales de la semana 06 (simulador, map_server,
lifecycle_manager, campo_verosimilitud + localizador, RViz) por un solo
comando:

    ros2 launch launch_rviz localizacion.launch.py

teleop_twist_keyboard queda afuera a propósito: necesita una terminal propia
para leer el teclado, así que se sigue corriendo a mano:

    ros2 run teleop_twist_keyboard teleop_twist_keyboard
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (LaunchConfiguration, PathJoinSubstitution)
from launch_ros.substitutions import FindPackageShare

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_launch_rviz = get_package_share_directory('launch_rviz')

    config_rviz = os.path.join(pkg_launch_rviz, 'rviz', 'realrobot.rviz')

    # # TODO - SACAR CUANDO TERMINEMOS DE TESTEAR
    # launch_mapa = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         PathJoinSubstitution([FindPackageShare('mapa_laberinto'), 'launch', 'mapa.launch.py'])
    #     ),
    #     launch_arguments={'use_sim_time': 'true'}.items(),
    # )

    tf2_ros = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='screen',
        arguments=['--frame-id', 'map', '--child-frame-id', 'odom'],
        parameters=[
            {'use_sim_time': True}
        ],
    )

    detector = Node(
        package='deteccion_color',
        executable='detector',
        name='detector',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ],
    )

    detector_scan = Node(
        package='deteccion_color',
        executable='detector_scan',
        name='detector_scan',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ],
    )

    medir_odometria = Node(
        package='evaluador_victimas',
        executable='medir_odometria',
        name='medir_odometria',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ],
    )

    parametros_odom = [{'escala_avance': 0.8,
        'escala_giro': -0.8,
        'use_sim_time': True}]

    corregir_odom = Node(
        package='evaluador_victimas',
        executable='odom_corregida',
        name='odom_corregida',
        output='screen',
        parameters=parametros_odom
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', config_rviz],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        tf2_ros,
        detector,
        detector_scan,
        medir_odometria,
        corregir_odom,
        rviz,
    ])
