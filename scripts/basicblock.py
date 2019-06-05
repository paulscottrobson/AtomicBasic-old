# *******************************************************************************************
# *******************************************************************************************
#
#		Name : 		basicblock.py
#		Purpose :	Basic code block manipulator
#		Date :		3rd June 2019
#		Author : 	Paul Robson (paul@robsons.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import re,os,sys
from gentokens import *
from tokeniser import *

# *******************************************************************************************
#
#										Basic Block Object
#
# *******************************************************************************************

class BasicBlock(object):
	def __init__(self,baseAddress = 0x0000,size = 0xFFFF,debug = False):
		self.baseAddress = baseAddress											# Block information
		self.blockSize = size
		self.endAddress = baseAddress + size
		self.data = [ 0 ] * size 												# containing data
		for i in range(0,4):													# set 4 byte header
			self.data[i] = ord(BasicBlock.ID[i])
		self.debug = False
		self.clearMemory()														# same as clear
		self.memoryVariableCreated = False 										# allocated memory
		self.debug = debug
		self.tokeniser = Tokeniser()											# tokenises things
		self.variables = {}														# variable info
		self.lastProgramLineNumber = 0
	#
	#	Write binary out
	#
	def export(self,fileName):
		h = open(fileName,"wb")													# write data as bytes
		h.write(bytes(self.data))
		h.close()
	#
	#	Erase all variables and code
	#
	def clearMemory(self):
		for v in range(ord('@'),ord('Z')+1):									# zero fast variables
			self.setFastVariable(chr(v),0)
		self.writeWord(self.baseAddress+BasicBlock.HIGHPTR,self.endAddress)		# reset high memory
		self.writeWord(self.baseAddress+BasicBlock.PROGRAM,0x0000)				# erase program
		self.resetLowMemory()													# reset low memory
	#
	#	Rewrite the spacer and low memory
	#
	def resetLowMemory(self):
		ptr = self.baseAddress+BasicBlock.PROGRAM 								# Where code starts
		while self.readWord(ptr) != 0x0000:										# follow the code link chain
			ptr = ptr + self.readWord(ptr)										# to the end.
		self.writeWord(ptr+2,0xEEEE)											# write EEEE twice after it
		self.writeWord(ptr+4,0xEEEE)											# visibility marker.
		self.writeWord(self.baseAddress+BasicBlock.LOWPTR,ptr+6)				# free memory starts here.
		return ptr 																# return where next line goes
	#
	#	Overwrite fast variable A-Z
	#
	def setFastVariable(self,variable,value):
		variable = variable.upper()
		assert re.match("^[\\@A-Z]$",variable) is not None						# check is fast variable
		value = value & 0xFFFFFFFF												# make 32 bit uint
		self.writeWord(self.baseAddress+(ord(variable)-ord('@'))*4+BasicBlock.FASTVARIABLES,value & 0xFFFF)
		self.writeWord(self.baseAddress+(ord(variable)-ord('@'))*4+BasicBlock.FASTVARIABLES+2,value >> 16)
	#
	#	Allocate low memory (e.g. from program end up)
	#
	def allocateLowMemory(self,count):
		addr = self.readWord(self.baseAddress+BasicBlock.LOWPTR)				# address to use
		self.writeWord(self.baseAddress+BasicBlock.LOWPTR,addr+count)			# update offset
		assert self.readWord(self.baseAddress+BasicBlock.LOWPTR) < self.readWord(self.baseAddress+BasicBlock.HIGHPTR)
		return addr 
	#
	#	Allocate high memory (e.g. from top down)
	#
	def allocateHighMemory(self,count):
		addr = self.readWord(self.baseAddress+BasicBlock.HIGHPTR) - count		# address to use
		self.writeWord(self.baseAddress+BasicBlock.HIGHPTR,addr)				# update new high address
		assert self.readWord(self.baseAddress+BasicBlock.LOWPTR) < self.readWord(self.baseAddress+BasicBlock.HIGHPTR)
		return addr
	#
	#	Read a word from memory
	#
	def readWord(self,addr):
		assert addr >= self.baseAddress and addr <= self.endAddress 			# validate
		addr = addr - self.baseAddress 											# offset in data
		return self.data[addr] + self.data[addr+1] * 256 						# return it
	#
	#	Write a word to memory
	#
	def writeWord(self,addr,data):
		assert addr >= self.baseAddress and addr <= self.endAddress 			# validate it
		data = data & 0xFFFF 													# force into 16 bit
		self.data[addr-self.baseAddress] = data & 0xFF 							# store in structure
		self.data[addr-self.baseAddress+1] = data >> 8
		if self.debug:															# debug display
			print("{0:04x} : {1:04x}".format(addr,data))
	#
	#	Read long as signed int
	#
	def readLong(self,addr):
		val = self.readWord(addr)+(self.readWord(addr+2) << 16)					# read as 32 bit unsigned
		if (val & 0x80000000) != 0:												# convert to signed
			val = val - 0x100000000
		return val
	#
	#	Create a representation of an identifier in high memory. We normally use the identifier representation
	#	in the program, but this is used for creating test code.
	#
	def createIdentifierReference(self,name):
		assert re.match("^[\\@A-Z][\\@A-Z0-9]*$",name.upper()) is not None 		# check legal variable name
		assert len(name) > 1													# check not fast variable
		tokens = self.tokeniser.tokenise(name)									# tokenise it
		addr = self.allocateHighMemory(len(tokens)*2)							# allocate high mem for name
		for i in range(0,len(tokens)):											# copy it (normally in program)
			self.writeWord(addr+i*2,tokens[i])
		return addr 															# return its address
	#
	#	Get hash for name at given address
	#
	def getHashEntry(self,nameAddr):
		parts = self.readWord(nameAddr)											# first token word
		eCalc = parts ^ (parts >> 8)											# xor bytes together
		eCalc = eCalc & BasicBlock.HASHMASK										# Force into range
		return (eCalc * 2) + self.baseAddress + BasicBlock.HASHTABLE 			# convert to hash table address
	#
	#	Create variable, with optional array
	#	
	def createVariable(self,name,initValue,memoryAllocated = 0):
		self.memoryVariableCreated = True 										# can't add more code
		name = name.lower()
		assert name != "" and name not in self.variables 						# check ok / not exists
		nameAddr = self.createIdentifierReference(name)							# create tokenised version in highmem
		hashAddr = self.getHashEntry(nameAddr)									# get hash address for variable
	
		varAddr = self.allocateLowMemory(8)										# create memory for it in low memory
		if memoryAllocated != 0:												# if not allocating memory for it
			assert memoryAllocated > 0 and memoryAllocated % 2 == 0 			# check size
			malloc = self.allocateHighMemory(memoryAllocated)					# allocate high memory for it.
			for i in range(0,memoryAllocated,4):								# initaialise data memory
				self.writeWord(malloc+i+0,initValue & 0xFFFF)
				self.writeWord(malloc+i+2,initValue >> 16)
				initValue += 0x10000
			initValue = malloc 													# store this in variable

		self.writeWord(varAddr+0,self.readWord(hashAddr))						# next link is old link header
		self.writeWord(varAddr+2,nameAddr)
		initValue = initValue & 0xFFFFFFFF 										# mask to 32 bits.
		self.writeWord(varAddr+4,initValue & 0xFFFF)							# write data or address of allocated
		self.writeWord(varAddr+6,initValue >> 16)
		self.variables[name] = { "address":varAddr,"allocated":memoryAllocated,"start":initValue }
		self.writeWord(hashAddr,varAddr) 										# link as first element in list.
	#
	#		Add a line of BASIC
	#
	def addBASICLine(self,lineNumber,code):
		assert not self.memoryVariableCreated									# check not created variables
		if lineNumber is None or lineNumber == 0:								# default line number
			lineNumber = self.lastProgramLineNumber + 1
		assert lineNumber > self.lastProgramLineNumber and lineNumber <= 32767 	# check line number
		pos = self.resetLowMemory()												# where does it go
		self.lastProgramLineNumber = lineNumber 								# remember last
		codeLine = self.tokeniser.tokenise(code) 								# convert to tokens
		codeLine.append(0)														# EOL
		codeLine.insert(0,lineNumber|0x8000) 									# insert line number
		codeLine.insert(0,len(codeLine)*2+2)									# skip
		codeLine.append(0)														# final program end marker
		for t in codeLine:														# write it out
			self.writeWord(pos,t)  
			pos += 2
		self.resetLowMemory() 													# and reset low memory
	#
	#		Export constants
	#
	def exportConstants(self,fileName):
		self.handle = open(fileName.replace("/",os.sep),"w")
		self._export("BlockFastVariables",BasicBlock.FASTVARIABLES)
		self._export("BlockHashTable",BasicBlock.HASHTABLE)
		self._export("BlockHashMask",BasicBlock.HASHMASK)
		self._export("BlockLowMemoryPtr",BasicBlock.LOWPTR)
		self._export("BlockHighMemoryPtr",BasicBlock.HIGHPTR)
		self._export("BlockProgranStart",BasicBlock.PROGRAM)
		self.handle.close()
	#
	def _export(self,name,value):
		self.handle.write("{0} = ${1:04x}\n".format(name,value))
	#
	#		List variables to a file object
	#
	def listVariables(self,h=sys.stdout):
		h.write("Non Zero Fast Variables\n")
		for r in range(ord("@"),ord("Z")+1):									# export non zero fast vars
			addr = (r-ord('@'))*4+BasicBlock.FASTVARIABLES+self.baseAddress 	# address of fast variable
			value = self.readLong(addr) 										# display it if nonzero
			if value != 0:
				h.write("\t${2:04x} {0} := {1} ${1:x}\n".format(chr(r).lower(),value,addr))
		lowestHighMem = self.readWord(self.baseAddress+BasicBlock.HIGHPTR)		# lowest address used in high memory
		for hn in range(0,BasicBlock.HASHMASK+1):								# work through hash table
			hPtr = BasicBlock.HASHTABLE+hn*2+self.baseAddress 					# address of head pointer
			ptr = self.readWord(hPtr)											# head pointer
			if ptr != 0:														# if occupied, show head
				h.write("Hash {0} Link at ${1:04x}\n".format(hn,hPtr))
				while ptr != 0:													# show variables in list
					value = self.readLong(ptr+4)
					h.write("\t${0:04x} {1} := {2} ${2:x}\n".format(ptr,self.decodeIdentifier(self.readWord(ptr+2)),value))
					if value >= lowestHighMem and value < self.endAddress:		# check to see if a string/int sequence.
						size = min(16,self.endAddress-value) 					# how much to display.
						data = [self.readWord(value+x) & 0xFF for x in range(0,size)]
						h.write("\t\t{0}\n".format(",".join(["{0:02x}".format(x) for x in data])))
						ePos = size if data.index(0) < 0 else data.index(0)		# if string, where does it end ?
						h.write("\t\t\"{0}\"".format("".join([chr(x) if x >= 32 and x < 128 else "." for x in data[:ePos]])))						
					ptr = self.readWord(ptr)									# follow list
	#
	#		Convert identifier at address
	#
	def decodeIdentifier(self,idPtr):
		s = ""
		done = False
		while not done:
			v = self.readWord(idPtr)											# get next
			idPtr = idPtr + 2
			s = s + self._decodeChar(v & 0x3F)+self._decodeChar((v>>6) & 0x3F)	# convert to characters
			done = (v & 0x1000) == 0											# continue if bit 12 set
		return s.lower()
	#
	def _decodeChar(self,c):
		return "" if c == 0 else chr(c+32)

BasicBlock.ID = "BASC"															# ID
BasicBlock.FASTVARIABLES = 0x10 												# Fast Variable Base
BasicBlock.HASHTABLE = 0x80 													# Hash Table Base
BasicBlock.LOWPTR = 0xA0 														# Low Memory Allocation
BasicBlock.HIGHPTR = 0xA2 														# High Memory Allocation
BasicBlock.PROGRAM = 0xC0 														# First line of program
BasicBlock.HASHMASK = 15 														# Hash mask (0,1,3,7,15)

if __name__ == "__main__":
	blk = BasicBlock(0x4000,0x8000)
	blk.addBASICLine(10,'x=42*len("hello")')
	blk.setFastVariable('@',22)
	blk.createVariable("w1",42)
	blk.createVariable("arr1",0xE22A,12)
	blk.listVariables()
	blk.export("temp/basic.bin")	
	blk.exportConstants("temp/block.inc")
