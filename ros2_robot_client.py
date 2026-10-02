import time
import requests
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class RobotMissionNode(Node):
    def __init__(self):
        super().__init__('robot_mission_node')
        # URL de la API FastApi en main.py
        self.api_url = "http://localhost:8000/missions/next"

        # Cliente de acción para Nav2 (navegación en ROS 2)
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Timer para consultar misiones cada 5 segundos
        self.timer = self.create_timer(5.0, self.check_for_missions)
        self.mission_in_progress = False

    def check_for_missions(self):
        if self.mission_in_progress:
            return

        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get("mission_id"):
                    self.get_logger().info(f"Nueva misión recibida: {data}")
                    self.execute_mission(data)
        except Exception as e:
            self.get_logger().error(f"Error consultando misión: {e}")

    def execute_mission(self, mission_data):
        self.mission_in_progress = True

        pickup = mission_data['pickup']
        dropoff = mission_data['dropoff']

        self.get_logger().info(f"Navegando hacia punto de recogida (pickup): {pickup}")
        pickup_pose = self.get_pose_from_location(pickup)

        # Enviar goal al pickup. Al terminar, irá al dropoff.
        self.send_goal(pickup_pose, dropoff)

    def get_pose_from_location(self, location_name):
        # Mapeo de ejemplo de nombres de ubicaciones a coordenadas XYZ / Orientación
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        if location_name == "STORAGE":
            pose.pose.position.x = 2.0
            pose.pose.position.y = 2.0
        else:
            pose.pose.position.x = 5.0
            pose.pose.position.y = 5.0

        pose.pose.orientation.w = 1.0
        return pose

    def send_goal(self, pose, next_location=None):
        self.get_logger().info("Esperando al servidor de acción navigate_to_pose...")
        self.nav_client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.get_logger().info("Enviando meta (goal)...")
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self.send_goal_future.add_done_callback(
            lambda future: self.goal_response_callback(future, next_location)
        )

    def goal_response_callback(self, future, next_location):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Meta rechazada por el robot :(')
            self.mission_in_progress = False
            return

        self.get_logger().info('Meta aceptada, el robot está en movimiento :)')
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(
            lambda fut: self.get_result_callback(fut, next_location)
        )

    def get_result_callback(self, future, next_location):
        result = future.result().result
        self.get_logger().info(f'Punto alcanzado con éxito')

        if next_location:
            self.get_logger().info(f"Procediendo al siguiente punto (dropoff): {next_location}")
            next_pose = self.get_pose_from_location(next_location)
            self.send_goal(next_pose, None)
        else:
            self.get_logger().info("Misión completada. Robot libre.")
            self.mission_in_progress = False

def main(args=None):
    rclpy.init(args=args)
    node = RobotMissionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
