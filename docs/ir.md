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

| Value | Button
|-------|------------------------------------------------------------
| 0x0C  | Power
| 0x64  | X (guide) button
| 0x28  | Eject
| 0x19  | Stop
| 0x18  | Pause
| 0x15  | Rewind
| 0x16  | Play
| 0x14  | Fast-forward
| 0x1B  | Back arrow
| 0x1A  | Forward arrow
| 0x4F  | Display
| 0x51  | Title
| 0x24  | DVD Menu
| 0x23  | Back
| 0x0F  | Info
| 0x1E  | Up
| 0x20  | Left
| 0x21  | Right
| 0x1F  | Down
| 0x22  | OK
| 0x26  | Y/Guide
| 0x68  | X
| 0x66  | A
| 0x25  | B/Live TV
| 0x10  | Volume Up
| 0x11  | Volume Down
| 0x0E  | Mute
| 0x6C  | Channel Up
| 0x6D  | Channel Down
| 0x0D  | Start/Windows button
| 0x0B  | Enter
| 0x17  | Record
| 0x0A  | Clear
| 0x01  | 1
| 0x02  | 2
| 0x03  | 3
| 0x04  | 4
| 0x05  | 5
| 0x06  | 6
| 0x07  | 7
| 0x08  | 8
| 0x09  | 9
| 0x1D  | 100/Asterisk
| 0x00  | 0
| 0x1C  | Back arrow/Pound

Pressing the big "TV" button (between the volume/channel controls) does nothing here.
