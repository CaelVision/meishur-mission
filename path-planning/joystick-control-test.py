#!/usr/bin/env python3
import time
import threading
import signal
import meishur
import dronekit
from pymavlink import mavutil

# create_msg = dronekit.Vehicle.message_factory.command_long_encode

joystick_msg = mavutil.mavlink.MAVLink_manual_control_message(
  target=0, # dronekit uses 0 as the "target_system" in command_long_encode
  # x, y, z, r are all "normalized" to [-1000, 1000]
  x=0,
  y=0,
  z=0,
  r=0,
  buttons=0, # 16 bit field
)

drone = meishur.Drone("127.0.0.1:14550")

stop_event = threading.Event()
send_msg = lambda : drone.vehicle.send_mavlink(joystick_msg)

def send_msg():
  while not stop_event.wait(1):
    drone.vehicle.send_mavlink(joystick_msg)
    print("msg sent", time.time())

send_msg_task = threading.Thread(target=send_msg)

def handler(sig, frame):
  stop_event.set()
  send_msg_task.join()

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

send_msg_task.start()

while not stop_event.isSet():
  time.sleep(5)
