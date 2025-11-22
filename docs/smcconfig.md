# "SMC Config"

TODO most of this.

See Falcon disassembly, 0x24A5 for how the SMC config gets loaded.

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
