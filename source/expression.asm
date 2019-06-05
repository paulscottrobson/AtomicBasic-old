; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		expression.asm
;		Purpose : 	Expression Evaluation
;		Date :		3rd June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;										Base Evaluate.
;
;		Evaluate expression at (DCodePtr), returning value in YA.
;
;		When calling from a non-base, e.g. inside a unary function, use EvaluateNext
;		function.
;
; *******************************************************************************************

Evaluate:
		ldx 	#EXSBase					; reset the stack base
		lda 	#0<<10 						; current precedence level.
											; fall through.

; *******************************************************************************************
;
;		Evaluate a term/operator sequence at the current precedence level. A contains the
;		precedence level shifted 10 left (matching the keyword position). X contains the 
;		expression stack offset.
;
;		Returns value in YA.
;
;		Precedence climber : See expression.py in documents
;
; *******************************************************************************************

EvaluateLevel:
		sta 	EXSPrecedence+0,x 				; save precedence level, also sets type to integer.
		;
		;		Get the next token, used for # which is ignored.
		;
_ELGetNext:
		lda 	(DCodePtr)						; look at the next token
		beq 	_ELExpressionSyntax 			; EOL token, there's an error.
		bmi 	_ELConstant 					; if 8000-FFFF 15 bit constant.

		cmp 	#$1000 							; string constant ? 00xx
		bcc 	_ELStringConstant
		cmp 	#$2000 							; constant shift ? 1xxx
		bcc 	_ELConstantShift				
		bcs 	_ELKeywordFunction 				; must be 2000-7FFF e.g. identifier or keyword.
;
;		Branch to syntax error (expression missing)
;
_ELExpressionSyntax:	
		jmp 	SyntaxError
;
;		0000 0000 llll llll String constant.
;
_ELStringConstant:
		lda 	DCodePtr 						; get the address of the token
		inc 	a 								; adding 2, start of the string in memory.
		inc 	a 	
		sta 	EXSValueL+0,x 					; the LSB of the string.
		lda 	DPageNumber 					
		sta 	EXSValueH+0,x 					; the MSB is the current page number.
		;
		clc
		lda 	(DCodePtr) 						; add length to pointer to skip over
		adc 	DCodePtr 						; the string data. 
		sta 	DCodePtr
		bra 	_ELGotAtom
;
;		0001 cccc cccc cccc Constant shift - provides bit 15-26 of integer constants
;
_ELConstantShift:
		sta 	DConstantShift 					; update constant shift
		inc 	DCodePtr 						; shift over constant shift
		inc 	DCodePtr 						; fall through to constant code.
;
;		1ccc cccc cccc cccc Constant Integer (with shift, which is reset afterwards)
;
_ELConstant:
		lda 	(DCodePtr)						; get the token (for fall through)
		asl 	a 								; shift left, also gets rid of the high bit
		sta 	EXSValueL+0,x 					; this is the low word , currently doubled.
		;
		lda 	DConstantShift 					; get the constant shift
		and 	#$0FFF 							; mask off bits 12-15 giving the shift data
		lsr 	a 								; rotate bit 0 of the shift into carry
		sta 	EXSValueH+0,x 					; this is the high word
		ror 	EXSValueL+0,x 					; rotate carry into the low word, undoes the doubling.
		;
		stz 	DConstantShift 					; reset the constant shift to zero.
		inc 	DCodePtr 						; skip over code pointer
		inc 	DCodePtr
;
;		Have the atom. Now we look to see if a binary token follows it, and if so is it of
;		a suitable precedence.
;
_ELGotAtom:
		lda 	(DCodePtr)						; get the next token.
		tay 									; save in Y, temporarily.
		and 	#$F000 							; is it a binary operator keyword, 010x xxxx xxxx xxxx
		cmp 	#$4000
		bne 	_ELExit 						; not a binary operator, exit.

		tya 									; get token back from Y
		and 	#15<<10 						; mask out the precedence data.
		cmp 	EXSPrecedence,x					; compare against current level
		bcc 	_ELExit 						; if too low, then exit back.
		phy 									; save operator token on stack.
		inc 	DCodePtr 						; skip over it in memory.
		inc 	DCodePtr

		clc 									; precedence data still in A, add 1 level to it
		adc 	#1<<10							
		inx 									; calculate the RHS at the next stack level.
		inx
		jsr 	EvaluateLevel 
		dex
		dex
		pla 									; get the binary operator back
;
;		Call the keyword in A. We use the lower 9 bits as an index into the vector table. Note that
;		this uses self modifying code. This section is not ROMmable.
;		
_ELExecuteA:		
		and 	#$01FF 							; keyword ID.
		asl 	a 								; double it as keyword vector table is word data
		txy 									; save X in Y
		tax 									; double keyword ID in X
		lda 	CommandJumpTable,x 				; this is the vector address
		tyx 									; restore X.
		sta 	_ELCallRoutine+1 				; Self modifying, will not work in ROM.
_ELCallRoutine:
		jsr 	_ELCallRoutine 					; this address here is overwritten with the keyword address
		bra 	_ELGotAtom 						; go round operator level again.
