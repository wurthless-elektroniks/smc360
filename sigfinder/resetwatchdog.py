from signature import SignatureBuilder

DEFAULT_TIMEOUT_PRE_JASPER = 0xAF
DEFAULT_TIMEOUT_POST_JASPER = 0x82

RESET_WATCHDOG_RELOAD_TIMEOUT_PRE_JASPER_SIGNATURE = SignatureBuilder() \
    .bits([
        0x75, 0x30, DEFAULT_TIMEOUT_PRE_JASPER,
    ]) \
    .andmask([
        0xFF, 0xF0, 0xFF
    ]) \
    .build()

RESET_WATCHDOG_RELOAD_TIMEOUT_POST_JASPER_SIGNATURE = SignatureBuilder() \
    .bits([
        0x75, 0x30, DEFAULT_TIMEOUT_POST_JASPER,
    ]) \
    .andmask([
        0xFF, 0xF0, 0xFF
    ]) \
    .build()
