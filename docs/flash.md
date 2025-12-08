# Flash controller

Lots of this TODO

The SFCX (flash controller) is, at least in part, exposed to the SMC, mainly for loading the SMC config.
The SMC is probably also responsible for writing blocks to the flash when in debug mode (from the SPI bus)...

## Main flash controller (SFCX)

Used on small block and big block systems.

### SFRs

Again, all has to be tested thoroughly on real hardware...

| SFR  | Ghidra symbol | Description
|------|---------------|-----------------------------
| 0E3h | RXDAT         | Configuration register
| 0E5h | RXFLG         | PSB: extended flash information (bit 1 = big block)
| 0EAh | CCAP0L        | Address register, bits 7-0 (LSB)
| 0EBh | CCAP1L        | Address register, bits 15-8
| 0ECh | CCAP2L        | Address register, bits 23-16
| 0EDh | CCAP3L        | Address register, bits 31-24 (MSB)
| 0EEh | CCAP4L        | Status register
| 0F1h | EPINDEX       | Data register, bits 7-0 (LSB)
| 0F2h | TXSTAT        | Data register, bits 15-8
| 0F3h | TXDAT         | Data register, bits 23-16
| 0F4h | TXCON         | Data register, bits 31-24 (MSB)
| 0F5h | TXFLG         | Command register

### Accessing flash via the SFCX

Commands should be the same as in xenon_sfcx.h, but as a reminder:

- 0x02 reads the page in the address register to the internal buffer
- 0x00 reads four bytes at the given address from the internal buffer to the data register

It is also possible to launch NAND-to-SDRAM DMAs from this mode, but the SFCX registers used to start
the DMA must be programmed via GPU JTAG, and those registers must be set before hwinit runs, as hwinit
will disable the GPU's JTAG port. (This is actually how the JTAG SMC works.)

## eMMC

Registers all in EXTMEM space

- 0x0020~0x0023: eMMC read result
- 0x00EC: eMMC command/status? (write 1 to set 256-byte block address, 0 to read within block)
- 0x00ED~0x00EF: eMMC address (little endian)
- 0x00F3: eMMC status, bit 7 = 4gbytes eMMC present, bit 6 = NAND ready

## See also

- [libxenon NAND driver](https://github.com/Free60Project/libxenon/tree/master/libxenon/drivers/xenon_nand)
- [JTAG exploit explanation](https://github.com/gligli/tools/blob/master/imgbuild/hack.txt)
