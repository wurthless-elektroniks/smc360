# Statemachine documentation

Hey, you! Do you like reading annoying, unreadable and difficult to debug spaghetti code? Well, I got the
deal of the century for you!

Because of Microsoft's decision to use the 8051 core to run the SMC, and not something more modern like an
ARM MCU (that would cost royalty money), the SMC is limited in how it can multitask. A bunch of different
tasks run in the mainloop at the same time, and each can't run in a loop because of how slow the 8051 is
(a reminder: one instruction is 12 cycles at best). The result is that everything is implemented as a
state machine, where each task checks if it's enabled, runs its logic for the given state, then gives up
its timeslice and moves on to the next task.

As mentioned, this is really annoying to debug, because when everything is implemented like this, you
can't just say "okay, power down the system"; the SMC code has to set one flag that's picked up by the power-down
state machine, which advances through its steps one at a time until it completes, and while it executes,
it's free to cause a bunch of side-effects that either start other tasks or set random flags somewhere
with no clear purpose.

Most tasks run in 20 ms intervals, but a few others run in "real time" after the 20 ms block is done.

## State machines at a glance

These are NOT listed in their order of operations as they're different between SMCs.

Every 20 ms:
- Monitor various powergood signals and RRoD if something goes wrong. Function documented [here](vregmon.md).
- Read /EXT_PWR_ON_N
- Read power and eject switches
- Read bind switch (that pairs wireless controllers to the RF board)
- Read tilt switch
- Update AUD_CLAMP to mute/unmute audio outputs
- Read IR receiver
- Update DVD tray status
- Check if temperature sensor is returning values via I2C and RRoD if it isn't
- Check temperature sensors and go into overheat protection if thermal protection trips; otherwise, update fan speeds
- Update debug LED logic. Behavior documented [here](dbgleds.md).
- Check various power-on events and act on them
- If powering up, run the power-up sequence. Behavior documented [here](powerup.md).
- If coming out of reset, make sure all devices reset and that GetPowerUpCause arrives from the CPU in time,
  trying several times until finally giving up with a RRoD. Behavior documented [here](resetwatchdog.md).
- If resetting, run the hardware reset sequence. Behavior documented [here](reset.md).
- If powering down, run the power-down sequence. Behavior documented [here](powerdown.md).

In a loop as fast as possible:
- Handle SMC-to-HANA communication over I2C (convoluted and not fun to disassemble)
- Handle CPU-to-SMC IPC communication (split into different tasks)
- Update Argon state
