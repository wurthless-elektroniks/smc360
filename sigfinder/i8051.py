import struct

def i8051_decode_sjmp_target(opcode_offset: int, opcode_bytes: bytes) -> int:
    rel_address = struct.unpack(">b", opcode_bytes[1])
    return (opcode_offset + 2) + rel_address

def i8051_try_find_sjmps(target_offset: int, progbytes: bytes) -> list:
    candidates = []
    for i in range(-0x82, 0x82):
        if progbytes[target_offset + i] == 0x80 and \
            i8051_decode_sjmp_target(target_offset + i, progbytes[target_offset + i:target_offset + i + 2]) == target_offset:
            candidates.append(target_offset + i)
    return candidates
