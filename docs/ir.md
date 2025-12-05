# Infrared Baboon, big star of cartoon

The Xbox 360 has an infrared receiver that's mostly used for the remote control accessory.
It is present on all revisions up until Stingray, where it is no longer populated; Winchester
removes it entirely.

IR receiving is done in an ISR at 0x0006, which seems to be mixed in with Argon handling.
That has yet to be fully untangled...

## Infrared address

Defaults to 15 (0x0F).

