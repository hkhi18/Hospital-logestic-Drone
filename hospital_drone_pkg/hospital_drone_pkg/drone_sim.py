import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Publisher node - simulates the hospital drone sending status updates
class DroneSimNode(Node):
    def __init__(self):
        super().__init__('drone_sim')
        # Create publisher on topic /drone/status
        self.publisher_ = self.create_publisher(String, '/drone/status', 10)
        self.counter = 0
        self.get_logger().info('Drone Sim Node is running!')
        # Timer calls publish_status every 1 second
        self.create_timer(1.0, self.publish_status)

    def publish_status(self):
        self.counter += 1
        msg = String()
        msg.data = f'Drone delivering medication - step: {self.counter}'
        # Send message to the topic
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = DroneSimNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
