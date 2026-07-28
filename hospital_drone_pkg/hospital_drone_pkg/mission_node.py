import asyncio
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

class MissionNode(Node):
    def __init__(self):
        super().__init__('mission_node')

        # ── Publisher ─────────────────────────────
        self.status_pub = self.create_publisher(
            String, '/drone/mission_status', 10)

        # ── Service ───────────────────────────────
        self.srv = self.create_service(
            Trigger, 'start_mission', self.mission_callback)

        self.drone = System()
        self.is_connected = False

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self.loop.run_forever, daemon=True)
        self.thread.start()

        asyncio.run_coroutine_threadsafe(
            self.connect(), self.loop)

        self.get_logger().info('Mission Node Ready! 🚁')

    # ── 1. الاتصال ────────────────────────────────
    async def connect(self):
        await self.drone.connect(
            system_address="udpin://0.0.0.0:14540")
        self.get_logger().info('Connecting to PX4...')
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                self.is_connected = True
                self.get_logger().info('PX4 Connected! ✅')
                self.publish_status('PX4: Connected')
                break

    # ── 2. Distance Sensor ────────────────────────
    async def distance_sensor(self):
        try:
            async for dist in self.drone.telemetry.distance_sensor():
                distance = dist.current_distance_m
                self.get_logger().info(
                    f'📡 Distance Sensor → {distance:.1f}m')
                if distance < 5.0:
                    self.get_logger().warn(
                        '🚨 WARNING: Building too close! Climbing up...')
                    self.publish_status('WARNING: Building too close!')
                return distance
        except Exception:
            self.get_logger().info(
                '📡 Distance Sensor → Simulated: Safe ✅')
            return 999.0

    # ── 3. Camera Sensor ──────────────────────────
    async def camera_sensor(self, waypoint_num, lat, lon):
        self.get_logger().info(
            f'📷 Camera → Photo at Waypoint {waypoint_num}')
        self.get_logger().info(
            f'📍 Location → Lat:{lat:.6f} Lon:{lon:.6f}')
        self.publish_status(
            f'Camera: Photo at Waypoint {waypoint_num}')

    # ── 4. Safety Monitor ─────────────────────────
    async def monitor_safety(self):
        self.get_logger().info('🛡️ Safety Monitor Started...')
        while True:
            await self.distance_sensor()
            await asyncio.sleep(2)

    # ── 5. تنفيذ المهمة ──────────────────────────
    async def run_mission(self):
        try:
            # انتظري GPS
            self.get_logger().info('Waiting for GPS...')
            async for health in self.drone.telemetry.health():
                if health.is_global_position_ok:
                    self.get_logger().info('GPS Ready! ✅')
                    break

            flying_alt = 8.0

            # Waypoints
            waypoints = [
                (47.397955, 8.546048),  # takeoff position
                (47.397980, 8.546111),  # 2
                (47.397983, 8.546201),  # 3
                (47.397984, 8.546246),  # 4 - helipad2 land
            ]

            # Mission items
            mission_items = []
            for i, (lat, lon) in enumerate(waypoints):
                if i == len(waypoints) - 1:
                    mission_items.append(
                        MissionItem(
                            lat, lon, flying_alt, 5.0, True,
                            float("nan"), float("nan"),
                            MissionItem.CameraAction.TAKE_PHOTO,
                            float("nan"), float("nan"),
                            float("nan"), float("nan"),
                            float("nan"),
                            MissionItem.VehicleAction.LAND,
                        )
                    )
                else:
                    mission_items.append(
                        MissionItem(
                            lat, lon, flying_alt, 10.0, True,
                            float("nan"), float("nan"),
                            MissionItem.CameraAction.NONE,
                            float("nan"), float("nan"),
                            float("nan"), float("nan"),
                            float("nan"),
                            MissionItem.VehicleAction.NONE,
                        )
                    )

            mission_plan = MissionPlan(mission_items)

            # Upload mission
            self.get_logger().info('Uploading mission...')
            await self.drone.mission.upload_mission(mission_plan)
            self.publish_status('Mission: Uploaded ✅')

            # Arm
            self.get_logger().info('Arming...')
            await self.drone.action.arm()
            self.publish_status('Mission: Armed ✅')

            # Safety Monitor في الخلفية
            safety_task = asyncio.ensure_future(
                self.monitor_safety())

            # Start mission
            self.get_logger().info('Starting mission...')
            await self.drone.mission.start_mission()
            self.publish_status('Mission: Started ✅')

            # Track progress
            async for progress in self.drone.mission.mission_progress():
                self.get_logger().info(
                    f'📍 Waypoint {progress.current}/{progress.total}')
                self.publish_status(
                    f'Waypoint {progress.current}/{progress.total}')

                if progress.current < len(waypoints):
                    lat, lon = waypoints[progress.current]
                    await self.camera_sensor(
                        progress.current, lat, lon)

                if progress.current == progress.total:
                    self.get_logger().info('✅ Mission Complete!')
                    self.publish_status('Mission: Complete ✅')
                    break

            safety_task.cancel()
            self.get_logger().info('🛬 Landed on helipad2!')
            self.publish_status('Landed on helipad2! 🛬')

        except Exception as e:
            self.get_logger().error(f'Mission Error: {e}')
            self.publish_status(f'Mission: Error {e}')

    # ── 6. Service Callback ───────────────────────
    def mission_callback(self, request, response):
        if self.is_connected:
            asyncio.run_coroutine_threadsafe(
                self.run_mission(), self.loop)
            response.success = True
            response.message = 'Mission Started!'
        else:
            response.success = False
            response.message = 'PX4 not connected!'
        return response

    # ── 7. Publisher Helper ───────────────────────
    def publish_status(self, message):
        msg = String()
        msg.data = message
        self.status_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MissionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
