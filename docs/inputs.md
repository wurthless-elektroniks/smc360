# Input handling

Input handling of various buttons (power, eject, bindswitch, tiltswitch, and /EXT_PWR_ON_N) is broken up
into several distinct statemachines. Half of it is easily debounce logic. (Fun exercise for the reader:
can you sizecode better input handling functions?)

## /EXT_PWR_ON_N

Quick refresher: this is the debug pin on the SMC header that turns the system on, and it's also connected to
pin 30 on the A/V port. Pulling it low powers the system on.

Locations:
- Falcon: 0x14A5

Statemachine is much more complex than expected, have to do that later, but it looks like it can trigger
an I2C event...

## Power/eject switch

Handles the obvious, but also handles some RRoD logic (hold bindswitch then press eject to display the error codes).
The power and eject switch flags are picked up by other statemachines.

Locations:
- Falcon: 0x1C87

### Falcon

- State 0: Check power and eject switches in that order. If either are pushed, wait for them not to be pushed.
  Otherwise, go to state 1.
- State 1: Similar to state 0; if power or eject switch pushed, go back to state 0, otherwise go to state 2.
- State 2: Read power and eject switches. If both are pressed, do nothing. If the power switch is pressed, go
  to state 3. If the eject switch is pressed, go to state 4.
- State 3: If the eject switch was pressed or the power button was released, go back to state 2. Otherwise,
  set the "power switch pushed" flag, and go back to state 0.
- State 4: If the power switch was pressed or the eject switch was released, then then go back to state 2.
  If RRoD is being displayed, also check if the bindswitch was pressed, and, if so, advance through the RRoD
  display states. Otherwise, it's a normal eject switch push, so set the "eject switch pushed" flag and go
  back to state 0.

## Bindswitch

This handles the input only; the Argon statemachine picks up the "bindswitch pushed" flag and runs that logic
for us.

Locations:
- Falcon: 0x1385

### Falcon

- State 0: Wait for bindswitch to be released, then go to state 1.
- State 1: Similar to state 0; if bindswitch is pushed, go back to state 0, else go to state 2.
- State 2: Actually read the bindswitch. Do nothing until it is pushed, else go to state 3.
- State 3: The bindswitch should still be pressed, if it isn't, then go back to state 2. Otherwise,
  set the "bindswitch pushed" flag and go to state 0.

## Tiltswitch

Somehow this requires even more debounce logic than the other switches.

Locations:
- Falcon: 0x20AB

### Falcon

- State 0: Reload timer value (set it to 4 =80ms). As long as the tiltswitch is not active, stay in
  state 0, otherwise go to state 1.
- State 1: If tiltswitch suddenly was released, go back to state 0. Otherwise, tick the timer down,
  staying in state 1 until it expires. When it does, we set some flags. First, set a general "tiltswitch
  is pushed" flag that will be read by IPC and Argon logic. Second, set a flag that will schedule an
  IPC "tiltswitch changed" asynchronous message (which will be cancelled if GetPowerUpCause hasn't arrived
  yet). Third, set a flag that will schedule an Argon message that changes the Ring of Light orientation.
  Finally, head to state 2.
- State 2: Reload the timer value (set it to 25 =500ms). While the tiltswitch is still pressed, keep running
  state 2 logic. Otherwise, go to state 3.
- State 3: Opposite of State 2 logic, but does something similar. If the tiltswitch is pushed again, go back
  to state 2, otherwise tick the timer down until it expires, at which point we clear the "tiltswitch pushed"
  flag, schedule the IPC and Argon events, and go back to state 0.
