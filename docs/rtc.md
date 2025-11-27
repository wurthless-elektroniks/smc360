# Real Time Clock

The Xbox 360's Real Time Clock (RTC) has the following characteristics:
- It resets whenever the SMC is reset (so either when power is connected or your NAND flasher releases it from reset)
- It starts counting immediately; no need to set the time to make it start counting
- It counts in milliseconds starting from 0
- Epoch (timestamp of all zeroes) is 2001 November 15th at midnight UTC (the original Xbox launch date)

It seems that the kernel has its own software-based RTC; it only uses the hardware RTC when getting the current
system time at startup. Setting the date and time will update the hardware RTC though.

