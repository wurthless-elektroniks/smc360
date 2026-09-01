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

## How the vanilla SMC programs handle I2C in a nutshell

The vanilla SMCs basically break down I2C handling as follows:

- Statemachines can request I2C operations through the main HANA/I2C handler in the "as fast as possible" part of the mainloop
  by setting bitflags.

- When the HANA/I2C handler is in state 0, and I2C processing is enabled, it will loop through the flags and react to them,
  usually by setting other flags, then calling a function that sets up a pointer to the start of a block in the I2C commandlist
  table and starts executing the command asynchronously.

- When a command is being handled asynchronously, the HANA/I2C statemachine will be placed in a state that isn't 0. Actual
  I2C driving is mostly done in an interrupt handler, but it's still expected that the HANA/I2C statemachine will constantly call
  the "try to continue execution" function, which will keep executing the commandlist until an end state is reached.

## The main HANA/I2C statemachine

This statemachine is typically the first to be updated in the "as fast as possible" loop.

| SMC revision | SM address | Interpreter start routine address | Interpreter continue routine address
|--------------|------------|-----------------------------------|------------------------------------
| Xenon v2     | 0x1936     | 0x258D                            | 0x2592
| Xenon v3     | 0x1969     | 0x25C0                            | 0x25C5
| Zephyr       | 0x19B7     | 0x258A                            | 0x299A
| Falcon       | 0x1A2E     | 0x265C                            | 0x2627
| Jasper       | 0x1A3A     | 0x2674                            | 0x2679
| Trinity      | 0x1B2C     | 0x27E4                            | 0x27E9
| Corona       | 0x1B31     | 0x2995                            | 0x29A3

The states vary depending on the SMC program and hardware revision, but state 0 is virtually always the same workflow:
- Set some mutex (which the program never reads by default)
- If the "run HANA/I2C logic" flag is clear (always the case in power off), exit immediately.
- Check if a flag has been set that requests some operation from this statemachine. If true,
  then the program calls a routine that sets up execution values for the I2C commandlist interpreter
  (start offset within the commandlist table, number of retry attempts, etc.) and execution falls through
  to the interpreter start routine. The HANA/I2C statemachine then changes its state value accordingly.

The other states will usually call the interpreter continue routine and react to its output:
- Carry flag: Set if execution has stopped, cleared if execution is still running
- F0 flag: Error occurred if set, success if cleared

These outputs are the same for the interpreter start routine.

The interpreter will try a given number of attempts to complete the operation; if it gives up, then
execution can fall through to an error handling case. The most important example is if the SMC can't
read the HANA temperature sensors: if that's the case, the system goes to an RRoD and shuts down.

## The commandlist (bytecode) table

The actual I2C driving is done through bytecode stored in the "commandlist table" that the interpreter executes.

Here's an example of bytecode from the Falcon SMC, which is offset 0 in the command list, and at 0x2907 in the SMC
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

### List of commandlist opeerations

Oh boy, this is gonna be fun to untangle and explain.

#### Init I2C bus

Byte format:
- Falcon: `00`

The initialization procedure is:
- Reset the I2C bus
- If SDA is still low after the reset, manually drive the I2C lines to try to get the bus in
  healthy condition, giving up if we can't (setting F0 in this case)
- Manually toggle SCL, then hand over I2C bus control to the I2C unit

#### End commandlist execution

Byte format:
- Xenon: `03`
- Falcon: `03`
- Jasper: `03`

Handlers:

- Falcon: 0x28DC -> 0x2686

Stops executing the commandlist and returns success (via F0 flag).

#### Do nothing (NOP)

Byte format:
- Zephyr onwards: `06`

Handlers:

| SMC revision | Absolute offset  | Jumptable entry |
|--------------|------------------|-----------------|
| Xenon        | Doesn't exist    | Doesn't exist   |
| Zephyr       | TODO             | TODO            |
| Falcon       | 0x28DF           | `ljmp 0x268A`   |
| Jasper       | TODO             | TODO            |
| Trinity      | TODO             | TODO            |
| Corona       | TODO             | TODO            |
| Winchester   | 0x2B95           | `ljmp 0x2998`   |

Does nothing; it simply increments the commandlist execution pointer and continues on to the
next instruction. Could be a development leftover stubbed out on retail consoles.

#### Run IPC-I2C transaction

Byte format:
- Xenon: `06`
- Zephyr onwards: `09`

Handlers:

