from setuptools import setup
from glob import glob
import os

package_name = 'water_monitoring'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andry Ortega',
    maintainer_email='andry@todo.todo',
    description='Nodos ROS 2 para monitoreo de calidad del agua.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
    'console_scripts': [
        'sensor_node = water_monitoring.sensor_node:main',
        'monitor_node = water_monitoring.monitor_node:main',
        'gps_node = water_monitoring.gps_node:main',
        'calibration_server = water_monitoring.calibration_server:main',
        'sampling_action_server = water_monitoring.sampling_action_server:main',
        'control_station = water_monitoring.control_station:main',
    ],
},
)
