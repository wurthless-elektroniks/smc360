'''
Same signature finder code as modern loadfare (and a N64 project before that),
shit's really getting tired... need to make this a generic library
'''

from abc import ABCMeta
import struct
import logging

logger = logging.getLogger(__name__)
WILDCARD = -666

def _pattern_to_bits_and_andmask(pattern: list) -> tuple:
    bits    = bytearray(len(pattern))
    andmask = bytearray(len(pattern))
    for i,val in enumerate(pattern):
        if val == WILDCARD:
            bits[i]    = 0x00
            andmask[i] = 0x00
        elif 0 <= val <= 0xFF:
            bits[i]  = val
            andmask[i] = 0xFF
        else:
            raise RuntimeError(f"illegal hex value in pattern: {val:x}")
    return ( bits, andmask )

def _compare_buffer(data: bytearray, offset: int, bits: bytes, andmask: bytes) -> bool:
    data_length = len(data)
    left_finger = 0
    right_finger = len(bits) - 1

    while left_finger <= right_finger:
        # prevent out-of-bounds
        if (offset + left_finger) >= data_length or (offset + right_finger) >= data_length:
            return False

        if (data[offset+left_finger] & andmask[left_finger]) != \
            (bits[left_finger] & andmask[left_finger]):
            return False
        
        if (data[offset+right_finger] & andmask[right_finger]) != \
            (bits[right_finger] & andmask[right_finger]):
            return False
        
        left_finger += 1
        right_finger -= 1
    return True

# -----------------------------------------------------------------------------

class Signature():
    '''
    Implements a Signature. Do not instantiate this directly, use the SignatureBuilder.
    '''
    def __init__(self):
        self._name = None
        self._meta = {}
        self._bits = None
        self._andmask = None
        self._tail_bits = None
        self._tail_andmask = None
        self._size = 0
        self._unresolved_xrefs = []
        self._unresolved_consts = []

    def meta(self, key: str) -> str | None:
        '''
        Return specific metadata item by key, or None if no such key exists.
        '''
        if key not in self._meta:
            return None
        return self._meta[key]
    
    def meta_items(self):
        '''
        Return dict_items of internal meta dict.
        '''
        return self._meta.items()

    def compare(self, data: bytearray, offset: int = 0) -> bool:
        '''
        Compare signature to given data buffer.
        '''
        pattern_matches = _compare_buffer(data, offset, self._bits, self._andmask)
        if pattern_matches is False or self._tail_bits is None:
            return pattern_matches

        return _compare_buffer(data,
                               offset + (self._size - len(self._tail_bits)),
                               self._tail_bits,
                               self._tail_andmask)
    
    def dump_unresolved_xrefs(self):
        pass

    def xrefs(self, segment_base: int, data: bytearray, offset: int = 0) -> dict:
        '''
        Using this signature, generate dict of xrefs pointing symbol_name -> resolvedxref.
        Returns None if signature didn't match.
        '''
        if self.compare(data, offset) is False:
            return None

        resolutions = {}

        return resolutions
    
    def dump_unresolved_consts(self):
        pass

    def consts(self, segment_base: int, data: bytearray, offset: int = 0) -> dict:
        '''
        Using this signature, generate dict of consts pointing symbol_name -> resolvedconst.
        Returns None if signature didn't match.
        '''
        if self.compare(data, offset) is False:
            return None

        resolutions = {}

        return resolutions

    def find(self, data: bytearray, offset: int = 0, align32: bool = False) -> None | int:
        '''
        Find match within given data buffer.
        Return offset within the array, or None if not found.
        '''
        step = 4 if align32 is True else 1
        data_len = len(data)
        while offset < data_len:
            if (offset + self._size) >= data_len:
                break
            if self.compare(data, offset) is True:
                return offset
            offset += step
        return None
    
    def bits(self):
        return bytes(self._bits)
    
    def andmask(self):
        return bytes(self._andmask)
    
    def tail_bits(self) -> bytes | None:
        if self._tail_bits is None:
            return None
        return bytes(self._bits)
    
    def tail_andmask(self):
        if self._tail_andmask is None:
            return None
        return bytes(self._andmask)
    
    def size(self):
        return self._size

