#encoding=utf-8
import sys

sys.path.append("./imports/class")
sys.path.append("./imports/function")

import msgpack
import shutil
from arquive import Arquive
from verilogfunctions import *
from benchfunctions import *
from circuit_class import *

def depthcalculator(cell_list,node,startingnode,checknodes,inputs,depth = 0): #juntar isso com select nodes?
	currentdepth = 0
	if node in inputs:
		cell_list[node].depthset = True
		cell_list[node].maxdepth = 0
		return 0
	for inputnode in cell_list[node].inputs:
		if (inputnode in checknodes):
			if cell_list[inputnode].depthset:
				newdepth = cell_list[inputnode].maxdepth
			else:	
				newdepth = depthcalculator(cell_list,inputnode,startingnode,checknodes,inputs,depth)
			if newdepth > currentdepth:
				currentdepth = newdepth
	cell_list[node].depthset = True
	cell_list[node].maxdepth = currentdepth + 1			
	return currentdepth + 1

def resetdepthcalculator(cell_list): 
	keys = list(cell_list.keys())
	for node in keys:
		cell_list[node].depthset = False

def fixIO(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,clockname, SIMPLE_MODE = True):
	for node in original_inputs:
		if node == clockname: #retira o clock do sinal!
			original_inputs.pop(original_inputs.index(node))
			break
	if not(SIMPLE_MODE):
		remove = []
		for node in extraoutputs:#extra porque ENTRADA de um flip flop
			if node not in original_inputs:
				if node in wiredata:
					wiredata.pop(wiredata.index(node)) #agora é uma i/o entao sai dos wires como estava antigamente
			else:
				remove.append(node)
				replacetext = extrainputs[extraoutputs.index(node)] #pega o nome da SAIDA do Flip Flop
				data = circuitreplace(data,replacetext,node)
		for itens in remove: #ja que já é um sinal de entrada, tirar os sinais das duas listas pois foi substituido
			extrainputs.pop(extraoutputs.index(itens))
			extraoutputs.pop(extraoutputs.index(itens))

		remove = []
		for extra in extrainputs:#SAIDA de um flip flop
			if extra in original_outputs:
				remove.append(extra)
				replacetext = extraoutputs[extrainputs.index(extra)] #pega o nome do seu input
				data = circuitreplace(data,replacetext,extra)
		for itens in remove: #ja que já é um sinal de entrada, tirar os sinais das duas listas pois foi substituido
			extraoutputs.pop(extrainputs.index(itens))
			extrainputs.pop(extrainputs.index(itens))
	return (data,extrainputs,extraoutputs,wiredata,original_inputs)		

def selectnodes(cell_list,currentnode,nodesused): #fazer com lista é mais rapido, ao custo de bastante memoria
	if cell_list[currentnode].computed == True:
		with open((currentnode.replace("\\","_backslash_") +'.msgpack'), 'rb') as data_file:
			indata = data_file.read()
			data_loaded = set(msgpack.unpackb(indata, raw=False))
		return data_loaded		  		
	nodesused.add(currentnode)
	for inputnode in cell_list[currentnode].inputs:
		nodesfrominput = selectnodes(cell_list,inputnode,set())
		nodesused.update(nodesfrominput)
	cell_list[currentnode].computed = True
	with open((currentnode.replace("\\","_backslash_") +'.msgpack'), 'wb') as outfile:
		outdata = list(nodesused)
		outfile.write(msgpack.packb(outdata, use_bin_type=True))
	return nodesused

def circuitreplace(data,replacetext,text):
	if "module " in data: #verilog
		if "assign" in data:
			data = data.replace(" "+replacetext+" "," "+text+" ")
			data = data.replace("~"+replacetext+" ","~"+text+" ")
			data = data.replace("~"+replacetext+";","~"+text+";")
			data = data.replace(" "+replacetext+";"," "+text+";")
		else:
			data = data.replace("("+replacetext+")","("+text+")")
	else: #bench
		data = data.replace("\n"+replacetext+" ","\n"+text+" ")
		data = data.replace("("+replacetext+")","("+text+")")
		data = data.replace("("+replacetext+",","("+text+",")
		data = data.replace(" "+replacetext+")"," "+text+")")
	return data	

