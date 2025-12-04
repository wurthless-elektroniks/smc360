# PWM controller

TODO.

- Default PWM frequency setting of 0x64 (=100) corresponds to 30 kHz (confirmed through scope)
- PWM channel 2 isn't connected to the fans after Xenon, but it's still configured and written to by the software
- PWM pulse width is set to 0 when the system is powered down, which turns the fans off; not sure if there's a universal
  PWM enable/disable register yet...
