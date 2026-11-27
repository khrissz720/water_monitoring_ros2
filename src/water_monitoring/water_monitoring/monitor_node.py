import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import HistoryPolicy

from rcl_interfaces.msg import SetParametersResult

from water_interfaces.msg import WaterQuality


class MonitorNode(Node):

    def __init__(self):
        super().__init__('monitor_node')

        # =====================================
        # PARAMETROS DINAMICOS
        # =====================================

        self.declare_parameter('ph_min', 6.5)
        self.declare_parameter('ph_max', 8.5)

        self.declare_parameter('turbidity_max', 50.0)

        self.declare_parameter('mercury_max', 0.002)
        self.declare_parameter('lead_max', 0.01)
        self.declare_parameter('cadmium_max', 0.003)

        # Configurar callback de parametros
        self.add_on_set_parameters_callback(
            self.parameter_callback
        )

        # =====================================
        # CONFIGURACION QoS
        # =====================================

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # =====================================
        # SUSCRIPTOR
        # =====================================

        self.subscription = self.create_subscription(
            WaterQuality,
            '/water_quality',
            self.water_callback,
            qos
        )

        self.get_logger().info(
            'Monitor de calidad del agua iniciado.'
        )

        self.get_logger().info(
            'Parametros dinamicos habilitados.'
        )

    # =====================================
    # VALIDACION DE PARAMETROS
    # =====================================

    def parameter_callback(self, parameters):

        values = {
            'ph_min': self.get_parameter('ph_min').value,
            'ph_max': self.get_parameter('ph_max').value,
            'turbidity_max': self.get_parameter('turbidity_max').value,
            'mercury_max': self.get_parameter('mercury_max').value,
            'lead_max': self.get_parameter('lead_max').value,
            'cadmium_max': self.get_parameter('cadmium_max').value
        }

        for parameter in parameters:

            if parameter.name not in values:
                continue

            if parameter.type_ != parameter.Type.DOUBLE:
                return SetParametersResult(
                    successful=False,
                    reason='El parametro debe ser numerico.'
                )

            if parameter.value < 0:
                return SetParametersResult(
                    successful=False,
                    reason='No se permiten valores negativos.'
                )

            values[parameter.name] = parameter.value

        if values['ph_min'] >= values['ph_max']:
            return SetParametersResult(
                successful=False,
                reason='ph_min debe ser menor que ph_max.'
            )

        return SetParametersResult(
            successful=True,
            reason='Parametros actualizados correctamente.'
        )

    # =====================================
    # MONITOREO DE CALIDAD DEL AGUA
    # =====================================

    def water_callback(self, msg):

        ph_min = self.get_parameter('ph_min').value
        ph_max = self.get_parameter('ph_max').value

        turbidity_max = self.get_parameter(
            'turbidity_max'
        ).value

        mercury_max = self.get_parameter(
            'mercury_max'
        ).value

        lead_max = self.get_parameter(
            'lead_max'
        ).value

        cadmium_max = self.get_parameter(
            'cadmium_max'
        ).value

        alerts = []

        if msg.ph < ph_min or msg.ph > ph_max:
            alerts.append('pH fuera del rango permitido')

        if msg.turbidity > turbidity_max:
            alerts.append('Turbidez elevada')

        if msg.mercury > mercury_max:
            alerts.append('Mercurio elevado')

        if msg.lead > lead_max:
            alerts.append('Plomo elevado')

        if msg.cadmium > cadmium_max:
            alerts.append('Cadmio elevado')

        print('\n' + '=' * 55)

        print('ESTACION ACUATICA - MONITOREO DE CALIDAD')

        print('=' * 55)

        print(
            f'Latitud: {msg.latitude:.6f} | '
            f'Longitud: {msg.longitude:.6f}'
        )

        print(f'pH: {msg.ph:.2f}')
        print(f'Turbidez: {msg.turbidity:.2f} NTU')
        print(f'Temperatura: {msg.temperature:.2f} °C')

        print(f'Mercurio: {msg.mercury:.5f} mg/L')
        print(f'Plomo: {msg.lead:.5f} mg/L')
        print(f'Cadmio: {msg.cadmium:.5f} mg/L')

        if alerts:

            print('\nESTADO: ALERTA DE CONTAMINACION')

            for alert in alerts:
                print(f'[ALERTA] {alert}')

        else:

            print('\nESTADO: CONDICIONES NORMALES')

        print('=' * 55)


def main(args=None):

    rclpy.init(args=args)

    node = MonitorNode()

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