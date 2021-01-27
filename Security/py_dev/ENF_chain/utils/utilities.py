'''
========================
utilities.py
========================
Created on Dec.8, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility function to support project.
@Reference: 
'''

from datetime import datetime, timedelta
import hashlib
import json
import pickle
import glob, os, fnmatch
import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt

'''
FileUtil class for handling file data
'''
class FileUtil(object):
	@staticmethod
	def csv_read(csv_file):
		'''
		Function: Read data from csv file
		@arguments: 
		(out) np_dataset:   	return np.array object
		(in) csv_file:   		csv file path
		'''
		ls_dataset = []
		with open(csv_file, 'r') as csvFile:
			csv_reader = csv.reader(csvFile, delimiter=',')
			for row in csv_reader:
				ls_dataset.append(row)
		# transfer to np array and return
		np_dataset = np.array(ls_dataset)
		return np_dataset

	@staticmethod
	def csv_write(csv_file, dataset):
		'''
		Function: Write data to csv file
		@arguments: 
		(in) dataset:   	np.array data
		(in) csv_file:   	csv file path
		'''
		ls_dataset = []
		with open(csv_file, 'a') as csvFile:
			csv_writer = csv.writer(csvFile, delimiter=',')
			for row in dataset:
				csv_writer.writerow(row)

	@staticmethod
	def ReadLines(filepath):
		'''
		Function:read line contents from file
		@arguments: 
		(in)  filepath:   	input file path
		(out) ls_lines:   	return line list object
		'''
		#define file handle to open select file
		fname = open(filepath, 'r')    
		#read text by line and saved as array list ls_lines
		ls_lines=fname.readlines()
		#close file
		fname.close()
		return ls_lines
	
	@staticmethod
	def AddLine(filepath, linedata):
		'''
		Function: write line string to file
		@arguments: 
		(in)  filepath:   	input file path
		(in)  linedata:   	line data for writing
		'''
		#define file handle to open select file for appending data
		fname = open(filepath, 'a') 
		
		#write line data to file
		fname.write("%s\n" %(linedata))
		
		#close file
		fname.close()
	
	@staticmethod
	def AddDataByLine(filepath, ls_data):
		'''
		Function: write list data to file by each line
		@arguments: 
		(in)  filepath:   	input file path
		(in)  ls_data:   	list data for writing
		'''
		#define file handle to open select file for write data
		fname = open(filepath, 'w') 
		
		#for each lines in data and write to file
		for linedata in ls_data:
			#write line data to file
			fname.write("%s\n" %(linedata))
		
		#close file
		fname.close()
	
	@staticmethod
	def DeleteLine(filepath, str_target):
		'''
		Function: remove line containing target string from file
		@arguments: 
		(in)  filepath:   	input file path
		(in)  str_target:   target string for delete
		'''
		#First, read all data from file
		fname = open(filepath, 'r')   
		ls_lines=fname.readlines()	
		fname.close()	

		#reopen file with 'w' option
		fname = open(filepath, 'w')
		
		#for each line to rewrite all data except ls_data
		for line in ls_lines:
			if((str_target in line) or line=='\n'):
				continue
			#write line data to file
			fname.write("%s" %(line))
		#close file
		fname.close()

	@staticmethod
	def UpdateLine(filepath, str_target, str_line):
		'''
		Function: update line containing target string in file
		@arguments: 
		(in)  filepath:   	input file path
		(in)  str_target:   target string for delete
		'''	
		#First, read all data from file
		fname = open(filepath, 'r')   
		ls_lines=fname.readlines()	
		fname.close()	

		#reopen file with 'w' option
		fname = open(filepath, 'w')
		
		#for each line to rewrite all data
		for line in ls_lines:
			if(str_target in line):
				#write updated data to file
				fname.write("%s" %(str_line))
			else:
				#write unchanged line to file
				fname.write("%s" %(line))
		#close file
		fname.close()
	
	@staticmethod
	def List_save(filepath, list_data):
		"""
		Save the list of nodes to file
		"""
		fname=open(filepath, 'wb') 
		pickle.dump(list_data, fname)
		fname.close()

	@staticmethod
	def List_load(filepath):
		"""
		Load list from file
		"""
		fname=open(filepath, 'rb') 
		list_data = pickle.load(fname)
		fname.close() 
		return list_data
	
	@staticmethod
	def JSON_save(filepath, json_data):
		"""
		Save the JSON data to file
		"""
		fname = open(filepath, 'w') 
		#json_str = json.dumps(json_data)
		json_str=TypesUtil.json_to_string(json_data)
		fname.write("%s" %(json_str))
		fname.close()
		
	@staticmethod
	def JSON_load(filepath):
		"""
		Load JSON data from file
		"""
		fname = open(filepath, 'r') 
		json_str=fname.read()
		fname.close()
		#json_data = json.loads(json_str)
		json_data=TypesUtil.string_to_json(json_str)
		return json_data
		

	@staticmethod
	def list_files(dir_path="./", reg_str='*'):
		'''
		Function: list all files in dir_path directory based on reg_str condition
		@arguments: 
		(in)    dir_path:   directory path for file search. set current path as default directory
		(in)    reg_str:   	input regex string to filter files, eg, *.log. list all files as default
		(out)   ls_files:   	return listed files
		'''
		# save pwd for restore path
		pwd = os.getcwd()
		os.chdir(dir_path)
		ls_files=[]
		for file in glob.glob(reg_str):
			ls_files.append(file)
		
		# restore original path
		os.chdir(pwd)
		return ls_files

	@staticmethod
	def save_testlog(test_dir, log_file, log_data):
		#save new key files
		#test_dir = 'test_results'
		if(not os.path.exists(test_dir)):
			os.makedirs(test_dir)
		test_file = test_dir + '/' + log_file
		FileUtil.AddLine(test_file, log_data)
		
