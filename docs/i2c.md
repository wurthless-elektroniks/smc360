# I2C

The SMC is connected to several other devices over I2C (also SMBus or PMBus). The actual code that handles everything
I2C-related is absolute torture to disassemble due to its asynchronous nature, as well as Microsoft not making things
easy to understand from the get-go.

By default, the SMC assumes it'll be the only I2C bus master; if anything else tries hijacking the I2C bus
(e.g. RGH2 glitch chips), then conflicts will happen and you'll get random SMC problems, usually because
the SMC will try reading the thermal sensors but will either be blocked off or read back random results.

Since the SMC assumes it's the bus master, it'll kick off I2C transfers on its own, but actual I2C communications
are mostly handled in hardware. There are SFRs dedicated to clocking data to and from the I2C bus, and there's
a dedicated interrupt handler for reacting to I2C events.

Also, because the CPU-to-SMC IPC code facilitates HANA control from the CPU, it shouldn't be a surprise that
the IPC and I2C code is intertwined at points, making things even more annoying to debug.

The I2C devices themselves shouldn't be documented here, that's a whole other barrel of monkeys.

## I2C address map

- 0x39: ????? (used for error reporting?)
- 0x69 (Xenon only): Backup clock generator (Cypress CY28517)
- 0x70: ANA/HANA on all XSB and PSB boards, KSB on Corona and Winchester (TBD)

Other things like the voltage regulators live on the I2C bus as well

## The big I2C command list buffer

Due to I2C being asynchronous, the actual code to drive the I2C bus (to do reads and writes) is a large
state machine that acts off a command list somewhere. To tell the I2C statemachine to do something, you
give it an offset within that command list, and it runs the commands for you. However, disassembling the
command list is annoying for one particular reason...

Here's an example from the Falcon SMC, which is offset 0 in the command list, and at 0x2907 in the SMC
program itself:

``00 09 03``

That doesn't say much, but here's how it's actually interpreted:

- Each command starts by reading one and then using it as a relative jump offset into a jump table.
  That's right, the commands aren't 00 to mean "run handler 0" and 01 to mean "run handler 1" and
  so on; they actually mean "jump to address jumptable+0" or "jump to address jumptable+1" etc.

- Each command is free to read more bytes from the command list as arguments; the HANA register
  writes are a good example of this.

- Each command can yield to the I2C statemachine so that the actual I2C transfers can take place
  asynchronously via the interrupt handler.

Now, let's look at what that Falcon example means:

- `00`: jump to 0x28D9, which initializes the I2C bus and SFRs, then runs the next command.
- `09`: jump to 0x28E2, which reads data from the IPC inbox and uses it to kick off an I2C operation,
  yielding until a response arrives, at which point the IRQ handler reads the response and copies it
  to the IPC outbox for the CPU to read
- `03`: jump to 0x28DC, which frees up the I2C bus and stops the I2C statemachine

The jump table varies between SMC program revisions, so documenting that will be "fun" in its own right...

## List of commandlist handlers

Oh boy, this is gonna be fun to untangle and explain.

### Init I2C bus

Byte format:
- Falcon: `00`

The initialization procedure is:
- Reset the I2C bus
- If SDA is still low after the reset, manually drive the I2C lines to try to get the bus in
  healthy condition, giving up if we can't (setting F0 in this case)
- Manually toggle SCL, then hand over I2C bus control to the I2C unit

### End commandlist execution

Byte format:
- Xenon: `03`
- Falcon: `03`
- Jasper: `03`

Handlers:
- Falcon: 0x28DC -> 0x2686

Stops executing the commandlist and returns success (via F0 flag).

### Do nothing (NOP)

Byte format:
- Zephyr: `06`
- Falcon: `06`
- Jasper: `06`

Handlers:

| SMC revision | Absolute offset  | Jumptable entry |
|--------------|------------------|-----------------|
| Xenon        | Doesn't exist    | Doesn't exist   |
| Zephyr       | TODO             | TODO            |
| Falcon       | 0x28DF           | `ljmp 0x268A`   |
| Jasper       | TODO             | TODO            |
| Trinity      | TODO             | TODO            |
| Corona       | TODO             | TODO            |
| Winchester   | TODO             | TODO            |

Does nothing; it simply increments the commandlist execution pointer and continues on to the
next instruction.

