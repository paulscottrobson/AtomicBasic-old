; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		comparison.asm
;		Purpose : 	Comparison operators (integer and string)
;		Date :		3rd June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;										Equality
;
; *******************************************************************************************

Binary_Equals: ;; = 
	lda 	EXSValueL,x 					; numeric comparison
	cmp 	EXSValueL+2,x
	bne 	Compare_Fail
	lda 	EXSValueH,x
	cmp 	EXSValueH+2,x
	bne 	Compare_Fail
	bra 	Compare_Succeed

; *******************************************************************************************
;
;										InEquality
;
; *******************************************************************************************

Binary_NotEquals: ;; <> 
	lda 	EXSValueL,x 					; numeric comparison
	cmp 	EXSValueL+2,x
	bne 	Compare_Succeed
	lda 	EXSValueH,x
	cmp 	EXSValueH+2,x
	bne 	Compare_Succeed
	bra 	Compare_Fail

; *******************************************************************************************
;
;										Less
;
; *******************************************************************************************

Binary_Less: ;; < 	
	sec
	lda 	EXSValueL,x 					; signed numeric <
	sbc 	EXSValueL+2,x
	lda 	EXSValueH,x
	sbc 	EXSValueH+2,x
	bvc 	*+5
	eor 	#$8000
	bmi 	Compare_Succeed
	bra 	Compare_Fail

; *******************************************************************************************
;
;									Return true or false
;
; *******************************************************************************************

Compare_Succeed:
	lda 	#$FFFF
	sta 	EXSValueL,x
	sta 	EXSValueH,x
	rts
Compare_Fail:
	stz 	EXSValueL,x
	stz 	EXSValueH,x
	rts

; *******************************************************************************************
;
;									Greater/Equals
;
; *******************************************************************************************

Binary_GreaterEqual: ;; >= 
	sec
	lda 	EXSValueL,x 					; numeric >= signed
	sbc 	EXSValueL+2,x
	lda 	EXSValueH,x
	sbc 	EXSValueH+2,x
	bvc 	*+5
	eor 	#$8000
	bpl 	Compare_Succeed
	bra 	Compare_Fail

; *******************************************************************************************
;
;									  Less/Equals
;
; *******************************************************************************************

Binary_LessEqual: ;; <= 	
	clc 									; numeric <= signed
	lda 	EXSValueL,x
	sbc 	EXSValueL+2,x
	lda 	EXSValueH,x
	sbc 	EXSValueH+2,x
	bvc 	*+5
	eor 	#$8000
	bmi 	Compare_Succeed
	bra 	Compare_Fail

; *******************************************************************************************
;
;									  Greater
;
; *******************************************************************************************

Binary_Greater: ;; > 
	clc 									; numeric > signed
	lda 	EXSValueL,x
	sbc 	EXSValueL+2,x
	lda 	EXSValueH,x
	sbc 	EXSValueH+2,x
	bvc 	*+5
	eor 	#$8000
	bpl 	Compare_Succeed
	bra 	Compare_Fail

_BGString: 									; string
	cmp 	#$0001
	beq 	Compare_Succeed
	bra 	Compare_Fail