def divideoutputs(mode,extraoutputs,extrainputs,original_inputs,original_outputs,data,namemodule,exportdata,numflipflops,dataenable): 
		masterdir = os.getcwd()
		os.mkdir("temp")		
		outputs = extraoutputs+original_outputs
		if mode == "verilog":
			cell_list = V_createcell_list(data,original_inputs,extrainputs)
		else:
			cell_list = B_createcell_list(data,original_inputs,extrainputs)
		data = data.split("\n")		

		if (dataenable):
			numinputscomb = []
			numdepthscomb = []
			keys = list(cell_list.keys()) 
			for signal in keys:
				for inputsignal in cell_list[signal].inputs:
					cell_list[inputsignal].drive = cell_list[inputsignal].drive + 1
			numcurrentfanoutcomb = 0
			for signal in keys:
				if cell_list[signal].drive > 1:
					numcurrentfanoutcomb = numcurrentfanoutcomb + 1
			numcurrentsignals = len(keys)
			inputset = set(extrainputs + original_inputs)
			outputset = set(extraoutputs + original_outputs)
			numcurrentgates = numcurrentsignals - len(inputset)
			numcurrentoutputs = len(outputset)
			numcurrentinputs = len(inputset)
				
		numinputs = []
		numfanouts =[]
		numdepths = [] 
		numgates = []
		numsignals = []
		gateinfluence = []
		for output in outputs: #percorre todos os outputs
			newdata = [] #começo do novo arquivo (p/ colocar na função de criar arquivo depois)
			keptlines = [] #linhas de data que vao para o output
			currentwires = []
			nodesused = []
			endcheck = True
			currentnode = [output]

			os.chdir(masterdir + "\\" + "temp")
			nodesused = selectnodes(cell_list,currentnode[0],set())
			os.chdir(masterdir)

			inputs = []
			if (dataenable):
				cell_list[output].influence = cell_list[output].influence + 1
				for inputsignal in cell_list[output].inputs:
					cell_list[inputsignal].drive = cell_list[inputsignal].drive + 1
				if data[cell_list[output].line] not in newdata:
					newdata.append(data[cell_list[output].line])
				for node in nodesused:
					cell_list[node].drive = 0 
				for node in nodesused:
					if cell_list[node].isinput:
						inputs.append(node)
						cell_list[node].influence = cell_list[node].influence + 1
					else:
						currentwires.append(node)
						cell_list[node].influence = cell_list[node].influence + 1
						if data[cell_list[node].line] not in newdata:
							newdata.append(data[cell_list[node].line])
						for inputsignal in cell_list[node].inputs:
							cell_list[inputsignal].drive = cell_list[inputsignal].drive + 1
				numinputs.append(len(inputs))
				numsignals.append(len(nodesused))
				circuitdepth = depthcalculator(cell_list,output,output,(currentwires + [output]),inputs)
				resetdepthcalculator(cell_list)
				numdepths.append(circuitdepth)
				numcurrentfanout = 0
				for signal in nodesused:
					if cell_list[signal].drive > 1:
						numcurrentfanout = numcurrentfanout + 1
				numfanouts.append(numcurrentfanout)
				gatenumber = len(currentwires)
				numgates.append(gatenumber)
			else: #possivel de fazer isso na recursao tbm
				if data[cell_list[output].line] not in newdata:
					newdata.append(data[cell_list[output].line])
				for node in nodesused:
					if cell_list[node].isinput:
						inputs.append(node)
					else:
						currentwires.append(node)
						if data[cell_list[node].line] not in newdata:
							newdata.append(data[cell_list[node].line])
			newmodule = namemodule.strip() + "_" + output + " "

			if mode == "verilog":
				newdata.append("\nendmodule\n")
				newdata = "\n".join(newdata)
				newdata = V_createfile(newdata,[],[],[output],inputs,currentwires,newmodule,True)
			else:
				newdata = "\n".join(newdata)
				newdata = B_createfile(newdata,[],[],[output],inputs,currentwires,namemodule,True)

			try:
				if mode == "verilog":
					arq2 = Arquive(newmodule.rstrip() + ".v")
				else:
					arq2 = Arquive(newmodule.rstrip() + ".bench")	
				arq2.save(newdata)
			except:
				print("Erro ao salvar o arquivo!")
				pass


		if (dataenable):
			influencevector = []
			mostimportantsignals  = []
			mostimportantsignalsnum = 0		
			for signal, sigdata in cell_list.items():
				influencevector.append(sigdata.influence)
				if sigdata.influence > mostimportantsignalsnum:
					mostimportantsignals = [signal]
					mostimportantsignalsnum = sigdata.influence
				elif sigdata.influence == mostimportantsignalsnum:
					mostimportantsignals.append(signal)

			segmentdata = {}
			segmentdata["namemodule"] = namemodule
			segmentdata["numinputs"] = numinputs
			segmentdata["numfanouts"] = numfanouts
			segmentdata["numdepths"] = numdepths
			segmentdata["numgates"] = numgates
			segmentdata["numsignals"] = numsignals
			segmentdata["influencevector"] = influencevector
			segmentdata["mostimportantsignals"] = mostimportantsignals
			segmentdata["numflipflops"] = numflipflops
			segmentdata["original_inputs"] = len(original_inputs)
			segmentdata["original_outputs"] = len(original_outputs)
			segmentdata["numgatescomb"] = numcurrentgates
			segmentdata["numsignalscomb"] = numcurrentsignals
			segmentdata["numoutputscomb"] = numcurrentoutputs
			segmentdata["numinputscomb"] = numcurrentinputs
			segmentdata["numfanoutscomb"] = numcurrentfanoutcomb

			exportdata.append(segmentdata)

		cell_list = {}	

		shutil.rmtree('temp')
		return 0
	