'''
DatetimeUtil class for format handle between datatime and string
'''
class DatetimeUtil(object):
	#switch int timestamp to datatime object
	@staticmethod
	def timestamp_datetime(_timestamp):
		obj_datetime=datetime.fromtimestamp(_timestamp/1e3)
		return obj_datetime

	#switch datatime object to int timestamp
	@staticmethod
	def datetime_timestamp(_datetime):
		int_datetime=int(_datetime.timestamp() * 1e3)
		return int_datetime

	#switch datatime object to format string
	@staticmethod
	def datetime_string(_datetime, _format="%Y-%m-%d %H:%M:%S"):
		str_datetime=_datetime.strftime(_format)
		return str_datetime
		
	#switch format string to datatime object
	@staticmethod
	def string_datetime(_strtime, _format="%Y-%m-%d %H:%M:%S"):
		_datetime=datetime.strptime(_strtime, _format)
		return _datetime
		
	#get datatime duration from format input
	@staticmethod
	def datetime_duration(_weeks=0,_days=0,_hours=0,_minutes=0):
		_duration=timedelta(weeks=_weeks,days=_days,hours=_hours,minutes=_minutes)
		return _duration
		
	#check whether input datatime has expired
	@staticmethod
	def IsExpired(str_datatime):
		time1=DatetimeUtil.string_datetime(str_datatime)
		time2=datetime.now()
		diff = (time1-time2).total_seconds()
		if(diff>0):
			return False
		else:
			return True
			
