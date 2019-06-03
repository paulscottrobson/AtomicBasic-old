; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		simpleunary.asm
;		Purpose : 	Simple unary functions.
;		Date :		3rd July 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									abs s => absolute value
;
; *******************************************************************************************

Function_Abs: ;; abs( 
		jsr 	EvaluateNext 				; get the value you are absoluting
		lda 	#RParenTokenID 				; check )
		jsr 	CheckNextToken
		lda 	EXSValueH+2,x 				; get sign of result from the upper word.
		bmi 	_FAbsNegative 				; negate it if negative
		sta 	EXSValueH+0,x 				; otherwise just copy it.
		lda 	EXSValueL+2,x
		sta 	EXSValueL+0,x
		rts		
_FAbsNegative:
		sec 								; copy 0 - 2nd stack => 1st stack.
		lda 	#0
		sbc 	EXSValueL+2,x
		sta 	EXSValueL+0,x		
		lda 	#0
		sbc 	EXSValueH+2,x
		sta 	EXSValueH+0,x		
		rts

; *******************************************************************************************
;
;										sign of number
;
; *******************************************************************************************

Function_Sgn: ;; sgn( 
		jsr 	EvaluateNext 				; get an integer
		lda 	#RParenTokenID 				; check )
		jsr 	CheckNextToken
		stz 	EXSValueL+0,x 				; zero the result
		stz 	EXSValueH+0,x
		lda 	EXSValueH+2,x 				; get sign of result from high bit of upper wod.
		bmi 	_FSgnNegative 				; set to -1 if signed
		ora 	EXSValueL+2,x 				; exit if zero as we already reset it.
		beq 	_FSgnExit
		;
		inc 	EXSValueL+0,x 				; > 0 so make result 1 if positive and non-zero
_FSgnExit:		
		rts
		;
_FSgnNegative:
		lda 	#$FFFF 						; set the return value to -1 as negative.
		sta 	EXSValueL+0,x		
		sta 	EXSValueH+0,x		
		rts

; *******************************************************************************************
;
;										random integer
;
;										 (Galois LFSR)
; *******************************************************************************************

Function_Random: ;; rnd()
		lda 	DRandom 					; check for non-zero 
		ora 	DRandom+2 					; they don't like these :)
		bne 	_Rnd_NotZero
		lda 	#$B7 						; initialise it to the same value. 
		sta 	DRandom 
		lda 	#$D5
		sta 	DRandom+2
_Rnd_NotZero:
		jsr 	_Rnd_Process 				; call randomiser twice
		sta 	EXSValueH+0,x
		jsr 	_Rnd_Process
		sta 	EXSValueL+0,x
		rts

_Rnd_Process:
		asl 	DRandom 					; shift right, exit 
		rol 	DRandom+2
		bcc 	_Rnd_Exit

		lda 	DRandom 					; taps effectively
		eor 	#$D454
		sta 	DRandom
		lda 	DRandom+2
		eor 	#$55D5
		sta 	DRandom+2
_Rnd_Exit:		
		lda 	DRandom
		eor 	DRandom+2
		rts
