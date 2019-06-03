;
;	Vector Jump table
;
CommandJumpTable:
	.word IllegalToken & $FFFF ; for the $0000 token.
	.word Binary_And               & $FFFF ; token $4001 "&"
	.word Binary_Or                & $FFFF ; token $4002 "|"
	.word Binary_Xor               & $FFFF ; token $4003 "^"
	.word Binary_Less              & $FFFF ; token $4404 "<"
	.word Binary_Greater           & $FFFF ; token $4405 ">"
	.word Binary_Equals            & $FFFF ; token $4406 "="
	.word Binary_LessEqual         & $FFFF ; token $4407 "<="
	.word Binary_GreaterEqual      & $FFFF ; token $4408 ">="
	.word Binary_NotEquals         & $FFFF ; token $4409 "<>"
	.word Binary_Add               & $FFFF ; token $480a "+"
	.word Binary_Subtract          & $FFFF ; token $480b "-"
	.word Binary_Multiply          & $FFFF ; token $4c0c "*"
	.word Binary_Divide            & $FFFF ; token $4c0d "/"
	.word Binary_Modulus           & $FFFF ; token $4c0e "%"
	.word Binary_ShiftRight        & $FFFF ; token $4c0f ">>"
	.word Binary_ShiftLeft         & $FFFF ; token $4c10 "<<"
	.word IllegalToken             & $FFFF ; token $5011 "?"
	.word IllegalToken             & $FFFF ; token $5012 "!"
	.word IllegalToken             & $FFFF ; token $5013 "$"
	.word Function_Random          & $FFFF ; token $7414 "rnd()"
	.word Function_Sgn             & $FFFF ; token $7415 "sgn("
	.word Function_Abs             & $FFFF ; token $7416 "abs("
	.word Function_Len             & $FFFF ; token $7417 "len("
	.word IllegalToken             & $FFFF ; token $7818 ","
	.word IllegalToken             & $FFFF ; token $7819 ";"
	.word IllegalToken             & $FFFF ; token $781a ":"
	.word IllegalToken             & $FFFF ; token $781b "("
	.word IllegalToken             & $FFFF ; token $781c ")"
	.word IllegalToken             & $FFFF ; token $7c1d "let"

;
;	Token text table. Byte is typeID[7:4] length[3:0]
;
TokenText:
	 .text $02,"&"        ; token $4001
	 .text $02,"|"        ; token $4002
	 .text $02,"^"        ; token $4003
	 .text $12,"<"        ; token $4404
	 .text $12,">"        ; token $4405
	 .text $12,"="        ; token $4406
	 .text $13,"<="       ; token $4407
	 .text $13,">="       ; token $4408
	 .text $13,"<>"       ; token $4409
	 .text $22,"+"        ; token $480a
	 .text $22,"-"        ; token $480b
	 .text $32,"*"        ; token $4c0c
	 .text $32,"/"        ; token $4c0d
	 .text $32,"%"        ; token $4c0e
	 .text $33,">>"       ; token $4c0f
	 .text $33,"<<"       ; token $4c10
	 .text $42,"?"        ; token $5011
	 .text $42,"!"        ; token $5012
	 .text $42,"$"        ; token $5013
	 .text $d6,"rnd()"    ; token $7414
	 .text $d5,"sgn("     ; token $7415
	 .text $d5,"abs("     ; token $7416
	 .text $d5,"len("     ; token $7417
	 .text $e2,","        ; token $7818
	 .text $e2,";"        ; token $7819
	 .text $e2,":"        ; token $781a
	 .text $e2,"("        ; token $781b
	 .text $e2,")"        ; token $781c
	 .text $f4,"let"      ; token $7c1d
	.byte $00

;
;	Constants
;
ampersandTokenID                 = $4001
barTokenID                       = $4002
hatTokenID                       = $4003
lessTokenID                      = $4404
greaterTokenID                   = $4405
equalTokenID                     = $4406
lessequalTokenID                 = $4407
greaterequalTokenID              = $4408
lessgreaterTokenID               = $4409
plusTokenID                      = $480a
minusTokenID                     = $480b
starTokenID                      = $4c0c
slashTokenID                     = $4c0d
percentTokenID                   = $4c0e
greatergreaterTokenID            = $4c0f
lesslessTokenID                  = $4c10
questionTokenID                  = $5011
plingTokenID                     = $5012
dollarTokenID                    = $5013
rndlparenrparenTokenID           = $7414
sgnlparenTokenID                 = $7415
abslparenTokenID                 = $7416
lenlparenTokenID                 = $7417
commaTokenID                     = $7818
semicolonTokenID                 = $7819
colonTokenID                     = $781a
lparenTokenID                    = $781b
rparenTokenID                    = $781c
letTokenID                       = $7c1d
