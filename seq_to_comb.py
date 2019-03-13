#encoding=utf-8
import sys

sys.path.append("./imports/class")
sys.path.append("./imports/function")

import datetime
from statistics import *
import os
from performancetimer import *
from arquive import Arquive
from circuit_module import *
from verilogfunctions import *
from benchfunctions import *
from circuit_class import *
		
temporizador1 = TIMERN()
masterdir = os.getcwd()
dataenable = False
exportdata = []

inscript = False
while True:
	if inscript == True: #Passa para a proxima linha do script
		datascript.pop(0)
		if len(datascript) == 0:
			inscript = False
		else:
			choice = datascript[0][0]
	if inscript == False:
		choice = input("Digite 1 p/ converter um verilog e 2 p/ converter um bench, 3 para um script, 4 para extrair dados dos circuitos convertidos, 5 computar arquivos de uma pasta, 6 para permitir/cancelar a extraçao de dados, 0 p/ sair : ")
	if choice == "1" or choice == "2":
		verilog = True
		if choice == "2":
			verilog = False
		if inscript == True:
			choice = datascript[0][1]
		else:	
			choice = input ("Digite o nome do arquivo (com extensão): ")
		try:
			arq = Arquive(choice)
			data = arq.load()
		except:
			print("Erro ao carregar o arquivo")
			break
		temporizador1.Pstarttimer()
		extrainputs = []
		extraoutputs = []
		original_outputs = []
		original_inputs = []
		wiredata = []
		namemodule = []
		numflipflops = 0
		clockname = "*-Nil-*"
		if verilog:
			try: #so para ver se funciona os combinacional puro
				(data,extrainputs,extraoutputs,clockname,numflipflops) = V_extractextrasignals(data)
				data = V_deleteline("reg ",data)
			except:
				print("Circuito Comb.")	
				numflipflops = 0
			(data,namemodule) = V_moduleextract(data)
			(data,original_outputs) = V_findextractline("output ",data)
			(data,original_inputs) = V_findextractline("input ",data)
			(data,wiredata) = V_findextractline("wire ",data)
			try:
				(data,extrainputs,extraoutputs,wiredata,original_inputs) = fixIO(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,clockname)
			except:
				print("Erro ao fazer os casos especiais.")
				pass
		else:
			data = data[(data.index("INPUT")):] #para tirar qualquer comentario do começo
			if "\\" in choice: # p/ tirar o path
				newchoice = choice[::-1] # inverte
				location = newchoice.index("\\") #pega a posiçao do primeiro "\"
				newchoice = newchoice[:location] #pega tudo antes do primeiro "\"
				namemodule = newchoice[::-1] #inverte denovo
				namemodule = namemodule.replace(".bench","") # tira o bench
			else:
				namemodule = choice.replace(".bench","")
			(data,original_inputs) = B_findextractline("INPUT",data)
			(data,original_outputs) = B_findextractline("OUTPUT",data)
			wiredata = []
			try: #test para combinacionais puros
				(data,extrainputs,extraoutputs,clockname,numflipflops) = B_extractextrasignals(data)
			except:
				print("Circuito Comb.")
				numflipflops = 0
			try:
				(data,extrainputs,extraoutputs,wiredata,original_inputs) = fixIO(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,clockname)
			except:
				print("Erro ao fazer os casos especiais.")
				pass		
		#ISSO SÓ PARA DEIXAR O ARQUIVO MAIS BONITO
		data = data.split("\n")
		cont = 0
		while cont < len(data):
			data[cont] = data[cont].lstrip()
			cont = cont + 1
		data = "\n".join(data)
		#######################################
		temporizador1.Pstoptimer()
		print("Tempo do processo (Parser, " + namemodule.strip() +"): ")
		temporizador1.show_time()
		if inscript == True:
			choice = datascript[0][2]
		else:
			choice = input ("Deseja separar o arquivo p/ cada saida? \"N\" para não, \"A\" para ambos, resto p/ sim: ")
		if choice == "A" or choice == "a":
			os.mkdir(namemodule)
			os.chdir(masterdir + "\\" + namemodule)
		if choice == "N" or choice == "n" or choice == "A" or choice == "a":
			temporizador1.Pstarttimer()
			if verilog:
				dataout = V_createfile(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,namemodule)
			else:
				dataout = B_createfile(data,extraoutputs,extrainputs,original_outputs,original_inputs,wiredata,namemodule)
			temporizador1.Pstoptimer()
			print("Tempo do processo (Salvar Comb, "+ namemodule.strip() +"): ")
			temporizador1.show_time()
			if choice == "A" or choice == "a":
				try:
					if verilog:
						arq2 = Arquive(namemodule.strip() + "_comb.v")
					else:
						arq2 = Arquive(namemodule.strip() + "_comb.bench")	
					arq2.save(dataout)
				except:
					print("Erro ao salvar o arquivo")
					break
			else:
				if inscript == True:
					choice2 == datascript[0][3]
				else:
					choice2 = input ("Digite o nome do arquivo novo (com extensão): ")
				try:
					arq2 = Arquive(choice2)
					arq2.save(dataout)
				except:
					print("Erro ao salvar o arquivo")
					break
		if choice != "N" and choice != "n":
			temporizador1.Pstarttimer()
			if verilog:
				divideoutputs("verilog",extraoutputs,extrainputs,original_inputs,original_outputs,data,namemodule,exportdata,numflipflops,dataenable)  
			else:
				divideoutputs("bench",extraoutputs,extrainputs,original_inputs,original_outputs,data,namemodule,exportdata,numflipflops,dataenable) 
			temporizador1.Pstoptimer()
			print("Tempo do processo (Dividir Saidas, "+namemodule.strip()+"): ")
			temporizador1.show_time()
		if choice == "A" or choice == "a":
			os.chdir(masterdir)
	elif choice == "3" and inscript == False:
		choice = input ("Digite o nome do arquivo (com a extensão .txt): ")
		inscript = True
		try:
			arq = Arquive(choice)
			datascript = arq.load()
			datascript = datascript.split("\n")
			i = 1
			while i < len(datascript):
				datascript[i] = datascript[i].split(" ")
				i = i + 1
		except:
			print("Erro ao carregar o arquivo")
			inscript = False
			break
	elif choice == "4" and dataenable:
		exporttextdata = ""
		for moduledata in exportdata:
			exporttextdata = exporttextdata + moduledata["namemodule"].rstrip() + " " + str(moduledata["numflipflops"]) + " " + str(moduledata["original_inputs"]) + " " + str(moduledata["original_outputs"]) + " " + str(moduledata["numgatescomb"]) + " " + str(moduledata["numinputscomb"]) + " "
			exporttextdata = exporttextdata + str(moduledata["numoutputscomb"]) + " " + str(moduledata["numfanoutscomb"]) + " " + str(moduledata["numsignalscomb"]) + " "
			exporttextdata = exporttextdata + str(max(moduledata["numdepths"])) + " " + str(mean(moduledata["numdepths"])) + " " + str(pstdev(moduledata["numdepths"])) + " "
			exporttextdata = exporttextdata + str(max(moduledata["numinputs"])) + " " + str(mean(moduledata["numinputs"])) + " " + str(pstdev(moduledata["numinputs"])) + " "
			exporttextdata = exporttextdata + str(max(moduledata["numfanouts"])) + " " + str(mean(moduledata["numfanouts"])) + " " + str(pstdev(moduledata["numfanouts"])) + " "
			exporttextdata = exporttextdata + str(max(moduledata["numgates"])) + " " + str(mean(moduledata["numgates"])) + " " + str(pstdev(moduledata["numgates"])) + " "
			exporttextdata = exporttextdata + str(max(moduledata["numsignals"])) + " " + str(mean(moduledata["numsignals"])) + " " + str(pstdev(moduledata["numsignals"])) + " "
			exporttextdata = exporttextdata + str(max(moduledata["influencevector"])) + " " + str(mean(moduledata["influencevector"])) + " " + str(pstdev(moduledata["influencevector"])) + " " + str(min(moduledata["influencevector"])) + "\n"
			
		try:
			arq3 = Arquive("exporteddata.txt")
			arq3.save(exporttextdata)
		except:
			print("Erro ao salvar o arquivo!")
			break
		exporttextdata = ""
		for moduledata in exportdata:
			exporttextdata = exporttextdata + moduledata["namemodule"] + "\n"
			exporttextdata = exporttextdata + "Depth: " + " ".join(str(x) for x in moduledata["numdepths"]) + "\n"
			exporttextdata = exporttextdata + "Inputs: " +  " ".join(str(x) for x in moduledata["numinputs"]) + "\n"	
			exporttextdata = exporttextdata + "Fanouts: " +  " ".join(str(x) for x in moduledata["numfanouts"]) + "\n"
			exporttextdata = exporttextdata + "Gates: " +  " ".join(str(x) for x in moduledata["numgates"]) + "\n"
			exporttextdata = exporttextdata + "Signals: : " +  " ".join(str(x) for x in moduledata["numsignals"]) + "\n"
			exporttextdata = exporttextdata + "Influence/gate: " +  " ".join(str(x) for x in moduledata["influencevector"]) + "\n"			
			exporttextdata = exporttextdata + "Most_important_signals: " + str(moduledata["mostimportantsignals"]) + "\n"
			exporttextdata = exporttextdata + "\n"
		try:
			arq4 = Arquive("exportedrawdata.txt")
			arq4.save(exporttextdata)
		except:
			print("Erro ao salvar o arquivo!")
			break
	elif choice == "5":
		if inscript == True:
			choice = datascript[0][1]
		else:	
			choice = input ("Digite o nome da pasta: ")
			datascript = []
			datascript.append(["---"])
		try:
			filelist = os.listdir(os.getcwd() + "\\" + choice)
			for file in filelist:
				if ".v" in file:
					if inscript == True:
						datascript.insert(1, ["1",(os.getcwd() + "\\" + choice + "\\" + file),"a"])
					else:
						datascript.append(["1",(os.getcwd() + "\\" + choice + "\\" + file),"a"])	
				else:
					if inscript == True:
						datascript.insert(1,["2",(os.getcwd() + "\\" + choice + "\\" + file),"a"])
					else:
						datascript.append(["2",(os.getcwd() + "\\" + choice + "\\" + file),"a"])	
			inscript = True		
		except:
			print("Erro ao carregar a pasta")
			inscript = False
			break
	elif choice == "6":
		if dataenable:
			dataenable = False
		else:
			dataenable = True	 		
	elif choice == "0":
		break
	else:
		print("Número ou comando inválido! Tente novamente!\n")
	print("\n")
