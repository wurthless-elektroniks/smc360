# Reset watchdog

The "reset watchdog" brings devices out of reset and makes sure that everything resets and runs correctly.

Locations:
- Xenon: 0x11C4
- Zephyr: 0x127A
- Falcon: 0x12C6
- Jasper: 0x12D5
- Trinity: 0x13E1
- Corona: 0x13E2
- Winchester: 0x13AD

## Xenon

### State 0

- Clear two flags (02Ah.6, purpose TODO and 023h.4=IPC RRoD raised)
- If IPC requested a reboot, then ask the reset statemachine to reboot everything, and go to state 11.
- Clear another flag (024h.7).
- If flag at 022h.1 is clear, set CPU_PWRGD and go to state 3.
- Bring GPU out of reset, load shared timer cell with 0x0D (13*20=260 ms), and go to state 1.

### State 1: Attempt to bring GPU out of coma

- Tick shared timer cell down until it expires. If it hasn't yet, do nothing else.
- Assert /GPU_RST_N, holding the GPU in reset.
- Load shared timer cell with 0x05 (5*20=100 ms), and go to state 2.

### State 2: Delay and then set CPU_POWERGD

- Tick shared timer cell down until it expires. If it hasn't yet, do nothing else.
- Set CPU_PWRGD and go to state 3.

### State 3

- Deassert /ANA_RST_N.
- Set SB_MAIN_PWRGD_R.
- Write some XSB magic SFR (SFR 0FCh), then kill a ton of cycles by writing that value to EXTMEM.
  The program always assumes XSB G0, so it always writes 0xC2.
- Go to state 4.

### State 4: Release GPU from reset

- Release GPU from reset and go to state 5.

### State 5

- Deassert /SB_RST_N.
- Set flag 022h.2.
- Load shared timer cell with 0x04 (4*20=80 ms), and go to state 2.

### State 6: GPU_RESET_DONE must go high in 80 ms

- If GPU_RESET_DONE is not 1, then tick the shared timer cell down; if that timer expires,
  then queue RRoD 0020 and go to state 10.
- Reload shared timer cell with 5 (=100 ms) and go to state 7.

### State 7: Check PCIe link status (must be OK in 100 ms), release CPU from reset, and start first GetPowerUpCause timeout

- Check PCIe status; if there is a link issue, tick the shared timer cell down, and if that timer
  expires, queue RRoD 0021 and and go to state 10.
- De-assert /CPU_RST_N.
- Load shared timer cell with 0xAF (175 * 20ms = 3500ms); this is the first half of the GetPowerUpCause timeout.
- Go to state 8.

### State 8: GetPowerUpCause timeout part 1

- If bit at 02Ah.6 set, immediately queue RRoD 0022 and go to state 10.
- If GetPowerUpCause arrived from IPC, shut the statemachine off as there's nothing more to do.
- If we got a RRoD from the IPC (probably hwinit failed), go to state 10 immediately.
- Tick the shared timer cell down, and if it expires, reload the timer (0xAF again, 3500ms more) and
  go to state 9.

### State 9: GetPowerUpCause timeout part 2

- If bit at 02Ah.6 set, immediately queue RRoD 0022 and go to state 10.
- If GetPowerUpCause arrived from IPC, shut the statemachine off as there's nothing more to do.
- If we got a RRoD from the IPC (probably hwinit failed), go to state 10 immediately.
- Tick the shared timer cell down, and if it expires, queue RRoD 0022 and go to state 10.

### State 10: Retry on failure, or give up

- The boot attempt has failed, so increment the number of boot attempts so far. We try up to 5
  times, so if this isn't our fifth attempt, then ask the reset statemachine to reboot everything,
  and go to state 11.
- The RRoD code has been set up for us already, but if the RRoD didn't get raised by the IPC, then
  default the RRoD general error pattern to the classic RRoD three lights pattern.
- Raise the RRoD and give up.

### State 11: Wait for reset sequence to finish

- Wait until the main reset sequence completes.
- If 02Ah.6 is clear, then go to state 0 to start the next boot attempt.
- Clear 024h.2, set DVD tray state to 0x65 ("error/unknown"), set 022h.0, and go to state 12.

