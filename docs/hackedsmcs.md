
# Hacked SMCs

## Infinite reboot patch

The "vanilla" SMC hack done for systems that need infinite boot attempts (i.e., RGH) is to look for the
pattern `05 3x E5 3x B4 05 1x`, which represents this code (Falcon in this example):

```
sysreset_watchdog_exec_state_10:
    INC        g_num_boot_tries      ; increment death counter
    MOV        A,g_num_boot_tries
    CJNE       A,#0x5,LAB_CODE_12ba  ; if it's not 5, try again
    
    ; execution falls through to failure case otherwise
```

Then it's enough to change the `inc` instruction to a `nop` (change `05 xx` to `00 00`).

There's one problem with this patch, however: any RRoD raised by CPU before GetPowerUpCause arrives
will be ignored, and the system will reboot. This means that if hwinit encounters an error, then
the reset watchdog will reboot infinitely instead of giving up.

Evolution of the pattern between different SMC revisions:

- Xenon:      `05 3E E5 3E B4 05 10`
- Zephyr:     `05 3E E5 3E B4 05 10`
- Falcon:     `05 3C E5 3C B4 05 1E`
- Jasper:     `05 3F E5 3F B4 05 10`
- Trinity:    `05 3C E5 3C B4 05 1E`
- Corona:     `05 3D E5 3D B4 05 1E`
- Winchester: `05 3D E5 3D B4 05 1E`

## xeBuild patches

The infinite reboot patch is as described above, but it searches for `05 xx E5 xx B4 05`.

The eject button disable patch looks for `A2 90 B3 22` and replaces it with `00 00 C3 22`.
This patches `ejectsw_read` to explicitly return false in the carry flag (i.e., pretend the eject button
is never pressed). This patch does not work on Corona, which has moved /EJECTSW_N to a different I/O line.
(For Corona/Winchester, the pattern should be `A2 93 B3 22`.)

