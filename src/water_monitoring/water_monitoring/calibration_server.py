import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from std_msgs.msg import Float32MultiArray
from water_interfaces.msg import WaterQuality
from water_interfaces.srv import SensorCalibration


class CalibrationServer(Node):

    def __init__(self):
        super().__init__('calibration_server')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        calibration_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.latest_values = {
            'ph': None,
            'turbidity': None
        }

        self.calibration_offsets = {
            'ph': 0.0,
            'turbidity': 0.0
        }

        # Publicador de offsets
        self.calibration_publisher = self.create_publisher(
            Float32MultiArray,
            '/sensor_calibration',
            calibration_qos
        )

        # Suscriptor de mediciones
        self.subscription = self.create_subscription(
            WaterQuality,
            '/water_quality',
            self.water_callback,
            qos
        )

        # Servicio de calibracion
        self.service = self.create_service(
            SensorCalibration,
            '/calibrate_sensor',
            self.calibration_callback
        )

        self.get_logger().info(
            'Servidor de calibracion iniciado.'
        )

        self.get_logger().info(
            'Publicador /sensor_calibration creado.'
        )

    def water_callback(self, msg):
        self.latest_values['ph'] = msg.ph
        self.latest_values['turbidity'] = msg.turbidity

    def publish_offsets(self):

        msg = Float32MultiArray()

        msg.data = [
            float(self.calibration_offsets['ph']),
            float(self.calibration_offsets['turbidity'])
        ]

        self.calibration_publisher.publish(msg)

    def calibration_callback(self, request, response):

        sensor = request.sensor_name.lower().strip()
        reference = float(request.reference_value)

        if sensor not in ('ph', 'turbidity'):

            response.success = False
            response.calibration_offset = 0.0
            response.message = 'Sensor no reconocido. Use ph o turbidity.'

            return response

        if not math.isfinite(reference):

            response.success = False
            response.calibration_offset = 0.0
            response.message = 'Referencia no valida.'

            return response

        if sensor == 'ph' and not 0.0 <= reference <= 14.0:

            response.success = False
            response.calibration_offset = 0.0
            response.message = 'El pH debe estar entre 0 y 14.'

            return response

        if sensor == 'turbidity' and reference < 0.0:

            response.success = False
            response.calibration_offset = 0.0
            response.message = 'La turbidez no puede ser negativa.'

            return response

        measured = self.latest_values[sensor]

        if measured is None:

            response.success = False
            response.calibration_offset = 0.0
            response.message = 'Esperando mediciones del sensor.'

            return response

        correction = reference - measured

        self.calibration_offsets[sensor] += correction

        self.publish_offsets()

        response.success = True
        response.calibration_offset = float(
            self.calibration_offsets[sensor]
        )

        response.message = (
            f'Sensor {sensor} calibrado. '
            f'Medicion anterior: {measured:.4f}. '
            f'Referencia: {reference:.4f}. '
            f'Correccion aplicada: {correction:.4f}. '
            f'Offset acumulado: '
            f'{self.calibration_offsets[sensor]:.4f}.'
        )

        self.get_logger().info(response.message)

        return response


def main(args=None):

    rclpy.init(args=args)
    node = CalibrationServer()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()