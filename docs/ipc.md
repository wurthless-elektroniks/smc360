# CPU-to-SMC IPC

Incomplete docs, might be different between SMC program revisions...

## Commands

### 0x01 - Get powerup cause

Input: `0x01`

Returns three bytes:
1. Power-up cause (see table below)
2. Number of boot attempts
3. Single bit (purpose TODO)

The SMC expects this command to be sent within a certain time period after the CPU is released from reset.
If it doesn't get it in time, it resets everything and tries again up to 5 times, then gives up with a RRoD.

The SMC doesn't care how many times this command is received; you can send it over and over and the values
should be the same every time. All that matters is you send it at least once.

Known power-up causes are taken from xeBuild and xenon-emu.

| Value | Description                                                                   |
|-------|-------------------------------------------------------------------------------|
| 0x11  | Console power button                                                          |
| 0x12  | Console DVD eject button                                                      |
| 0x15  | Undocumented (TODO)                                                           |
| 0x16  | Undocumented (TODO)                                                           |
| 0x20  | IR remote power button                                                        |
| 0x21  | Eject button on Xbox universal remote                                         |
| 0x22  | IR remote guide/X button                                                      |
| 0x24  | IR remote Windows button                                                      |
| 0x30  | "HalReturnToFirmware(1 or 2 or 3) = hard reset by smc"                        |
| 0x31  | "After leaving pnc charge mode via power button"                              |
| 0x41  | Kiosk/debug pin (EXT_PWR_ON_N pulled low)                                     |
| 0x55  | Wireless controller X button                                                  |
| 0x56  | Wired controller 1 X button (fat front top USB, slim front left USB)          |
| 0x57  | Wired controller 2 X button (fat front bottom USB, slim front right USB)      |
| 0x58  | Wired controller 3 X button (slim back middle USB)                            |
| 0x59  | Wired controller 4 X button (slim back top USB)                               |
| 0x5A  | Wired controller 5 X button (fat back USB, slim back bottom USB)              |

### 0x04 - TODO

TODO

### 0x07 - Get temperatures

TODO

### 0x0A - Get DVD tray state

TODO

### 0x0F - Get A/V pack status

TODO

### 0x12 - Get SMC version and two persistent memory cells

Input: `0x12`

Returns the following bytes:
1. SMC program type (should be the same as the byte at 0x100)
2. SMC major version (should be the same as the byte at 0x101)
3. SMC minor version (should be the same as the byte at 0x102)
4. Persistent memory cell A
5. Persistent memory cell B

This is actually the first SMC command to be sent, although it's in hwinit so it's understandable that
a lot of people missed it.

For whatever reason, the program doesn't actually read the header bytes at 0x100~0x102; instead it
hardcodes those values right into the command handler. Here's how it looks in the Falcon SMC:

```
       CODE:0a7c 74 01           MOV        A,#0x1
       CODE:0a7e 12 24 2a        LCALL      FUN_CODE_242a
       CODE:0a81 74 31           MOV        A,#0x31
       CODE:0a83 12 24 2f        LCALL      ipc_fifo_write
       CODE:0a86 74 01           MOV        A,#0x1
       CODE:0a88 12 24 2f        LCALL      ipc_fifo_write
       CODE:0a8b 74 06           MOV        A,#0x6
       CODE:0a8d 12 24 2f        LCALL      ipc_fifo_write
       CODE:0a90 e5 66           MOV        A,DAT_INTMEM_66
       CODE:0a92 12 24 2f        LCALL      ipc_fifo_write
       CODE:0a95 e5 67           MOV        A,DAT_INTMEM_67
       CODE:0a97 12 24 2f        LCALL      ipc_fifo_write
       CODE:0a9a 22              RET
```

Note that the persistent memory cells (labelled DAT_INTMEM_66 and DAT_INTMEM_67 here) will have been cleared to zero if the
power-up cause is 0x16.

### 0x13 - TODO

TODO

### 0x16 - TODO

TODO

### 0x17 - Get tilt switch status

TODO

### 0x1E - TODO

TODO

### 0x20 - TODO

TODO

### 0x82 - Reset/powerdown

TODO

### 0x85 - TODO

TODO

### 0x88 - TODO

TODO

### 0x89 - TODO

TODO

### 0x8B - Open/close DVD tray

TODO

### 0x8C - Set power LED/do Ring of Light boot animation

TODO

### 0x8D - TODO

TODO

### 0x90 - TODO

TODO

### 0x94 - TODO

TODO

### 0x95 - TODO

TODO

### 0x98 - TODO

TODO

### 0x99 - Set RoL LEDs

TODO

### 0x9A - System error (RRoD)

Input bytes:
1. Command `0x9A`
2. TODO (must be less than 0x0F?)
3. Error code as 4x2-bit packed values
4. Flags (bit 0 = hardware failure, bit 1 = one green/two red?, both bits 0/1 clear = RRoD classic)

TODO

### 0x9B - TODO

TODO

### 0x9C - Set persistent memory cell values

Inputs:
1. Command `0x9C`
2. Persistent memory cell value 1 (e.g., in Falcon at DAT_INTMEM_66)
3. Persistent memory cell value 2 (e.g., in Falcon at DAT_INTMEM_67)

Outputs: Nothing

### 0x9D - TODO

TODO

### 0x9F - TODO

TODO

## See also

xenon-emu SMC code (some of these are wrong)
- [source](https://github.com/xenon-emu/xenon/blob/main/Xenon/Core/PCI/Devices/SMC/SMC.cpp)
- [header](https://github.com/xenon-emu/xenon/blob/main/Xenon/Core/PCI/Devices/SMC/SMC.h)

