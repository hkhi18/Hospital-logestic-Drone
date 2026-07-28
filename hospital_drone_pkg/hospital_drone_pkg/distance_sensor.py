import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DistanceSensor(Node):
    def __init__(self):
        super().__init__('distance_sensor')
        self.publisher_ = self.create_publisher(
            String, '/drone/distance', 10)
        self.create_timer(1.0, self.publish_distance)
        self.get_logger().info('Distance Sensor Running!')

    def publish_distance(self):
        msg = String()
        msg.data = 'Distance: 10.5m - Safe'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = DistanceSensor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
