#
#		Unsigned Integer Division in Python (16 bit version)
#
import random

def divide(dividend,divisor):
	actualQ = int(dividend/divisor)
	actualR = dividend % divisor

	a = 0  					# DTemp1 	(remainder)
	q = dividend 			# Left 		(quotient) 	+0
	m = divisor 			# Right 				+2
	for i in range(0,16):
		# shift left AQ as 32 bit value
		a = ((a << 1) | ((q >> 15) & 1)) & 0xFFFF
		q = (q << 1) & 0xFFFF
		# subtract m from a for testing
		t = a - m
		# if +ve save result in A and set LSB of q
		if t >= 0:
			q = q | 1
			a = t

	quotient = q
	remainder = a

	#print(quotient,remainder,actualQ,actualR)
	assert actualQ == quotient
	assert actualR == remainder

for t in range(0,1000*1000):
	v1 = random.randint(1,0x7FFF)
	v2 = random.randint(1,0x7FFF)
	if random.randint(0,1) == 0:
		v2 = random.randint(1,0x7FFF)
	divide(v1,v2)

