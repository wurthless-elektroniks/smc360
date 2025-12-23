from signature import SignatureBuilder,WILDCARD

IPC_OUTBOX_WRITE_DATA_SIGNATURE = SignatureBuilder() \
    .pattern([
        0xf5, 0xd5,
        0x22
    ]) \
    .build()

IPC_OUTBOX_LOCK_AND_SET_POINTER_SIGNATURE = SignatureBuilder() \
    .pattern([
        0xd2, 0xe4,
        0xf5, 0xd6,
        0x22
    ]) \
    .build()

IPC_OUTBOX_RELEASE_SIGNATURE = SignatureBuilder() \
    .pattern([
        0x75, 0xd6, 0x00,
        0x22
    ]) \
    .build()

IPC_INBOX_GET_MESSAGE_TYPE_SIGNATURE = SignatureBuilder() \
    .pattern([
        0x75, 0xe0, 0x00,
        0xd2, 0xe4,
        0xf5, 0xe2,
        0xe5, 0xe1,
        0xa2, 0xe7,
        0x22,
    ]) \
    .build()
