# I2C

The SMC is connected to several other devices over I2C (also SMBus or PMBus).

TODO: everything. I2C appears to be bitbanged by the SMC (TODO: it's not, describe it later), yadda yadda yadda.

I2C devices themselves shouldn't be documented here, that's a whole other barrel of monkeys.

By default, the SMC assumes it'll be the only I2C bus master; if anything else tries hijacking the I2C bus
(e.g. RGH2 glitch chips), then conflicts will happen and you'll get random SMC problems, usually because
the SMC will try reading the thermal sensors but will either be blocked off or read back random results.

## I2C address map

- 0x69 (Xenon only): Clock generator
- 0x70: ANA/HANA on all XSB and PSB boards, KSB on Corona and Winchester (TBD)

Other things like the voltage regulators live on the I2C bus as well

