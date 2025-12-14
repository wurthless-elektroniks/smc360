# "SMC Config"

TODO most of this.

The "SMC Config" is the 360 community name for a bunch of pages that affect not only the "real" SMC
configuration, but a bunch of other system settings to. In the context of this doc, "SMC config"
refers only to what the SMC sees.

See Falcon disassembly, 0x24A5 for how the SMC config gets loaded.

## SMC config locations

Small block and big block locations depend on what SFR 0E3h bits 4/5 (NAND size) read back.
On eMMC systems, the SMC config will always be read from 0x02FFC000.

### Small block systems

This should be true for all XSB-based boards. 

| Bits | NAND size | Logical address | Physical address  |
|------|-----------|-----------------|-------------------|
| 00   | 8 mbytes  | 0x007BE000      | 0x007FBF00        |
| 01   | 16 mbytes | 0x00F7C000      | 0x00FF7E00        |
| 10   | 32 mbytes | 0x01EFC000      | 0x01FF3E00        |
| 11   | 64 mbytes | 0x03DFC000      | 0x03FEBE00        |

Table from Falcon SMC, matches one in Jasper too. This table is also in the Trinity SMC program
but I'm not sure if it's used there because it's a PSB board.

The 8 and 32 mbytes configurations were never used in any console; 16mbytes is standard for retail
and 64 mbytes was used in devkits.

### Big block systems

| Bits | NAND size | Logical address | Physical address  |
|------|-----------|-----------------|-------------------|
| 00   | 16 mbytes | 0x00F7C000      | 0x00FF7E00        |
| 01   | 16 mbytes | 0x00F7C000      | 0x00FF7E00        |
| 10   | Big boy   | 0x03BE0000      | 0x03DBF000        |
| 11   | Big boy   | 0x03BC0000      | 0x03D9E000        |

Table from Jasper SMC.

I put "big boy" for the big block NANDs on Jasper arcade systems because Microsoft gave them no
specific size. In the Jasper and Tonkaset schematics they simply refer to those configurations
as "various sizes".

## SMC config values

Most of this shamelessly stolen from J-Runner.

Again, keep in mind that there are other fields in the SMC config; these are only the ones that the
SMC program cares about.

| Offset(s) | Description                                                             |
|-----------|-------------------------------------------------------------------------|
| 0x00,0x01 | Checksum of all bytes from 0x10 to 0x3F inclusive                       |
| 0x0E      | Structure version (4 for fats, 5 for slims)                             |
| 0x11      | Fan 1 speed override (bit 7 must be 1 to override)                      |
| 0x12      | Fan 2 speed override (bit 7 must be 1 to override)                      |
| 0x13      | ????????? (slims only)                                                  |
| 0x14      | If bit 1 set, stop loading the config and use default SMC config values |
| 0x18,0x19 | CPU temperature sensor gain                                             |
| 0x1A,0x1B | CPU temperature sensor offset                                           |
| 0x1C,0x1D | GPU temperature sensor gain                                             |
| 0x1E,0x1F | GPU temperature sensor offset                                           |
| 0x20,0x21 | eDRAM temperature sensor gain                                           |
| 0x22,0x23 | eDRAM temperature sensor offset                                         |
| 0x24,0x25 | Chassis temperature sensor gain                                         |
| 0x26,0x27 | Chassis temperature sensor offset                                       |
| 0x28      | HANA register 0xDB override                                             |
| 0x29      | CPU target temperature                                                  |
| 0x2A      | GPU target temperature                                                  |
| 0x2B      | eDRAM target temperature                                                |
| 0x2C      | CPU thermal protection trip temperature                                 |
| 0x2D      | GPU thermal protection trip temperature                                 |
| 0x2E      | eDRAM thermal protection trip temperature                               |
| 0x2F      | ????????? (slims only)                                                  |

### Default config values

The SMC program will setup default SMC config values at startup until it's able to read the real
configuration from flash. This is a failsafe in case the flash turns out to be unreadable, or the
SMC config ends up being corrupt.

The default configuration values are:

| Field                | Xenon    | Zephyr  | Falcon  | Jasper  | Trinity | Corona  | Winchester
|----------------------|----------|---------|---------|---------|---------|---------|----------------
| Fan 1 speed override | n/a      | `e4`    | `e4`    | `e4`    | `e4`    | `??`    | `??`
| Fan 2 speed override | n/a      | `e4`    | `e4`    | `e4`    | ????    | `??`    | `??`
| CPU temp gain        | `57 2a`  | `57 2a` | `57 2a` | `57 2a` | `TO DO` | `TO DO` | `TO DO`
| CPU temp offset      | `be 8a`  | `be 8a` | `be 8a` | `be 8a` | `TO DO` | `TO DO` | `TO DO`
| GPU temp gain        | `4b f1`  | `4b f1` | `4b f1` | `4b f1` | `TO DO` | `TO DO` | `TO DO`
| GPU temp offset      | `74 b9`  | `74 b9` | `74 b9` | `74 b9` | `TO DO` | `TO DO` | `TO DO`
| eDRAM temp gain      | `4b f1`  | `4b f1` | `4b f1` | `4b f1` | `TO DO` | `TO DO` | `TO DO`
| eDRAM temp offset    | `74 b9`  | `74 b9` | `74 b9` | `74 b9` | `TO DO` | `TO DO` | `TO DO`
| Board temp gain      | `4a b4`  | `4a b4` | `4a b4` | `4a b4` | `TO DO` | `TO DO` | `TO DO`
| Board temp offset    | `75 6a`  | `75 6a` | `75 6a` | `75 6a` | `TO DO` | `TO DO` | `TO DO`
| HANA 0xDB override   | `03`     | `03`    | `03`    | `03`    | `03`    | `??`    | `??`      
| CPU target temp      | `4e`     | `50`    | `50`    | `50`    | `52`    | `??`    | `??`      
| GPU target temp      | `5f`     | `61`    | `61`    | `47`    | `4c`    | `??`    | `??`      
| eDRAM target temp    | `5f`     | `64`    | `64`    | `49`    | `4c`    | `??`    | `??`      
| CPU trip temp        | `64`     | `64`    | `64`    | `64`    | `59`    | `??`    | `5b`      
| GPU trip temp        | `6e`     | `6e`    | `6e`    | `6e`    | `52`    | `??`    | `52`      
| eDRAM trip temp      | `6e`     | `75`    | `75`    | `75`    | `52`    | `??`    | `52`      

Note, of course, that these temperature sensor calibration values will likely not be accurate on your
console as they're calibrated at the factory.

## Ignoring SMC config load errors

The Falcon SMC has an odd feature where SMC config load errors can be suppressed if DBG_LED0 is pulled high.
This doesn't inhibit SMC config loading; it only prevents error reporting to the CPU.