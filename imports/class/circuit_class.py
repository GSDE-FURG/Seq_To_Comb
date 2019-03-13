#encoding=utf-8

class Nodeinfo:
	def __init__(self,line,inputs,isinput,used = False):
		self.line = line
		self.inputs = inputs
		self.isinput = isinput
		self.used = used
		self.influence = 0
		self.maxdepth = 0
		self.depthset = False
		self.drive = 0
		self.computed = False
		self.computeddrive = []
	#colocar certas funções aqui
