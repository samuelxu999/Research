#!/usr/bin/env python

'''
========================
pkt_analysis
========================
Created on Oct.18, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide packet analysis function, such as extract data.
@Reference: 
'''

import ast
import sys
from scapy.all import *
from utilities import DatetimeUtil, FileUtil

'''
FileUtil class for handling packet data 
'''
class PktData(object):
	#static class variable
	split_layer_tag=['Ether', 'IP', 'IPv6', 'ARP', 'UDP', 'ICMP']
	
	'''
		Extract all data from packet and saved as [layer, value] list
		@pkt: packet raw data from sniff
		@op_mode: 0-return raw data list; 1-return split options data list
	'''
	@staticmethod
	def extract_data_from_packet(pkt, op_mode=0):
		#transfer pkt to command string
		cmd_str=pkt.command()    
		#print(cmd_str)
		
		
		#=============split cmd_str to get header and raw data==============
		tmp=cmd_str.split('/Raw')
		headers=tmp[0]
		
		#add raw payload to raw_data
		raw_data=[]
		if(len(tmp)>1):
			raw_data.append(tmp[1][1:5])
			raw_data.append(tmp[1][7:-2])
		
		#print headers
		#print raw_data
		'''if(raw_data!=[]):
			print hexdump(raw_data[1])'''
		
		#===================split header into individual layers==============
		layers=headers.split('/')
		#print layers
		
		pkt_data=[]
		for layer in layers: 
			layer_data=[]    
			#get layer name and options list
			seg_tag=layer.find('(')
			layer_name=layer[:seg_tag]
			layer_value=layer[seg_tag+1:-1]
			
			if(op_mode==1):
				#split options
				layer_options=[]        
				if(layer_name in PktData.split_layer_tag):
					#split options
					ls_options=layer_value.split(', ')
					#seperate [op=value]
					for op in ls_options:
						tmp=op.split('=')
						#print '---'+tmp[0]+':'+tmp[1].replace("'", '')
						layer_options.append(tmp)
				elif(layer_name=='TCP'):
					seg=layer_value.find('options')
					if(seg!=-1):
						ls_options=layer_value[:seg-2].split(', ')
						ls_options.append(layer_value[seg:])
					else:
						ls_options=layer_value.split(', ')
					#seperate [op=value]
					for op in ls_options:
						tmp=op.split('=')
						#print '---'+tmp[0]+':'+tmp[1].replace("'", '')
						layer_options.append(tmp)
				else:
					#print '---'+layer_data[1]
					layer_options.append(layer_value)
			
			
			layer_data.append(layer_name)
			
			#add option value based on op_mode
			if(op_mode==1):
				layer_data.append(layer_options)
			else:
				layer_data.append(layer_value)
				
			#add layer_data list to pkt_data
			pkt_data.append(layer_data)
		
		#add raw_data list to pkt_data
		if(raw_data!=[]):
			pkt_data.append(raw_data)
		
		return pkt_data


	'''
		Print out packet data
		@ls_data: extracted pkt data
		@op_mode: 0-use raw data list; 1-use split options data list 
	'''
	@staticmethod
	def display_data(ls_data, op_mode=0):
		print('======================================================')
		#print ls_data

		for layer_data in ls_data:
			#get tag and value
			layer_tag=layer_data[0]
			layer_value=layer_data[1]
			 
			print layer_tag        
			#print option value based on op_mode
			if(op_mode==0):
				if(layer_tag in PktData.split_layer_tag):
					#split options
					ls_options=layer_value.split(', ')
					#seperate [op=value]
					for op in ls_options:
						tmp=op.split('=')
						print '---'+tmp[0]+':'+tmp[1].replace("'", '')
				elif(layer_tag=='TCP'):
					seg=layer_value.find('options')
					if(seg!=-1):
						ls_options=layer_value[:seg-2].split(', ')
						ls_options.append(layer_value[seg:])
					else:
						ls_options=layer_value.split(', ')
					#seperate [op=value]
					for op in ls_options:
						tmp=op.split('=')
						print '---'+tmp[0]+':'+tmp[1].replace("'", '')
				else:
					print '---'+layer_value
			else:
				if(layer_tag!='load'):
					ls_options=layer_value
					if(len(ls_options)>1):
						for op in ls_options:
							print '---'+op[0]+':'+op[1].replace("'", '')
					else:
						print '---'+ls_options[0]
				else:
					print '---'+layer_value
					#hexdump(layer_value)
		print('\n')
	
	'''
		Save packet data to log file
		@filepath: log file path
		@ls_data: extracted pkt data
	'''
	@staticmethod
	def log_data(filepath, ls_data):
		ls_record=[]
		curr_time=DatetimeUtil.datetime_string(datetime.now())
		ls_record.append(curr_time)
		ls_record.append(ls_data)
		#print ls_record
		
		#write to log file
		FileUtil.AddLine(filepath, ls_record)

	'''
		Read packet data from log file
		@filepath: log file path
		@ls_data: extracted pkt data
	'''
	@staticmethod
	def read_log(filepath):
		ls_lines=FileUtil.ReadLines(filepath)
		ls_data=[]
		for line in ls_lines:
			#read list from line files
			ls_data.append(ast.literal_eval(line))
		return ls_data