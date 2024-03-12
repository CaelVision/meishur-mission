import dronekit
import time
import math
from collections import namedtuple

EARTH_RADIUS = 6378137.0 # approx spherical earth in meters

class Mission:

  def __init__(self, drone, altitude=5):
    self.drone = drone
    self.drone.vehicle.commands.clear()
    self.home = drone.vehicle.location.global_frame
    self.waypoints_len = 0
    self.last_point = None
    self.takeoff_alt = altitude

    self.add_takeoff(altitude)

  def add_waypoint(self, ref_type, loc: tuple, point_type=dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT):
    self.waypoints_len += 1
    self.last_point = dronekit.Command(0, 0, 0,
      ref_type,
      point_type,
      0, 0, 0, 0, 0, 0,
      *loc)
    self.drone.vehicle.commands.add(self.last_point)

  def add_takeoff(self, alt):
    self.add_waypoint(dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                      (self.home.lat, self.home.lon, alt),
                      dronekit.mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)

  def add_global_waypoint(self, loc):
    self.add_waypoint(dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                      (loc.lat, loc.lon, loc.alt))

  def add_local_waypoint(self, loc):
    self.add_waypoint(dronekit.mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                      (loc.north, loc.east, loc.down))

  def upload(self):
    self.drone.vehicle.commands.add(self.last_point)
    self.drone.vehicle.commands.upload()

  def start(self):
    while not self.drone.vehicle.is_armable:
      print(" Waiting for vehicle to initialise...")
      time.sleep(1)

    # prob better to perform pre-arm checks here
      
    self.drone.vehicle.mode = dronekit.VehicleMode("GUIDED")
    # self.drone.vehicle.mode = dronekit.VehicleMode("AUTO")
    self.drone.vehicle.arm()

    while not self.drone.vehicle.armed:
      print(" Waiting for arming...")
      time.sleep(1)

    self.drone.vehicle.simple_takeoff(self.takeoff_alt)

    while self.drone.vehicle.location.global_relative_frame.alt < self.takeoff_alt * 0.9:
      print(" Altitude: ", self.drone.vehicle.location.global_relative_frame.alt)
      time.sleep(1)

    self.drone.vehicle.mode = dronekit.VehicleMode("AUTO")

  def join(self):
    # wait for the last waypoint and land
    # for i in range(int(120/5)):
    try:
      while self.drone.vehicle.commands.next < self.waypoints_len:
        print(f"self.drone.vehicle.command len: {len(self.drone.vehicle.commands)}")
        time.sleep(2)
    except KeyboardInterrupt:
      print("mission terminated, proceeding to land")

    self.land()

  def clear(self):
    self.drone.vehicle.commands.clear()

  def land(self):
    # TODO: implement aruco guidance in a separate module
    # then periodically call it here
    # use PRECISION_LAND_MODE
    self.drone.vehicle.mode = dronekit.VehicleMode("RTL")
    pass

class Drone:

  def __init__(self, target):
    print("connecting to drone")
    self.vehicle = dronekit.connect(target, wait_ready=True, timeout=120)
    print("drone connected")

  def __del__(self):
    print("closing connection to drone")
    self.vehicle.close()
    print("drone disconnected")

def local2global(global_ref, local):
  rad2deg = 180 / math.pi
  return dronekit.LocationGlobal(
    global_ref.lat + local.north / EARTH_RADIUS * rad2deg,
    global_ref.lon + local.east / EARTH_RADIUS * rad2deg,
    -local.down,
  )

def parse_waypoints_file(filename):
  waypoints = []
  with open(filename) as f:
    for line in f:
      lat, lon, alt = line.split()
      waypoints.append(dronekit.LocationGlobal(lat, lon, alt))
  return waypoints
