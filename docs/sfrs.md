# SFRs at a glance

Most undocumented, many unused...

Remember: Most of these are Falcon-specific (XSB), other revisions are to be done later...

Anything marked as "???" below is accessed by the SMC program, but its purpose is unclear.

| SFR  | Purpose 
|------|--------------------------------------------------|
| 080h | GPIO port 0
| 081h | Stack pointer
| 082h |
| 083h |
| 084h |
| 085h |
| 086h |
| 087h | ???
| 088h | Mystery bitfield
| 089h |
| 08Ah |
| 08Bh | ???
| 08Ch | ???
| 08Dh |
| 08Eh |
| 08Fh | PCIe status (bits 4/5), IRQ mask?
| 090h | GPIO port 1
| 091h | PWM channel 1 duty cycle
| 092h | PWM channel 1 frequency
| 093h | PWM channel 2 duty cycle
| 094h | PWM channel 2 frequency
| 095h | Set to 0x88 constantly
| 096h | Set to 0x00
| 097h |
| 098h | ???
| 099h |
| 09Ah |
| 09Bh | ???
| 09Ch | ???
| 09Dh | Pinmode port 0
| 09Eh | Pinmode port 1
| 09Fh | Pinmode port 2
| 0A0h | GPIO port 2
| 0A1h | Pinmode port 3
| 0A2h | DDR port 0
| 0A3h | DDR port 1
| 0A4h | DDR port 2
| 0A5h | DDR port 3
| 0A6h | DDR port 4
| 0A7h | Pinmode port 4
| 0A8h | ??? (some bitfield modified by certain GPIO polls)
| 0A9h |
| 0AAh | RTC timestamp in milliseconds, bits 0-7
| 0ABh | RTC timestamp in milliseconds, bits 8-15
| 0ACh | RTC timestamp in milliseconds, bits 16-23
| 0ADh | RTC timestamp in milliseconds, bits 24-31
| 0AEh | RTC timestamp in milliseconds, bits 32-39
| 0AFh | RTC command (1 = read current time into 0AAh-0AEh, 2 = set RTC using those values)
| 0B0h | Mystery status control register (certain IRQs set it to 0x01 or 0x04; could be Argon and IR related)
| 0B1h | ???
| 0B2h | ???
| 0B3h | ???
| 0B4h | ???
| 0B5h | Infrared receiver (purpose unclear)
| 0B6h | Infrared receiver (purpose unclear)
| 0B7h | ???
| 0B8h | ???
| 0B9h | Initialized to 0
| 0BAh | Initialized to 0
| 0BBh | Initialized to 0
| 0BCh | IRQ mask? 
| 0BDh | Set to 0xFF
| 0BEh | Set to 0xFF
| 0BFh | IRQ control (0 = enable all, 1 = disable all)
| 0C0h | GPIO port 3
| 0C1h | ???
| 0C2h | ???
| 0C3h | ???
| 0C4h | ???
| 0C5h | ???
| 0C6h | ???
| 0C7h | ???
| 0C8h | GPIO port 4
| 0C9h | ???
| 0CAh | ???
| 0CBh | ???
| 0CCh | ???
| 0CDh | ???
| 0CEh | ???
| 0CFh | ???
| 0D0h | 8051 standard flags
| 0D1h | ???
| 0D2h | ???
| 0D3h | ???
| 0D4h | ???
| 0D5h | CPU-to-SMC IPC outbox, data
| 0D6h | CPU-to-SMC IPC outbox, control
| 0D7h | USB presence detect/powerup event detect, channel 1
| 0D8h | I2C status/control bits (bit 0 = rx/tx next byte?, bit 1 = start I2C/ack IRQ?, bit 2 = error?, bit 3 = ???)
| 0D9h | I2C ??? (used in IRQ handler for some sort of error detection)
| 0DAh | I2C rx/tx byte
| 0DBh | I2C (set to 0 on handover)
| 0DCh | I2C related (3 when releasing bus, 0 when locking it)
| 0DDh | I2C (set to 0xE1 on handover)
| 0DEh | I2C (set to 0x83 on handover)
| 0DFh |
| 0E0h | 8051 accumulator (A) register
| 0E1h | CPU-to-SMC IPC inbox, data
| 0E2h | CPU-to-SMC IPC inbox, control
| 0E3h | SFCX: Configuration register, bits 0-7
| 0E4h | SFCX: Configuration register, bits 8-15
| 0E5h | SFCX: Configuration register, bits 16-23
| 0E6h |
| 0E7h | UART data out
| 0E8h | UART enable/configuration
| 0E9h | UART speed
| 0EAh | SFCX: Address register, bits 7-0 (LSB)
| 0EBh | SFCX: Address register, bits 15-8
| 0ECh | SFCX: Address register, bits 23-16
| 0EDh | SFCX: Address register, bits 31-24 (MSB)
| 0EEh | SFCX: Status register
| 0EFh | Flash controller? (TODO)
| 0F0h | 8051 register B
| 0F1h | SFCX: Data register, byte 0
| 0F2h | SFCX: Data register, byte 1
| 0F3h | SFCX: Data register, byte 2
| 0F4h | SFCX: Data register, byte 3
| 0F5h | SFCX: Command register
| 0F6h |
| 0F7h |
| 0F8h |
| 0F9h |
| 0FAh |
| 0FBh |
| 0FCh | ???
| 0FDh | USB presence detect/powerup event detect, channel 2
| 0FEh | Program to map on watchdog reboot? (0x00 = SRAM?, 0xFF = bootstrap ROM?)
| 0FFh | Watchdog? (write 0 to kick)

## KSB EXTMEM registers

The KSB adds more registers in EXTMEM space (use MOVX opcodes to read/write).

- 0x0020~0x0023: eMMC read result
- 0x00EC: eMMC command/status? (write 1 to set 256-byte block address, 0 to read within block)
- 0x00ED~0x00EF: eMMC address (little endian)
- 0x00F3: Extended SFCX configuration register, bits 24-31. bit 7 = 4gbytes eMMC present, bit 6 = NAND ready
