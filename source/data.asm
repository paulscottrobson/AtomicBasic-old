; ********************************************************************************
; ********************************************************************************
;
;		Name: 		data.asm
;		Purpose:	Data Description for Basic
;		Date:		3rd June 2019
;		Author:		Paul Robson (paul@robsons.org.uk)
;
; ********************************************************************************
; ********************************************************************************

; ********************************************************************************
;
;								This is the Zero Page Data
;
; ********************************************************************************

DPBaseAddress = $00 						; Base address used for direct page.
											; (e.g. variables start at DP+nn)

DPageNumber = DPBaseAddress 				; page number of workspace area
DBaseAddress = DPBaseAddress+2 				; low memory for workspace area
DHighAddress = DPBaseAddress+4 				; high memory for workspace area

DCodePtr = DPBaseAddress+6 					; address of code - current token.

DTemp1 = DPBaseAddress + 8 					; *** LONG *** Temporary value
DTemp2 = DPBaseAddress + 12 				; *** LONG *** Temporary value

DSignCount = DPBaseAddress + 16 			; Sign count in division.
DConstantShift = DPBaseAddress + 18 		; Constant Shift
DRandom = DPBaseAddress + 20 				; *** LONG *** Random Seed

; ********************************************************************************
;
;		Expression stack : Each entry is a word size, and there are three
;		run in parallel - the low word, the high word, and the precedence level.
;
; ********************************************************************************


EXSBase = $100 								; Initial value of X at lowest stack level.

											; offsets from stack base (each stack element = 2 bytes)
EXSValueL = 0 								; Low word
EXSValueH = 16  							; High word
EXSPrecedence = 32							; Precedence


