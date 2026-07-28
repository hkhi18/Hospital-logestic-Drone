import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from hospital_drone_interfaces.action import DroneAction
import time

class DroneActionServer(Node):
    def __init__(self):
        super().__init__('drone_action_server')

        self._action_server = ActionServer(
            self,
            DroneAction,
            'drone_mission',
            self.execute_callback
        )
        self.get_logger().info('Drone Action Server Ready!')

    async def execute_callback(self, goal_handle):
        self.get_logger().info(
            f'Starting Mission: {goal_handle.request.mission_name}'
        )

        # Waypoints of the mission
        waypoints = [
            (47.397955, 8.546048),  # takeoff
            (47.397959, 8.546419),  # helipad1
            (47.397980, 8.546111),  # waypoint 2
            (47.397983, 8.546201),  # waypoint 3
            (47.397984, 8.546246),  # helipad2 land
        ]

        feedback_msg = DroneAction.Feedback()
        feedback_msg.total_waypoints = len(waypoints)

        # Fly through each waypoint
        for i, (lat, lon) in enumerate(waypoints):
            feedback_msg.current_waypoint = i + 1
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(
                f'Waypoint {i+1}/{len(waypoints)} → Lat:{lat} Lon:{lon}'
            )
            time.sleep(2)  # simulate flying

        # Mission complete
        goal_handle.succeed()
        result = DroneAction.Result()
        result.success = True
        result.message = 'Landed on helipad2 successfully!'
        return result


def main():
    rclpy.init()
    node = DroneActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