;
;		Exit - put value in YA.
;
_ELExit:
		lda 	EXSValueL+0,x 					; put value in YA
		ldy 	EXSValueH+0,x
		rts
;
;		Code to handle non-constant atoms : - # ( ! ? and Unary Functions 001xx and Identifiers 01xx
;
_ELKeywordFunction:
		cmp 	#$4000 							; identifier (e.g. variable) if in range $2000-$3FFF
		bcc 	_ELVariable 					; (we've already discounted 8000-FFFF)
		;
		;		Special case keywords
		;
		cmp 	#minusTokenID 					; -<atom> unary negate
		beq 	_ELMinusAtom
		cmp 	#lparenTokenID 					; (<expression>) parenthesis
		beq 	_ELParenthesis
		cmp 	#questionTokenID 				; ?<atom> byte indirection
		beq 	_ELByteIndirection
		cmp 	#plingTokenID 					; !<atom> word indirection
		beq 	_ELWordIndirection
		cmp 	#hashTokenID 					; # is ignored, it is an instruction to the detokeniser
		beq 	_ELIgnoreToken

		tay 									; save token in Y
		and 	#$FC00 							; look for 0111 01xx ? i.e. a unary function.
		cmp 	#$7400 							; if it isn't then exit
		bne 	_ELExit
;
;		Handle Unary Function. We just call the routine, so skip the token and go back to the keyword execute
;		code.
;
_ELUnaryFunction:
		inc 	DCodePtr 						; skip over the unary function token
		inc 	DCodePtr
		tya 									; get token back
		bra 	_ELExecuteA 					; and execute it.
;
;		Ignore the token and loop back. Used for '#' which is an instruction to the detokeniser
;		to output the next constant in hexadecimal.
;	
_ELIgnoreToken:
		inc 	DCodePtr 						; skip over the token to ignore
		inc 	DCodePtr
		brl 	_ELGetNext 						
;
;		Handle variable (sequence of identifier tokens)
;
_ELVariable:
		nop
		nop
		nop
		bra 	_ELGotAtom
;
;		Handle (Parenthesis)
;
_ELParenthesis:
		inc 	DCodePtr 						; skip over the ( token
		inc 	DCodePtr
		jsr 	EvaluateNext 					; calculate the value in parenthesis, using next space on the stack.
		lda 	#rparenTokenID 					; check for ) which should close the parenthesised expression.
		jsr 	CheckNextToken		
		lda 	EXSValueL+2,x 					; copy the value in directly from level 2 to level 0.
		sta 	EXSValueL+0,x
		lda 	EXSValueH+2,x
		sta 	EXSValueH+0,x
		brl 	_ELGotAtom 						; and go round looking for the next binary operator
;
;		Handle -<atom>
;
_ELMinusAtom:
		inc 	DCodePtr 						; skip over the - token
		inc 	DCodePtr
		jsr 	EvaluateNextAtom 				; get the atom value to negate
		sec 									; do the subtraction 0-atom value
		lda 	#0
		sbc 	EXSValueL+2,x
		sta 	EXSValueL+0,x
		lda 	#0
		sbc 	EXSValueH+2,x
		sta 	EXSValueH+0,x
		brl 	_ELGotAtom
;
;		Handle ?<atom> byte indirection
;
_ELByteIndirection:
		inc 	DCodePtr 						; skip over the - token
		inc 	DCodePtr
		jsr 	EvaluateNextAtom 				; address to read.
		sta 	DTemp1+0 						; save address to indirect over.
		sty 	DTemp1+2
		lda 	[DTemp1] 						; read the word there as a byte.
		and 	#$00FF 							; make a byte out of it.
		sta 	EXSValueL+0,x 					; write it to the stack
		stz 	EXSValueH+0,x 					; zero the top word.
		brl 	_ELGotAtom
;
;		Handle !<atom> word indirection
;
_ELWordIndirection:
		inc 	DCodePtr 						; skip over the - token
		inc 	DCodePtr
		jsr 	EvaluateNextAtom 				; address to read.
		sta 	DTemp1+0 						; save address to indirect over.
		sty 	DTemp1+2
		lda 	[DTemp1] 						; read the word there
		sta 	EXSValueL+0,x 					; write it back
		ldy 	#2 								; read the high word.
		lda 	[DTemp1],y
		sta 	EXSValueH+0,x
		brl 	_ELGotAtom

; *******************************************************************************************
;
;		Calculate a result at the next stack level. This is used when expression evaluation
;		is required within expression evaluation, e.g. unary functions, parenthesis, negation
;		and so on. The value is in YA, or ESXValue?+2,x
;
; *******************************************************************************************

EvaluateNext:
		inx 									; stack forward
		inx
		lda 	#0<<10 							; lowest precedence.
		jsr 	EvaluateLevel 					; do at next level
		dex 									; reset stack
		dex
		rts

; *******************************************************************************************
;
;			As EvaluateNext, but gets an Atomic value, not a full expression.
;
; *******************************************************************************************

EvaluateNextAtom:
		inx 									; make space
		inx
		lda 	#8<<10 							; means binary operation will be impossible.
		jsr 	EvaluateLevel
		dex
		dex
		rts
