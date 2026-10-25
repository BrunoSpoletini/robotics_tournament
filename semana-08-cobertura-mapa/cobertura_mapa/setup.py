from glob import glob

from setuptools import find_packages, setup

package_name = 'cobertura_mapa'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='bruno_spoletini@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'cobertura_mapa = cobertura_mapa.explorador:main',
            'cobertura_mapa_node = cobertura_mapa.grilla_cobertura:main',
            'cobertura_mapa_publisher = cobertura_mapa.planificador:main',
            'cobertura_mapa_subscriber = cobertura_mapa.trazado:main',
        ],
    },
)
