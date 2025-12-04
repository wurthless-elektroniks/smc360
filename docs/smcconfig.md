# "SMC Config"

TODO most of this.

See Falcon disassembly, 0x24A5 for how the SMC config gets loaded.

## Default SMC config

The SMC program will setup default SMC config values at startup until it's able to read the real
configuration from flash. This is a failsafe in case the flash turns out to be unreadable, or the
SMC config ends up being corrupt.

## Flash (?) SFRs

Again, all has to be tested thoroughly on real hardware...

| SFR  | Ghidra symbol | Description
|------|---------------|-----------------------------
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

## Ignoring SMC config load errors

The Falcon SMC has an odd feature where SMC config load errors can be suppressed if DBG_LED0 is pulled high.
This doesn't inhibit SMC config loading; it only prevents error reporting to the CPU.