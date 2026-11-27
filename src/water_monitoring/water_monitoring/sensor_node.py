import random

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from std_msgs.msg import Float32MultiArray
from water_interfaces.msg import WaterQuality
from sensor_msgs.msg import NavSatFix


class SensorNode(Node):

    def __init__(self):
        super().__init__('sensor_node')

        self.declare_parameter('sampling_period', 1.0)

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

        self.ph_offset = 0.0
        self.turbidity_offset = 0.0

        self.publisher_ = self.create_publisher(
            WaterQuality,
            '/water_quality',
            qos
        )

        self.gps_subscription = self.create_subscription(
            NavSatFix,
            '/gps/fix',
            self.gps_callback,
            qos
        )

        self.calibration_subscription = self.create_subscription(
            Float32MultiArray,
            '/sensor_calibration',
            self.calibration_callback,
            calibration_qos
        )

        self.latitude = -3.7210
        self.longitude = -79.6240
        self.gps_received = False

        period = self.get_parameter('sampling_period').value

        self.timer = self.create_timer(
            period,
            self.publish_measurements
        )

        self.get_logger().info('Nodo de sensores iniciado.')
        self.get_logger().info('Suscrito a /sensor_calibration.')

    def gps_callback(self, msg):
        self.latitude = msg.latitude
        self.longitude = msg.longitude
        self.gps_received = True

    def calibration_callback(self, msg):

        if len(msg.data) < 2:
            return

        self.ph_offset = float(msg.data[0])
        self.turbidity_offset = float(msg.data[1])

        self.get_logger().info(
            f'Offsets actualizados: pH={self.ph_offset:.4f}, '
            f'Turbidez={self.turbidity_offset:.4f}'
        )

    def publish_measurements(self):

        msg = WaterQuality()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'water_station'

        raw_ph = random.uniform(6.0, 9.0)
        raw_turbidity = random.uniform(1.0, 80.0)

        msg.ph = raw_ph + self.ph_offset

        msg.turbidity = max(
            0.0,
            raw_turbidity + self.turbidity_offset
        )

        msg.temperature = random.uniform(18.0, 35.0)

        msg.mercury = random.uniform(0.0001, 0.005)
        msg.lead = random.uniform(0.001, 0.05)
        msg.cadmium = random.uniform(0.0001, 0.01)

        msg.latitude = self.latitude
        msg.longitude = self.longitude

        msg.contamination_detected = (
            msg.ph < 6.5 or
            msg.ph > 8.5 or
            msg.turbidity > 50.0 or
            msg.mercury > 0.002 or
            msg.lead > 0.01 or
            msg.cadmium > 0.003
        )

        self.publisher_.publish(msg)

        gps_status = 'GPS OK' if self.gps_received else 'GPS esperando'

        self.get_logger().info(
            f'pH: {msg.ph:.2f} | '
            f'Turbidez: {msg.turbidity:.2f} NTU | '
            f'Temperatura: {msg.temperature:.2f} C | '
            f'Ubicacion: ({msg.latitude:.6f}, {msg.longitude:.6f}) | '
            f'{gps_status} | '
            f'Contaminacion: {msg.contamination_detected}'
        )


def main(args=None):

    rclpy.init(args=args)
    node = SensorNode()

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