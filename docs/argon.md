# Argon/Boron 

The Argon and Boron boards are the RF boards. The Ring of Light and some RF-related commands are sent by the SMC over a serial
bus, while controller reading itself is done using USB.

There is a microcontroller on the Argon/Boron board that handles Ring of Light animations and RF pairing logic for us. Unfortunately
it's a custom part that should be dumped for preservation's sake.

Reverse engineering the board is beyond the scope of this project, so anything documented here only applies to SMC program reversing.

## Serial commands

See [here](https://www.appliedcarbon.org/xboxrf.html)
