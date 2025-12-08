# "SMC Config"

TODO most of this.

The "SMC Config" is the 360 community name for a bunch of pages that affect not only the "real" SMC
configuration, but a bunch of other system settings to. In the context of this doc, "SMC config"
refers only to what the SMC sees.

See Falcon disassembly, 0x24A5 for how the SMC config gets loaded.

## Default SMC config

The SMC program will setup default SMC config values at startup until it's able to read the real
configuration from flash. This is a failsafe in case the flash turns out to be unreadable, or the
SMC config ends up being corrupt.

## SMC config locations

Small block and big block locations depend on what SFR 0E3h bits 4/5 (NAND size) read back.
On eMMC systems, the SMC config will always be read from 0x02FFC000.

### Small block systems

| Bits | Logical address |
|------|-----------------|
| 00   | 0x007BE000      |
| 01   | 0x00F7C000      |
| 10   | 0x01EFC000      |
| 11   | 0x03DFC000      |

(Table from Falcon SMC, matches one in Jasper too)

### Big block systems

| Bits | Logical address |
|------|-----------------|
| 00   | 0x00F7C000      |
| 01   | 0x00F7C000      |
| 10   | 0x03BE0000      |
| 11   | 0x03BC0000      |

(Table from Jasper SMC)

## Ignoring SMC config load errors

The Falcon SMC has an odd feature where SMC config load errors can be suppressed if DBG_LED0 is pulled high.
This doesn't inhibit SMC config loading; it only prevents error reporting to the CPU.