# *******************************************************************************************
# *******************************************************************************************
#
#		Name : 		gentokens.py
#		Purpose :	Creates tokens files.
#		Date :		3rd June 2019
#		Author : 	Paul Robson (paul@robsons.org.uk)
#
# *******************************************************************************************
# *******************************************************************************************

import re,os,sys

# *******************************************************************************************
#									Represents a single token
# *******************************************************************************************

class Token(object):
	def __init__(self,token,type,id):
		self.name = token.strip().lower()
		self.type = type
		self.id = id + (type << 10) + 0x4000
		self.vector = "IllegalToken"
		assert self.name != "" and len(self.name) < 15,"Name "+self.name
		assert (type >= 0 and type <= 7) or (type >= 13 and type <= 15)
	def setRoutine(self,routine):
		self.vector = routine

# *******************************************************************************************
#									Represent the token set
# *******************************************************************************************

class TokenList(object):
	def __init__(self):
		self.tokens = []													# Tokens read in
		self.lookup = {} 													# access them via hash
		duplicates = {} 													# Checking for duplicates using hash
																			# Read the tokens file.																				
		src = [x.strip().lower().replace("\t"," ") for x in open("tokens.txt").readlines()]
		src = [x if x.find("##") < 0 else x[:x.find("##")] for x in src]	# comments out
		src = [x for x in " ".join(src).split(" ") if x != ""]
		currentGroup = None 												# Group is none
		tokenID = 1															# Next free token ID
		for token in src:													# Work through them
			assert token not in duplicates,"Duplicate "+token 				# Check duplicates
			duplicates[token] = token

			if token.startswith("[") and token.endswith("]"):				# [n] [unary] [syntax] [keyword] change group
				group = token[1:-1]
				if re.match("^\\d+$",group) is not None:
					currentGroup = int(group)
				elif group == "unary":
					currentGroup = 13
				elif group == "syntax":
					currentGroup = 14
				elif group == "keyword":
					currentGroup = 15
				else:
					assert False,"Bad group "+token					
			else:
				assert currentGroup is not None,"Group not defined"
				self.tokens.append(Token(token,currentGroup,tokenID))		# add to list
				self.lookup[token] = self.tokens[-1]						# and lookup
				tokenID += 1												# bump next free token.
	#
	#		Access the list of tokens
	#
	def getList(self):
		return self.tokens
	#
	#		Render the include file.
	#
	def renderInclude(self,tgtdir):
		tgtdir = tgtdir.replace("/",os.sep)
		h = open(tgtdir+"tokens.inc","w")
		h.write(";\n;\tVector Jump table\n;\n")
		h.write("CommandJumpTable:\n")
		h.write("\t.word IllegalToken & $FFFF ; for the $0000 token.\n")
		for t in self.getList():
			h.write('\t.word {0:24} & $FFFF ; token ${1:04x} "{2}"\n'.format(t.vector,t.id,t.name))
		h.write("\n")
		#
		h.write(";\n;\tToken text table. Byte is typeID[7:4] length[3:0]\n;\n")
		h.write("TokenText:\n")
		for t in self.getList():
			b = (len(t.name)+1)+t.type * 16
			h.write('\t .text ${0:02x},{1:10} ; token ${2:04x}\n'.format(b,'"'+t.name+'"',t.id))
		h.write("\t.byte $00\n\n")			
		#
		h.write(";\n;\tConstants\n;\n")
		for t in self.getList():
			h.write("{0:32} = ${1:04x}\n".format(self.process(t.name)+"TokenID",t.id))
		h.close()
	#
	#		Convert tokens to legal labels.
	#
	def process(self,n):
		n = n.replace("<","less").replace(">","greater").replace("=","equal").replace("+","plus")
		n = n.replace("-","minus").replace("*","star").replace("/","slash").replace(";","semicolon")
		n = n.replace("(","lparen").replace(")","rparen").replace(",","comma").replace(":","colon")
		n = n.replace("$","dollar").replace("?","question").replace("!","pling").replace("'","squote")
		n = n.replace("|","bar").replace("^","hat").replace("&","ampersand").replace("%","percent")
		assert re.match("^([a-zA-Z]+)$",n) is not None,"error in constant naming "+n
		return n.lower()
	#
	#		Scan source files looking for labels.
	#
	def scanSource(self,rootDir):
		rootDir = rootDir.replace("/",os.sep)
		for root,dirs,files in os.walk(rootDir):
			for f in [f for f in files if f.endswith(".asm")]:
				for l in open(root+os.sep+f).readlines():
					if l.find(";;") >= 0:
						m = re.match("^(.*?)\\:\\s*\\;\\;\\s*(.*)$",l.strip())
						assert m is not None,"Bad line "+l
						token = m.group(2).strip()
						assert token in self.lookup,"Token unknown "+token
						self.lookup[token].setRoutine(m.group(1).strip())

if __name__ == "__main__":
		print("Creating token tables and includes.")
		tokens = TokenList()
		tokens.scanSource("../source")
		tokens.renderInclude("temp/")