| SMC revision | Absolute offset  | Jumptable entry |
|--------------|------------------|-----------------|
| Xenon        | 0x281B           | `sjmp 0x27CD`   |
| Zephyr       | 0x284A           | `sjmp 0x27F9`   |
| Falcon       | 0x28E2           | `sjmp 0x2891`   |
| Jasper       | 0x2934           | `sjmp 0x28E3`   |
| Trinity      | 0x2AAA           | `sjmp 0x2A59`   |
| Corona       | 0x2D2E           | `sjmp 0x2CDD`   |
| Winchester   | 0x2B98           | `sjmp 0x2B47`   |

This will block until the transfer completes.

The logic here is spaghetti code because of how the I2C interrupt handler works. When an IPC transaction is running
the I2C IRQ handler overrides the usual read/write buffers and uses the IPC inbox and outbox instead for those operations.

#### Write backup clockgen register (Xenon only)

Byte format:
- Xenon: `17 rr dd` (to be confirmed)

Handlers:
- Xenon: 0x282C -> 0x272B

Writes to the backup clock generator, which is a Cypress CY28517.

#### Write ANA/HANA/KSB register

Byte format:
- Xenon: `08 rr dd dd dd dd` or `08 DB dd dd dd`  (registers 0xD5, 0xD9 and 0xDB treated specially, see below)
- Zephyr, Falcon, Jasper, Trinity: `0B rr dd dd dd dd` or `0B DB dd dd dd` (register 0xDB treated specially, see below)
- Corona and Winchester: `0E rr dd dd dd dd`

Handlers:

| SMC revision | Absolute offset  | Jumptable entry |
|--------------|------------------|-----------------|
| Xenon        | 0x281D           | `ljmp 0x2611`   |
| Zephyr       | 0x284C           | `ljmp 0x25F6`   |
| Falcon       | 0x28E4           | `ljmp 0x268E`   |
| Jasper       | 0x2936           | `ljmp 0x26E0`   |
| Trinity      | 0x2AAC           | `ljmp 0x2850`   |
| Corona       | 0x2D33           | `ljmp 0x2A30`   |
| Winchester   | 0x2B9D           | `ljmp 0x29AC`   |

Writes 4 bytes `dd dd dd dd` to the given ANA/HANA/KSB register `rr`. This will block until the transfer completes.

The data is byteswapped due to how the I2C statemachine buffers work (last in/first out),
so a write to the HANA clock mode select register 0xCE will have the data represented
in the command as `08 e8 40 14` but the I2C bus will actually write `14 40 e8 08`.

Special cases:
- HANA register 0xDB is treated specially because it is set by the SMC config. If register 0xDB is used,
  only three bytes will be read from the commandlist; the fourth will come from the SMC config cell.
- Xenon handles 0xDB identically to HANA-based boards, but also has special cases for ANA registers 0xD5
  and 0xD9. They both check if a flag somewhere (022h.1) is set to 1, and if it is, then overrides will
  be performed. 0xD5 applies the override `-- -- e0 --`, 0xD9 applies the override `-- -- -- 01`.
  Also note for 0xD5 and 0xD9 that the I2C commandlist pointer will still be incremented for those cases,
  unlike 0xDB, which will skip reading a fourth byte.

On KSB systems, there is no special case for register 0xDB as the registers have changed.

#### Write 0 to given KSB register

Byte format:
- Corona and Winchester: `0B rr`

Handlers:

| SMC revision | Absolute offset  | Jumptable entry |
|--------------|------------------|-----------------|
| Xenon        | Doesn't exist    | Doesn't exist   |
| Zephyr       | Doesn't exist    | Doesn't exist   |
| Falcon       | Doesn't exist    | Doesn't exist   |
| Jasper       | Doesn't exist    | Doesn't exist   |
| Trinity      | Doesn't exist    | Doesn't exist   |
| Corona       | 0x2D30           | `ljmp 0x2A20`   |
| Winchester   | 0x2B9A           | `ljmp 0x299C`   |

Reuses the bulk of the "write ANA/HANA/KSB register" code, but writes 0 to the given register.

#### Read HANA register

Byte format:
- Xenon: `0B rr`
- Falcon: `0E rr`

Reads the given register into memory, then it's up to some other command to process the results.
This will block until the transfer completes.

#### Convert I2C result to temperature sensor fields

Byte format:
- Falcon: `1A`

TODO

#### Convert I2C result to CPU temperature fields

Byte format:
- Falcon: `1D`

TODO

#### Convert I2C result to chassis temperature fields

Byte format:
- Falcon: `20`

TODO

#### Dump RRoD error code to I2C buffer

TODO

## Commandlist disassemblies

### Xenon

Commandlist table at 0x283E-0x28A2 (100 bytes).


