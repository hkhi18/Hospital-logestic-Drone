#!/usr/bin/env python3
import asyncio
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

class CameraSafetyNode(Node):
    def __init__(self):
        super().__init__('camera_safety_node')

        self.bridge = CvBridge()
        self._frame = None
        self._lock = threading.Lock()

        # ── Subscriber - كاميرا الدرون ────────────
        self.create_subscription(
            Image,
            '/world/finalproject1/model/x500_0/link/camera_link/sensor/camera/image',
            self.camera_callback,
            10)

        # ── Publisher - تحذير الاصطدام ───────────
        self.safety_pub = self.create_publisher(
            String, '/drone/camera_safety', 10)

        # ── Publisher - حالة الكاميرا ─────────────
        self.status_pub = self.create_publisher(
            String, '/drone/distance', 10)

        self.get_logger().info('Camera Safety Node Ready! 📷')

    def camera_callback(self, msg):
        try:
            # تحويل الصورة
            frame = self.bridge.imgmsg_to_cv2(
                msg, desired_encoding='bgr8')

            with self._lock:
                self._frame = frame

            # فحص الأمان
            self.check_safety(frame)

        except Exception as e:
            self.get_logger().error(f'Camera Error: {e}')

    def check_safety(self, frame):
        # تحويل لـ grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # كشف الأجسام القريبة
        h, w = gray.shape
        center = gray[h//3:2*h//3, w//3:2*w//3]
        brightness = center.mean()

        safety_msg = String()
        distance_msg = String()

        # إذا الجسم قريب جداً (brightness عالية)
        if brightness > 200:
            safety_msg.data = '🚨 WARNING: Object too close!'
            distance_msg.data = 'Distance: CRITICAL < 2m'
            self.get_logger().warn('⚠️ Building too close!')
        elif brightness > 150:
            safety_msg.data = '⚠️ CAUTION: Object nearby'
            distance_msg.data = 'Distance: WARNING 2-5m'
            self.get_logger().info('⚠️ Object nearby')
        else:
            safety_msg.data = '✅ SAFE: Path clear'
            distance_msg.data = 'Distance: SAFE > 5m'

        self.safety_pub.publish(safety_msg)
        self.status_pub.publish(distance_msg)

    def get_latest_frame(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

def main(args=None):
    rclpy.init(args=args)
    node = CameraSafetyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
