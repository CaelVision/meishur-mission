#!/usr/bin/env python3
import meishur
import dronekit

def goto_point_n_back(mission):
  mission.add_global_waypoint(
    meishur.local2global(mission.home, dronekit.LocationLocal(10, 0, -10)))
  mission.add_global_waypoint(
    meishur.local2global(mission.home, dronekit.LocationLocal(0, 0, -10)))

if __name__ == "__main__":
  drone = meishur.Drone("127.0.0.1:14550")
  mission = meishur.Mission(drone)

  goto_point_n_back(mission)

  mission.upload()
  # leaving room for checks and assertions
  mission.start()

  # join blocks the process and periodically prints out diagnostic msgs
  mission.join()

  print("mission complete")
