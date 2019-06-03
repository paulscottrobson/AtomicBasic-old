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
		self.isProtected = True
		self.lastProgramLineNumber = 0
	#
	#	Write binary out
	#
	def export(self,fileName):
		h = open(fileName,"wb")
		h.write(bytes(self.data))
		h.close()
	#
	#	Set Protection
	#
	def setProtection(self,isProtected):
		self.isProtected = isProtected
	#
	#	Erase all variables and code
	#
	def clearMemory(self):
		for v in range(ord('@'),ord('Z')+1):									# zero fast variables
			self.setFastVariable(chr(v),0)
		self.writeWord(self.baseAddress+BasicBlock.HIGHPTR,self.endAddress)		# reset high memory
		self.writeWord(self.baseAddress+BasicBlock.PROGRAM,0x0000)				# erase program
		self.resetLowMemory()
	#
	#	Rewrite the spacer and low memory
	#
	def resetLowMemory(self):
		ptr = self.baseAddress+BasicBlock.PROGRAM 								# Where code starts
		while self.readWord(ptr) != 0x0000:										# follow the code link chain
			ptr = ptr + self.readWord(ptr)
		self.writeWord(ptr+2,0xEEEE)											# write EEEE twice after it
		self.writeWord(ptr+4,0xEEEE)
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
		assert addr >= self.baseAddress and addr <= self.endAddress
		addr = addr - self.baseAddress
		return self.data[addr] + self.data[addr+1] * 256
	#
	#	Write a word to memory
	#
	def writeWord(self,addr,data):
		assert addr >= self.baseAddress and addr <= self.endAddress
		data = data & 0xFFFF
		self.data[addr-self.baseAddress] = data & 0xFF
		self.data[addr-self.baseAddress+1] = data >> 8
		if self.debug:
			print("{0:04x} {1:04x}".format(addr,data))
	#
	#	Read long as signed int
	#
	def readLong(self,addr):
		val = self.readWord(addr)+(self.readWord(addr+2)<<16)
		if (val & 0x80000000) != 0:
			val = val - 0x100000000
		return val
	#
	#	Create a representation of an identifier in high memory.
	#
	def createIdentifierReference(self,name):
		assert re.match("^[\\@A-Z][\\@A-Z0-9]*$",name.upper()) is not None 		# check legal variable name
		assert len(name) > 1													# check not fast variable
		tokens = self.tokeniser.tokenise(name)									# tokenise it
		addr = self.allocateHighMemory(len(tokens)*2)							# allocate high mem for name
		for i in range(0,len(tokens)):											# copy it (normally in program)
			self.writeWord(addr+i*2,tokens[i])
		return addr
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
		nameAddr = self.createIdentifierReference(name)							# create tokenised version
		hashAddr = self.getHashEntry(nameAddr)									# get hash address for variable
	
		varAddr = self.allocateLowMemory(8)										# create memory for it
		value = initValue														# put this in
		if memoryAllocated != 0:												# if not allocating memory for it
			assert memoryAllocated > 0 and memoryAllocated % 2 == 0 			# check size
			actual = memoryAllocated+6 if self.isProtected else memoryAllocated	# allow for protection
			malloc = self.allocateLowMemory(actual)								# alloc memory
			if self.isProtected:
				self.writeWord(malloc+0,BasicBlock.PROTECTMARKER & 0xFFFF)		# protection marker
				self.writeWord(malloc+2,BasicBlock.PROTECTMARKER >> 16)
				self.writeWord(malloc+4,memoryAllocated)						# size of memory
				malloc += 6 													# skip over
			for i in range(0,memoryAllocated,4):								# initaialise data memory
				self.writeWord(malloc+i+0,initValue & 0xFFFF)
				self.writeWord(malloc+i+2,initValue >> 16)
				initValue += 0x10000
			value = malloc 														# store this in variable

		self.writeWord(varAddr+0,self.readWord(hashAddr))						# patch into hash linked list
		self.writeWord(varAddr+2,nameAddr)
		value = value & 0xFFFFFFFF
		self.writeWord(varAddr+4,value & 0xFFFF)								# write data or address of allocated
		self.writeWord(varAddr+6,value >> 16)
		self.variables[name] = { "address":varAddr,"allocated":memoryAllocated,"start":value }
		self.writeWord(hashAddr,varAddr)
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
		self._export("BlockProtectMarker",BasicBlock.PROTECTMARKER)
		self.handle.close()
	#
	def _export(self,name,value):
		self.handle.write("{0} = ${1:04x}\n".format(name,value))
	#
	#		List variables to a file object
	#
	def listVariables(self,h=sys.stdout):
		for r in range(ord("@"),ord("Z")+1):									# export non zero fast vars
			addr = (r-ord('@'))*4+BasicBlock.FASTVARIABLES+self.baseAddress
			value = self.readLong(addr)
			if value != 0:
				h.write("{0} = {1} ${1:x} @${2:04x}\n".format(chr(r).lower(),value,addr))
		for hn in range(0,BasicBlock.HASHMASK+1):								# work through hash table
			hPtr = BasicBlock.HASHTABLE+hn*2+self.baseAddress 					# address of head pointer
			ptr = self.readWord(hPtr)											# head pointer
			if ptr != 0:														# if occupied, show head
				h.write("Hash {0} Table at ${1:04x}\n".format(hn,hPtr))
				while ptr != 0:													# show variables in list
					value = self.readLong(ptr+4)
					h.write("\t${0:04x} {1} = {2} ${2:x}\n".format(ptr,self.decodeIdentifier(self.readWord(ptr+2)),value))
					if value > self.baseAddress+6 and value < self.endAddress:	# check to see if a string/int sequence.
						if self.readLong(value-6) == BasicBlock.PROTECTMARKER:	# because the marker is there
							size = self.readWord(value-2)
							h.write("\t\t{0} bytes {1} words\n".format(size,size >> 2))
							h.write("\t\t\t{0}\n".format(self.wordData(value,size >> 2)))
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
			s = s + self._decodeChar(v)+self._decodeChar(v >> 6)				# convert to characters
			done = (v & 0x1000) == 0											# continue if bit 12 set
		return s.lower()
	#
	#		Convert 6 bit char value back to ASCII
	#
	def _decodeChar(self,c):
		c = c & 0x3F 															# 6 bits
		return "" if c == 0 else chr(c+32)
	#
	#		Data as words
	#
	def wordData(self,addr,count):
		words = [self.readLong(addr+i*4) for i in range(0,count)]
		return " ".join(["${0:x}".format(x) for x in words])

BasicBlock.ID = "BASC"															# ID
BasicBlock.PROTECTMARKER = 0x7B62CE4A											# Protected marker.
BasicBlock.FASTVARIABLES = 0x10 												# Fast Variable Base
BasicBlock.HASHTABLE = 0x80 													# Hash Table Base
BasicBlock.LOWPTR = 0xA0 														# Low Memory Allocation
BasicBlock.HIGHPTR = 0xA2 														# High Memory Allocation
BasicBlock.PROGRAM = 0xC0 														# First line of program
BasicBlock.HASHMASK = 15 														# Hash mask (0,1,3,7,15)

if __name__ == "__main__":
	blk = BasicBlock(0x4000,0x8000)
	blk.addBASICLine(10,'a="hello"+1')
	blk.export("temp/basic.bin")	
	blk.exportConstants("temp/block.inc")
