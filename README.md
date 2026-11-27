# Estación Acuática Autónoma para el Monitoreo de Metales Pesados

Sistema de monitoreo de calidad del agua desarrollado con **ROS 2 Jazzy y Python**, orientado a la identificación de posibles contaminantes asociados a actividades mineras en zonas como Portovelo y las cuencas de la Amazonía ecuatoriana.

El proyecto implementa una arquitectura distribuida de nodos ROS 2 que permite simular la adquisición de parámetros de calidad del agua, obtener coordenadas GPS, detectar posibles condiciones de contaminación, calibrar sensores y ejecutar un procedimiento automatizado de muestreo.

> **Nota:** Este proyecto es una simulación funcional desarrollada en ROS 2. Los sensores, las mediciones y el mecanismo de muestreo son simulados. No existe conexión con sensores físicos ni actuadores reales.

---

## 1. Objetivos del proyecto

- Simular la adquisición de parámetros fisicoquímicos del agua.
- Monitorear concentraciones de mercurio, plomo y cadmio.
- Asociar las mediciones con coordenadas geográficas GPS.
- Detectar posibles condiciones de contaminación mediante límites configurables.
- Implementar calibración remota mediante servicios ROS 2.
- Simular un mecanismo de recolección de muestras mediante acciones ROS 2.
- Implementar comunicación confiable utilizando perfiles QoS.
- Visualizar la arquitectura de comunicación mediante herramientas ROS 2.

---

## 2. Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| Ubuntu 24.04 LTS | Sistema operativo |
| ROS 2 Jazzy | Middleware de comunicación robótica |
| Python 3 | Desarrollo de nodos |
| CMake | Compilación de interfaces |
| colcon | Construcción del workspace |
| ROS 2 Launch | Ejecución integrada |
| rqt_graph | Visualización de nodos y tópicos |

---

## 3. Arquitectura del sistema

El proyecto está compuesto por cinco nodos principales:

| Nodo | Función |
|---|---|
| `sensor_node` | Genera y publica mediciones simuladas de calidad del agua. |
| `gps_node` | Publica coordenadas geográficas simuladas. |
| `monitor_node` | Analiza los datos y genera alertas de contaminación. |
| `calibration_server` | Proporciona servicios de calibración para pH y turbidez. |
| `sampling_action_server` | Gestiona el procedimiento simulado de recolección de muestras. |

### Diagrama de comunicación

```text
                 ┌──────────────────┐
                 │     gps_node     │
                 └────────┬─────────┘
                          │
                       /gps/fix
                          │
                          ▼
                 ┌──────────────────┐
                 │   sensor_node   │
                 └────────┬─────────┘
                          │
                    /water_quality
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
     ┌────────────────┐     ┌────────────────────┐
     │  monitor_node  │     │ calibration_server│
     └────────────────┘     └─────────┬──────────┘
                                      │
                            /sensor_calibration
                                      │
                                      ▼
                                sensor_node

                 ┌───────────────────────┐
                 │ sampling_action_server│
                 └───────────┬───────────┘
                             │
                       /collect_sample
                             │
                       Acción ROS 2
```

---

## 4. Estructura del workspace

```text
water_monitoring_ws/
│
├── src/
│   │
│   ├── water_interfaces/
│   │   ├── action/
│   │   │   └── Sampling.action
│   │   ├── msg/
│   │   │   └── WaterQuality.msg
│   │   ├── srv/
│   │   │   └── SensorCalibration.srv
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   │
│   └── water_monitoring/
│       ├── launch/
│       │   └── water_station.launch.py
│       ├── resource/
│       │   └── water_monitoring
│       ├── water_monitoring/
│       │   ├── __init__.py
│       │   ├── sensor_node.py
│       │   ├── gps_node.py
│       │   ├── monitor_node.py
│       │   ├── calibration_server.py
│       │   ├── sampling_action_server.py
│       │   └── control_station.py
│       ├── package.xml
│       ├── setup.cfg
│       └── setup.py
│
├── .gitignore
└── README.md
```

---

## 5. Interfaces personalizadas

El paquete `water_interfaces` contiene los mensajes, servicios y acciones personalizados.

### 5.1. Mensaje WaterQuality

Archivo: `WaterQuality.msg`

```text
std_msgs/Header header

float32 ph
float32 turbidity
float32 temperature

float32 mercury
float32 lead
float32 cadmium

float64 latitude
float64 longitude

bool contamination_detected
```

Este mensaje transporta las mediciones simuladas de calidad del agua y su ubicación geográfica.

### 5.2. Servicio SensorCalibration

Archivo: `SensorCalibration.srv`

```text
string sensor_name
float32 reference_value
---
bool success
float32 calibration_offset
string message
```

Permite solicitar la calibración de los sensores de pH y turbidez mediante un valor de referencia.

### 5.3. Acción Sampling

Archivo: `Sampling.action`

