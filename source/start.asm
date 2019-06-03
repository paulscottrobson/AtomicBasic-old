; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		start.asm
;		Purpose : 	Test bed for BASIC
;		Date :		3rd June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

	* = 0
	clc												; switch into 65816 16 bit mode.
	xce	
	rep 	#$30 									
	.al	
	.xl
	ldx 	#$FFF0 									; 6502 stack at $FFE0
	txs
	lda 	#$FE00 									; set DP to $FE00
	tcd
	lda 	#CodeSpace >> 16 						; put the page number in A ($2)
	ldx 	#CodeSpace & $FFFF 						; and the base address in X ($4000)
	ldy 	#CodeEndSpace & $FFFF					; and the end address in Y ($C000)
	jmp 	SwitchBasicInstance

	* = $10000
	.include "basic.asm"

	*=$24000 										; actual code goes here, demo at 02-4000
CodeSpace:
	.binary "temp/basic.bin"
CodeEndSpace:
