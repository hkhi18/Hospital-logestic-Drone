import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DistanceMonitor(Node):
    def __init__(self):
        super().__init__('distance_monitor')
        self.subscription = self.create_subscription(
            String,
            '/drone/distance',
            self.listener_callback,
            10)
        self.get_logger().info('Distance Monitor Running!')

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = DistanceMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
