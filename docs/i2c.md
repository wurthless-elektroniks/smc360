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
- 0x69 (Xenon only): Clock generator
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
