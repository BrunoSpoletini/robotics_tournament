import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu, LaserScan
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path


def yaw_de_quaternion(q):
    """Ángulo de yaw (rotación en el plano) de un quaternion. La misma
    cuenta de las semanas 06 y 07."""
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def normalizar_angulo(angulo):
    """Lleva un ángulo al rango (-pi, pi]."""
    return math.atan2(math.sin(angulo), math.cos(angulo))


def segundos(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


class OdomCorregida(Node):
    def __init__(self):
        super().__init__("odom_corregida")

        self.declare_parameter('escala_avance', 1.0)
        self.declare_parameter('escala_giro', 1.0)

        self.escala_avance = self.get_parameter('escala_avance').get_parameter_value().double_value
        self.escala_giro = self.get_parameter('escala_giro').get_parameter_value().double_value

        self.odom_sub = self.create_subscription(
            Odometry, "/odom", self.odom_callback, qos_profile_sensor_data
        )

        self.camino_odom_pub = self.create_publisher(Path, "/camino_odom", 10)
        self.camino_corregido_pub = self.create_publisher(Path, "/camino_corregido", 10)

        self.corrected_pose = PoseStamped()
        self.corrected_pose.header.frame_id = "odom"
        self.corrected_pose.pose.orientation.w = 1.0

        self.camino_odom = Path()
        self.camino_odom.header.frame_id = "odom"

        self.camino_corregido = Path()
        self.camino_corregido.header.frame_id = "odom"

        self.last_odom = None
        self.current_odom = None


    def odom_callback(self, msg):

        self.current_odom = msg
        
        # Calcular cuanto se movio el robot desde la ultima odometria
        if self.last_odom is None:
            self.last_odom = msg

            initial_pose = PoseStamped()
            initial_pose.header = msg.header
            initial_pose.pose = msg.pose.pose

            self.camino_odom.header.stamp = msg.header.stamp
            self.camino_odom.poses.append(initial_pose)
            self.camino_odom_pub.publish(self.camino_odom)

            self.corrected_pose.header = msg.header
            self.corrected_pose.pose = msg.pose.pose

            corrected_initial = PoseStamped()
            corrected_initial.header = msg.header
            corrected_initial.pose = self.corrected_pose.pose

            self.camino_corregido.header.stamp = msg.header.stamp
            self.camino_corregido.poses.append(corrected_initial)
            self.camino_corregido_pub.publish(self.camino_corregido)

            return
        
        delta_x = self.current_odom.pose.pose.position.x - self.last_odom.pose.pose.position.x
        delta_y = self.current_odom.pose.pose.position.y - self.last_odom.pose.pose.position.y
        delta_theta = yaw_de_quaternion(self.current_odom.pose.pose.orientation) - yaw_de_quaternion(self.last_odom.pose.pose.orientation)

        delta_theta = normalizar_angulo(delta_theta)

        # Aplicar el desplazamiento y giro corregidos a la pose corregida
        self.corrected_pose.pose.position.x += (self.escala_avance * delta_x)
        self.corrected_pose.pose.position.y += (self.escala_avance * delta_y)
        current_yaw = yaw_de_quaternion(self.corrected_pose.pose.orientation)
        new_yaw = current_yaw + self.escala_giro * delta_theta
        new_yaw = normalizar_angulo(new_yaw)

        self.corrected_pose.header.stamp = self.current_odom.header.stamp
        self.corrected_pose.header.frame_id = "odom"

        self.corrected_pose.pose.orientation.x = 0.0
        self.corrected_pose.pose.orientation.y = 0.0
        self.corrected_pose.pose.orientation.z = math.sin(new_yaw / 2.0)
        self.corrected_pose.pose.orientation.w = math.cos(new_yaw / 2.0)

        original_pose = PoseStamped()
        original_pose.header = msg.header
        original_pose.pose = msg.pose.pose

        self.camino_odom.header.stamp = msg.header.stamp
        self.camino_odom.poses.append(original_pose)
        self.camino_odom_pub.publish(self.camino_odom)

        # Publish corrected path.
        corrected_pose = PoseStamped()
        corrected_pose.header = self.corrected_pose.header
        corrected_pose.pose = self.corrected_pose.pose

        self.camino_corregido.header.stamp = msg.header.stamp
        self.camino_corregido.poses.append(corrected_pose)
        self.camino_corregido_pub.publish(self.camino_corregido)

        self.last_odom = msg

 
def main(args=None):
    rclpy.init(args=args)
    nodo = OdomCorregida()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
