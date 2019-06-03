; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		arithmetic.asm
;		Purpose : 	Simple binary operators 
;		Date :		3rd June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;										32 bit Add
;
; *******************************************************************************************

Binary_Add: ;; + 
	clc
	lda		EXSValueL+0,x
	adc 	EXSValueL+2,x
	sta 	EXSValueL+0,x
	lda		EXSValueH+0,x
	adc 	EXSValueH+2,x
	sta 	EXSValueH+0,x
	rts

; *******************************************************************************************
;
;											 32 bit subtract
;
; *******************************************************************************************

Binary_Subtract: ;; - 
	sec
	lda		EXSValueL+0,x
	sbc 	EXSValueL+2,x
	sta 	EXSValueL+0,x
	lda		EXSValueH+0,x
	sbc 	EXSValueH+2,x
	sta 	EXSValueH+0,x
	rts

; *******************************************************************************************
;
;									Logical shift right
;
; *******************************************************************************************

Binary_ShiftRight: ;; >>
	lda 	EXSValueL+2,x
	and 	#63
	beq		_Binary_SRExit
_Binary_SRLoop:
	lsr 	EXSValueH+0,x
	ror 	EXSValueL+0,x
	dec 	a
	bne 	_Binary_SRLoop
_Binary_SRExit:
	rts

; *******************************************************************************************
;
;									Logical shift left
;
; *******************************************************************************************

Binary_ShiftLeft: ;; << 
	lda 	EXSValueL+2,x
	and 	#63
	beq		_Binary_SLExit
_Binary_SLLoop:
	asl 	EXSValueL+0,x
	rol 	EXSValueH+0,x
	dec 	a
	bne 	_Binary_SLLoop
_Binary_SLExit:
	rts
