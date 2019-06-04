; *******************************************************************************************
; *******************************************************************************************
;
;		Name : 		utility.asm
;		Purpose : 	General Utility functions
;		Date :		4th June 2019
;		Author : 	paul@robsons.org.uk
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;				Default handler for keywords, produces error if not implemented
;
; *******************************************************************************************

IllegalToken:
		jsr 	ReportError
		.text 	"Bad token",0

; *******************************************************************************************
;
;										Report Syntax Error
;
; *******************************************************************************************

SyntaxError:
		jsr 	ReportError
		.text 	"Syntax Error",0

; *******************************************************************************************
;
;								Report Error, at return address
;
; *******************************************************************************************
	
ReportError:
		rep 	#$30 						; in case we changed it.
		nop
		bra 	ReportError

; *******************************************************************************************
;
;								Check what the next token is
;
; *******************************************************************************************

CheckNextComma:
		lda 	#commaTokenID 				; shorthand because comma is used a fair bit.
CheckNextToken:
		cmp 	(DCodePtr) 					; does it match the next token
		bne 	_CTKError					; error if not
		inc 	DCodePtr 					; skip the token
		inc 	DCodePtr
		rts	
_CTKError:
		jsr 	ReportError					
		.text	"Missing token",0
