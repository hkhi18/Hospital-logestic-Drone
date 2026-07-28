import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DroneMonitorNode(Node):
    def __init__(self):
        super().__init__('drone_monitor')
        self.subscription = self.create_subscription(
            String,
            '/drone/status',
            self.status_callback,
            10)
        self.get_logger().info('Drone Monitor Node is running!')

    def status_callback(self, msg):
        self.get_logger().info(f' Received: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = DroneMonitorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
