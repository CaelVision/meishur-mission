# Device Forwarding

Awesome `socat` can forward the character device to another computer via networking.
This means one path planning app can be used either to debug and to monitor, or to be deployed on the Jetson.

1. Start the server on the Jetson
```bash
socat TCP-LISTEN:5001 /dev/ttyACM0,rawer
```
2. Run the local "proxy"
```bash
socat PTY,link=$HOME/capstone/ttyACM0,rawer,wait-slave TCP4:100.117.46.142:5001
```

# Simulation

To start the Software-in-the-loop (SITL) software called`SITL`, make sure that the following prerequisites are installed.
They are not installed automatically.
1. `empy==3.3.4` newer versions don't parse the templates right
2. `wxPython` is installed, otherwise the "map" and "console" UI modules won't load and yield "import failed" instead.

The package `dronekit-sitl` downloads its own ArduCopter + flight dynamics simulation binary by default.
A built binary can be optionally specified as `SITL_BINARY`.

I'm trying to
1. Start SITL
	1. `../Tools/autotest/sim_vehicle.py --map --console` doesn't allow me to connect to the SITL instance :(
	2. I can either
		1. Forward the MAVProxy MAVlink connection to another port to allow a different app to send MAVlink msgs to the virtual Copter
		2. Figure out how to launch SITL using `dronekit_sitl`
			1. I ran into an issue running `basic_example.py`, where it launched SITL with `dronekit_sitl`
			2. I can try running my own binary. Maybe that will help
2. Connect to the virtual Copter and run my own scenario scripted in Python using `dronekit`

Right now I can connect to a running session after the SITL binary is built by `sim_vehicle.py`.
No idea why the commands didn't work after building but I can launch them individually:

```bash
/Users/stephenw/capstone/ardupilot/Tools/autotest/run_in_terminal_window.sh ArduCopter /Users/stephenw/capstone/ardupilot/build/sitl/bin/arducopter -S --model + --speedup 1 --slave 0 --defaults /Users/stephenw/capstone/ardupilot/Tools/autotest/default_params/copter.parm --sim-address=127.0.0.1 -I0
```

```bash
mavproxy.py --out 127.0.0.1:14550 --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --console --map
```

# Dronekit

Drone kit is an abstraction over working directly with `pymavlink`.
I needed to build my own abstraction either way so `dronekit` is a very nice point to start with.

Since `dronekit` isn't maintained anymore, this patch needs to be manually installed:

In `INSTALLATION_PATH/lib/python3.x/site-packages/dronekit/__init__.py`, change
```python
class Parameters(collections.MutableMapping, HasObservers):
```
to
```python
class Parameters(collections.abc.MutableMapping, HasObservers):
```
