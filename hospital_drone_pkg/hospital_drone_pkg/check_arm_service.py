import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from std_msgs.msg import String
import random

class CheckArmService(Node):
    def __init__(self):
        super().__init__('check_arm_service')

        # ── Service ──────────────────────────────
        self.srv = self.create_service(
            Trigger,
            'check_arm',
            self.check_arm_callback
        )

        # ── Publisher -drone
        self.publisher_ = self.create_publisher(
            String, '/drone/arm_status', 10)

        # ── Subscriber -
        self.subscription = self.create_subscription(
            String,
            '/drone/status',
            self.status_callback,
            10)

        self.get_logger().info('Check Arm Service is ready!')

    # ──status arm  ──────────────────────
    def status_callback(self, msg):
        self.get_logger().info(f'Received drone status: {msg.data}')

    # ── detect الـ Arm ──────────────────────────────
    def check_arm_callback(self, request, response):
        gps_ok = True
        battery_level = random.randint(50, 100)
        distance_safe = True

        if gps_ok and battery_level > 30 and distance_safe:
            response.success = True
            response.message = f'Arm OK! Battery: {battery_level}%, GPS: Ready'
            self.get_logger().info('Drone is ready to ARM ')


            msg = String()
            msg.data = f'ARM: Ready  Battery: {battery_level}%'
            self.publisher_.publish(msg)

        else:
            response.success = False
            response.message = f'Arm Denied! Battery: {battery_level}%'
            self.get_logger().warn('Drone NOT ready to ARM ')

            msg = String()
            msg.data = f'ARM: Denied  Battery: {battery_level}%'
            self.publisher_.publish(msg)

        return response

def main():
    rclpy.init()
    node = CheckArmService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
