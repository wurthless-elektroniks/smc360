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

## Hacked SMCs

Typical hacked SMCs:

- CR4 was created by Team Xecuter and adds I2C slowdown control on DBG_LED0 for RGH2+ (also Muffin/Mufas).
- SMC+ is a hexedit of CR4 that shortens SMC handshake timeouts.

JTAG, RGH3 and others that are actively used in glitch/software exploits are to be documented in more detail later.

## Board compatibility

- Xenon boards use two different southbridges (G0 and R0). Xenon v2 should be compatible with both revisions;
  the Xenon JTAG SMC is a hacked version of v2.

- Zephyr/Falcon/Jasper are more or less the same board from a SMC perspective so Jasper can be used for all
  three boards. Note however that the checkstop signal on Falcon/Jasper is a jumper on Zephyr (SB_DETECT).
  RGH3 v1 uses the Jasper SMC for Falcon/Jasper; the Z/F/J JTAG SMC is also a hacked Jasper SMC.

