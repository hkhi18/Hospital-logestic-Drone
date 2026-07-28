import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, NavSatFix
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage


class DroneTracker(Node):

  def __init__(self):
    super().__init__('drone_tracker')

    # State Variables
    self.current_orientation = None
    self.angular_velocity = None
    self.latitude = None
    self.longitude = None

    # Subscriber - Dynamic Pose / TF
    self.subscription = self.create_subscription(
        TFMessage,
        '/world/finalproject1/dynamic_pose/info',
        self.pose_callback,
        10,
    )

    # Subscriber - IMU 
    self.imu_sub = self.create_subscription(
        Imu,
        '/world/finalproject1/model/x500_0/link/base_link/sensor/imu_sensor/imu',
        self.imu_callback,
        10,
    )

    # Subscriber - GPS
    self.gps_sub = self.create_subscription(
        NavSatFix,
        '/world/finalproject1/model/x500_0/link/base_link/sensor/navsat_sensor/navsat',
        self.gps_callback,
        10,
    )

    # Publisher - 
    self.publisher_ = self.create_publisher(String, '/drone/tracking', 10)

    self.get_logger().info('Drone Tracker Ready!')

  def pose_callback(self, msg: TFMessage):
    if not msg.transforms:
      return

    translation = msg.transforms[0].transform.translation
    x, y, z = translation.x, translation.y, translation.z

    tracking_msg = String()
    tracking_msg.data = f'X:{x:.2f} Y:{y:.2f} Z:{z:.2f}'
    self.publisher_.publish(tracking_msg)

    self.get_logger().info(f'Drone Position → X:{x:.2f} Y:{y:.2f} Z:{z:.2f}')

  def imu_callback(self, msg: Imu):
    self.current_orientation = msg.orientation
    self.angular_velocity = msg.angular_velocity
  #print 
    self.get_logger().info(
        f'IMU Received → Angular Vel Z: {msg.angular_velocity.z:.2f}'
    )

  def gps_callback(self, msg: NavSatFix):
    self.latitude = msg.latitude
    self.longitude = msg.longitude
   #print 
    self.get_logger().info(
        f'GPS Received → Lat: {msg.latitude:.5f}, Lon: {msg.longitude:.5f}'
    )


def main(args=None):
  rclpy.init(args=args)
  node = DroneTracker()
  rclpy.spin(node)
  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()
