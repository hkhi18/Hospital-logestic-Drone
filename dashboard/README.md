# Hospital Drone System — KFSHRC Flight Operations Dashboard

A single-file React dashboard (`index.html`) — no Node/npm install required. React,
ReactDOM, Babel (in-browser JSX) and `roslibjs` are vendored locally in `vendor/`
(downloaded once, checked into this folder) so the page has **no runtime dependency
on internet access** — only on `rosbridge_server` for live ROS2 data. Earlier this
loaded those 4 libraries from unpkg.com over CDN, which produced a blank page on a
flaky connection since the whole app failed to boot if even one script was
unreachable; vendoring removes that failure mode entirely. If the page ever *does*
show a blank/error banner instead of the console, that now means an actual JS error —
open devtools (F12) and read the message the page itself prints.

## Run it

Just open the file in a browser:

```bash
firefox /home/hanin/hospital_drone_ws/dashboard/index.html
# or: xdg-open index.html
```

No local server is needed — it works fine from a `file://` URL, including the
WebSocket connection to rosbridge.

## Going live (connecting to ROS2)

The dashboard looks for `rosbridge_server` at `ws://localhost:9090`. Until that's
running, every panel operates in a clearly-tagged **SIMULATION MODE** with animated
demo values, so the dashboard is fully viewable with nothing else running.

To go live:

```bash
sudo apt install ros-humble-rosbridge-suite
source /opt/ros/humble/setup.bash
source /home/hanin/hospital_drone_ws/install/setup.bash   # required: rosbridge must see hospital_drone_interfaces
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

The second `source` line is not optional: `/drone/full_status` is a custom
`hospital_drone_interfaces/msg/DroneStatus` message (battery, roll/pitch/yaw,
GPS, arm/flight state). If `rosbridge_server` is launched from a shell that
hasn't sourced this workspace's `install/setup.bash`, it can't introspect
that message type and the battery/attitude fields will silently stay in SIM.

Then, in another terminal, bring up your existing launch files as usual
(`hospital_drone_launch.py`, `tracking_bridge_launch.py`, Gazebo/PX4 sim). The
dashboard auto-reconnects every 5s and each gauge/panel flips its own badge from
`SIM` to `LIVE` independently, the moment its specific topic starts publishing.

## Topic wiring (as requested) and how each is used

| UI element | Topic | Message | Notes |
|---|---|---|---|
| Drone Position gauge | `/drone/tracking` | `std_msgs/String` (`X:.. Y:.. Z:..`, published by `drone_tracker.py`) | Parsed into x/y/z, displayed as a derived heading 0–350°. Real data (Gazebo TF). |
| Distance to Building gauge | `/drone/distance` | `std_msgs/String` (`distance_sensor.py` / `camera_safety_node.py`) | First numeric value in the string is extracted. `distance_sensor.py` currently publishes a constant `10.5m` regardless of reality (kept as-is by request); `camera_safety_node.py` publishes a real brightness-derived bucket on the same topic. |
| Speed gauge | *(derived)* | from `/drone/tracking` | No dedicated speed topic exists in the workspace, so speed is derived from consecutive position samples (Δdistance/Δtime → km/h, smoothed). Real, since it's derived from real position. |
| Battery ring | `/drone/full_status` | `hospital_drone_interfaces/msg/DroneStatus` (`battery_percentage`) | Real MAVSDK telemetry: `mavsdk_node.py` streams `drone.telemetry.battery()` onto `/drone/battery_status` (`std_msgs/Float32`), which `px4_bridge.py` folds into `/drone/full_status`. Falls back to SIM until `mavsdk_node` connects to PX4 (`udpin://0.0.0.0:14540`). |
| Flight Telemetry Detail rows (X/Y/Z/Speed) | `/drone/tracking` | same as Drone Position gauge | Row-style readout of the same real x/y/z/derived-speed values. |
| Flight Telemetry Detail rows (Pitch/Roll/Yaw) | `/drone/full_status` | `hospital_drone_interfaces/msg/DroneStatus` (`roll`, `pitch`, `yaw`, degrees) | Real: `px4_bridge.py`'s `_on_imu` converts the Gazebo IMU orientation quaternion to Euler angles every IMU sample. |
| Hospital Map | `/drone/tracking` (real local x/y), geo-calibrated | — | Background is a real satellite image of KFSHRC, Riyadh (`vendor/kfshrc_map.png`, ArcGIS World Imagery export). The drone marker is the real live local x/y transformed to real lat/lon via a 2-point Helmert (similarity) transform calibrated from the two real helipad GPS fixes vs. their known local Gazebo coordinates — see `HELIPAD1`/`HELIPAD2`/`makeLocalToLatLon` in `index.html`. Mission end is Helipad2 (dashed line = planned path, teal trail = actual flown path). |
| Live Camera panel | `/drone/camera_safety` | `std_msgs/String` (`✅ SAFE...` / `⚠️ CAUTION...` / `🚨 WARNING...`, from `camera_safety_node.py`) | Drives the HUD safety banner color/text. This topic is a safety status string, not image bytes — there's no pixel video here. For an actual live video tile, add `ros-humble-web-video-server` and point an `<img>` at `http://localhost:8080/stream?topic=/world/finalproject1/model/x500_0/link/camera_link/sensor/camera/image`. |

## GAZEBO bridges panel

Purely a labeled status display of the 4 requested bridge → topic mappings
(`/camera/image_raw`, `/gps/data`, `/imu/data`, `/pose`). It doesn't attempt to
measure per-bridge throughput — it shows ACTIVE/STANDBY tied to the overall
rosbridge connection state.

## ROS2 node graph

Static topology diagram matching the requested layout (`Mission Control → Arm
Status`, `Helipad1 → Helipad2 → Building Distance Monitor`, a self-monitoring loop
on Building Distance Monitor, `Mission Control → PX4 Sensory`, all six nodes
converging on `PX4 SIMULATION`), namespaced `/drone`. Edges animate (flowing dashes)
when rosbridge is connected.