'''
TypesUtil class for data type format transfer
'''
class TypesUtil(object):
	# list dataset to numpy matrix
	@staticmethod
	def list2np(ls_data):
		# transfer to np array and return
		np_data = np.array(ls_data, dtype=np.float32)
		return np_data

	# numpy matrix to list dataset
	@staticmethod
	def np2list(np_data):
		# transfer to list dataset and return
		ls_data = np_data.tolist()
		return ls_data

	#integer to hex
	@staticmethod
	def int_to_hex(int_data):
		return hex(int_data)
		
	#hex to integer
	@staticmethod
	def hex_to_int(hex_data):
		return int(hex_data, 16)
		
	#string to hex
	@staticmethod
	def string_to_hex(str_data):
		hex_data=str_data.hex()
		return hex_data
		
	#hex to string
	@staticmethod
	def hex_to_string(hex_data):
		str_data=bytes.fromhex(hex_data)
		return str_data
		
	#string to bytes
	@staticmethod
	def string_to_bytes(str_data):
		bytes_data=str_data.encode(encoding='UTF-8')
		return bytes_data
		
	#bytes to string
	@staticmethod
	def bytes_to_string(byte_data):
		str_data=byte_data.decode(encoding='UTF-8')
		return str_data
		
	#string to json
	@staticmethod
	def string_to_json(json_str):
		json_data = json.loads(json_str)
		return json_data
		
	#json to string
	@staticmethod
	def json_to_string(json_data):
		json_str = json.dumps(json_data)
		return json_str

	#json list to string
	@staticmethod
	def jsonlist_to_string(json_list):
		list_str="|".join(TypesUtil.json_to_string(e) for e in json_list)
		return list_str

	#string to json list
	@staticmethod
	def string_to_jsonlist(str_data):
		list_data=str_data.split('|')
		json_list=[]
		for data in list_data: 
			json_list.append(TypesUtil.string_to_json(data))
		return json_list

	# get hashed json data
	@staticmethod
	def hash_json(json_block, hash_type='sha256'):
		"""
		Create a SHA-256 hash of a json block
		"""
		# We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
		block_string = json.dumps(json_block, sort_keys=True).encode()

		if(hash_type=='sha1'):
			return hashlib.sha1(block_string).hexdigest()
		elif(hash_type=='sha256'):
			return hashlib.sha256(block_string).hexdigest()
		else:
			return None

'''
FuncUtil class to support utils functions
'''
class FuncUtil(object):
	# sha 256 hash func
	@staticmethod
	def hashfunc_sha256(data_value):
		return hashlib.sha256(data_value).hexdigest()

	# sha1 hash func
	@staticmethod
	def hashfunc_sha1(data_value):
		return hashlib.sha1(data_value).hexdigest()

'''
PlotUtil class for data visualization
'''
class PlotUtil(object):
	@staticmethod
	def Plotline(ENF_dataset, legend_label='', font_size=14, is_show=True, is_savefig=False, datafile=''):
		'''
		Function: plot ENF data as line on fig
		@arguments: 
		(in) ENF_dataset: 	ENF list dataset that can input two ENF signals
			   font_size:	font size for label and legend
			     is_show:	Display plot on screen
			  is_savefig:	Save plot on local as *.png
			  	datafile:	file name to save plot
		'''
		ls_color=['green', 'seagreen', 'darkorange', 'r', 'g', 'b', 'gray']
		leg_label = []
		for ENF_id in range(len(ENF_dataset)):
			#generate x and y data
			xdata = [];
			ydata = [];
			ls_dataset = ENF_dataset[ENF_id]
			for i in range(0, len(ls_dataset)):
				xdata.append(i)
				ydata.append( float(ls_dataset[i][1]) )

			line_list=[]
			line_list.append(plt.plot(xdata, ydata, lw=2.0, color=ls_color[ENF_id]))
			leg_label.append("ENF-{}".format(ENF_id))

		plt.xlabel('Time slot', fontsize=font_size)
		plt.ylabel('ENF (HZ)', fontsize=font_size) 
		# plt.ylim(59.995, 60.005)
		if(legend_label == ''):
			plt.legend(leg_label, loc='best', fontsize=font_size)
		else:
			plt.legend(legend_label, loc='best', fontsize=font_size)
		
		if( is_show ):
			plt.show()
		if( is_savefig ):
			figname = os.path.splitext(datafile)[0] +'.png'
			plt.savefig(figname)
		plt.close()
