

	* = 0	
	nop
	clc
	xce	
	rep 	#$30
	.al	
	.xl
	ldy 	#0000
	ldx 	#$CDEF
	lda 	#$1234
	inc 	
loop:
	clc
	adc		#$1001
	jsr 	doit
	bra 	loop


doit:
	rts
	