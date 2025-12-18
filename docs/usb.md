# USB

The SMC has rudimentary support for USB devices, but it can only detect whether something's plugged into
a USB port, and, if it's a controller, if the X (guide) button is being pressed.

While the system is in standby, the "execute every 1 ms" handler will read the USB ports. There is a
special doorknock protocol which is confusing to document, but I'll give it my best try:

- Wait for a device to be plugged in
- While that device is plugged in, read the doorknock bit
- The doorknock bit must be high for at least 2 ms and no more than 50 ms or we throw this attempt out

The doorknock bit must then toggle every millisecond (or be zero, not sure which) for the next 100 ms.
If it does, then the device has requested a powerup, and the SMC obliges.

This is likely a variant on the standard USB wake-from-standby procedure (read the USB specs), but
that has to be confirmed...

## Port mappings

| Port     | Fat name  | Fat location   | Trinity name  | Trinity location | Corona name   | Corona location  |
|----------|-----------|----------------|---------------|------------------|---------------|------------------|
| USBA_D0  | GAMEPORT1 | Front top      | EXPPORT_PORT3 | Rear top         | EXPPORT_PORT2 | Rear middle      |
| USBA_D1  | GAMEPORT2 | Front bottom   | EXPPORT_RJ45  | Kinect port      | EXPPORT_PORT3 | Rear top         |
| USBA_D2  | USBPORTA2 | Unused         | EXPPORT_PORT1 | Rear bottom      | EXPPORT_PORT1 | Rear bottom      |
| USBA_D3  | USBPORTA3 | Unused         | EXPPORT_PORT2 | Rear middle      | EXPPORT_RJ45  | Kinect port      |
| USBB_D0  | MEMPORT3  | Unused         | GAMEPORT1     | Front left       | BORONFPMPORT  | Boron RF board   |
| USBB_D1  | MEMPORT2  | Memory unit    | GAMEPORT2     | Front right      | USBB_D1       | J1D1 header      |
| USBB_D2  | EXPPORT   | Rear           | WAVEPORT      | Wireless adapter | GAMEPORT1     | Front left       |
| USBB_D3  | MEMPORT1  | Memory unit    | BORONFPMPORT  | Boron RF board   | WAVEPORT      | Wireless adapter |
| USBB_D4  | ARGONPORT | Argon RF board | MUPORT        | 4GB memory unit  | GAMEPORT2     | Front right      |

### USBA channels

Read from SFR 0D7h.

| Bit | Purpose
|-----|------------------------------
| 7   | USBA_D3 doorknock
| 6   | USBA_D3 presence detect
| 5   | USBA_D2 doorknock
| 4   | USBA_D2 presence detect
| 3   | USBA_D1 doorknock
| 2   | USBA_D1 presence detect
| 1   | USBA_D0 doorknock
| 0   | USBA_D0 presence detect

## USBB channels

Read from SFR 0FDh.

| Bit | Purpose
|-----|------------------------------
| 7   | USBB_D3 doorknock
| 6   | USBB_D3 presence detect
| 5   | USBB_D2 doorknock
| 4   | USBB_D2 presence detect
| 3   | USBB_D1 doorknock
| 2   | USBB_D1 presence detect
| 1   | USBB_D0 doorknock
| 0   | USBB_D0 presence detect

USBB_D4 is read from SFR 087h (bit 0 = presence detect, bit 1 = doorknock).
