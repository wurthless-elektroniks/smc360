# SMC I/Os

Work-in-progress...

## ??? - Port 0

| Bit    | Ghidra symbol | All fats          | Trinity | Corona | Winchester |
|--------|---------------|-------------------|---------|--------|------------|
| ???h.0 | P0.0          | CPU_PWRGD         | TODO    | TODO   | TODO       |
| ???h.1 | P0.1          | GPU_RST_N         | TODO    | TODO   | TODO       |
| ???h.2 | P0.2          | ARGON_CLK         | TODO    | TODO   | TODO       |
| ???h.3 | P0.3          | ARGON_DATA        | TODO    | TODO   | TODO       |
| ???h.4 | P0.4          | SB_RST_N          | TODO    | TODO   | TODO       |
| ???h.5 | P0.5          | SB_MAIN_PWRGD_R   | TODO    | TODO   | TODO       |
| ???h.6 | P0.6          | CPU_RST_N         | TODO    | TODO   | TODO       |
| ???h.7 | P0.7          | GPU_RESET_DONE    | TODO    | TODO   | TODO       |

## ??? - Port 1

| Bit    | Ghidra symbol | All fats          | Trinity | Corona | Winchester |
|--------|---------------|-------------------|---------|--------|------------|
| ???h.0 | P1.0          | EJECTSW_N         | TODO    | TODO   | TODO       |
| ???h.1 | P1.1          | TILTSW_N          | TODO    | TODO   | TODO       |
| ???h.2 | P1.2          | BINDSW_N          | TODO    | TODO   | TODO       |
| ???h.3 | P1.3          | VREG_V1P8_EN_N    | TODO    | TODO   | TODO       |
| ???h.4 | P1.4          | VREG_V5P0_SEL     | TODO    | TODO   | TODO       |
| ???h.5 | P1.5          | 5VPO_ENABLE       | TODO    | TODO   | TODO       |
| ???h.6 | P1.6          | VREG_CPU_PWRGD    | TODO    | TODO   | TODO       |
| ???h.7 | P1.7          | VREG_CPU_EN       | TODO    | TODO   | TODO       |

- TILTSW_N is the tilt switch and it's used to change the orientation of the
  Ring of Light depending on if the system is standing upright or laying down.
  On Xbox 360 E, the Ring of Light is simplified, so there's no more tilt switch.
  Stingray leaves the tiltswitch position unpopulated and Winchester removes it
  entirely, but both still have the line pulled up to 3v3.

## ??? - Port 2

| Bit    | Ghidra symbol | All fats          | Trinity | Corona | Winchester |
|--------|---------------|-------------------|---------|--------|------------|
| ???h.0 | P2.0          | ANA_CLK_OE        | TODO    | TODO   | TODO       |
| ???h.1 | P2.1          | PSU_12V_ENABLE    | TODO    | TODO   | TODO       |
| ???h.2 | P2.2          | VREG_GPU_EN_N     | TODO    | TODO   | TODO       |
| ???h.3 | P2.3          | ANA_RST_N         | TODO    | TODO   | TODO       |
| ???h.4 | P2.4          | VREG_GPU_PWRGD    | TODO    | TODO   | TODO       |
| ???h.5 | P2.5          | ANA_V12P0_PWRGD   | TODO    | TODO   | TODO       |
| ???h.6 | P2.6          | VREG_3P3_EN_N     | TODO    | TODO   | TODO       |
| ???h.7 | P2.7          | POWERSW_N         | TODO    | TODO   | TODO       |

## 0C0h - Port 3

| Bit    | Ghidra symbol | Xenon    | Zephyr/Falcon/Jasper   | Trinity | Corona | Winchester |
|--------|---------------|----------|------------------------|---------|--------|------------|
| 0C0h.0 | FIFLG.0       | DBG_LED0 | DBG_LED0               | TODO    | TODO   | TODO       |
| 0C0h.1 | FIFLG.1       | DBG_LED1 | VREG_V5P0_VMEM_PWRGD   | TODO    | TODO   | TODO       |
| 0C0h.2 | FIFLG.2       | DBG_LED2 | ANA_VRST_OK            | TODO    | TODO   | TODO       |
| 0C0h.3 | FIFLG.3       | DBG_LED3 | GPU_TCLK_R             | TODO    | TODO   | TODO       |
| 0C0h.4 | FIFLG.4       | DDC_CLK  | HDMI_DDC_CLK           | TODO    | TODO   | TODO       |
| 0C0h.5 | FIFLG.5       | AV_MODE0 | AV_MODE0               | TODO    | TODO   | TODO       |
| 0C0h.6 | FIFLG.6       | AV_MODE1 | AV_MODE1               | TODO    | TODO   | TODO       |
| 0C0h.7 | FIFLG.7       | AV_MODE2 | AV_MODE2               | TODO    | TODO   | TODO       |

- DBG_LED0-3 on Xenon are left floating externally
- DBG_LED0 on Zephyr onwards is usually pulled low externally
- AV_MODE0, AV_MODE1, AV_MODE2 are connected to the A/V port and are pulled up externally;
  the A/V port device pulls those lines low to signal what kind of device is connected.
  On Stingray only AV_MODE1 is used for the TRS-like A/V connector; the others are pulled high
  (with debouncing capacitors) and are otherwise unused.


## 0C8h - Port 4

| Bit    | Ghidra symbol | Xenon        | Zephyr        | Falcon/Jasper          | Trinity | Corona | Winchester |
|--------|---------------|--------------|---------------|------------------------|---------|--------|------------|
| 0C8h.0 |               | SMB_CLK      | SMB_CLK       | SMB_CLK                | TODO    | TODO   | TODO       |
| 0C8h.1 |               | SMB_DATA     | SMB_DATA      | SMB_DATA               | TODO    | TODO   | TODO       |
| 0C8h.2 | TR2           | DDC_CLK_OUT  | SB_DETECT     | SMC_CPU_CHKSTOP_DETECT | TODO    | TODO   | TODO       |
| 0C8h.3 |               | DDC_DATA_OUT | HDMI_DDC_DATA | HDMI_DDC_DATA          | TODO    | TODO   | TODO       |
| 0C8h.4 | TCLK          | AUD_CLAMP    | AUD_CLAMP     | AUD_CLAMP              | TODO    | TODO   | TODO       |
| 0C8h.5 | RCLK          | EXT_PWR_ON_N | EXT_PWR_ON_N  | EXT_PWR_ON_N           | TODO    | TODO   | TODO       |
| 0C8h.6 |               | TRAY_STATUS  | TRAY_STATUS   | TRAY_STATUS            | TODO    | TODO   | TODO       |
| 0C8h.7 |               | TRAY_OPEN_R  | TRAY_OPEN_R   | TRAY_OPEN_R            | TODO    | TODO   | TODO       |

- SB_DETECT on Zephyr is a jumper which is either pulled high by a resistor at R2N26 or pulled low by a resistor
  at R2N27. In practice it should be always pulled high to indicate the use of a R0 southbridge.

- SMC_CPU_CHKSTOP_DETECT is switched from the CPU via an NPN transistor, with the CPU signal being active low.
  This I/O line is normally pulled up to 3v3 via a 10k ohm resistor. This would allow the SMC to detect a checkstop
  error and shut down the system with a RRoD, but in practice (on Falcon and Jasper) the SMC only reads the line,
  sets a flag, and does nothing else with it.
