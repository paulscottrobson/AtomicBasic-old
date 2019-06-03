# *******************************************************************************
#
#						Expression (Precedence Climbing) v4.
#
# *******************************************************************************

import re

class Evaluator4:
	#
	#		Evaluate an expression
	#	
	def evaluate(self,expression,answer):
		#
		#		Precedence list
		#
		self.precedence = { "+":2,"-":2,"*":3,"/":3,"!":4,"^":1,"|":1,"&":1 }		
		#
		#		Memory for ! operator to accesss
		#
		self.memory = [ 100,201,302,403,504 ]
		#
		#		Preprocess expression
		#
		expression = expression.lower().replace(" ","").strip()
		self.source = [x for x in re.split("(\\d+)",expression) if x != ""]
		#
		#		Evaluate it and show answer and expected answer.
		#
		result = self.evaluateCode()
		print("{0} -> {1} ({2}) {3}".format(expression,result,answer,"" if result == answer else "*FAIL*"))
	#
	#		Get a single element onto the stack. The stack data is
	#		0 [value,reference/value] 1 min_level 2 operator
	#
	def getAtom(self):
		self.stack.append([[int(self.source[0]),True],0,None])
		self.source = self.source[1:]
	#
	#		Calculate the result of binary operations.
	#
	def calculate(self,l,r,op):		
		#
		#		If values are references, convert to numbers
		#	
		l = self.toValue(l)
		r = self.toValue(r)
		#
		#		Return [answer,constant]
		#
		if op == "+":
			return [l[0]+r[0],True]
		if op == "-":
			return [l[0]-r[0],True]
		if op == "*":
			return [l[0]*r[0],True]
		if op == "/":
			return [l[0]/r[0],True]
		if op == "&":
			return [l[0]&r[0],True]
		if op == "|":
			return [l[0]|r[0],True]
		if op == "^":
			return [l[0]^r[0],True]
		#
		#		Indirect read. This returns [address,reference]
		#
		if op == "!":
			return [l[0]+r[0],False]
	#
	#		Convert reference to a value by doing the actual lookup
	#		this is delayed.
	#
	def toValue(self,value):
		return value if value[1] else [self.memory[value[0]],True]
	#
	#		Evaluator. 
	#
	def evaluateCode(self):
		self.stack = []
		self.evaluateLevel(1)
		assert len(self.stack) == 1
		return self.toValue(self.stack[-1][0])[0]
	#
	#		Evaluate recursive. You could loop this but we need GOTO.
	#
	def evaluateLevel(self,level):
		#
		#		Get the first atom and save the level.
		#		
		self.getAtom()
		self.stack[-1][1] = level
		#
		#		While more binary operations, and precedence is higher than current
		#
		while len(self.source) != 0 and self.precedence[self.source[0]] >= self.stack[-1][1]:
			#
			#		Save operator
			#
			self.stack[-1][2] = self.source[0]
			self.source = self.source[1:]
			#
			#		Evaluate in the next stack level up.
			#
			self.evaluateLevel(self.precedence[self.stack[-1][2]]+1)
			#
			#		Calculate the rsult.
			#
			self.stack[-2][0] = self.calculate(self.stack[-2][0],self.stack[-1][0],self.stack[-2][2])
			#
			#		Throw away the stack for the RHS
			#
			self.stack = self.stack[:-1]


ev = Evaluator4()
ev.evaluate("42",42)
ev.evaluate("2+13",15)
ev.evaluate("2+13+9",24)
ev.evaluate("4^3",7)
ev.evaluate("2+13*4",54)
ev.evaluate("2*13+4*3",38)
ev.evaluate("2^4+13",19)
ev.evaluate("1!2",403)
ev.evaluate("1000+1!2",1403)
ev.evaluate("2*13+4*3^2",36)
