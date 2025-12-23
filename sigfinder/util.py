import struct

def get16(offset: int, progbytes: bytes) -> int:
    return struct.unpack(">H", progbytes[offset:offset+2])[0]
