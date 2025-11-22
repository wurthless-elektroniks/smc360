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


