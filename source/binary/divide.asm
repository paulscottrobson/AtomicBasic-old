; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		divide.asm
;		Purpose : 	32 bit Divide (and Modulus)
;		Date :		3rd June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									32 bit divide
;
;				(there is a python version in the documentation directory)
; *******************************************************************************************

Binary_Divide: ;; / 
	lda 	EXSValueL+2,x						; check for division by zero
	ora	 	EXSValueH+2,x
	bne 	_BinaryDivide_Ok
	jsr 	ReportError							; error if so.
	.text	"Division by zero",$00

_BinaryDivide_Ok:
	stz 	DTemp1+0							; clear remainder (DTemp)
	stz 	DTemp1+2
	stz 	DSignCount  						; zero sign count.

	phy 										; save Y (bit counter)

	lda 	EXSValueH+2,x 						; check sign of H+2 (right)
	bpl 	_BinaryDivide_RightDone
	inx 
	inx
	jsr 	Binary_DivNegate 					
	dex
	dex
_BinaryDivide_RightDone:

	lda 	EXSValueH+0,x 				 		; check sign of H+0 (left)
	bpl 	_BinaryDivide_LeftDone
	jsr 	Binary_DivNegate 					
_BinaryDivide_LeftDone:

	ldy 	#32 								; number to do.
_BinaryDivide_Loop:
	asl 	EXSValueL+0,x 						; shift Q into carry
	rol 	EXSValueH+0,x

	rol 	DTemp1+0 							; rotate A left, with carry in
	rol 	DTemp1+2

	sec											; calculate A-M
	lda 	DTemp1+0 							; but don't save it.
	sbc 	EXSValueL+2,x
	sta 	DTemp2
	lda 	DTemp1+2
	sbc 	EXSValueH+2,x

	bcc 	_Binary_NoSubract 					; if A < M skip this

	sta 	DTemp1+2 							; save the calculated value.
	lda 	DTemp2
	sta 	DTemp1+0
	inc 	EXSValueL+0,x						; set bit 0 of Q

_Binary_NoSubract:
	dey 										; do it 32 times.
	bne 	_BinaryDivide_Loop

_BinaryDivide_Exit:
	lda 	DSignCount 							; restore sign
	and 	#1
	beq 	_BinaryDivide_Exit2
	jsr 	Binary_DivNegate
_BinaryDivide_Exit2:	
	ply 										; restore Y
	rts	

;
;		Negate value at X, and increment the sign count.
;
Binary_DivNegate:
	inc 	DSignCount 							; increment the count of signs.
	sec 										; negate the value at stack X.
	lda 	#$0000
	sbc 	EXSValueL+0,x 
	sta 	EXSValueL+0,x
	lda 	#$0000
	sbc 	EXSValueH+0,x
	sta 	EXSValueH+0,x
	rts

; *******************************************************************************************
;
;									32 bit modulus
;
; *******************************************************************************************

Binary_Modulus: ;; %
	jsr 	Binary_Divide 						; do the divide
	lda 	DTemp1+0 							; copy modulus into data area.
	sta 	EXSValueL+0,x
	lda 	DTemp1+2
	sta 	EXSValueH+0,x
	rts
