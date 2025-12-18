# Power down statemachine

Locations:
- Falcon: 0x0EA4

## Falcon

### State 0: Wait for DVD tray to fully open or close

- If power or thermal protection RRoDs raised, don't bother waiting for the DVD tray;
  just go straight to state 1.

- If DVD tray state is 0x63 or 0x64, just keep waiting until it isn't before we go
  to state 1.

### State 1: Disable HANA clock outputs

Self explanatory; proceeds to state 1 after.

### State 2: Kill CPU power regulation

Clears the "VCPU regulator enabled" flag before actually disabling the CPU power regulator.
Proceeds to state 2 after.

### State 3: Kill 3v3 and re-assign 5v to the standby rail

### State 4: Kill 1v8

### State 5: Kill 5v regulator

### State 6: Kill GPU power (and other things)

### State 7: Kill 12v

- Kill 12v from the power brick by pulling PSU_12V_ENABLE low.

- If we powered off normally, then kill the HANA statemachine, turn off the ring of light, and set
  the shared timer cell to 0x19 (=500 ms) before going to state 8.

- If we were powered off by a power or thermal RRoD, then keep waiting until the user presses the power
  button (or similar) before we shut everything else off, otherwise they won't be able to see the error code.

### State 8: Tick cooldown timer down

### State 9

### State 10