| Rel offset | Abs offset | Bytecode            | Operation
|------------|------------|---------------------|---------------------------------------------
| `00`       | 0x283E     | `00`                | Init I2C bus
|            | 0x283F     | `06`                | Run IPC-I2C transaction
|            | 0x2840     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `03`       | 0x2841     | `00`                | Init I2C bus
|            | 0x2842     | `08 E4 00 00 00 1B` | Write ANA register 0xE4: `1B 00 00 00`
|            | 0x2848     | `08 E3 0F FF FF FF` | Write ANA register 0xE3: `FF FF FF 0F`
|            | 0x284E     | `08 DB 00 00 00`    | Write ANA register 0xDB: `-- 00 00 00` (special case)
|            | 0x2853     | `08 D5 00 00 00 0F` | Write ANA register 0xD5: `0F 00 00 00` (note: override possible)
|            | 0x2859     | `08 D9 00 01 EE 00` | Write ANA register 0xD9: `00 EE 01 00` (note: override possible)
|            | 0x285F     | `08 DC 00 00 42 AA` | Write ANA register 0xDC: `AA 42 00 00`
|            | 0x2865     | `03`                | End of commandlist
| `-`        | `-`        | `-`                 | `-`
| `28`       | TODO       | TODO                | TODO
| `-`        | `-`        | `-`                 | `-`
| `36`       | TODO       | TODO                | TODO
| `-`        | `-`        | `-`                 | `-`
| `44`       | TODO       | TODO                | TODO
| `-`        | `-`        | `-`                 | `-`
| `53`       | TODO       | TODO                | TODO
| `-`        | `-`        | `-`                 | `-`
| `57`       | TODO       | TODO                | TODO
| `-`        | `-`        | `-`                 | `-`
| `62`       | 0x28A0     | `00`                | Init I2C bus
|            | 0x28A1     | `26`                | Write current RRoD error code to I2C address 0x30
|            | 0x28A2     | `03`                | End of commandlist

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
|            | 0x299B     | `1D`                | Use results of that read to update CPU temperature sensor values
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
2. Not sure yet (in upper nibble), number of bytes to read (in lower nibble)
3. I2C write address (lower 7 bits); bit 7 is the "operation pending" flag and should be set always
4. I2C register??? (lower 7 bits, shifted left once); bit 7 is still a mystery
5. I2C read address (lower 7 bits, shifted left once and ORed with 0x01); bit 7 indicates read (1) or write (0)
6. Data to write (continues for remainder of message)

A libxenon example, `xenon_smc_ana_read()` (see [here](https://github.com/Free60Project/libxenon/blob/master/libxenon/drivers/xenon_smc/xenon_smc.c)):

```
	buf[0] = 0x11;            <-- command 0x11
	buf[1] = 0x10;            <-- write 1 byte (register field)
	buf[2] = 5;               <-- read 5 bytes back
	buf[3] = 0x80 | 0x70;     <-- write register 0x70, set bit 7 to make operation work
	buf[5] = 0xF0;            <-- read register 0x70, bit 7 set to indicate read
	buf[6] = addr;            <-- start of write buffer
```

Note that any error handling for this message will already have been done by the IPC handler.

The I2C interrupt handler will continue reading the IPC inbox where this code left off.
If the CPU requested a read, the results of the read will be dumped to the outbox starting at offset 0x03.

Continuing the libxenon example in `xenon_smc_ana_read()`:

```
	if (buf[1] != 0)
	{
		uprintf("xenon_smc_ana_read failed, addr=%02x, err=%d\n", addr, buf[1]);
		return -1;
	}
	*val = buf[4] | (buf[5] << 8) | (buf[6] << 16) | (buf[7] << 24);
```

In this case, `buf[3]` is ignored because that's the "size of message" field from the I2C response. The code
assumes it'll always be 4 bytes wide, and copies the rest of the response to the output field.

## Hacking custom operations into the commandlist table

This is what you're after, aren't you?

- The commandlist table, by default, can't be more than 256 bytes, as the interpreter reads opcodes
  using a single 8-bit memory cell, that is added to the dptr to read values.

- There are usually some functions in that 256 byte range that you'll have to relocate if you want
  to add custom bytecode.

The open source RGH3 code is the best example of how to handle things. It patches custom operations
at the end of the commandlist table while relocating functions that live there. It will start operations
in its own statemaching when the main HANA/I2C statemachine is in state 0. Once it's kicked off an operation,
it will then override the HANA/I2C statemachine state to 4, as that's a state which will call the interpreter
continue routine and exit silently with little side effects regardless if the slowdown/speedup operation
succeeds.

See [snippets/i2c_custom_example.s](snippets/i2c_custom_example.s) for a basic way of patching custom I2C bytecode
into the commandlist table on the Corona SMC.