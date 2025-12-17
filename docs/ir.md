# Infrared Baboon, big star of cartoon

The Xbox 360 has an infrared receiver that's mostly used for the remote control accessory.
It is present on all revisions up until Stingray, where it is no longer populated; Winchester
removes it entirely.

IR receiving is done in an ISR at 0x0006, which seems to be mixed in with Argon handling.
That has yet to be fully untangled...

## Infrared address

Defaults to 15 (0x0F).

## Remote button mappings

I dumped this table with the Universal Media Remote (X801979-002), a logic analyzer, and a hacked Jasper SMC with a debug print
function installed at 0x1C33. The table matches the [Free60 Wiki](https://free60.org/Hardware/Accessories/Media_Remote/)
with some typos corrected. Buttons were pressed from the top to the bottom of the remote control.

| Value | Button                           | Special case?
|-------|----------------------------------|---------------
| 0x0C  | Power                            | Yes 
| 0x64  | X (guide) button                 | Yes
| 0x28  | Eject                            | Yes
| 0x19  | Stop                             | No
| 0x18  | Pause                            | No
| 0x15  | Rewind                           | No
| 0x16  | Play                             | No
| 0x14  | Fast-forward                     | No
| 0x1B  | Back arrow                       | No
| 0x1A  | Forward arrow                    | No
| 0x4F  | Display                          | No
| 0x51  | Title                            | No
| 0x24  | DVD Menu                         | No
| 0x23  | Back                             | No
| 0x0F  | Info                             | No
| 0x1E  | Up                               | No
| 0x20  | Left                             | No
| 0x21  | Right                            | No
| 0x1F  | Down                             | No
| 0x22  | OK                               | No
| 0x26  | Y/Guide                          | No
| 0x68  | X                                | No
| 0x66  | A                                | No
| 0x25  | B/Live TV                        | No
| 0x10  | Volume Up                        | No
| 0x11  | Volume Down                      | No
| 0x0E  | Mute                             | No
| 0x6C  | Channel Up                       | No
| 0x6D  | Channel Down                     | No
| 0x0D  | Start/Windows button             | Yes
| 0x0B  | Enter                            | No
| 0x17  | Record                           | No
| 0x0A  | Clear                            | No
| 0x01  | 1                                | No
| 0x02  | 2                                | No
| 0x03  | 3                                | No
| 0x04  | 4                                | No
| 0x05  | 5                                | No
| 0x06  | 6                                | No
| 0x07  | 7                                | No
| 0x08  | 8                                | No
| 0x09  | 9                                | No
| 0x1D  | 100/Asterisk                     | No
| 0x00  | 0                                | No
| 0x1C  | Back arrow/Pound                 | No
| 0x29  | ???? (behaves like power button) | Yes
| 0x2A  | ???? (can power system on)       | Yes

Pressing the big "TV" button (between the volume/channel controls) does nothing here.

Special cases are button presses that the SMC will specifically intercept:
- Any power or eject button press will be handled like a normal power or eject button press
  and will schedule a power on or eject event respectively.
- The X (guide) button, Windows button, and button 0x2A will only trigger power events when the
  system is powered off. If the system is on, then they'll fall through to the normal asynchronous
  IPC event, which the CPU can process.
