# SMC versions

## Known versions

| Revision      | Rev. Byte @ 0x100 | Version @ 0x101,0x102 |
|---------------|-------------------|-----------------------|
| Xenon v2      | 0x12              | 1.51                  |
| Zephyr v1     | 0x21              | 1.10                  |
| Falcon v1     | 0x31              | 1.06                  |
| Jasper v1     | 0x41              | 2.03                  |
| Trinity v1    | 0x51              | 3.01                  |
| Corona v2     | 0x62              | 2.05                  |
| Winchester v1 | 0x71              | 1.03                  |

## Hacked SMCs

### Infinite reboot patch

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

### More elaborate hacked SMCs

Typical hacked SMCs:

- CR4 was created by Team Xecuter and adds I2C slowdown control on DBG_LED0 for RGH2+ (also Muffin/Mufas).
- SMC+ is a hexedit of CR4 that shortens SMC handshake timeouts.

JTAG, RGH3 and others that are actively used in glitch/software exploits are to be documented in more detail later.

## Board compatibility

- Xenon boards use two different southbridges (G0 and R0). Xenon v2 should be compatible with both revisions;
  the Xenon JTAG SMC is a hacked version of v2.

- Zephyr/Falcon/Jasper are more or less the same board from a SMC perspective so Jasper can be used for all
  three boards. Note however that the checkstop signal on Falcon/Jasper is a jumper on Zephyr (SB_DETECT).
  RGH3 v1 uses the Jasper SMC for Falcon/Jasper; the Z/F/J JTAG SMC is also a hacked Jasper SMC.

