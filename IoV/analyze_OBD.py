#!/usr/bin/python

'''
Created on April 16, 2017

@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: 
1) Extract OBD data in *.csv.
2) plot based on OBD data
'''
import sys
import re
import datetime
import glob, os

import matplotlib.pyplot as plt
import numpy as np

'''
Function:read line contents from file
@arguments: 
(input)  filepath:   	input file path
(out)    ls_lines:   	return line list object
'''
def ReadLines(filepath):
	#define file handle to open select file
	fname = open(filepath, 'r')    
	#read text by line and saved as array list ls_lines
	ls_lines=fname.readlines()
	#close file
	fname.close()
	return ls_lines
    
'''
Function: split line string and saved record as array list.
@arguments: 
(in)    ls_line:   		input line list to parse need information
(out)   ls_info:   		return split line data
'''
def Parselines(ls_line):
	#Define ls_info[] to save split data	
	ls_info=[]
	
	# 1.split each line racord into ls_info[]
	for tmp_line in ls_line:
		ls_data=[]
		#remove redundent strings
		if("Device Time" in tmp_line):
			continue
		
		tmp_line=tmp_line.replace("\n" , "")			
		#remove empty line
		if(len(tmp_line.split())!=0):
			tmp_data=tmp_line.split(',')
			if("-"==tmp_data[5] or "-"==tmp_data[6] or "-"==tmp_data[7] or "-"==tmp_data[8]):
				continue
			#add time
			ls_data.append(tmp_data[0])
			#add Speed (OBD)(km/h)
			ls_data.append(tmp_data[5])
			#add Engine RPM(rpm)
			ls_data.append(tmp_data[6])
			#add Engine Load(%)
			ls_data.append(tmp_data[7])
			#add Engine Load(Absolute)(%)
			ls_data.append(tmp_data[8])
			ls_info.append(ls_data)
		#print(ls_data)
	return ls_info
 
'''
Function: split line string and saved record as array list.
@arguments: 
(in)    ls_line:   		input line list to parse need information
(out)   ls_info:   		return split line data
'''
def plot_ODB(ls_records):
	x=[]
	Speed=[]
	Engine_RPM=[]
	Engine_Load=[]
	ABS_Engine_Load=[]
	
	#prepare data for plot
	i=1
	for record in ls_records:
		x.append(i)
		Speed.append(record[1])
		Engine_RPM.append(record[2])
		Engine_Load.append(record[3])
		ABS_Engine_Load.append(record[4])
		i+=1
	
	#define figure
	plt.figure(22)  
	
	#-----------subplot-Speed-----------
	plt.subplot(221)
	#labels
	plt.xlabel("Time slot (Sec)")
	plt.ylabel("Speed(km/h)")
	#plot data
	plt.plot(x, Speed)
	
	#-----------subplot-Engine_RPM-----------
	plt.subplot(222)
	#labels
	plt.xlabel("Time slot (Sec)")
	plt.ylabel("Engine RPM(rpm)")
	#plot data
	plt.plot(x, Engine_RPM)
	
	#-----------subplot-Engine Load-----------
	plt.subplot(223)
	#labels
	plt.xlabel("Time slot (Sec)")
	plt.ylabel("Engine Load(%)")
	#plot data
	plt.plot(x, Engine_Load)
	
	#-----------subplot-Engine Load(Absolute)-----------
	plt.subplot(224)
	#labels
	plt.xlabel("Time slot (Sec)")
	plt.ylabel("Engine Load(Absolute)(%)")
	#plot data
	plt.plot(x, ABS_Engine_Load)
	
	#plt.savefig("test.pdf")
	
	#show plot
	plt.show()


'''
Function: list all OBD files(*.csv) in current directory
@arguments: 
(in)    reg_str:   	input regex string to filter files
(out)   ls_logs:   	return scanlog files
'''
def list_log(reg_str):
	#set current path as default directory
	os.chdir("./")
	#reg_str="tcpdump*"
	ls_logs=[]
	for file in glob.glob(reg_str):
		ls_logs.append(file)
		#print(file)
	return ls_logs
	
'''
Function: used as main for executing data aggregation and plot
@arguments: NULL
'''
def main(): 
    #Check argument validation
	if(len(sys.argv)<2):
		print("Usage: %s @regex\nExample:%s *.csv" %(sys.argv[0],sys.argv[0]))
		return -1
	
	#define regex_str to filter data files
	regex_str=sys.argv[1]
	
    #get all OBD data files under current directory
	ls_scanlog=[]
	ls_scanlog=list_log(regex_str)

	#save aggregated data
	ls_data=[]
	
    #========================== aggregate data for each log file =================================
	for logname in ls_scanlog:		
		#read log file and save data as arraylist ls_line
		ls_line=ReadLines(logname)
		print("Extract OBD data from '%s'." %(logname))	
		
		#handle line list data and save result as ls_info	
		ls_info=Parselines(ls_line)
		#aggregate data as ls_data[]
		for tmp_data in ls_info:
			ls_data.append(tmp_data)
	#plot based on ls_data[]
	plot_ODB(ls_data)
	
	return 0

  
#Call main function   
if __name__ == "__main__":
    main()
    