### Run IPC-I2C transaction

Byte format:
- Xenon: `06`
- Zephyr: `09`
- Falcon: `09`
- Jasper: `09`

Handlers:
- Falcon: 0x28E2 -> 0x2891

This will block until the transfer completes.

The logic here is spaghetti code because of how the I2C interrupt handler works. When an IPC transaction is running
the I2C IRQ handler overrides the usual read/write buffers and uses the IPC inbox and outbox instead for those operations.

### Write backup clockgen register (Xenon only)

Byte format:
- Xenon: `17 rr dd` (to be confirmed)

Handlers:
- Xenon: 0x282C -> 0x272B

Writes to the backup clock generator, which is a Cypress CY28517.

### Write ANA/HANA/KSB register

Byte format:
- Xenon: `08 rr dd dd dd dd`
- Falcon: `0B rr dd dd dd dd` or `0B DB dd dd dd` (register 0xDB treated specially, see below)
- Jasper: `0B rr dd dd dd dd` or `0B DB dd dd dd` (register 0xDB treated specially, see below)

Handlers:
- Falcon: 0x28E4 -> 0x268E

Writes 4 bytes `dd dd dd dd` to the given HANA register `rr`. This will block until the transfer completes.

The data is byteswapped due to how the I2C statemachine buffers work (last in/first out),
so a write to the HANA clock mode select register 0xCE will have the data represented
in the command as `08 e8 40 14` but the I2C bus will actually write `14 40 e8 08`.

Important gotcha: HANA register 0xDB is treated specially because it is set by the SMC config. If register 0xDB is used,
only three bytes will be read from the commandlist; the fourth will come from the SMC config cell.

### Read HANA register

Byte format:
- Xenon: `0B rr`
- Falcon: `0E rr`

Reads the given register into memory, then it's up to some other command to process the results.
This will block until the transfer completes.

### Store I2C result to temperature sensor fields

Byte format:
- Falcon: `1A`

TODO

### Store I2C result to CPU temperature fields

Byte format:
- Falcon: `1D`

TODO

### Store I2C result to chassis temperature fields

Byte format:
- Falcon: `20`

TODO

### Dump RRoD error code to I2C buffer

TODO

## Commandlist disassemblies

### Xenon

Commandlist table at 0x283E-0x28A2 (100 bytes).

Disassembly TODO.

### Zephyr

Commandlist table at 0x286F-0x2923 (180 bytes).

Disassembly TODO.

### Falcon

Commandlist table at 0x2907-0x29C7 (192 bytes).

Relative offset column only populated for known commandlist start points.

| Rel offset | Abs offset | Bytecode            | Operation
|------------|------------|---------------------|---------------------------------------------
| `00`       | 0x2907     | `00`                | Init I2C bus
|            | 0x2908     | `09`                | Run IPC-I2C transaction
|            | 0x2909     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `03`       | 0x290A     | `00`                | Init I2C bus
|            | 0x290B     | `0B E4 00 00 00 1B` | Write HANA register 0xE4: `1B 00 00 00`
|            | 0x2911     | `0B E3 0F FF FF FF` | Write HANA register 0xE3: `FF FF FF 0F`
|            | 0x2917     | `0B DB 00 00 00`    | Write HANA register 0xDB: `-- 00 00 00` (special case)
|            | 0x291C     | `0B D5 00 00 00 00` | Write HANA register 0xD5: `00 00 00 00`
|            | 0x2922     | `0B D9 00 00 00 08` | Write HANA register 0xD9: `08 00 00 00`
|            | 0x2928     | `0B D4 09 90 E0 0E` | Write HANA register 0xD4: `0E E0 90 09`
|            | 0x292E     | `0B CE 08 E8 40 14` | Write HANA register 0xCE: `14 40 E8 08`
|            | 0x2934     | `0B DC 00 00 42 AA` | Write HANA register 0xDC: `AA 42 00 00`
|            | 0x293A     | `0B DF 00 00 00 00` | Write HANA register 0xDF: `00 00 00 00`
|            | 0x2940     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `3A`       | 0x2941     | `00`                | Init I2C bus
|            | 0x2942     | `0B D9 00 00 00 20` | Write HANA register 0xD9: `20 00 00 00`
|            | 0x2948     | `0B E3 84 36 F6 66` | Write HANA register 0xE3: `66 F6 36 84`
|            | 0x294E     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `48`       | 0x294F     | `00`                | Init I2C bus
|            | 0x2950     | `0B E3 0F FF FF FF` | Write HANA register 0xE3: `FF FF FF 0F`
|            | 0x2956     | `0B D9 00 00 00 08` | Write HANA register 0xD9: `08 00 00 00`
|            | 0x295C     | `0B DF 00 00 00 00` | Write HANA register 0xDF: `00 00 00 00`
|            | 0x2962     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `5C`       | 0x2963     | `06`                | Do nothing
|            | 0x2964     | `06`                | Do nothing (execution falls through to 5E below)
| `5E`       | 0x2965     | TODO                | TODO
| `-`        | `-`        | `-`                 | `-`
| `8E`       | 0x2995     | `00`                | Init I2C bus
|            | 0x2996     | `0E E0`             | Read HANA register 0xE0
|            | 0x2998     | `1A`                | Use results of that read to update temperature sensor values
|            | 0x2999     | `0E E1`             | Read HANA register 0xE1
|            | 0x299B     | `1A`                | Use results of that read to update CPU temperature sensor values
|            | 0x299C     | `0E E2`             | Read HANA register 0xE2
|            | 0x299E     | `20`                | Use results of that read to update chassis temperature sensor values
|            | 0x299F     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `99`       | 0x29A0     | TODO                | TODO