### State 12: Do nothing until 022h.0 is cleared

- If 022h.0 is still set, do nothing.
- Set 024h.3, set memory cell at 062h to 0, set 021h.5, and go to state 13.

### State 13: Do nothing until 021h.5 is cleared

- If 021h.5 is still set, do nothing.
- Otherwise, go to state 0.

## Zephyr/Falcon

Behavior is more or less identical between these two.

### State 0: Reset SMC config to defaults and request SFCX to load the config from flash

- Clear any RRoD requested from IPC.
- If the system is starting from a cold boot, reset SMC config to defaults and read the SMC config
  page from flash (but don't process it yet), set CPU powergood and go to state 1.
- If the IPC requested a reboot, then ask the reset statemachine to reboot everything, and go to state 11.

### State 1: Parse SMC config

- Parse the SMC config from the flash page we loaded earlier. If there was a problem loading it,
  then fall back on defaults, and, if the SMC is not in development mode, set the "SMC config load
  error" flag that will be sent when the CPU runs GetPowerUpCause.
- Set southbridge powergood signal.
- Write some XSB magic SFR (SFR 0FCh), then kill a ton of cycles by writing that value to EXTMEM.
  On Zephyr, the value depends on the SB_DETECT I/O signal; if it's high (XSB R0) then write 0x43, otherwise
  write 0xC2. Falcon always shipped with a XSB R0, so the southbridge detection is removed and the
  code always writes 0x43.
- Proceed to state 2.

### State 2: GPU_RESET_DONE should be low

- Check GPU_RESET_DONE. If it's stuck high, queue RRoD 0020 and go to state 10.
- De-assert /GPU_RST_N (odd), then go to state 3.

### State 3: Assert /GPU_RST_N

- Assert /GPU_RST_N, then go to state 4.

### State 4: De-asssert /GPU_RST_N

- De-assert /GPU_RST_N, then go to state 5.

### State 5: Release southbridge reset and setup GPU_RESET_DONE timeout

- De-assert southbridge reset, set shared timer cell to 4 (=80 ms), and go to state 6.

### State 6: GPU_RESET_DONE must go high in 80 ms

- If GPU_RESET_DONE is not 1, then tick the shared timer cell down; if that timer expires,
  then queue RRoD 0020 and go to state 10.
- Reload shared timer cell with 5 (=100 ms) and go to state 7.

### State 7: Check PCIe link status (must be OK in 100 ms), release CPU from reset, and start first GetPowerUpCause timeout

- Check PCIe status; if there is a link issue, tick the shared timer cell down, and if that timer
  expires, queue RRoD 0021 and and go to state 10.
- Set "CPU running" flag and de-assert /CPU_RST_N.
- Load shared timer cell with 0xAF (175 * 20ms = 3500ms); this is the first half of the GetPowerUpCause timeout.
- Go to state 8.

### State 8: GetPowerUpCause timeout part 1

- If GetPowerUpCause arrived from IPC, shut the statemachine off as there's nothing more to do.
- If we got a RRoD from the IPC (probably hwinit failed), go to state 10 immediately.
- Tick the shared timer cell down, and if it expires, reload the timer (0xAF again, 3500ms more) and
  go to state 9.

### State 9: GetPowerUpCause timeout part 2

- If GetPowerUpCause arrived from IPC, shut the statemachine off as there's nothing more to do.
- If we got a RRoD from the IPC (probably hwinit failed), go to state 10 immediately.
- Tick the shared timer cell down, and if it expires, queue RRoD 0022 and go to state 10.

### State 10: Retry on failure, or give up

- The boot attempt has failed, so increment the number of boot attempts so far. We try up to 5
  times, so if this isn't our fifth attempt, then ask the reset statemachine to reboot everything,
  and go to state 11.
- The RRoD code has been set up for us already, but if the RRoD didn't get raised by the IPC, then
  default the RRoD general error pattern to the classic RRoD three lights pattern.
- Raise the RRoD and give up.

### State 11: Wait for reset sequence to finish

- Wait until the main reset sequence completes, then go to state 0.

