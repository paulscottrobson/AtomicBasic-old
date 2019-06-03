#
#		Create dasm table from opcodes.txt
#
import re
opcodes = [ None ] * 256

src = [x.strip().replace("\t"," ") for x in open("opcodes.txt").readlines()]
src = [x if x.find("//") < 0 else x[:x.find("//")].strip() for x in src	]
src = [x.lower() for x in src if x != ""]

formats = { 
	"immediate":"{0} #%m",						# 8 or 16 depending on M
	"immediateindex":"{0} #%x",					# 8 or 16 depending on X
	"absolute":"{0} %2",						# Absolute.
	"absolutex":"{0} %2,x",						# Absolute X
	"absoluteindirect":"{0} (%2)",				# Absolute Indirect
	"absoluteindirectx":"{0} (%2,x)",			# Absolute Indirect X
	"absolutelongindirect":"{0} [%2]",			# Absolute Long Indirect
	"absolutey":"{0} %2,y",						# Absolute Y
	"absolutelong":"{0} %3",					# Long
	"absolutelongx":"{0} %3,x",					# Long X
	"absolutelongy":"{0} %3,y",					# Long Y
	"direct":"{0} %1",							# direct
	"directx":"{0} %1,x",						# direct x
	"directy":"{0} %1,y",						# direct y
	"indirect":"{0} (%1)",						# indirect
	"indirectx":"{0} (%1,x)",					# indirect x
	"indirecty":"{0} (%1),y",					# indirect y
	"indirectlong":"{0} [%1]",					# indirect long
	"indirectlongy":"{0} [%1],y",				# indirect long y
	"stack":"{0} %1,s",							# stack rel
	"indirectstack":"{0} (%1,s),y",				# indirect stack
	"accumulator":"{0} a",						# acc
	"branch":"{0} %1",							# 8 bit relative
	"noarguments":"{0}",						# no args
	"transfer":"{0} %2",						# transfer (fudge)
	"pcrelativeword":"{0} %2"					# pc relative word
}

for s in src:
	decode = None

	m = re.match("^0x([0-9a-f]+)\\:\\s*op_(.*)\\(\\\"(.*)\\\"\\)\\,$",s)	
	if m is not None:
		assert m.group(2) in formats,"Unknown "+m.group(2)+" "+s
		opcode = int(m.group(1),16)
		decode = formats[m.group(2)].format(m.group(3))

	m = re.match("^0x([0-9a-f]+)\\:\\s*(.*)_immediate\\,$",s)
	if m is not None:
		opcode = int(m.group(1),16)
		decode = "{0} %1".format(m.group(2))

	m = re.match("^0x([0-9a-f]+)\\:\\s*(.*)_pcrelativeword\\,$",s)
	if m is not None:
		opcode = int(m.group(1),16)
		decode = formats["pcrelativeword"].format(m.group(2))

	m = re.match("^0x([0-9a-f]+)\\:\\s*(.*)_noarguments\\,$",s)
	if m is not None:
		opcode = int(m.group(1),16)
		decode = m.group(2)

	m = re.match("^0x([0-9a-f]+)\\:\\s*(jmp)_(.*)\\,$",s)	
	if m is None:
		m = re.match("^0x([0-9a-f]+)\\:\\s*(jsr)_(.*)\\,$",s)	
	if m is not None:
		assert m.group(3) in formats,"Unknown "+m.group(3)+" "+s
		opcode = int(m.group(1),16)
		decode = formats[m.group(3)].format(m.group(2))

	m = re.match("^0x([0-9a-f]+)\\:\\s*(pe[air])_(.*)\\,$",s)	
	if m is not None:
		assert m.group(3) in formats,"Unknown "+m.group(3)+" "+s
		opcode = int(m.group(1),16)
		decode = formats[m.group(3)].format(m.group(2))

	assert decode is not None,"Failed "+s

	if decode != "":
		assert opcodes[opcode] is None
	opcodes[opcode] = decode
	print(opcodes)

for i in range(0,256):
	if opcodes[i] is None:
		assert False

strn = ",".join('"'+x+'"' for x in opcodes)
open("../emulator/dasm65816.h","w").write("static const char *opcodes[256] = { "+strn+" };\n\n")
#
#		Now create assembly table. Format is adc.fiy 42 adc# 42 etc.
#
assembly = [ None ] * 256
cvMode = 	{	"":"","(%1,x)":"ix","%1,s":"zs","%1":"z","[%1]":"fi","a":"","(%1),y":"iy","(%1)":"i",
				"%1,x":"zx","[%1],y":"fiy","%1,y":"zy",
				"%2":"a","%2,y":"ay","%2,x":"ax","(%2)":"ai","(%2,x)":"aix","[%2]":"fai",
				"%3":"f","%3,x":"fy",
				"(%1,s),y":"siy",
				"#%m":"ima","#%x":"imx",
			}

for i in range(0,256):
	asm = opcodes[i]
	opcode = asm[:3]
	mode = asm[3:].strip()
	print(opcode,mode)
	print(cvMode[mode])