```text
float32 target_depth
float32 sample_volume
---
bool success
float32 collected_volume
string message
---
float32 current_depth
float32 collection_percentage
string actuator_status
```

Permite simular el descenso del mecanismo, la estabilización y la recolección de una muestra. También proporciona feedback y admite solicitudes de cancelación.

---

## 6. Instalación y configuración

### Requisitos previos

- Ubuntu 24.04 LTS.
- ROS 2 Jazzy instalado.
- Python 3.
- colcon.
- Git.

Instalar herramientas de compilación:

```bash
sudo apt update

sudo apt install python3-colcon-common-extensions python3-rosdep git
```

Si ROS 2 Jazzy ya está instalado, continuar con la configuración del workspace.

### Clonar el repositorio

```bash
mkdir -p ~/water_monitoring_ws/src

cd ~/water_monitoring_ws/src

git clone https://github.com/khrissz720/water_monitoring_ros2.git
```

Si se clona el repositorio directamente dentro de `src`, comprobar que su estructura contiene los dos paquetes:

```text
src/
└── water_monitoring_ros2/
    ├── water_interfaces/
    └── water_monitoring/
```

**Importante:** para compilar correctamente, los paquetes ROS 2 deben encontrarse directamente dentro de `src/`. Si el repositorio contiene ambos paquetes dentro de una carpeta adicional, moverlos:

```bash
cd ~/water_monitoring_ws/src/water_monitoring_ros2

mv water_interfaces ../
mv water_monitoring ../

cd ~/water_monitoring_ws/src

rmdir water_monitoring_ros2
```

Si los paquetes ya están directamente dentro de `src/`, no es necesario ejecutar esos comandos.

### Instalar dependencias

Desde el workspace:

```bash
cd ~/water_monitoring_ws

source /opt/ros/jazzy/setup.bash

rosdep install --from-paths src --ignore-src -r -y
```

### Compilar el proyecto

```bash
cd ~/water_monitoring_ws

source /opt/ros/jazzy/setup.bash

colcon build --packages-up-to water_monitoring
```

Cargar los paquetes compilados:

```bash
source install/setup.bash
```

---

## 7. Ejecutar el sistema completo

La forma recomendada de iniciar el proyecto es mediante el archivo Launch.

```bash
source /opt/ros/jazzy/setup.bash

source ~/water_monitoring_ws/install/setup.bash

ros2 launch water_monitoring water_station.launch.py
```

Este comando inicia automáticamente los cinco nodos principales.

**No es necesario ejecutar cada nodo individualmente cuando se utiliza Launch.**

### Verificar los nodos activos

En otra terminal:

```bash
source /opt/ros/jazzy/setup.bash

source ~/water_monitoring_ws/install/setup.bash

ros2 node list
```

Resultado esperado:

```text
/calibration_server
/gps_node
/monitor_node
/sampling_action_server
/sensor_node
```

---

## 8. Tópicos de comunicación

### Tópicos principales

| Tópico | Tipo de mensaje | Función |
|---|---|---|
| `/water_quality` | `water_interfaces/msg/WaterQuality` | Mediciones de calidad del agua. |
| `/gps/fix` | `sensor_msgs/msg/NavSatFix` | Coordenadas GPS simuladas. |
| `/sensor_calibration` | `std_msgs/msg/Float32MultiArray` | Comunicación de offsets de calibración. |

### Consultar los tópicos disponibles

```bash
ros2 topic list
```

### Consultar mediciones de calidad del agua

```bash
ros2 topic echo /water_quality
```

Para visualizar una sola medición:

```bash
ros2 topic echo /water_quality --once
```

### Consultar coordenadas GPS

```bash
ros2 topic echo /gps/fix
```

### Consultar información de comunicación

```bash
ros2 topic info /water_quality --verbose
```

---

## 9. Calidad de servicio (QoS)

Se implementaron perfiles QoS para mejorar la confiabilidad de la comunicación entre nodos.

### Tópico /water_quality

Configuración:

- Reliability: `RELIABLE`
- History: `KEEP_LAST`
- Depth: `10`

### Tópico /sensor_calibration

Configuración:

- Reliability: `RELIABLE`
- History: `KEEP_LAST`
- Depth: `1`
- Durability: `TRANSIENT_LOCAL`

Para inspeccionar los perfiles:

```bash
ros2 topic info /water_quality --verbose
```

```bash
ros2 topic info /sensor_calibration --verbose
```

---

## 10. Monitoreo y parámetros dinámicos

El nodo `monitor_node` permite configurar los límites utilizados para detectar posibles condiciones de contaminación.

Parámetros iniciales:

| Parámetro | Valor |
|---|---:|
| `ph_min` | 6.5 |
| `ph_max` | 8.5 |
| `turbidity_max` | 50.0 |
| `mercury_max` | 0.002 |
| `lead_max` | 0.01 |
| `cadmium_max` | 0.003 |

