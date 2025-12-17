# USB

The SMC has rudimentary support for USB devices, but it can only detect whether something's plugged into
a USB port, and, if it's a controller, if the X (guide) button is being pressed.

While the system is in standby, the "execute every 1 ms" handler will read the USB ports. There is a
special doorknock protocol which is confusing to document, but I'll give it my best try:

- Wait for a device to be plugged in
- While that device is plugged in, read the doorknock bit
- If the bit is 1 on subsequent reads, then it must toggle within 50 ms or we throw this attempt out

The doorknock bit must then toggle every millisecond for the next 100 ms. If it does, then the device
has requested a powerup, and the SMC obliges.

## Front port

Read from SFR 0D7h.

- Bit 3: Bottom USB device doorknock
- Bit 2: Bottom USB device present (active low)
- Bit 1: Top USB device doorknock
- Bit 0: Top USB device present (active low)

## Rear port

Read from SFR 0FDh.

- Bit 5: Fat: rear USB device doorknock
- Bit 4: Fat: rear USB device present (active low)

