# Debug LED state machine

The SMC has a dedicated state machine to update the DBG_LED header. Other statemachines set up
blink patterns, and when the debug LED state machine is enabled, it rotates through the bit patterns every
100 ms, flashing the lights.

Xenon boards of course feature four slots for debug LEDs. Newer boards reduce this to just one LED, and the
SMC program likewise no longer attempts to update those LEDs; although there is still code that tries to
update them, the actual functions that turn those LEDs on or off are stubbed out.

| Xenon LED | Normal LED | What sets it
|-----------|------------|------------------------------------------------------------------------------
| DBG_LED0  | n/a        | PCIe link problem
| DBG_LED1  | n/a        | Boot failed; trying again
| DBG_LED2  | DBG_LED0   | Power-up state machine events
| DBG_LED3  | n/a        | Rapidly pulsed when GPU is released from reset, not normally visible

DBG_LED3 on Xenon is tied to the GPU's JTAG port on the GPU_TCLK_R pin. This remains in place
for all other fats. The SMC code will strobe this line before releasing the GPU from reset,
and it's not clear why this is needed, because you can patch this out and the system will boot
without it. This is removed from slims.

## The state machine

Locations:
- Falcon: 0x13FC
- Corona: 0x14DB

This is a simple two-state state machine that didn't really need to be a state machine.

- State 0 updates the LEDs in this order: boot status, boot attempt, PCIe link status. Then it
  sets up the 100 ms delay and goes to state 1. On post-Xenon fats, the boot attempt and PCIe link
  status flasher update code is still there, but the functions that update the LEDs are stubbed out
  (immediate `ret`). On slims, only the boot attempt update code is present.
- State 1 just runs the delay timer so the LEDs advance every 100 ms; when that timer expires, we
  go back to state 0.

## Blink patterns

Note that when blink patterns are updated, the current position isn't automatically reset, so you will
get some misleading results.

### DBG_LED2 (Xenon), DBG_LED0 (all others): boot status

- 10000000 (one short blink): something powered the system up; checking what it is
- 11111110 (one long blink): not sure yet, TODO
- 10101010 (constant blinking): all normal here

### DBG_LED0 (Xenon): PCIe link issue

- 11110000 (slow flashing): PCIe link status register bit 4 not set
- 11111111 (stays lit): PCIe link status register bit 4 is set but bit 5 isn't

### DBG_LED1 (Xenon): Boot attempt

- 10000000 (one blink): Boot attempt 1 failed
- 10100000 (two blinks): Boot attempt 2 failed
- 10101000 (three blinks): Boot attempt 3 failed
- 10101010 (four blinks): Boot attempt 4 failed
- 11111111 (stays lit): Boot attempt 5 failed (RRoD should be displayed on front)

## Hacked SMCs kill this statemachine

Hacked SMCs like JTAG, CR4 and RGH3 abuse the DBG_LED0 pin for various and very naughty purposes,
so this state machine is usually disabled on those to prevent conflicts. In addition to the obvious GPIO-related
patches, the call to the debug LED statemachine in the mainloop is typically NOPed out.
