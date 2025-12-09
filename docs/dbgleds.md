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

Two quick notes about DBG_LED3:
- This is actually strobed in the reset watchdog statemachine; the debug LED statemachine never
  accesses this.
- Some SMC versions (Falcon for sure) have buggy behavior that assumes the LED still exists there and
  attempts to strobe it upon releasing GPU reset. (TODO: was this bug ever fixed?)

## Blink patterns

### DBG_LED2 (Xenon), DBG_LED0 (all others)

- 10000000 (one short blink): something powered the system up; checking what it is
- 11111110 (one long blink): not sure yet, TODO
- 10101010 (constant blinking): all normal here

### DBG_LED0 (Xenon)

- 11110000 (slow flashing): PCIe link status register bit 4 not set
- 11111111 (stays lit): PCIe link status register bit 4 is set but bit 5 isn't

### DBG_LED1 (Xenon)

- 10000000 (one blink): Boot attempt 1 failed
- 10100000 (two blinks): Boot attempt 2 failed
- 10101000 (three blinks): Boot attempt 3 failed
- 10101010 (four blinks): Boot attempt 4 failed
- 11111111 (stays lit): Boot attempt 5 failed (RRoD should be displayed on front)

## Hacked SMCs kill this statemachine

Hacked SMCs like JTAG, CR4 and RGH3 abuse the DBG_LED0 pin for various and very naughty purposes,
so this state machine is usually disabled on those to prevent conflicts. In addition to the obvious GPIO-related
patches, the call to the debug LED statemachine in the mainloop is typically NOPed out.