Consultar parámetros:

```bash
ros2 param list /monitor_node
```

Consultar un parámetro:

```bash
ros2 param get /monitor_node turbidity_max
```

Modificar dinámicamente el límite de turbidez:

```bash
ros2 param set /monitor_node turbidity_max 30.0
```

Restaurar su valor inicial:

```bash
ros2 param set /monitor_node turbidity_max 50.0
```

Los cambios se aplican durante la ejecución, sin reiniciar el nodo.

---

## 11. Servicio de calibración

El servicio `/calibrate_sensor` permite ajustar los valores simulados de pH y turbidez.

### Consultar el servicio

```bash
ros2 service list
```

Consultar su tipo:

```bash
ros2 service type /calibrate_sensor
```

### Calibrar el sensor de pH

```bash
ros2 service call /calibrate_sensor water_interfaces/srv/SensorCalibration "{sensor_name: 'ph', reference_value: 7.0}"
```

### Calibrar el sensor de turbidez

```bash
ros2 service call /calibrate_sensor water_interfaces/srv/SensorCalibration "{sensor_name: 'turbidity', reference_value: 10.0}"
```

El servidor calcula el offset correspondiente y lo publica para que el nodo de sensores corrija las siguientes mediciones.

---

## 12. Acción de muestreo automatizado

La acción `/collect_sample` simula un procedimiento de recolección de muestras.

### Consultar acciones disponibles

```bash
ros2 action list
```

Consultar el tipo:

```bash
ros2 action type /collect_sample
```

### Configurar duración de las etapas

El parámetro `step_duration_sec` determina cuánto dura cada paso de la simulación.

Para realizar una demostración rápida:

```bash
ros2 param set /sampling_action_server step_duration_sec 1.0
```

### Ejecutar una solicitud de muestreo

```bash
ros2 action send_goal /collect_sample water_interfaces/action/Sampling "{target_depth: 5.0, sample_volume: 500.0}" --feedback
```

Durante la ejecución se proporciona información sobre:

- Profundidad actual.
- Porcentaje de recolección.
- Estado del actuador.
- Resultado final de la operación.

Para restaurar la duración normal:

```bash
ros2 param set /sampling_action_server step_duration_sec 10.0
```

### Cancelación de acciones

El servidor implementa soporte para cancelar solicitudes durante su ejecución. La cancelación se realiza mediante un cliente ROS 2 que envía la solicitud de cancelación al servidor.

---

## 13. Visualización de la arquitectura

Para visualizar las conexiones entre los nodos y tópicos:

```bash
ros2 run rqt_graph rqt_graph
```

Se recomienda seleccionar la visualización de todos los nodos y tópicos y actualizar el gráfico.

También se puede consultar información individual:

```bash
ros2 node info /sensor_node
```

```bash
ros2 node info /monitor_node
```

---

## 14. Interfaces disponibles

Consultar el mensaje personalizado:

```bash
ros2 interface show water_interfaces/msg/WaterQuality
```

Consultar el servicio:

```bash
ros2 interface show water_interfaces/srv/SensorCalibration
```

Consultar la acción:

```bash
ros2 interface show water_interfaces/action/Sampling
```

---

## 15. Detener el sistema

Para detener todos los nodos iniciados mediante Launch:

```text
Ctrl + C
```

Para cerrar las demás terminales de prueba, utilizar también `Ctrl + C`.

---

## 16. Reconstruir el proyecto después de realizar cambios

Si se modifican los mensajes, servicios o acciones:

```bash
cd ~/water_monitoring_ws

source /opt/ros/jazzy/setup.bash

colcon build --packages-up-to water_monitoring

source install/setup.bash
```

Si solamente se modifican los nodos Python:

```bash
cd ~/water_monitoring_ws

source /opt/ros/jazzy/setup.bash

colcon build --packages-select water_monitoring

source install/setup.bash
```

---

## 17. Autores y repositorio

**Autor:** Andry Ortega Vera

**Institución:** Escuela Superior Politécnica del Litoral (ESPOL)

**Carrera:** Ingeniería en Mecatrónica

**Repositorio:** [water_monitoring_ros2](https://github.com/khrissz720/water_monitoring_ros2)

**Licencia:** MIT

---

## 18. Consideraciones finales

Este proyecto demuestra la integración de diferentes herramientas y mecanismos de comunicación de ROS 2 Jazzy:

- Nodos distribuidos.
- Mensajes personalizados.
- Publicación y suscripción mediante tópicos.
- Perfiles de comunicación QoS.
- Parámetros dinámicos.
- Servicios para calibración.
- Acciones con feedback y cancelación.
- Integración mediante archivos Launch.
- Visualización de la arquitectura mediante rqt_graph.

La implementación constituye una base de software para el desarrollo futuro de una estación acuática de monitoreo ambiental con sensores y mecanismos físicos.
