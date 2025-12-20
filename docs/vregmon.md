# Voltage regulation/powergood monitor

Simple function that checks powergood signals while the power brick is enabled, and RRoDs with a power error if a problem is detected.
A check will be skipped if its respective regulator or supply is disabled.

Locations:

- Xenon: 0x1C4A
- Falcon: 0x1D0F
- Jasper: 0x1D2A
- Trinity: 0x1E47
- Corona: TODO
- Winchester: 0x1EAE

## Xenon

Checks powergood signals in the order: 12v, CPU, GPU.

| Rail | RRoD error code
|------|------------------
| 12v  | 0001
| CPU  | 0002
| GPU  | 0003

## Zephyr

Checks powergood signals in the order: 12v, 5v, CPU, GPU.

| Rail | RRoD error code
|------|------------------
| 12v  | 0001
| 5v   | 0031
| CPU  | 0002
| GPU  | 0003

Note that the 5v rail is only checked if the 1v8 regulator is enabled.

## Falcon/Jasper

Does everything Zephyr does (in the same order), then does checkstop stuff.

If the CPU is running and it raises a checkstop error, then this function sets flags, one of which is to be picked
up by the Argon statemachine, which in turn sends command 0x42. In practice however this does nothing useful on
a retail console.

## Trinity

Checks powergood signals in the order: 12v, 5v, VMEM, VCPU, VEDRAM. (VCPU powers the CGPU, and thus both the CPU and GPU, on slims.)

| Rail   | RRoD error code
|--------|------------------
| 12v    | 0001
| 5v     | 0031
| VMEM   | 0003
| VCPU   | 0002
| VEDRAM | 0023

Checkstop behavior is similar to Falcon/Jasper (sends Argon command 0x49 but does nothing else).

## Winchester

Checks powergood signals in the order: 12v, 5v, 3v3, VMEM, VCPU.

| Rail   | RRoD error code
|--------|------------------
| 12v    | 0001
| 5v     | 0031
| 3v3    | 0003
| VMEM   | 0033
| VCPU   | 0002

Checkstop behavior unchanged from Trinity.
