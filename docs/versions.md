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

### Zephyr

TODO

### Falcon

- Adds checkstop support, although the program doesn't use it to raise any errors

### Jasper

- Big block support
- Reset watchdog statemachine changes
- Buggy Xenon code that strobes DBG_LED3 still present

### Trinity

TODO

### Corona

- KSB support

### Winchester

- IR driver code seems to be left in

## Board compatibility

- Xenon boards use two different southbridges (G0 and R0). Xenon v2 should be compatible with both revisions;
  the Xenon JTAG SMC is a hacked version of v2.

- Zephyr/Falcon/Jasper are more or less the same board from a SMC perspective so Jasper can be used for all
  three boards. Note however that the checkstop signal on Falcon/Jasper is a jumper on Zephyr (SB_DETECT).
  RGH3 v1 uses the Jasper SMC for Falcon/Jasper; the Z/F/J JTAG SMC is also a hacked Jasper SMC.
