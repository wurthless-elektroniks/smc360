# Real Time Clock

The Xbox 360's Real Time Clock (RTC) has the following characteristics:
- It resets whenever the SMC is reset (so either when power is connected or your NAND flasher releases it from reset)
- It starts counting immediately; no need to set the time to make it start counting
- It counts in milliseconds starting from 0

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
