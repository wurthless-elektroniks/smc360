# Flash controller

Lots of this TODO

The SMC needs to access flash to load the SMC config. The SMC is probably also responsible for writing
blocks to the flash when in debug mode (from the SPI bus)...

## Main flash controller 

Used on small block and big block systems.

### SFRs

Again, all has to be tested thoroughly on real hardware...

| SFR  | Ghidra symbol | Description
|------|---------------|-----------------------------
| 0E5h | RXFLG         | PSB: extended flash information (bit 1 = big block)
| 0EAh | CCAP0L        | Word select?
| 0EBh | CCAP1L        | Offset????
| 0ECh | CCAP2L        | Offset????
| 0EDh | CCAP3L        | Offset????
| 0EEh | CCAP4L        | Status????
| 0F1h | EPINDEX       | Read result byte 0
| 0F2h | TXSTAT        | Read result byte 1
| 0F3h | TXDAT         | Read result byte 2
| 0F4h | TXCON         | Read result byte 3
| 0F5h | TXFLG         | Operation command?

## eMMC

Registers all in EXTMEM space

- 0x0020~0x0023: eMMC read result
- 0x00EC: eMMC command/status? (write 1 to set 256-byte block address, 0 to read within block)
- 0x00ED~0x00EF: eMMC address (little endian)
- 0x00F3: eMMC status, bit 7 = 4gbytes eMMC present, bit 6 = NAND ready