class SignatureBuilder():
    '''
    Implements a SignatureBuilder.
    '''
    def __init__(self):
        self._bits = None
        self._andmask = None
        self._tail_bits = None
        self._tail_andmask = None
        
        self._name = None
        self._size = None
        self._meta = {}
        self._unresolved_xrefs = []
        self._unresolved_consts = []

    # pylint:disable=protected-access
    def build(self) -> Signature:
        '''
        Build and return a `Signature` object.
        '''
        if self._bits is None or self._andmask is None:
            raise RuntimeError("bits / andmask not specified")

        if len(self._bits) != len(self._andmask):
            raise RuntimeError("bits and andmask must be the same length")

        sig = Signature()
        sig._bits    = self._bits
        sig._andmask = self._andmask

        if (self._tail_andmask is not None and self._tail_bits is not None):
            if len(self._tail_andmask) != len(self._tail_bits):
                raise RuntimeError("tail_bits and tail_andmask must be the same length")

            if self._size is not None and len(self._tail_bits) + len(self._bits) > self._size:
                raise RuntimeError(f"size of bits and tail_bits exceeds total signature size (expected {self._size}, got {len(self._tail_bits) + len(self._bits)})")

            sig._tail_andmask = self._tail_andmask
            sig._tail_bits = self._tail_bits
        elif (self._tail_andmask is not None or self._tail_bits is not None):
            raise RuntimeError("one of tail_bits/tail_andmask not specified (both or neither must be specified)")

        sig._name = self._name
        sig._size = self._size if self._size is not None else len(sig._bits) + (0 if sig._tail_bits is None else len(sig._tail_bits))
        sig._meta = self._meta
        sig._unresolved_xrefs  = self._unresolved_xrefs
        sig._unresolved_consts = self._unresolved_consts
        return sig

    def name(self, name: str):
        self._name = name
        return self
    
    def meta(self, key: str, value: any):
        self._meta[key] = value
        return self

    def size(self, sizeof: int):
        '''
        Sets size of the function (NOT the signature itself).
        '''
        self._size = sizeof
        return self
    
    def bits(self, bitpattern: bytes):
        '''
        Set bitpattern.
        '''
        self._bits = bitpattern
        return self
    
    def modify_andmask(self, offset: int, patchedmask: bytes):
        self._andmask[offset:offset+len(patchedmask)] = patchedmask
        return self

    def andmask(self, andmask: bytes):
        '''
        Set AND mask.
        '''
        self._andmask = andmask
        return self
    
    def tail_bits(self, bitpattern: bytes):
        self._tail_bits = bitpattern
        return self
    
    def tail_andmask(self, andmask: bytes):
        self._tail_andmask = andmask
        return self

    def pattern(self, pattern: list):
        '''
        Set pattern.

        This does not control AND masking at the bit level; for that, use `bits()` and `andmask()`.
        '''
        parsed = _pattern_to_bits_and_andmask(pattern)
        return self.bits(parsed[0]).andmask(parsed[1])

    def tail_pattern(self, tail_pattern: list):
        parsed = _pattern_to_bits_and_andmask(tail_pattern)
        return self.tail_bits(parsed[0]).tail_andmask(parsed[1])

def bulk_find(sigdict: dict, buffer: bytes):
    resolved = {}
    for name, signature in sigdict.items():
        resolved[name] = signature.find(buffer)
    return resolved

def check_bulk_find_results(resolved_sigs: dict) -> bool:
    any_none = False
    for name, offset in resolved_sigs.items():
        if offset is not None:
            print(f"{name} = 0x{offset:04x}")
        else:
            print(f"{name} = NOT FOUND")
            any_none = True

    return any_none

def find_all_instances(buffer: bytes, signature: Signature, align32: bool = False) -> list:
    matches = []
    offset = 0
    while True:
        offset = signature.find(buffer, offset, align32=align32)
        if offset is None:
            return matches
        matches.append(offset)
        offset += signature.size()
