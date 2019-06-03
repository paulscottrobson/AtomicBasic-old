; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		multiply.asm
;		Purpose : 	32 bit Multiply
;		Date :		3rd June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									32 bit multiply
;
; *******************************************************************************************

Binary_Multiply: ;; * 
	lda 	EXSValueL+0,x 						; multiplier to DTemp1, multiplicand in Value+2
	sta 	DTemp1
	lda 	EXSValueH+0,x
	sta		DTemp1+2
	stz 	EXSValueL+0,x						; zero result
	stz 	EXSValueH+0,x
_BinaryMultiply_Loop:
	lda 	DTemp1 								; multiplier zero then exit
	ora 	DTemp1+2
	beq 	_BinaryMultiply_Exit
	lda 	DTemp1 								; check bit 0 of multiplier
	and 	#1
	beq 	_BinaryMultiply_NoAdd

	clc 										; add multiplicand to result.
	lda 	EXSValueL+0,x
	adc 	EXSValueL+2,x
	sta 	EXSValueL+0,x
	lda 	EXSValueH+0,x
	adc 	EXSValueH+2,x
	sta 	EXSValueH+0,x

_BinaryMultiply_NoAdd:
	lsr 	DTemp1+2 							; halve multiplier
	ror 	DTemp1
	asl 	EXSValueL+2,x 						; double multiplicand
	rol 	EXSValueH+2,x
	bra 	_BinaryMultiply_Loop 				; go round again.

_BinaryMultiply_Exit:
	rts
