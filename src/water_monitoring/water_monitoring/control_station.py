import threading

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient

from water_interfaces.srv import SensorCalibration
from water_interfaces.action import Sampling


class ControlStation(Node):

    def __init__(self):
        super().__init__('control_station')

        # Cliente del servicio de calibracion
        self.calibration_client = self.create_client(
            SensorCalibration,
            '/calibrate_sensor'
        )

        # Cliente de la accion de recoleccion
        self.sampling_client = ActionClient(
            self,
            Sampling,
            '/collect_sample'
        )

        self.get_logger().info('Estacion de control iniciada.')

    # Esperar resultados de operaciones asincronas
    def wait_for_future(self, future, timeout):

        event = threading.Event()
        future.add_done_callback(lambda _: event.set())

        if not event.wait(timeout):
            raise TimeoutError('Tiempo de espera agotado.')

        return future.result()

    # Calibracion de sensores
    def calibrate_sensor(self, sensor_name, reference_value):

        self.get_logger().info(
            f'Solicitando calibracion del sensor: {sensor_name}'
        )

        if not self.calibration_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(
                'El servicio /calibrate_sensor no esta disponible.'
            )
            return

        request = SensorCalibration.Request()
        request.sensor_name = sensor_name
        request.reference_value = float(reference_value)

        future = self.calibration_client.call_async(request)

        response = self.wait_for_future(future, 30.0)

        if response.success:
            print('\n========== CALIBRACION EXITOSA ==========')
            print(f'Sensor: {sensor_name}')
            print(f'Offset: {response.calibration_offset:.4f}')
            print(f'Mensaje: {response.message}')
            print('=========================================')
        else:
            print('\nERROR EN LA CALIBRACION')
            print(response.message)

    # Mostrar progreso de recoleccion
    def feedback_callback(self, feedback_msg):

        feedback = feedback_msg.feedback

        print(
            f'\rProfundidad: {feedback.current_depth:.2f} m | '
            f'Progreso: {feedback.collection_percentage:.0f}% | '
            f'Estado: {feedback.actuator_status}       ',
            end='',
            flush=True
        )

    # Solicitar recoleccion de muestra
    def collect_sample(self, target_depth, sample_volume):

        self.get_logger().info(
            'Esperando servidor de recoleccion...'
        )

        if not self.sampling_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                'El servidor /collect_sample no esta disponible.'
            )
            return

        goal = Sampling.Goal()
        goal.target_depth = float(target_depth)
        goal.sample_volume = float(sample_volume)

        self.get_logger().info(
            'Enviando solicitud de recoleccion...'
        )

        future = self.sampling_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        goal_handle = self.wait_for_future(future, 15.0)

        if not goal_handle.accepted:
            print('\nLa solicitud de recoleccion fue rechazada.')
            return

        print('\nSolicitud aceptada. Iniciando recoleccion...')

        result_future = goal_handle.get_result_async()

        wrapped_result = self.wait_for_future(
            result_future,
            120.0
        )

        result = wrapped_result.result

        print('\n\n========== RESULTADO DE RECOLECCION ==========')
        print(f'Estado: {wrapped_result.status}')
        print(f'Exito: {result.success}')
        print(f'Volumen recolectado: {result.collected_volume:.2f} ml')
        print(f'Mensaje: {result.message}')
        print('================================================')

    # Menu principal
    def show_menu(self):

        while rclpy.ok():

            print('\n')
            print('=' * 48)
            print('          ESTACION ACUATICA AUTONOMA')
            print('                SISTEMA DE CONTROL')
            print('=' * 48)
            print('1. Calibrar sensor')
            print('2. Recolectar muestra de agua')
            print('3. Salir')
            print('=' * 48)

            option = input('Seleccione una opcion: ').strip()

            try:

                if option == '1':

                    print('\nSensores disponibles:')
                    print('- ph')
                    print('- turbidity')
                    print('- temperature')

                    sensor = input(
                        'Ingrese el nombre del sensor: '
                    ).strip().lower()

                    if sensor not in [
                        'ph',
                        'turbidity',
                        'temperature'
                    ]:
                        print('Sensor no valido.')
                        continue

                    reference = float(
                        input('Ingrese el valor de referencia: ')
                    )

                    self.calibrate_sensor(sensor, reference)

                elif option == '2':

                    depth = float(
                        input('Profundidad objetivo (m): ')
                    )

                    volume = float(
                        input('Volumen de muestra (ml): ')
                    )

                    if depth <= 0 or depth > 20:
                        print(
                            'La profundidad debe estar entre 0 y 20 m.'
                        )
                        continue

                    if volume <= 0 or volume > 5000:
                        print(
                            'El volumen debe estar entre 0 y 5000 ml.'
                        )
                        continue

                    self.collect_sample(depth, volume)

                elif option == '3':

                    print('\nCerrando estacion de control...')
                    break

                else:
                    print('Opcion no valida.')

            except ValueError:
                print('Error: ingrese un valor numerico valido.')

            except TimeoutError as error:
                print(f'\nERROR: {error}')

            except Exception as error:
                self.get_logger().error(
                    f'Error durante la operacion: {error}'
                )


def main(args=None):

    rclpy.init(args=args)

    station = ControlStation()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(station)

    spin_thread = threading.Thread(
        target=executor.spin,
        daemon=True
    )

    spin_thread.start()

    try:
        station.show_menu()

    except KeyboardInterrupt:
        pass

    finally:
        executor.shutdown()
        station.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

        spin_thread.join(timeout=2.0)


if __name__ == '__main__':
    main()