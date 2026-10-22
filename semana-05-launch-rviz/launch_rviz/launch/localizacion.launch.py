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
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_sim = get_package_share_directory('yahboom_rosmaster_bringup')
    pkg_gazebo = get_package_share_directory('yahboom_rosmaster_gazebo')
    pkg_launch_rviz = get_package_share_directory('launch_rviz')

    launch_simulador = os.path.join(
        pkg_sim, 'launch', 'rosmaster_x3_sim.launch.py')
    # El mundo y el mapa tienen que corresponderse: el .yaml es el que se
    # generó mapeando justamente ese .world.
    mundo_por_defecto = os.path.join(pkg_gazebo, 'worlds', 'laberinto_simple.world')
    mapa_por_defecto = os.path.join(pkg_gazebo, 'maps', 'laberinto_simple.yaml')
    config_rviz = os.path.join(pkg_launch_rviz, 'rviz', 'localizacion.rviz')

    declarar_world = DeclareLaunchArgument(
        'world', default_value=mundo_por_defecto,
        description='Ruta al .world de Gazebo que se va a cargar.')
    declarar_mapa = DeclareLaunchArgument(
        'map', default_value=mapa_por_defecto,
        description='Ruta al .yaml del mapa que sirve map_server.')
    declarar_sigma = DeclareLaunchArgument(
        'sigma_sensor', default_value='0.2',
        description='Ancho (m) del halo de probabilidad alrededor de cada pared.')
    declarar_particulas = DeclareLaunchArgument(
        'num_particulas', default_value='300',
        description='Cantidad de partículas del filtro.')
    declarar_gamma = DeclareLaunchArgument(
        'gamma', default_value='0.0025',
        description='Varianza de ruido del modelo de movimiento (gamma1-gamma6).')

    simulador = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_simulador),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'motion_profile': 'ideal',
            'rviz': 'false',
        }.items(),
    )

    # map_server es un nodo lifecycle: arranca sin publicar nada y espera que
    # alguien lo pase a configure → activate. Eso lo hace lifecycle_manager
    # con autostart=True, igual que en la Terminal 3 del README.
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'yaml_filename': LaunchConfiguration('map'),
        }],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localizacion',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server'],
        }],
    )

    # No hace falta esperar a que map_server esté activo antes de arrancar
    # estos dos: /map y /likelihood_map son transient local, así que cada
    # suscriptor recibe el último mensaje aunque se conecte tarde.
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

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', config_rviz],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        declarar_world,
        declarar_mapa,
        declarar_sigma,
        declarar_particulas,
        declarar_gamma,
        simulador,
        map_server,
        lifecycle_manager,
        campo_verosimilitud,
        localizador,
        rviz,
    ])