The Ring of Light blink disable patch (used when there's no DVD drive) looks for `E4 A2 CF 92 E0 A2 CE 22`
and replaces it with `E4 D3 22 00 00 00 00 00`. This patches `tray_read_status_and_open_state` to
clear the accumulator and set the carry flag, then immediately return. This pretends that
TRAY_OPEN_R is 0 and TRAY_STATUS is 1. This patch is also broken on Corona, as TRAY_OPEN_R and TRAY_STATUS
have been remapped. (For Corona/Winchester, the pattern should be `E4 A2 C3 92 E0 A2 C0 22`.)

## JTAG

This is probably the most important SMC hack ever made, simply because of how much of a joke it made of Microsoft's efforts
to secure the 360. The code was written by Tiros, which would normally make him a hero, except for the fact that, like cOz
and a lot of the early 360 scene programmers, he hoarded code and knowledge which makes things annoying for us fifteen years
later.

First, a primer on the JTAG exploit: it's basically a self-booting King Kong exploit. The CPU normally runs encrypted code
that can't be tampered with, except for on two kernel versions, where a completely boneheaded vulnerability compromised that and
allowed arbitrary code execution in the hypervisor. The King Kong exploit used a shader to exploit the hypervisor, but that
was patched. Eventually tmbinc found out how to use the GPU's JTAG port to run attacks on vulnerable kernels, but that required
specialized hardware, so hackers ported the attack to the SMC.

Our goal here is to get a payload into SDRAM so that the hypervisor runs code it's not supposed to. On the SMC side
we have access to the SFCX flash controller, but several of its registers aren't accessible, especially the ones that
can be used to setup NAND-to-SDRAM DMA transfers. The SMC's task will be to program those registers over JTAG, then start
the DMA through the SFCX command register.

This documentation applies to the Xenon patches.

The JTAG SMC was written with the assumption that all four pins on the debug LED header would be used for the attack,
so when reading the code you will see accesses to pins that are unused with the common two-wire/diode scheme.

The remapped I/Os are:

| I/O    | Normal pin | JTAG purpose 
|--------|------------|--------------------------------------------------------
| 0C0h.0 | DBG_LED0   | GPU_TDI
| 0C0h.1 | DBG_LED1   | GPU_TMS
| 0C0h.2 | DBG_LED2   | GPU_TRST (obsolete)
| 0C0h.3 | DBG_LED3   | GPU_TCLK (tied to the JTAG port on the PCB!!)

Things to note here:
- GPU_TRST is used in the old three-wire JTAG scheme, but in the two-wire scheme it's simply tied to
  /GPU_SCAN_BUFF_EN_N.
- Yes, DBG_LED3 really is tied to the JTAG port on the PCB. Who knows why Microsoft did this, but either
  way, it means one less wire for us to solder.

A bunch of custom code is dropped at 0x2DC0~, and the following patches are made.

There is a nonsensical hook installed at 0x0775, which causes execution to jump down all the way to a handler at
0x2DDD, but all it does is set the stack pointer to 0x7C (same as on a clean Xenon SMC), and continues execution
as normal. This is likely a development leftover.

Since the SMC needs to repurpose the debug LED header, the mainloop call to the debug LED statemachine (at 0x7B6)
is NOPed out.

The real fun begins just before the CPU is brought out of reset. A ljmp is placed at 0x1148 which sends execution
to the main function at 0x2DE3. The gist of it is that, if the CPU is not running (which should already be the case;
probably leftover sanity check behavior), the JTAG bus is initialized, then a function at 0x2F3B programs the JTAG port.
After that, we can finally release the CPU from reset and let the boot continue as normal.

The code written over the JTAG bus is:
```
d0 00 00 1b 00 02 01 00

d0 00 00 1b 00 02 01 00

d0 14 00 13 ea 00 c0 00 - init SFCX PCI BAR

d0 14 00 07 00 00 00 06

d0 15 00 13 ea 00 10 00 - init southbridge/SMC PCI BAR

d0 15 00 07 00 00 00 06

ea 00 c0 0f 00 00 02 00 - set SFCX_ADDRESS to 0x200, where the DMA payload lives in (logical) flash space

ea 00 c0 1f 00 13 03 60 - set SFCX_DPHYSADD to the idle thread context
                          which will redirect execution to our custom code

ea 00 c0 23 00 00 20 80 - set SFCX_MPHYSADD to 0x2080, which points to hypervisor syscall 0x46
```

When IPC command 0x04 arrives, that means the kernel is far enough into the boot process that it is now trying to
grab the current time from the RTC. The IPC handler is hooked so that any attempt to request the system time redirects
to the following:

- Wait for some operation to finish.
- If the GPU_TRST GPIO line was left high, then write 0x07 to SFR 0F5h (SFCX command register), which tells the flash
  controller to start the NAND-to-SDRAM DMA. Once that's sent, pull that GPIO line low.
- Clear the JTAG state and head back to the normal IPC code to finish handling the IPC command.

This code demonstrates a lot of low-level knowledge of the Xbox 360's boot process, including stuff that would normally be
done by hwinit. This is basically confirmed by [hack.txt](https://github.com/gligli/tools/blob/master/imgbuild/hack.txt).
But, because this is the 360 scene we're talking about, the actual details of hwinit and how it worked were left undocumented
for fifteen god damn years, when Mate Kukri had to reinvent the wheel with his hwinit disassembler. Great job guys!!!

One additional bit of lameness: the Glitch2 xenon.ecc in J-Runner with Extras reuses this SMC code, but it's been patched to
reboot infinitely. I mean, the normal Xenon v2/1.51 code was right there...

## CR4

This is a Team Xecuter SMC hack, and it's another entry in Team Xecuter's legacy of lameness. It was created for the RGH2+
method (also called Project Muffin/Mufas), which moves I2C slowdown toggling to the SMC so as to try not to interfere with
normal SMC I2C operation.

Note that this documents the changes to the Falcon SMC code.

The CR4 code installs a hook in the "1ms has passed" IRQ handler, which leads to a function that does the following
(on Falcon):
- Read SFR 0BAh (!??!?!), which the program is abusing as a memory cell (who knows what that SFR actually does!!)
- Read DBG_LED0 status
- If DBG_LED0 is high and 0BAh is 1, write `43 08 80 03` to HANA register 0xCD (standard RGH2 slowdown) and set 0BAh to 2.
  Otherwise, if DBG_LED0 is low and 0BAh is 2, write `4E 80 0C 02` to that register (its default setting).
- Update SFR 0BAh and return to main IRQ handler flow.

Remember, of course, that the 0xCD register is one that causes a lot of clock jitter and is a big reason why RGH2 was so slow
and unreliable. The clock bypass modes in 0xCE would have been better, but TX didn't know about it or even investigate it;
they just went off what they knew worked. Even if what they knew worked, didn't actually work well.

When it comes to actually setting the I2C register, the program does this (mostly copypasted from other code lying around in
the SMC program):
- Kick the watchdog endlessly in a loop until the current I2C data transfer finishes execution (ignoring that there might be
  more I2C commands pending after the current one).
- Kick the watchdog again for good measure.
- Reset the I2C bus.
- If there's some problem with the I2C bus (to be documented), the attempt to set the I2C register is aborted, and
  the higher-level code doesn't even bother to check if there was an error.
- The rest of it pretends a command happened in the I2C list at offset 0, which kicks off the transfer somehow.

Besides this, the patches do this:
- Stack pointer is moved up for some reason (the memory cells in the now unused space there don't seem to be used)
- DBG_LED0 statemachine is disabled (pretty typical for hacked SMCs)
- DBG_LED0 is always set as an input
- Standard infinite retry patch in the handshake watchdog
- Installs hook in some function I still don't understand yet, that initializes the I2C slowdown state to 1

The way they set the I2C slowdown state is also worth a laff:

```
    MOV R1,#0x1
    MOV DAT_SFR_ba,R1
```

...when they could have just done a one-instruction write to the SFR.

Anyway, there are some problems with this code:
- The aforementioned abuse of the mystery SFR register isn't the best solution; they should have used `mov @r0` or
  similar to access higher memory cells.
- The program doesn't actually check if whatever I2C command running from the command list is finished before
  starting a new I2C transaction, which can cause conflicts with other I2C operations.

All in all, this is a solution that doesn't really improve the success rate of glitch attempts, and it introduces some
hazards that can cancel out any advantages it would have over setting the I2C registers from the glitch chip. It's really
just TX in a nutshell, in that they didn't really attempt to understand the software or hardware and were more interested
in pushing out a half-baked solution so they could make a quick buck.

## SMC+

SMC+ is a two-byte hexedit of CR4 that shortens SMC handshake timeouts. As usual for the 360 scene, it's a half solution
that was touted as the second coming of Jesus by 360 scene hype men.

When glitch attempts fail on RGH1 and RGH2, the system sits there drooling like an idiot until the SMC finally
times out and reboots. Naturally, the scene picked the path of least resistance, which was just to lower the
timeouts so the SMC starts the next boot attempt sooner.

However, there were two better solutions that were not considered or investigated:
- hwinit sends SMC command 0x12 before SDRAM training begins. This was documented in the JTAG hack.txt all the way
  back in 2009, although in a vague and incorrect manner, saying that some sort of handshake happens during hwinit.
  Had this been used, SMC+ could have been maybe twice as fast as it was.

- The SMC isn't actually monitoring the boot process at all, despite any claim that SMC+ provides some sort of
  acceleration. If, however, the SMC is connected to POST lines, or can somehow monitor boot progress via IPC,
  then timeouts can be set at different points during the boot, allowing reboots to happen sooner. RGH3 ended
  up being the first to implement this, and that means that the slow and unreliable glitch method that all
  the RGH1.2 purists sneered at had a massive possible improvement that they chose to ignore.

Of course, the CR4 base patches eat up a bit of space in the SMC program, so coding these improvements would involve
some sizecoding trickery. But who cares? It's the 360 scene, and egoboosting and console mod shop promotion is
far more important than actually helping people.

If you have a hex editor, you can be an elite modder, too. Here's how to make your own SMC+:

| SMC version | Offsets to change | Original (clean SMC)               | Modified (CR4)                     | Modified (SMC+)                    |
|-------------|-------------------|------------------------------------|------------------------------------|------------------------------------|
| Xenon v2    | 0x114D, 0x115E    | `AF`/`AF` (175 * 2 * 20 = 7000 ms) | n/a                                | n/a                                |
| Zephyr v1   | 0x122B, 0x1238    | `AF`/`AF` (175 * 2 * 20 = 7000 ms) | n/a                                | n/a                                |
| Falcon v1   | 0x1276, 0x1284    | `AF`/`AF` (175 * 2 * 20 = 7000 ms) | Unchanged                          | `8A`/`8A` (138 * 2 * 20 = 5520 ms) |
| Jasper v1   | 0x127B, 0x1292    | `82`/`82` (130 * 2 * 20 = 5200 ms) | `54`/`54` (84 * 2 * 20 = 3360 ms)  | `50`/`50` (80 * 2 * 20 = 3200 ms)  |
| Trinity v1  | 0x1380, 0x1396    | `82`/`82` (130 * 2 * 20 = 5200 ms) | `60`/`60` (90 * 2 * 20 = 3600 ms)  | `41`/`41` (65 * 2 * 20 = 2600 ms)  |
| Corona v2   | 0x1381, 0x1397    | `82`/`82` (130 * 2 * 20 = 5200 ms) | `50`/`50` (80 * 2 * 20 = 3200 ms)  | `41`/`41` (65 * 2 * 20 = 2600 ms)  |

Or you can search `75 3x AF` or `75 3x 82` (the memory cell is 03Bh, 03Ch or 03Dh depending on the SMC version) and change the last byte of that
for all instances you find.

Just keep in mind that the actual timings here depend on the size of CB_B and how long it takes for hwinit to run. GetPowerUpCause is sent in
CD on Glitch2 (either by CDxell or Freeboot), so you can get the base times by counting how long it takes from CPU reset release until the
POST 0x40 -> 0x10 transistion (on Freeboot).

In short, this could have been a dropdown in J-Runner.

## RGH3

RGH3 is, like most Xbox 360 scene productions, something that should have happened years ago but
didn't because people were too busy making money and padding their CVs. It's actually a bit of a
triumph because it's not just a SMC program, but a complete technique for glitching the system.

RGH3 did the following things that hadn't really been done before:
- Glitch attack now runs from the SMC (was attempted previously but deemed to be unstable).
- SMC now monitors the boot process, not just to know when to time the glitch, but also to know
  if the glitch succeeded or not.
- CPU now gets an intermediate CB loader called CB_X, which speeds up glitch attempts.

There are two different versions of RGH3 (nicknames mine): "RGH3 v1" is the closed source release
from 2021, and "RGH3 v2" is the open source release from 2024/2025.

### RGH3 v1

Documentation applies to Falcon/Jasper code, which itself is based off the Jasper SMC.
Not much differences apply between 10 MHz and 27 MHz except for the delays in the glitching code
and the slowdown values written. 10 MHz uses the already known but unstable HANA register 0xCD;
27 MHz uses the clock bypass mode in HANA register 0xCE.

The bulk of the patch code is dropped in to 0x2D73, which is the end of the normal Jasper codespace.

The reset vector (0x0000) is patched `e1 56 21` to `02 2e 21` which is a pretty fancy hack
redirecting code to a new startup function while leaving the `ajmp` to the "every 1ms" IRQ handler.

The code at 0x2E21 then does this:
- If /CPU_RST_N is high, increment counter at 03Fh. Then, if GPU_RESET_DONE is high, fall through
  to stock SMC code in the reset watchdog statemachine, which requests a reset and goes to state 10.

- If /CPU_RST_N was NOT high, increment counter at 0C2h. Code then falls through to a very strange
  handler...

At 0x2E40 is this very odd code:
```

       CODE:2e40 e5 02           MOV        A,BANK0_R2
       CODE:2e42 65 03           XRL        A,BANK0_R3
       CODE:2e44 f6              MOV        @R0,A
       CODE:2e45 e5 06           MOV        A,BANK0_R6
       CODE:2e47 24 49           ADD        A,#0x49
       CODE:2e49 c0 e0           PUSH       A
       CODE:2e4b 54 32           ANL        A,#0x32
       CODE:2e4d 24 f5           ADD        A,#0xf5
       CODE:2e4f c0 e0           PUSH       A
       CODE:2e51 22              RET
```

This code is doing two things:
- It's obfuscating the real entry point to the code, which is lame and unnecessary.
- It's seemingly trying to redirect code execution depending on how the SMC watchdog reset function
  fires. Remember that if the SMC code gets stuck, a watchdog will eventually fire that resets it.

Meanwhile, in the init/mainloop block at 0x756:
- Stack pointer is moved up from 0B9h to 0C4h to make room for additional memory cells.
- The call to 0x1408 in the mainloop, which runs the debug LED state machine, is removed, and
  the "run as fast as possible" portion now calls a handler at 0x2D73.

So what does the code at 0x2D73 do?
- Read memory cell 03Fh into accumulator.
- If /CPU_RST_N is low, clear DBG_LED0, which has been repurposed to assert CPU_PLL_BYPASS.
  Check 03Fh.2; if it's 0, set 03Fh to 0 and exit. Otherwise, run I2C logic, retrying
  until it succeeds, after which 03Fh is set to 0.

The I2C handling code is:
- If 0A6h is not zero, set carry and exit (failure/busy case).
- Call 0x2692, which is the "reset I2C bus and exit" function.
- Call 0x2A48, which checks the I2C SDA state (it should be high) and returns the inverse of it.
- If 0x2A48 returned CY=0 (bus is OK), do some variant on the normal I2C reset process, where
  SDA is manually driven, the I2C bus is reset, and code execution jumps to a freshly inserted
  code block at 0x13CF, which toggles the I2C slowdown state.
- Call 0x2A62, which tries to get the I2C bus back in stable condition. If it succeeds,
  run the I2C toggle logic (same as previous case).
- Otherwise, jump to 0x2690, which is the I2C "give up" case; it will set the carry flag too.

The I2C toggle code seems to be "inspired" by the buggy CR4 code, in that it forces the I2C
statemachine to manually write values instead of going through the commandlist like it's supposed to.
Either way, slowdown is enabled when 03Fh is 4, and disabled otherwise.

Now for the bulk of the statemachine code, which 03Fh determines.

- State 0: Set 0C0h to 12 and jump to a common handler at 0x2E13.
- State 1: Wait until memory cell at 077h (the milliseconds counter) is 0x15. Once it is,
  decrement timer at 0C0h; once that hits 0, proceed to the next state. In practice this
  is killing about 255 ms while the bootrom executes most of its logic.
- State 2: Wait until GPU_RESET_DONE, which is now tied to POST bit 1, goes high. Once it
  does, proceed to the next state. At this point, the code is waiting for POST 0x1E.
- State 3: Disable interrupts, then track POST states. POST bit 1 must toggle high/low/high/low/high,
  i.e., 0x1E/0xD0/0xD2/0xD4/0xD6. Once 0xD6 arrives, set DBG_LED0 to enable PLL bypass, re-enable
  interrupts, set 0C0h to 5, and proceed to the next state. (PLL bypass is enabled while I2C slowdown
  is switched, probably to buy some time while the command executes on the slow I2C bus.)
- State 4: Force I2C toggle logic to execute until it succeeds. When it does,
  proceed to the next state. Remember that state 4 is a special case; the I2C logic will try
  to enable I2C slowdown here.
- State 5: Same logic as state 1: wait for timer to expire (100 ms?), then go to next state.
- State 6: The meat of the glitch attack. Clear PLL bypass and kill interrupts. Spin until POST 0xD8, kick watchdog, then
  load PLL delay (valuies load to R2/R3/R4). Once delay expires, assert CPU_PLL_BYPASS, and wait for
  the POST bit to rise again, taking us to POST 0xDA. Kick watchdog and begin reset delay (values copied from
  0C2h/0C3h to R5/R6). Once second delay expires, do glitch pulse (`CLR gpio_cpu_rst_n` immediately
  followed by `SETB gpio_cpu_rst_n`). Kick watchdog again, de-assert CPU_PLL_BYPASS, re-enable interrupts,
  increment the 03Fh state, set 0C0h to 3 (delay for state 8), then attempt to disable I2C slowdown.
  (Whether slowdown is successfully disabled or not is not checked here.)
- State 7: Same as state 4: force I2C toggle logic to execute until it succeeds. When it does,
  proceed to the next state. Since the state value is now 7, this will try turning I2C slowdown off.
- State 8: Same logic as state 1/5: wait for timer to expire, then go to next state. In this case,
  we're waiting about 60 ms.
- State 9: This is the same logic in the reset vector. Since /CPU_RST_N is high, execution falls through
  to 0x2E52, which increments the state counter. It then checks the POST bit, which should now be 0.
  If it is, then that means CB_X must have cleared it (POST 0x54) and the glitch has (seemingly) succeeded.
  If it hasn't, then execution jumps to 0x12D1, which tells the reset watchdog statemachine to request a
  reboot and start the reset process over again.
- State 10 (and all other states) is the idle state.

### RGH3 v2

This is open source (read it [here](https://github.com/15432/RGH3)), so I won't document everything.

- All calls in the mainloop get redirected to stubs which execute the main RGH3 statemachine logic
  as often as possible, in an attempt to make timings more accurate.
- I2C slowdown now executes through proper I2C commandlists that have been patched into the main
  commandlist table. In addition to changing HANA register 0xCE, the Jasper code also writes to
  HANA register 0xD4, which overclocks the SMC in an attempt to make glitching more precise.
- The millisecond wait code is now finer-grained.
- The Argon statemachine is disabled while the glitch is running.
- In addition to checking for POST 0x54, the SMC code also checks for POST bit 1 to rise afterwards,
  which it should at POST 0x2E (hwinit running). This however is controlled by an #ifdef statement
  (`SKIP_CBB_POST_CHECK`).

## RGH1.3

This is where I have to toot my own horn and do shameless self-promotion like any 360 scene lamer should.
I've written the bulk of the story before, but here are the basics.

RGH1.3 is an stupid idea that turned serious. It's basically RGH3 but with a glitch chip. But by offloading the
glitching logic to the glitch chip, the SMC is free to do boot progress monitoring even more aggressively than
RGH3.

I think this is the first SMC to do the following:
- Extremely aggressive glitching against stubborn Jaspers, by hard-resetting the system under "badjasper" builds
- Boot progress indication on the Ring of Light
- Custom IPC logic handling for tracking boot progress on 1wire and 0wire builds

Read the source [here](https://github.com/wurthless-elektroniks/RGH1.3).
