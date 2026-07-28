import asyncio
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from std_srvs.srv import Trigger
from mavsdk import System

class MavsdkNode(Node):
    def __init__(self):
        super().__init__('mavsdk_node')

        # ── Publisher - ينشر حالة PX4 ────────────
        self.status_pub = self.create_publisher(
            String, '/drone/px4_status', 10)

        # ── Publisher - نسبة البطارية الحقيقية ────
        self.battery_pub = self.create_publisher(
            Float32, '/drone/battery_status', 10)

        # ── Service - يستقبل أمر Arm من check_arm ─
        self.srv = self.create_service(
            Trigger,
            'mavsdk_arm',
            self.arm_callback
        )

        # ── Subscriber - يستقبل أوامر Mission ─────
        self.create_subscription(
            String,
            '/drone/status',
            self.status_callback,
            10)

        self.drone = System()
        self.is_connected = False
        self.get_logger().info('MAVSDK Node Ready!')

        # شغل asyncio في background
        self.loop = asyncio.new_event_loop()
        import threading
        self.thread = threading.Thread(
            target=self.loop.run_forever, daemon=True)
        self.thread.start()

        # اتصل بـ PX4
        asyncio.run_coroutine_threadsafe(
            self.connect(), self.loop)

    # ── 1. الاتصال بـ PX4 ────────────────────────
    async def connect(self):
        await self.drone.connect(
            system_address="udpin://0.0.0.0:14540")
        self.get_logger().info('Connecting to PX4...')

        async for state in self.drone.core.connection_state():
            if state.is_connected:
                self.is_connected = True
                self.get_logger().info('PX4 Connected! ✅')

                # انشري الحالة
                msg = String()
                msg.data = 'PX4: Connected'
                self.status_pub.publish(msg)

                asyncio.run_coroutine_threadsafe(
                    self.stream_battery(), self.loop)
                break

    # ── 1b. بث نسبة البطارية الحقيقية ─────────────
    async def stream_battery(self):
        async for battery in self.drone.telemetry.battery():
            # remaining_percent is already 0-100, not a 0-1 fraction
            msg = Float32()
            msg.data = battery.remaining_percent
            self.battery_pub.publish(msg)

    # ── 2. Arm + Takeoff ─────────────────────────
    async def arm_and_takeoff(self):
        try:
            # انتظري GPS
            self.get_logger().info('Waiting for GPS...')
            async for health in self.drone.telemetry.health():
                if health.is_global_position_ok:
                    self.get_logger().info('GPS Ready! ✅')
                    break

            # Arm
            self.get_logger().info('Arming...')
            await self.drone.action.arm()

            msg = String()
            msg.data = 'PX4: Armed ✅'
            self.status_pub.publish(msg)

            # Takeoff
            self.get_logger().info('Taking off...')
            await self.drone.action.takeoff()

            msg.data = 'PX4: Taking off ✅'
            self.status_pub.publish(msg)

            await asyncio.sleep(10)

            # Land
            self.get_logger().info('Landing...')
            await self.drone.action.land()

            msg.data = 'PX4: Landed ✅'
            self.status_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(f'Error: {e}')

    # ── 3. Service Callback ───────────────────────
    def arm_callback(self, request, response):
        if self.is_connected:
            asyncio.run_coroutine_threadsafe(
                self.arm_and_takeoff(), self.loop)
            response.success = True
            response.message = 'Arm and Takeoff started!'
        else:
            response.success = False
            response.message = 'PX4 not connected!'
        return response

    # ── 4. Status Callback ────────────────────────
    def status_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = MavsdkNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
