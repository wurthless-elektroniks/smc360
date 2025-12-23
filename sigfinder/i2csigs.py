import sys
import struct
from signature import SignatureBuilder,WILDCARD
from util import get16

I2C_COMMAND_EXEC_WITH_THREE_RETRIES_SIGNATURE = SignatureBuilder() \
    .pattern([
        0x75, WILDCARD, 0x03,
        0x85, WILDCARD, WILDCARD,
        0x80, WILDCARD,
    ]) \
    .build()

def _ident_3tries_labels(signature_offset: int, progbytes: bytes):
    return {
        "g_i2c_retry_count": progbytes[signature_offset+1],
        "g_i2c_command_current_pointer": progbytes[signature_offset+4],
        "g_i2c_command_start_pointer":   progbytes[signature_offset+5],
    }

I2C_COMMAND_STEP_SIGNATURE = SignatureBuilder() \
    .pattern([
        0x90, WILDCARD, WILDCARD,  # MOV        DPTR,#i2c_message_table
        0xe5, WILDCARD,            # MOV        A,g_i2c_command_current_pointer
        0x93,                      # MOVC       A,@A+DPTR=>i2c_message_table
        0x90, WILDCARD, WILDCARD,  # MOV        DPTR,#LAB_CODE_28d9
        0x73                       # JMP        @A+DPTR
    ]) \
    .build()

def _ident_commandstep_labels(signature_offset: int, progbytes: bytes):
    return {
        "i2c_message_table": get16(signature_offset+1, progbytes),
        "g_i2c_command_current_pointer": progbytes[4],
        "i2c_bytecode_handler_jumptable": get16(signature_offset+7, progbytes)
    }
