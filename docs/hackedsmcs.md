
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

Evolution of the pattern between different SMC revisions:

- Xenon:      `05 3E E5 3E B4 05 10`
- Zephyr:     `05 3E E5 3E B4 05 10`
- Falcon:     `05 3C E5 3C B4 05 1E`
- Jasper:     `05 3F E5 3F B4 05 10`
- Trinity:    `05 3C E5 3C B4 05 1E`
- Corona:     `05 3D E5 3D B4 05 1E`
- Winchester: `05 3D E5 3D B4 05 1E`

## More elaborate hacked SMCs

JTAG, RGH3 and others that are actively used in glitch/software exploits are to be documented in more detail later.

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
- hwinit sends SMC command 0x12 before SDRAM training begins. This was actually documented by Free60, although in
  a vague and incorrect manner, saying that some sort of handshake happens during hwinit.
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
