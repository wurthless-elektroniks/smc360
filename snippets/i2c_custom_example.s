;
; I2C custom bytecode example
; Patches are based on Corona SMC
;
; This will NOT assemble as is!!
;


; ------------------------------------------------------------------------------------
;
; Patchlist
;
; ------------------------------------------------------------------------------------
    .org 0x0000
    
    ; ... most base patches omitted ...

    ; there are some functions after the commandlist table that
    ; will be trashed by custom code, so we have to relocate them
    mov dptr,#lab_2a05_move_patches_start
    mov dptr,#lab_2a05_move_patches_end
    
    ; mov dptr,#i2c_slowdown_by_default_patch_start
    ; mov dptr,#i2c_slowdown_by_default_patch_end 

    ; drop custom I2C bytecode into the commandlist table
    mov dptr,#i2c_command_table_patches_start
    mov dptr,#i2c_command_table_patches_end

    ; more functions to be relocated
    mov dptr,#fcn_2e97_move_patches_start
    mov dptr,#fcn_2e97_move_patches_end

    ; hacked code lives here
    mov dptr,#main_code_segment_start
    mov dptr,#main_code_segment_end

    .byte 0 ; end of list

; ------------------------------------------------------------------------------------
;
; Patches
;
; ------------------------------------------------------------------------------------

    .org 0x2A05
lab_2a05_move_patches_start:
    lcall fcn_2e59
    lcall 0x31CF
    lcall fcn_2e63
lab_2a05_move_patches_end:

    ; the commandlist pointers are offsets of this address
    ; so we need this here to calculate those offsets at assembly time
    .org 0x2D66
i2c_command_table_start:


    .org 0x2E49
i2c_command_table_patches_start:

i2c_command_table_slowdown:
    .byte 0x00                       ; init I2C bus
    .byte 0x0E                       ; send I2C command to clock synthesizer
    .byte 0xDB                       ; clock select register
    .byte 0x01, 0xF0, 0x01, 0xF8     ; switch to 25 MHz bypass mode
    .byte 0x03                       ; done

i2c_command_table_speedup:
    .byte 0x00                       ; init I2C bus
    .byte 0x0E                       ; send I2C command to clock synthesizer
    .byte 0xDB                       ; clock select register
    .byte 0x01, 0xF0, 0x01, 0xF0     ; go full speed
    .byte 0x03                       ; done

i2c_command_table_patches_end:

    .org 0x2E9A
fcn_2e97_move_patches_start:
    lcall fcn_2e49
    lcall 0x31CF
    lcall fcn_2e53
fcn_2e97_move_patches_end:

; ------------------------------------------------------------------------------------
;
; Custom code follows
;
; ------------------------------------------------------------------------------------

    .org 0x3200
main_code_segment_start:


;
; I2C-related functions that had to be moved because we patched commands into the I2C command table
;
fcn_2e49:
    jb 02Eh.5,_fcn_2e49_alt_case
    clr 0C8h
    ret
_fcn_2e49_alt_case:
    anl 0FCh,#0xFE
    ret

fcn_2e53:
    setb 0C8h
    orl 0FCh,#1
    ret

fcn_2e59:
    jb 02Eh.5,_fcn_2e59_alt_case
    clr 0C9h
    ret
_fcn_2e59_alt_case:
    anl 0FCh,#0xFD
    ret

fcn_2e63:
    setb 0C9h
    orl 0FCh,#2
    ret

    ; ... place your l33t haxxx code here ...

;
; How you start your custom I2C commands is up to you.
; The typical way to do it will be in a function that basically does:
;
;   mov g_i2c_interpreter_initial_pc,#(i2c_command_table_slowdown-i2c_command_table_start)
;   lcall 0x2999 ; starts interpreter with 3 retries
;   jb F0,_my_fancy_failure_case_handler
;   mov r0,g_i2c_sm_state
;   mov @r0,#4
;
; Good luck and have fun.
;


main_code_segment_end:
    .end
