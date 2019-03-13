#encoding=utf-8
import sys

sys.path.append("./imports/class")

import os
import datetime
from arquive import Arquive
from circuit_class import *

def B_extractextrasignals(data):
	end = False
	extrainputs = []
	extraoutputs = []
	numflipflops = 0
	while end == False:
		try:
			location = data.index("DFF(")
			location2 = -1
			location2 = data.index ("\n")
			while location2 < location: #quando nao der nada quer dizer que estamos na mesma linha
				data = data[(location2 + 1):]
				location2 = data.index ("\n")
				location = data.index("DFF(")
			outputtext = data[:location2]
			outputtext = outputtext.replace(")","")
			outputtext = outputtext.replace(" ","")
			outputtext = outputtext.replace("=","")
			outputtext = outputtext.split("DFF(")
			extrainputs.append(outputtext[0])
			extraoutputs.append(outputtext[1])
			data = data[(location2 + 1):]
			numflipflops = numflipflops + 1
		except (ValueError):
			end = True
	return (data,extrainputs,extraoutputs,"*-Nil-*", numflipflops)
	

def B_findextractline(text,data):
	end = False
	inputs = []
	while end == False:
		try:
			location = data.index(text) #pega output se existir
			outputtext = data[(location + len(text)):] #tira o que entrou
			location2 = outputtext.index("\n") #acha o final da linha
			outputtext = outputtext[:(location2)] # pega so o pedaço que contem a informação do output
			outputtext = outputtext.replace("(","") #limpa os parenteses
			outputtext = outputtext.replace(")","")
			inputs.append(outputtext) #salva na lista de outputs 
			data = data[:location] + data[(location + location2 + 1 + len(text)):] #data agora não tem mais o output feito, contruir novamente no final
		except (ValueError):
			end = True
	return (data,inputs)

def B_createfile(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,namemodule,partial=False):
	return ("null")

def B_createcell_list(data,original_inputs,extrainputs):
	data = data.split("\n")
	cont = 0
	cell_list = {}
	while cont < len(data):
		word = data[cont]
		if len(word) > 1:
			word = word.replace(" ","")
			word = word.replace(")","")
			location = word.index("=")
			location2= word.index("(")
			word = word[:(location + 1)] + word[location2 + 1:] #primeiro é tudo antes do "=", inclusive ele, segundo é tudo depois do "(",ignorando ele
			word = word.strip()
			word = word.split("=")
			if "," in word[1]:
				word[1] = word[1].split(",")	
			else:
				word[1] = [word[1]]
			cell_list[word[0]] = Nodeinfo(cont,word[1],False)
		cont = cont + 1	
	for inputnode in original_inputs:
		cell_list[inputnode] = Nodeinfo(-1,[],True)
	for inputnode in extrainputs:
		cell_list[inputnode] = Nodeinfo(-1,[],True)
	return cell_list	