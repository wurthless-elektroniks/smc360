# CPU-to-SMC IPC

Incomplete docs, might be different between SMC program revisions...

## Talking to the SMC from the CPU

To talk to the SMC, you must initialize the PCI space fully. Normally hwinit does this for you and you'll
be able to talk to the SMC (and other southbridgey stuff) at 0xEA001000. But if your code runs before hwinit
happens, or you're running a completely custom CB or other payload, then it's up to you to initialize everything
before accessing the SMC. [Mate's CPU key dumper](https://codeberg.org/hax360/tools/src/branch/main/glitchtools/dumpkey/src/dumpkey.S)
was probably the first custom code to do this; [CB_Y in RGH1.3](https://github.com/wurthless-elektroniks/RGH1.3/blob/main/ppc/cb_y.s)
takes a similar approach but was written to be easier to read and maintain.

The SMC has two FIFOs, which are its inbox (0xEA001080 for data and 0xEA001084 status) and its outbox
(0xEA001090 for data and 0xEA001094 for status). Plenty of code exists to demonstrate how to use all of these,
but the basics are:

- The PowerPC reads and writes data from the SMC FIFOs 32 bits at a time. The PCI space is little-endian
  so `lwbrx` and `stwbrx` are typically used to access it. In reality it's better to use big endian accesses with the SMC
  inbox and outbox because a hypothetical command `f0 01 02 03` would be written in little endian as 0x030201F0.

- The flags at 0xEA001084 and 0xEA001094 are simple mutex registers; the CPU and SMC can both write to these
  to indicate that something is accessing the FIFOs. When writing a message, the CPU will spin while
  `(0xEA001084 & 4)` (the SMC inbox) is non-zero, then will set the register to 4, write its message,
  then clear it. The SMC will then pick up the message, set the flag, process the message (even to discard it),
  then clear it. The same goes for 0xEA001094, which belongs to the SMC's outbox.


## Talking to the CPU from the SMC

Much TODO.

- The SMC reads and writes data from the SMC FIFOs eight bits at at a time. The SMC doesn't really care that
  the CPU has written 8 bytes when the message only requires 6, it will ignore the rest of the message.
  You'll see code in libxenon writing more bytes than necessary to the FIFO, but it was probably written that way 
  to make the code easier to reuse.

### IPC SFRs

These have to be reverse engineered in full. Don't think anyone's done that before...

| SFR  | Ghidra symbol | Description                            |
|------|---------------|----------------------------------------|
| 0D5h | HPSC          | Outbox write; pointer auto-increments  |
| 0D6h | DAT_SFR_d6    | Outbox control; sets pointer           |
| 0E1h | EPCON         | Inbox read; pointer auto-increments    |
| 0E2h | RXSTAT        | Inbox control, sets pointer            |

## Commands

SMC commands are broken up into two kinds: getters (bit 7 clear), which are expected to return
a response, and setters (bit 7 set) which do not respond at all.

When a getter command is sent, the SMC will clear the outbox to zero, then the first byte (i.e., byte 0)
of the outbox will be set to the command ID (needed because some SMC-to-CPU IPC messages happen asynchronously).
If it turns out to be an unrecognized command, the SMC will short-circuit here and not respond with anything
else, only an acknowledgement that it got the message. If it does recognize the getter command ID, then the rest
of the message will be populated. This is why the output formats listed below start with index 0.

Setter messages aren't acknowledged at all; no response is sent, and unrecognized commands are silently dropped.

### 0x01 - Get powerup cause (also complete handshake/disable reset watchdog)

Input bytes:
1. Command `0x01`

Output bytes:
1. Power-up cause (see table below)
2. Always zero
3. Number of boot attempts
4. Single bit, bit 0 indicates SMC config load error (1 if true)

The SMC expects this command to be sent within a certain time period after the CPU is released from reset.
If it doesn't get it in time, it resets everything and tries again. After five failed attempts, the SMC
gives up with a RRoD.

The SMC doesn't care how many times this command is received; you can send it over and over and the values
should be the same every time. All that matters is you send it at least once.

Known power-up causes are taken from xeBuild and xenon-emu.

| Value | Description                                                                   |
|-------|-------------------------------------------------------------------------------|
| 0x11  | Console power button                                                          |
| 0x12  | Console DVD eject button                                                      |
| 0x15  | RTC wakeup                                                                    |
| 0x16  | RTC wakeup unexpectedly?? (clears persistent SMC memory values)               |
| 0x20  | IR remote power button                                                        |
| 0x21  | Eject button on Xbox universal remote                                         |
| 0x22  | IR remote guide/X button                                                      |
| 0x24  | IR remote Windows button                                                      |
| 0x30  | CPU requested reboot via IPC                                                  |
| 0x31  | "After leaving pnc charge mode via power button"                              |
| 0x41  | Kiosk/debug pin (/EXT_PWR_ON_N pulled low)                                    |
| 0x55  | Wireless controller X button                                                  |
| 0x56  | Wired controller 1 X button (fat front top USB, slim front left USB)          |
| 0x57  | Wired controller 2 X button (fat front bottom USB, slim front right USB)      |
| 0x58  | Wired controller 3 X button (slim back middle USB)                            |
| 0x59  | Wired controller 4 X button (slim back top USB)                               |
| 0x5A  | Wired controller 5 X button (fat back USB, slim back bottom USB)              |

### 0x04 - Get RTC value and RTC alarm setting

Input bytes:
1. Command `0x04`

Output bytes:

0. Command `0x04` 
1. RTC value in milliseconds, bits 0-7
2. RTC value in milliseconds, bits 8-15
3. RTC value in milliseconds, bits 16-23
4. RTC value in milliseconds, bits 24-31
5. RTC value in milliseconds, bits 32-40
6. Flags: bit 0 = has time been set yet?, bit 1 = is RTC wake feature enabled?
6. RTC wakeup value in milliseconds, bits 32-40
7. RTC wakeup value in milliseconds, bits 24-31
8. RTC wakeup value in milliseconds, bits 16-23
9. RTC wakeup value in milliseconds, bits 8-15

### 0x07 - Get temperatures

Input bytes:
0. Command `0x07`

Output bytes:

0. Command `0x07`
1. CPU temperature, fraction of degrees
2. CPU temperature, degrees
3. GPU temperature, fraction of degrees
4. GPU temperature, degrees
5. eDRAM temperature, fraction of degrees
6. eDRAM temperature, degrees
7. Chassis temperature, fraction of degrees
8. Chassis temperature, degrees
9. Not sure yet

All temperatures returned are in degrees Celsius.

### 0x0A - Get DVD tray state

TODO

### 0x0F - Get A/V pack status

TODO

### 0x11 - I2C transaction

Also called "pure pain and suffering to fully reverse engineer", as I2C operations are handled asynchronously.

I hope you can understand this TODO item.

### 0x12 - Get SMC version and two persistent memory cells

Input: `0x12`

Returns the following bytes:
1. SMC program type (should be the same as the byte at 0x100)
2. SMC major version (should be the same as the byte at 0x101)
3. SMC minor version (should be the same as the byte at 0x102)
4. Persistent memory cell A
5. Persistent memory cell B

This is actually the first command the CPU sends to the SMC, although it's in hwinit so it's understandable that
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

### 0x13 - Copy inbox contents to outbox

This does exactly what it does on the tin: it copies the entire inbox to the outbox. It doesn't care how many bytes the CPU
has written to the inbox; it will always read and write 16 bytes.

### 0x16 - TODO

TODO

### 0x17 - Get tilt switch status

Outputs:

0. Command `0x17`
1. Single bit indicating tilt switch orientation (0 = no tilt, 1 = tilt)

### 0x1E - Read 12 bytes from SMC memory (SMC_READ_82_INT)

TODO

Not present on Xenon

### 0x20 - Read 12 bytes from SMC memory (SMC_READ_8E_INT)

TODO

Not present on Xenon

### 0x82 - Reset/powerdown

TODO

### 0x85 - Set RTC

Input bytes:
1. Command `0x85`
2. RTC value byte 1
3. RTC value byte 2
4. RTC value byte 3
5. RTC value byte 4
6. RTC flags???

TODO

### 0x88 - Set fans

Inputs:
1. Command `0x88`
2. Bit field. bit 0 = TODO, bit 1 = force fans to run at full speed

### 0x89 - TODO

TODO

### 0x8B - Open/close DVD tray

TODO

### 0x8C - Set power LED/do Ring of Light boot animation

TODO

### 0x8D - Assert/de-assert AUD_CLAMP

Inputs:
1. Command `0x8D`
2. One bit (bit 0): if 0, assert AUD_CLAMP (mutes audio), else de-assert it (unmutes audio)

No outputs.

The flag that sets AUD_CLAMP defaults to 0 on reboot, which mutes audio until the CPU requests it to be unmuted.

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
2. Error code as 4x2-bit packed values
3. Error code as 4x2-bit packed values (always sent twice)
4. Flags (bit 0 = hardware failure, bit 1 = one green/two red?, both bits 0/1 clear = RRoD classic)

Outputs: Nothing

Error code from IPC cannot be less than 0100 (reserved for SMC errors); if it is, it'll be ignored.

### 0x9B - Set RTC wake time

Input bytes:
1. Command `0x9B`
2. RTC wakeup timestamp byte 1
3. RTC wakeup timestamp byte 2
4. RTC wakeup timestamp byte 3
5. RTC wakeup timestamp byte 4

Setting all bytes to 0 disables the alarm.

TODO

### 0x9C - Set persistent memory cell values

Inputs:
1. Command `0x9C`
2. Persistent memory cell value 1 (e.g., in Falcon at DAT_INTMEM_66)
3. Persistent memory cell value 2 (e.g., in Falcon at DAT_INTMEM_67)

Outputs: Nothing

### 0x9D - Write 12 bytes from FIFO to SMC memory (SMC_SET_82_INT)

TODO

Not present on Xenon

### 0x9F - Write 12 bytes from FIFO to SMC memory (SMC_SET_9F_INT)

Same as command 0x9D but writes to a different address.

Not present on Xenon

## Asynchronous operations

The SMC can also send statuses back to the CPU whenever it feels like it. When that happens,
the outbox will contain the command code 0x83. Byte 1 contains the event type.

### 0x11 - Power switch pushed

Outputs:

0. Command `0x83`
1. Fixed byte `0x11`
2. Fixed byte `0x01` (there's no "pushed" or "unpushed" state)

### 0x13 - Bind switch (controller sync button) pushed

Outputs:

0. Command `0x83`
1. Fixed byte `0x13`

### 0x14 - Tilt switch changed

Outputs:

0. Command `0x83`
1. Fixed byte `0x14`
2. One bit; bit 0 = new tilt switch state

### 0x20 - IR remote power button pushed

Outputs:

0. Command `0x83`
1. Fixed byte `0x20`
2. Fixed byte `0x01` (there's no "pushed" or "unpushed" state)

### 0x23 - IR remote event??

TODO

### 0x31 - TODO

Outputs:

0. Command `0x83`
1. Fixed byte `0x31`
2. Fixed byte `0x04`

### 0x40 - AV pack changed

Outputs:

0. Command `0x83`
1. Fixed byte `0x40`
2. New AV pack value

### 0x42 - TODO

TODO

### 0x44 - TODO

TODO

Appears to be Argon-related

### 0x60 - TODO (SMC_TRAY_OPEN)

TODO

### 0x61 - TODO (SMC_TRAY_OPEN_REQUEST)

TODO

### 0x62 - TODO (SMC_TRAY_CLOSED)

TODO

### 0x63 - TODO (SMC_TRAY_OPENING)

TODO

### 0x64 - TODO (SMC_TRAY_CLOSING)

TODO

### 0x65 - TODO (SMC_TRAY_UNKNOWN)

TODO

## See also

xenon-emu SMC code (some of these are wrong)
- [source](https://github.com/xenon-emu/xenon/blob/main/Xenon/Core/PCI/Devices/SMC/SMC.cpp)
- [header](https://github.com/xenon-emu/xenon/blob/main/Xenon/Core/PCI/Devices/SMC/SMC.h)
