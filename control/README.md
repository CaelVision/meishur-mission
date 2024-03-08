Thank you ArduPilot you implement (pretty much) everything we need.

# Ardupilot Architecture

Here are some brief notes of the control architecture
- `Copter` adds tasks to the scheduler so that tasks run "concurrently"
	-  `run_rate_controller` updates `dt` for the discrete attitude and position controllers, then call attitude controller iteration
	- `update_throttle_hover` update estimated throttle required to hover :O
	- `update_flight_mode` calls `run` for the current mode, which calls other "run"s that checks conditions and "turn features on/off"

In Copter,
- `ModeAuto::wp_bearing()` returns the bearing calculated from current position to the next waypoint but doesn't appear to be used by any controller; probably only logging
- AC_AttitudeControl_Multi addes `_sysid_ang_vel_body.z` to `_ang_vel_body.z` and uses that for `_motors.set_yaw()`, where `_motors` is `AP_Motors`
- An AC_PID object has `get_ff()`, which multiplies a "FF gain" (`_kff`) to the reference (`_target`)
	- How does this param get initialized?

## Questions about control flow
1. How does the transition between copter mode and plane mode work? Do I make another Flight Mode within copter?
2. Which metrics are relevant to copter control? Are they logged already?
3. 

# Servo Control

Modifications were made to ArduPilot to output PWM signals to I2C instead of the default PWM pins.

`AP_HAL::RCOutput` has 32 channels.
If I can figure out where they are individually initialized, maybe I can change a specific channel to use I2C.
This way all the RC passthrough magic and whatnot will still work.

Oh wow `SRV_Channels::var_info[]` looks like where each channel is initialized.
Nope it "fills up" a constant struct array based on the hardware capability.
No function assignment or options here.

`SRV_Channel` seems to be a layer of abstraction for `RCOutput` huh.

The workflow seems to be `Plane` -> `SRV_Channels` -> `SRV_Channel` -> `RCOutput` (aka `hal.rcout`).
In ChibiOS, `RCOutput` is hardwired to be using PWM in GPIO pins.
So much for "I2C peripheral" mentioned in the docs.
ChibiOS handles STM32F4 boards, so there isn't a "special case" that I can overwrite rn.

Ik the lingo in ArduPilot code for the role of a servo motor is a **function**, but I'll refer to it as **role** so that it doesn't sound like a C++ function.

Now I'm hard-coding behaviour for `SRV_Channel` that have our motor roles.
I think it's important to bypass the `SRC_Channels::disabled_mask` check because the bit flags get their values from `hal.rcout->get_disabled_channels()`, which "deactivates" channels that are being occupied by another digital channel.

Currently tof 16, compass 28/30

# Ardupilot Parameters

Imma track the parameters uploaded to the flight controller here.

Here are the control parameters:
