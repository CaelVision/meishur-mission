#!/usr/bin/env python3
import time
import threading
import signal
import meishur
import dronekit
from pymavlink import mavutil
import pynput
import termios
import sys

class Pos:
  x = 0
  y = 0
  z = 0
  ctr = 0
  def __str__(self):
    return f"{self.x:.3f},{self.y:.3f},{self.z:.3f}"
pos = Pos()

# turn off echo for stdin
# fd = sys.stdin.fileno()
# (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(fd)
# lflag &= ~termios.ECHO
# new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
# termios.tcsetattr(fd, termios.TCSANOW, new_attr)

drone = meishur.Drone("127.0.0.1:14550")

stop_event = threading.Event()

# TODO: make a const location for testing
DEG2RAD = 3.14 / 180
angle_x = 5 * DEG2RAD
angle_y = 0 * DEG2RAD
size_x = 45 * DEG2RAD
size_y = 30 * DEG2RAD

def make_msg():
  msg = mavutil.mavlink.MAVLink_landing_target_message(
    time_usec=int(time.time()*1e6),
    target_num=0,
    frame=pos.ctr,
    angle_x=angle_x,
    angle_y=angle_y,
    distance=5,
    size_x=size_x,
    size_y=size_y,
  )
  pos.ctr += 1
  return msg

def send_msg():
  while not stop_event.is_set():
    msg = make_msg()
    drone.vehicle.send_mavlink(msg)
    drone.vehicle.flush()
    print("msg sent", time.time())
    print(f"sent {msg}")
    time.sleep(0.1)

send_msg_task = threading.Thread(target=send_msg)

def handler(sig, frame):
  stop_event.set()
  send_msg_task.join()

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

send_msg_task.start()

while not stop_event.is_set():
  time.sleep(5)
