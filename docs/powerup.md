# Powerup statemachine

Locations:
- Falcon: 0x106D

## Falcon

### State 0: Enable 12v

- Enable 12v from the power brick by pulling PSU_12V_ENABLE high.
- Set shared timer cell to 10 (=200 ms) and go to state 1.

### State 1: 12v powergood must be true within 200ms

Tick the shared timer cell down; if it times out, raise RRoD 0001 and give up.
Otherwise, go to state 2.

### State 2: Enable GPU power

- Check 12v powergood signal again (has sideffects that set some SFR flag).
- Set flag indicating that 12v is enabled.
- Enable GPU power rail.
- Go to state 3

### State 3: GPU powergood must be true

- Check GPU powergood signal; if it's bad, fail immediately with RRoD 0003.
- Run GPU powergood signal check again (has sideffects that set some SFR flag).
- Set flag indicating that GPU power is enabled.
- Go to state 4.

### State 4

- Enable 5v and 1v8 regulators.
- Set shared timer cell to 2 (=40 ms).

### State 5

TODO, looks buggy

### State 6

- Handover 5v from 5vsb to main 5v regulator.
- Go to state 7.

### State 7: Enable HANA clock outputs

Enable clock generators and go to state 8.

### State 8: Enable CPU power

### State 9: Check CPU powergood signal and finish up

- Check CPU powergood signal; if it's bad, fail immediately with RRoD 0002.
- Check CPU powergood signal again (has sideffects that set some SFR flag).
- Set flag indicating that CPU power is enabled.
- Powerup is complete, so shut the powerup statemachine off.
