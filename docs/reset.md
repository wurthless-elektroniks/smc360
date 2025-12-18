# Reset statemachine

Locations:
- Falcon: 0x1122

## Falcon

### State 0

- Clear "has GetPowerUpCause arrived" flag.
- Clear "unmute audio flag" and assert AUD_CLAMP.
- Assert /GPU_RST_N and /CPU_RST_N, in that order.
- Clear "is CPU running" flag.
- Clear southbridge powergood flag and assert /SB_RST_N.
- Disable HANA(??) statemachine.
- Go to state 1.

### State 1

- Reset SFCX.
- Kill a ton of cycles.
- Set some SFR flag (to check later).
- Clear CPU powergood signal.
- If HANA mutex flag is cleared, run HANA reset logic immediately, otherwise
  go to state 2.

### State 2

- Spin until HANA mutex flag cleared. When it is, run the HANA reset logic below.

### HANA reset logic

Shared between states 1 and 2.

- Assert, then immediately de-assert HANA reset line.
- Set HANA active flag.
- We're done, so disable this statemachine and exit.