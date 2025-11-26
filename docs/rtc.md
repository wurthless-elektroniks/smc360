# Real Time Clock

The Xbox 360's Real Time Clock (RTC) has the following characteristics:
- It resets whenever the SMC is reset (so either when power is connected or your NAND flasher releases it from reset)
- It starts counting immediately; no need to set the time to make it start counting
- It counts in milliseconds starting from 0

Actual epoch, system configuration, etc. is all TODO... building xell a million times isn't very fun.
The RTC wake feature is implemented entirely in software too.

