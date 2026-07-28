import math
import re

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import Imu, NavSatFix
from tf2_msgs.msg import TFMessage

from hospital_drone_interfaces.msg import DroneStatus


def quaternion_to_euler_deg(x, y, z, w):
    """ZYX (aerospace) convention quaternion -> roll/pitch/yaw in degrees."""
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    sinp = max(-1.0, min(1.0, sinp))
    pitch = math.asin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)

DRONE_MODEL = 'x500_0'
WORLD = 'finalproject1'
IMU_TOPIC = f'/world/{WORLD}/model/{DRONE_MODEL}/link/base_link/sensor/imu_sensor/imu'
GPS_TOPIC = f'/world/{WORLD}/model/{DRONE_MODEL}/link/base_link/sensor/navsat_sensor/navsat'
POSE_TOPIC = f'/world/{WORLD}/dynamic_pose/info'

WAYPOINT_RE = re.compile(r'step:\s*(\d+)')


class PX4Bridge(Node):
    """Central hub: aggregates the camera-safety, IMU, GPS, pose and mission/arm
    status topics into one hospital_drone_interfaces/DroneStatus message."""

    def __init__(self):
        super().__init__('px4_bridge')

        self._status = DroneStatus()
        self._status.distance_to_obstacle = 999.0
        self._status.battery_percentage = -1.0  # until mavsdk_node's real reading arrives

        self.status_pub = self.create_publisher(DroneStatus, '/drone/full_status', 10)

        self.create_subscription(String, '/drone/status', self._on_drone_sim_status, 10)
        self.create_subscription(String, '/drone/mission_status', self._on_mission_status, 10)
        self.create_subscription(String, '/drone/arm_status', self._on_arm_status, 10)
        self.create_subscription(String, '/drone/camera_safety', self._on_camera_safety, 10)
        self.create_subscription(Imu, IMU_TOPIC, self._on_imu, 10)
        self.create_subscription(NavSatFix, GPS_TOPIC, self._on_gps, 10)
        self.create_subscription(TFMessage, POSE_TOPIC, self._on_pose, 10)
        self.create_subscription(Float32, '/drone/battery_status', self._on_battery, 10)

        self.create_timer(0.5, self._publish_status)

        self.get_logger().info('PX4 Bridge Node Ready!')

    def _on_drone_sim_status(self, msg):
        match = WAYPOINT_RE.search(msg.data)
        if match:
            self._status.current_waypoint = f'step_{match.group(1)}'

    def _on_mission_status(self, msg):
        # mission_node's real PX4 mission progress (upload/arm/waypoint/land)
        self._status.mission_status = msg.data

    def _on_arm_status(self, msg):
        self._status.is_armed = 'ARM: Ready' in msg.data

    def _on_camera_safety(self, msg):
        # camera_safety_node buckets brightness into these three ranges
        if 'WARNING' in msg.data:
            self._status.distance_to_obstacle = 2.0
        elif 'CAUTION' in msg.data:
            self._status.distance_to_obstacle = 3.5
        else:
            self._status.distance_to_obstacle = 10.0

    def _on_imu(self, msg):
        q = msg.orientation
        roll, pitch, yaw = quaternion_to_euler_deg(q.x, q.y, q.z, q.w)
        self._status.roll = roll
        self._status.pitch = pitch
        self._status.yaw = yaw

    def _on_gps(self, msg):
        self._status.latitude = msg.latitude
        self._status.longitude = msg.longitude
        self._status.altitude = msg.altitude

    def _on_battery(self, msg):
        self._status.battery_percentage = msg.data

    def _on_pose(self, msg):
        for transform in msg.transforms:
            if DRONE_MODEL in transform.child_frame_id:
                self._status.is_flying = transform.transform.translation.z > 0.3
                break

    def _publish_status(self):
        self.status_pub.publish(self._status)


def main(args=None):
    rclpy.init(args=args)
    node = PX4Bridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
