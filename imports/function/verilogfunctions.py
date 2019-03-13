#encoding=utf-8
import sys

sys.path.append("./imports/class")

import os
import datetime
from arquive import Arquive
from circuit_class import *

def V_extractextrasignals(data):
	numflipflops = 0
	extrainputs = []
	extraoutputs = []
	data = data.split("always @")
	data[1] = data[1].split(" begin")
	clockdata = data[1].pop(0).strip()
	clockdata = clockdata.replace(")","")
	clockdata = clockdata.split(" ")
	clockdata = clockdata.pop()
	data[1][0] = data[1][0].replace(" ","") #limpa espaço vazio
	data[1][0] = data[1][0].replace("\t","")
	data[1][0] = data[1][0].replace("\n","")
	data[1][0] = data[1][0].split(";")
	data[1][0].pop(len(data[1][0]) - 1)
	data[1] = data[1].pop(0)
	for itens in data[1]:
		itens = itens.split("<=")
		extrainputs.append(itens[0])
		extraoutputs.append(itens[1])
		numflipflops = numflipflops + 1
	data.pop(1) 
	data.append("endmodule\n")
	data = " ".join(data)
	return (data,extrainputs,extraoutputs,clockdata,numflipflops)

def V_deleteline(text,data): # "reg " p/ reg, ...
	while True:
		data = data.split(text)
		if len(data) == 1:
			data = data[0]
			break
		location = data[1].index(";")
		data[1] = data[1][(location + 2):]
		data = " ".join(data)
	return data

def V_moduleextract(data):
	location = data.index("module ") 
	data = data[(location + 7):]
	location2 = data.index("(")
	namemodule = data[:location2]
	location2 = data.index(";")
	data = data[location2+2:]
	return (data,namemodule)

def V_findextractline(text,data): #"output " p/ output, "input " p/ input, "reg " p/ reg, "wire " p/wire
	end = False
	original_outputs = []
	while end == False:
		try:
			location = data.index(text) #pega output se existir
			outputtext = data[(location + len(text)):] #tira o output e o espaço e pega todo o texto depois
			location2 = outputtext.index(";") #acha o final da linha
			outputtext = outputtext[:(location2+1)] # pega so o pedaço que contem a informação do output
			outputtext = outputtext.replace(" ","") #limpa os espaços e o ponto virgula recomendado
			outputtext = outputtext.replace(";","")
			outputtext = outputtext.replace("\n","")
			if ("," in outputtext):
				outputtext = outputtext.split(",")
				original_outputs = original_outputs + outputtext #salva na lista de outputs 
			else:
				original_outputs.append(outputtext)
			data = data[:location] + data[(location + location2 + 1 + len(text) + 1):] #data agora não tem mais o output feito, contruir novamente no final
		except (ValueError):
			end = True
	return (data,original_outputs)

def V_createfile(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,namemodule,partial=False):
	time = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()).isoformat()
	if partial == False:
		modulo = "//Converted to Combinational , Module name: "+ namemodule + ", Timestamp: " + time + " \nmodule " + namemodule + "( "
	else:
		modulo = "//Converted to Combinational (Partial output: "+ original_outputs[0]+") , Module name: "+ namemodule + ", Timestamp: " + time + " \nmodule " + namemodule + "( "
	istring = "input "
	ostring = "output "
	inputset = set(extrainputs + original_inputs)
	outputset = set(extraoutputs + original_outputs)
	for inputs in inputset :
		modulo = modulo + inputs + ", "
		istring = istring + inputs + ", "
	for outputs in outputset : 
		modulo = modulo + outputs + ", "
		ostring = ostring + outputs + ", "
	modulo = modulo[:len(modulo) - 2] + " );\n"
	istring = istring[:len(istring) - 2] + ";\n"
	ostring = ostring[:len(ostring) - 2] + ";\n"
	if len(wiredata) == 0:
		wirestring = ""
	else:
		wirestring = "wire "
		for wires in wiredata:
			wirestring = wirestring + wires + ", "
		wirestring = wirestring[:len(wirestring) - 2] + ";\n"
	data = modulo + istring + ostring + wirestring + data
	return data	

def V_createcell_list(data,original_inputs,extrainputs):
	teste = "assign " in data
	data = data.split("\n")
	word = ""
	while "endmodule" not in word:
		word = data.pop() #P/ tirar o endmodule
	if teste:
		cont = 0
		cell_list = {}
		while cont < len(data):
			word = data[cont]
			word = word.replace(" ","")
			word = word.replace(";","")
			word = word.replace("~","")
			word = word.replace("assign","")
			word = word.strip()
			word = word.split("=")
			if "|" in word[1]:
				word[1] = word[1].split("|")
			elif "&" in word[1]:
				word[1] = word[1].split("&")
			elif "^" in word[1]:
				word[1] = word[1].split("^")	
			else:
				word[1] = [word[1]]
			cell_list[word[0]] = Nodeinfo(cont,word[1],False)
			cont = cont + 1
	else:
		cont = 0
		cell_list = {}
		while cont < len(data):
			word = data[cont]
			cell = []
			location = 0
			while location != -1:
				try:
					location = word.index(".")
					word = word[(location+1):]
					location = word.index("(")
					location2 = word.index(")")
					cell.append(word[(location+1):location2])
				except (ValueError):
					location = -1
			cell = cell[::-1] #para o primeiro ser o output assim como o assign
			node = cell.pop(0)
			cell_list[node] = Nodeinfo(cont,cell,False)
			cont = cont + 1
	for inputnode in original_inputs:
		cell_list[inputnode] = Nodeinfo(-1,[],True)
	for inputnode in extrainputs:
		cell_list[inputnode] = Nodeinfo(-1,[],True)
	return cell_list	