### Jasper

Commandlist table at 0x2959-0x2A37 (222 bytes).

Disassembly TODO.

### Trinity

Commandlist table at 0x2ACF-0x2BAD (222 bytes).

One byte changes between Trinity and Jasper. The HANA write to register 0xE4 is now `0B E4 00 00 00 1F`
(that's `1F 00 00 00` byteswapped). The rest of the code is identical, so it will not be disassembled in detail.

### Corona

Commandlist table at 0x2D66-0x2E48 (226 bytes).

Disassembly TODO.

### Winchester

Commandlist table at 0x2BC4-0x2C75 (177 bytes).

Disassembly TODO.

## I2C over IPC

The CPU-to-SMC IPC can be used to read or write different registers on the I2C bus. It all centers around 
IPC command 0x11.

### IPC command 0x11

The basic request is:

0. Command byte `0x11`
1. Number of bytes to write (in upper nibble), command flags (lower nibble) (in r2)
2. TODO (in r3)
3. TODO (in r4)
4. TODO (in r5)
5. TODO (in r6)

The basic response is:

0. Command byte `0x11`
1. Status/error code

The error codes are:
- `00`: Accepted/success
- `01`: I2C busy?
- `02`: Invalid request
- `03`: Error on the I2C bus
- `04`: Operation already in progress (DDC lock??)

Note that even though this command is handled asynchronously by the SMC, the SMC will treat this as
a synchronous event, and will block all other IPC requests until the command completes.

Here's how the command is handled... (still work in progress obvs)

If bit 0 in the command flags is set, an attempt is being made to do a DDC lock(?):
- If bit 1 set, set the lock and return success
- If bit 2 set, clear the lock and return success
- If both bits clear, check if the lock is clear, and if it is, return error code 4 and stop
- Otherwise execution continues into common block

Bit 0 of first byte goes to F0.

General error check part:
- Number of bytes to write cannot be 10 or greater
- Number of bytes to read cannot be 13 or greater
- Bit 7 of either command bytes 3, 4 or 5 must be 1

If any of these checks fail, return error code 2.

### How the message is parsed by the I2C commandlist handler

See Falcon code at 0x2891.

If the command is accepted by the IPC, it's passed off to the I2C spaghetti factory, which treats the request
as follows:

0. Command byte `0x11`
1. Number of bytes to write (in upper nibble)
2. Number of bytes to read (in upper nibble), I2C data size? (in lower nibble)
3. I2C address (lower 7 bits); bit 7 is still a mystery
4. Mystery byte (lower 7 bits, shifted left once); bit 7 is still a mystery
5. Mystery byte (lower 7 bits, shifted left once); bit 7 indicates read pending
6. Data to write (continues for remainder of message)

Note that any error handling for this message will already have been done by the IPC handler.

The I2C interrupt handler will continue reading the IPC inbox where this code left off.
If the CPU requested a read, the results of the read will be dumped to the outbox starting at offset 0x03.


