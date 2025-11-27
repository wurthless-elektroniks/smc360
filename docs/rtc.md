# Real Time Clock

The Xbox 360's Real Time Clock (RTC) has the following characteristics:
- It resets whenever the SMC is reset (so either when power is connected or your NAND flasher releases it from reset)
- It starts counting immediately; no need to set the time to make it start counting
- The RTC timestamp is an unsigned 40 bit value and counts in milliseconds starting from 0

## SFRs

The RTC is mapped in the SFR space from 0AAh to 0AFh.

- 0AAh through 0AEh are memory cells that store the timestamp value for reads and writes (0AAh = LSB, 0AEh = MSB).
- 0AFh is the control register.
- To read the RTC, write 1 to 0AFh, and 0AAh-0AEh will be populated with the current timestamp.
- To set the RTC, put your intended timestamp in 0AAh-0AEh, and then write 2 to 0AFh.

## Software features

The SMC handles two major features in software: the "is the RTC set yet?" flag, and the RTC wake alarm.

The "RTC has been set" flag is there so the kernel can act on it, possibly to set its own time or to ignore the RTC's
timestamp until the RTC has been set.

The RTC wake alarm is an interesting feature that I'm not sure was ever used. The wakeup value is the upper 32 bits of
the 40-bit RTC timestamp. When the alarm is enabled, the SMC code will poll the RTC every so often and compare the
relevant bytes of the timestamp to the stored wakeup value. If the current time exceeds the alarm value, the system
is powered on, and the alarm is disabled.

## XSS oddities

- The kernel's epoch (timestamp of all zeroes) is 2001 November 15th at midnight UTC (the original Xbox launch date).
  Obviously the hardware doesn't care about the exact date, and third-party software can ignore what the kernel wants.

- Knowing the kernel's epoch, the RTC timestamp will roll over to zero on 2036 September 17th at 19:53:47 UTC.

- It seems that the kernel has its own software-based RTC; it only uses the hardware RTC when getting the current
  system time at startup. Setting the date and time will update the hardware RTC though.

- For whatever reason, you can't enter a year after 2025 in the system settings, even though the kernel is fine with it
  and will be fine with it for about a decade more.

## See also

- [Linux kernel driver](https://github.com/Free60Project/linux-kernel-xbox360/blob/b7bff7ccb400dfc2604e87bfc3d4202cf43633cb/patch-6.17-xenon0.30.diff#L4592),
  which I didn't know about until after confirming everything here
