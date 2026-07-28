import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

class CheckArmClient(Node):
    def __init__(self):
        super().__init__('check_arm_client')
        self.cli = self.create_client(Trigger, 'check_arm')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
        self.req = Trigger.Request()

    def send_request(self):
        return self.cli.call_async(self.req)

def main():
    rclpy.init()
    client = CheckArmClient()
    future = client.send_request()
    rclpy.spin_until_future_complete(client, future)
    response = future.result()
    client.get_logger().info(
        f'Success={response.success} Message="{response.message}"'
    )
    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

