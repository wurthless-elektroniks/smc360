# UART

The SMC exposes a transmit-only debugging UART which was completely undocumented for years until 15432
found a way to enable it (see the RGH3 making-of [here](https://web.archive.org/web/20250401163119/https://swarm.ptsecurity.com/xbox-360-security-in-details-the-long-way-to-rgh3/)).

The retail SMC code does not use the UART at all, and keeps the UART disabled by writing 0 to 0E8h.

### SFRs

TODO: find proper way to configure stop bit, also document busy registers (not really clearly explained in document above)

- 0E7h: Data out
- 0E8h: Enable/disable UART (write 0xC0 to enable)
- 0E9h: UART speed (see below)

### UART speeds

They're completely different than the CPU's UART.

The base bitrate is 1.5 mbaud and the UART speed register acts as a divider, so the following calculation applies...

```
output_baudrate = 1_500_000 / (0x100-speed)
```

### The (usually) disabled UART RX pin

The southbridge does expose a RX pin for the SMC UART, but it is almost always tied to 3v3 and is useless without hacking up the board.

- Xenon does not expose a test point for this pin.
- Falcon exposes a test point under the southbridge (unlabeled) for the RX pin, but it's tied to 3v3 and is useless.
- Corona, for whatever reason, doesn't tie the RX pin to 3v3 and it is accessible on the SMC debug header on pin 3. However, it goes
  back to being tied to 3v3 on Stingray.
