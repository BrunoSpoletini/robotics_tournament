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


    declarar_sigma = DeclareLaunchArgument(
        'sigma_sensor', default_value='0.2',
        description='Ancho (m) del halo de probabilidad alrededor de cada pared.')
    declarar_particulas = DeclareLaunchArgument(
        'num_particulas', default_value='300',
        description='Cantidad de partículas del filtro.')
    declarar_gamma = DeclareLaunchArgument(
        'gamma', default_value='0.0025',
        description='Varianza de ruido del modelo de movimiento (gamma1-gamma6).')
    declarar_escala_avance = DeclareLaunchArgument(
        'escala_avance', default_value='1.0',
        description='Escala de correccion sobre el avance de la odometria.')
    declarar_escala_giro = DeclareLaunchArgument(
            'escala_giro', default_value='1.0',
            description='Escala de correccion sobre el giro de la odometria.')
    declarar_umbral = DeclareLaunchArgument(
            'umbral_probabilidad', default_value='25.0',
            description='Probabilidad (0-100) por debajo de la cual un punto es "no mapeado".')
    declarar_racha = DeclareLaunchArgument(
        'racha_minima', default_value='3',
        description='Puntos contiguos mínimos para que una racha cuente como objeto.')
    declarar_distancia = DeclareLaunchArgument(
        'distancia_minima_valida', default_value='0.25',
        description='Rango mínimo (m) válido, para filtrar el rebote contra el propio robot.')

    parametros = [declarar_sigma,
         declarar_particulas,
         declarar_gamma,
         declarar_escala_avance,
         declarar_escala_giro,
         declarar_umbral,
         declarar_racha,
         declarar_distancia]


    # # TODO - SACAR CUANDO TERMINEMOS DE TESTEAR
    # launch_mapa = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         PathJoinSubstitution([FindPackageShare('mapa_laberinto'), 'launch', 'mapa.launch.py'])
    #     ),
    #     launch_arguments={'use_sim_time': 'true'}.items(),
    # )

    # tf2_ros = Node(
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     name='static_transform_publisher',
    #     output='screen',
    #     arguments=['--frame-id', 'map', '--child-frame-id', 'odom'],
    #     parameters=[
    #         {'use_sim_time': True}
    #     ],
    # )

    campo_verosimilitud = Node(
        package='localizacion',
        executable='campo_verosimilitud',
        name='campo_verosimilitud',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'sigma_sensor': ParameterValue(
                LaunchConfiguration('sigma_sensor'), value_type=float),
        }],
    )

    gamma = ParameterValue(LaunchConfiguration('gamma'), value_type=float)

    localizador = Node(
        package='localizacion',
        executable='localizador',
        name='localizador',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'escala_avance': ParameterValue(LaunchConfiguration('escala_avance'), value_type=float),
            'escala_giro': ParameterValue(LaunchConfiguration('escala_giro'), value_type=float),
            'num_particulas': ParameterValue(
                LaunchConfiguration('num_particulas'), value_type=int),
            'gamma1': gamma,
            'gamma2': gamma,
            'gamma3': gamma,
            'gamma4': gamma,
            'gamma5': gamma,
            'gamma6': gamma,
        }],
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

   # Hasta que localizador publique la primera map → odom, este nodo avisa
    # "Todavía no hay tf" y descarta los scans; después arranca solo.
    detector_obstaculos = Node(
        package='obstaculos_no_mapeados',
        executable='obstaculos_no_mapeados',
        name='detector_obstaculos',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'umbral_probabilidad': ParameterValue(
                LaunchConfiguration('umbral_probabilidad'), value_type=float),
            'racha_minima': ParameterValue(
                LaunchConfiguration('racha_minima'), value_type=int),
            'distancia_minima_valida': ParameterValue(
                LaunchConfiguration('distancia_minima_valida'), value_type=float),
        }],
    )

    juntar_victimas = Node(
        package = 'evaluador_victimas',
        executable='juntar_victimas',
        name='juntar_victimas',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ],
    )

    # medir_odometria = Node(
    #     package='evaluador_victimas',
    #     executable='medir_odometria',
    #     name='medir_odometria',
    #     output='screen',
    #     parameters=[
    #         {'use_sim_time': True}
    #     ],
    # )

    # corregir_odom = Node(
    #     package='evaluador_victimas',
    #     executable='odom_corregida',
    #     name='odom_corregida',
    #     output='screen',
    #     parameters=[{
    #         'escala_avance': 0.8,
    #         'escala_giro': -0.8,
    #         'use_sim_time': True
    #     }]
    # )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', config_rviz],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        declarar_sigma,
        declarar_particulas,
        declarar_gamma,
        declarar_escala_avance,
        declarar_escala_giro,
        declarar_umbral,
        declarar_racha,
        declarar_distancia,
        localizador,
        campo_verosimilitud,
        detector,
        detector_scan,
        detector_obstaculos,
        juntar_victimas,
        rviz,
    ])
