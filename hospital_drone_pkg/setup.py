from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'hospital_drone_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hanin',
    maintainer_email='hanin@todo.todo',
    description='Hospital Drone Package',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'drone_sim            = hospital_drone_pkg.drone_sim:main',
            'drone_monitor        = hospital_drone_pkg.drone_monitor:main',
            'distance_sensor      = hospital_drone_pkg.distance_sensor:main',
            'distance_monitor     = hospital_drone_pkg.distance_monitor:main',
            'check_arm_service    = hospital_drone_pkg.check_arm_service:main',
            'check_arm_client     = hospital_drone_pkg.check_arm_client:main',
            'drone_action_server  = hospital_drone_pkg.drone_action_server:main',
            'drone_action_client  = hospital_drone_pkg.drone_action_client:main',
            'px4_bridge           = hospital_drone_pkg.px4_bridge:main',
            'drone_tracker = hospital_drone_pkg.drone_tracker:main',
            'mavsdk_node = hospital_drone_pkg.mavsdk_node:main',
            'mission_node = hospital_drone_pkg.mission_node:main',
           'camera_safety_node = hospital_drone_pkg.camera_safety_node:main',


        ],
    },
)
