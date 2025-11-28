# Error handling

## Error types

System errors are divided into three types:

1. Power errors, which shut the system down immediately and return it to standby mode with the error codes flashing
2. Thermal errors, which will send the system into overheat protection with the fans running full speed
3. IPC errors, raised by the CPU, which will keep the system powered on so the system can display an error
   message if it is able to

## Error codes

The error codes are 4 digits long and are packed into a single byte in 4x2 bit format, so
0x1B decodes to binary `00 01 10 11`, or error code 0123.

Any error code below 0100 (0x0F or less) is to be raised by the SMC only, and the IPC handling code will reject
any attempt by the CPU to raise a SMC-specific system error.