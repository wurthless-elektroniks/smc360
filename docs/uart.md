# UART

The SMC exposes a transmit-only debugging UART which was completely undocumented for years until 15432
found a way to enable it (see the RGH3 making-of [here](https://web.archive.org/web/20250401163119/https://swarm.ptsecurity.com/xbox-360-security-in-details-the-long-way-to-rgh3/)).

The retail SMC code does not use the UART at all, and keeps the UART disabled by writing 0 to 0E8h.

### SFRs

TODO: find proper way to configure stop bit, also document busy registers (not really clearly explained in document above)

- 0E7h: Data out
- 0E8h: Enable/disable UART (write 0xC0 to enable)
- 0E9h: UART speed (0xFF = 1.5 mbps)

