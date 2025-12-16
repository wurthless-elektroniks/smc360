# SMC versions

## Known versions

| Revision      | Rev. Byte @ 0x100 | Version @ 0x101,0x102 |
|---------------|-------------------|-----------------------|
| Xenon v2      | 0x12              | 1.51                  |
| Zephyr v1     | 0x21              | 1.10                  |
| Falcon v1     | 0x31              | 1.06                  |
| Jasper v1     | 0x41              | 2.03                  |
| Trinity v1    | 0x51              | 3.01                  |
| Corona v2     | 0x62              | 2.05                  |
| Winchester v1 | 0x71              | 1.03                  |

TODO: there must be a Xenon v1, but I couldn't find it in any of my NAND dumps... someone else have it?

## Version differences

These basically mirror hardware revisions, but whatevs...

### Xenon

TODO

- SFR 0FCh is always set to 0xC2

### Zephyr

- First HANA board
- Function that halts execution now moves past 0x2000 (the SMC bootstrapping ROM is probably mapped before there)
- Debug LED statemachine keeps most of the Xenon features, but writes to anything other than DBG_LED0 are stubbed out
- Xenon code that strobes DBG_LED3 when GPU is released from reset was left in by mistake
- SFR 0FCh is now set to 0x43 for XSB R0 systems (detected using a jumper on I/O signal SB_DETECT)

### Falcon

- Adds weird debug buffers accessible over IPC
- Adds checkstop support, although the program doesn't use it to raise any errors
- Buggy Xenon code that strobes DBG_LED3 still present
- SFR 0FCh now set to 0x43 always

### Jasper

- PSB support, with XSB backwards compatibility
- Reset watchdog statemachine changes
- Buggy Xenon code that strobes DBG_LED3 still present
- GetPowerUpCause watchdog timeout shortened from 7000 ms to 5200 ms to account for faster hwinit
- New sanity check function in reset watchdog statemachine that behaves differently between XSB and PSB boards (at 0x0084)
- SFRs 097h, 0A9h and 0DFh are set to 0 when CPU is brought out of reset

### Trinity

- RRoD handling code simplified (there also have to be lots of other Boron changes to document)
- Debug LED statemachine massively cleaned up; no more state tracking for LEDs that were removed ages ago
- Buggy Xenon leftover code that strobed DBG_LED3 is finally removed
- Big boy NANDs are still supported, even if no retail Trinity systems ever used anything other than 16mbytes
- Partial XSB support remains although it's useless as Trinity never shipped with a XSB
- Fan speed algorithm tables have changed because of the new CGPU fan setup
- Support for the second (GPU) fan dropped: PWM channel 2 duty cycle now set to 0 always, thermal stuff no
  longer updates the second fan, IPC command 0x94 is removed
- SMC config loader now uses structure version 5

### Corona

- KSB support
- SFR 0FCh usage is completely different now

### Winchester

- IR driver code seems to be left in

## Board compatibility

- Xenon boards use two different southbridges (G0 and R0). Xenon v2 should be compatible with both revisions;
  the Xenon JTAG SMC is a hacked version of v2.

- Zephyr/Falcon/Jasper are more or less the same board from a SMC perspective so Jasper can be used for all
  three boards. Note however that the checkstop signal on Falcon/Jasper is a jumper on Zephyr (SB_DETECT).
  RGH3 v1 uses the Jasper SMC for Falcon/Jasper; the Z/F/J JTAG SMC is also a hacked Jasper SMC.
