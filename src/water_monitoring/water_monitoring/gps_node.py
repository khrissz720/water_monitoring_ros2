import random

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import NavSatFix, NavSatStatus


class GPSNode(Node):

    def __init__(self):
        super().__init__('gps_node')

        # Coordenadas aproximadas de la zona de Portovelo, Ecuador
        self.base_latitude = -3.7210
        self.base_longitude = -79.6240

        # QoS
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Publisher GPS
        self.publisher_ = self.create_publisher(
            NavSatFix,
            '/gps/fix',
            qos_profile
        )

        # Publicacion cada segundo
        self.timer = self.create_timer(
            1.0,
            self.publish_position
        )

        self.get_logger().info(
            'Simulador GPS iniciado. Ubicacion: Portovelo, Ecuador.'
        )

    def publish_position(self):

        msg = NavSatFix()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'gps_link'

        msg.status.status = NavSatStatus.STATUS_FIX
        msg.status.service = NavSatStatus.SERVICE_GPS

        # Pequena variacion para simular lecturas GPS
        msg.latitude = self.base_latitude + random.uniform(-0.0005, 0.0005)
        msg.longitude = self.base_longitude + random.uniform(-0.0005, 0.0005)
        msg.altitude = 600.0 + random.uniform(-2.0, 2.0)

        # Incertidumbre simulada del receptor GPS
        msg.position_covariance = [
            4.0, 0.0, 0.0,
            0.0, 4.0, 0.0,
            0.0, 0.0, 9.0
        ]

        msg.position_covariance_type = (
            NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN
        )

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'GPS | Latitud: {msg.latitude:.6f} | '
            f'Longitud: {msg.longitude:.6f} | '
            f'Altitud: {msg.altitude:.2f} m'
        )


def main(args=None):

    rclpy.init(args=args)

    node = GPSNode()

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