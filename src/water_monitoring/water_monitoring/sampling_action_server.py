import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from water_interfaces.action import Sampling


class SamplingActionServer(Node):

    def __init__(self):
        super().__init__('sampling_action_server')

        # Duracion de cada paso en segundos.
        # Valor predeterminado: 10 segundos.
        self.declare_parameter('step_duration_sec', 10.0)

        self.callback_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            Sampling,
            '/collect_sample',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info(
            'Servidor de recoleccion de muestras iniciado.'
        )

        self.get_logger().info(
            'Duracion predeterminada del proceso: 180 segundos.'
        )

        self.get_logger().info(
            'Esperando solicitudes de recoleccion.'
        )

    # -------------------------------------------------
    # VALIDACION DE SOLICITUDES
    # -------------------------------------------------

    def goal_callback(self, goal_request):

        if goal_request.target_depth <= 0.0:
            self.get_logger().warning('Profundidad invalida.')
            return GoalResponse.REJECT

        if goal_request.target_depth > 20.0:
            self.get_logger().warning(
                'Profundidad maxima permitida: 20 metros.'
            )
            return GoalResponse.REJECT

        if goal_request.sample_volume <= 0.0:
            self.get_logger().warning('Volumen invalido.')
            return GoalResponse.REJECT

        if goal_request.sample_volume > 5000.0:
            self.get_logger().warning(
                'Volumen maximo permitido: 5000 ml.'
            )
            return GoalResponse.REJECT

        self.get_logger().info(
            f'Nueva solicitud: profundidad={goal_request.target_depth:.2f} m, '
            f'volumen={goal_request.sample_volume:.2f} ml'
        )

        return GoalResponse.ACCEPT

    # -------------------------------------------------
    # SOLICITUD DE CANCELACION
    # -------------------------------------------------

    def cancel_callback(self, goal_handle):

        self.get_logger().warning(
            'Solicitud de cancelacion recibida.'
        )

        return CancelResponse.ACCEPT

    # -------------------------------------------------
    # ESPERA INTERRUMPIBLE
    # -------------------------------------------------

    def wait_with_cancel(self, goal_handle, duration):

        start_time = time.monotonic()

        while time.monotonic() - start_time < duration:

            if goal_handle.is_cancel_requested:
                return False

            time.sleep(0.2)

        return not goal_handle.is_cancel_requested

    # -------------------------------------------------
    # FINALIZACION POR CANCELACION
    # -------------------------------------------------

    def finish_cancelled(
        self,
        goal_handle,
        result,
        collected_volume,
        phase
    ):

        goal_handle.canceled()

        result.success = False
        result.collected_volume = collected_volume
        result.message = (
            f'Operacion cancelada durante la fase: {phase}. '
            f'Volumen recolectado: {collected_volume:.2f} ml.'
        )

        self.get_logger().warning(result.message)

        return result

    # -------------------------------------------------
    # EJECUCION DE LA ACCION
    # -------------------------------------------------

    def execute_callback(self, goal_handle):

        request = goal_handle.request

        target_depth = request.target_depth
        target_volume = request.sample_volume

        feedback = Sampling.Feedback()
        result = Sampling.Result()

        collected_volume = 0.0

        # Leer duracion configurable.
        step_duration = float(
            self.get_parameter('step_duration_sec').value
        )

        if step_duration <= 0.0:
            self.get_logger().warning(
                'Duracion invalida. Se utilizara 10 segundos.'
            )
            step_duration = 10.0

        self.get_logger().info(
            f'Iniciando operacion. Cada paso durara '
            f'{step_duration:.2f} segundos.'
        )

        # =================================================
        # FASE 1: DESCENSO
        # 6 pasos x 10 segundos = 60 segundos
        # =================================================

        self.get_logger().info(
            'FASE 1: Iniciando descenso del mecanismo.'
        )

        descent_steps = 6

        for step in range(1, descent_steps + 1):

            if goal_handle.is_cancel_requested:
                return self.finish_cancelled(
                    goal_handle,
                    result,
                    collected_volume,
                    'DESCENSO'
                )

            feedback.current_depth = (
                target_depth * step / descent_steps
            )

            feedback.collection_percentage = 0.0
            feedback.actuator_status = 'DESCENDIENDO'

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Descenso: {feedback.current_depth:.2f} m '
                f'({step}/{descent_steps})'
            )

            if not self.wait_with_cancel(
                goal_handle,
                step_duration
            ):
                return self.finish_cancelled(
                    goal_handle,
                    result,
                    collected_volume,
                    'DESCENSO'
                )

        # =================================================
        # FASE 2: ESTABILIZACION
        # 3 pasos x 10 segundos = 30 segundos
        # =================================================

        self.get_logger().info(
            'FASE 2: Profundidad alcanzada. '
            'Iniciando estabilizacion.'
        )

        stabilization_steps = 3

        for step in range(1, stabilization_steps + 1):

            if goal_handle.is_cancel_requested:
                return self.finish_cancelled(
                    goal_handle,
                    result,
                    collected_volume,
                    'ESTABILIZACION'
                )

            feedback.current_depth = target_depth
            feedback.collection_percentage = 0.0
            feedback.actuator_status = 'ESTABILIZANDO'

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Estabilizacion: {step}/{stabilization_steps}'
            )

            if not self.wait_with_cancel(
                goal_handle,
                step_duration
            ):
                return self.finish_cancelled(
                    goal_handle,
                    result,
                    collected_volume,
                    'ESTABILIZACION'
                )

        # =================================================
        # FASE 3: RECOLECCION DE SEDIMENTOS
        # 9 pasos x 10 segundos = 90 segundos
        # =================================================

        self.get_logger().info(
            'FASE 3: Iniciando recoleccion de sedimentos.'
        )

        collection_steps = 9

        for step in range(1, collection_steps + 1):

            if goal_handle.is_cancel_requested:
                return self.finish_cancelled(
                    goal_handle,
                    result,
                    collected_volume,
                    'RECOLECCION'
                )

            feedback.current_depth = target_depth

            feedback.collection_percentage = (
                step * 100.0 / collection_steps
            )

            feedback.actuator_status = 'RECOLECTANDO_SEDIMENTOS'

            collected_volume = (
                target_volume * step / collection_steps
            )

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f'Recoleccion: '
                f'{feedback.collection_percentage:.1f}% | '
                f'Volumen: {collected_volume:.2f} ml'
            )

            if not self.wait_with_cancel(
                goal_handle,
                step_duration
            ):
                return self.finish_cancelled(
                    goal_handle,
                    result,
                    collected_volume,
                    'RECOLECCION'
                )

        # =================================================
        # FASE 4: FINALIZACION
        # =================================================

        if goal_handle.is_cancel_requested:
            return self.finish_cancelled(
                goal_handle,
                result,
                collected_volume,
                'FINALIZACION'
            )

        feedback.current_depth = target_depth
        feedback.collection_percentage = 100.0
        feedback.actuator_status = 'FINALIZADO'

        goal_handle.publish_feedback(feedback)

        result.success = True
        result.collected_volume = target_volume

        result.message = (
            'Muestra recolectada correctamente. '
            f'Profundidad: {target_depth:.2f} m. '
            f'Volumen: {target_volume:.2f} ml. '
            'Proceso completado en aproximadamente 180 segundos.'
        )

        goal_handle.succeed()

        self.get_logger().info(result.message)

        return result


# -----------------------------------------------------
# FUNCION PRINCIPAL
# -----------------------------------------------------

def main(args=None):

    rclpy.init(args=args)

    node = SamplingActionServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()

    except KeyboardInterrupt:
        pass

    finally:
        executor.shutdown()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()