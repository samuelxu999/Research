#!/usr/bin/env python

'''
========================
utilities.py
========================
Created on Oct.23, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility function to support project.
@Reference: 
'''

from datetime import datetime, timedelta

'''
FileUtil class for handling file data
'''
class FileUtil(object):

	'''
	Function:read line contents from file
	@arguments: 
	(input)  filepath:   	input file path
	(out)    ls_lines:   	return line list object
	'''
	@staticmethod
	def ReadLines(filepath):
		#define file handle to open select file
		fname = open(filepath, 'r')    
		#read text by line and saved as array list ls_lines
		ls_lines=fname.readlines()
		#close file
		fname.close()
		return ls_lines
	
	@staticmethod
	def AddLine(filepath, linedata):
		#define file handle to open select file for appending data
		fname = open(filepath, 'a') 
		
		#write line data to file
		fname.write("%s" %(linedata))
		
		#close file
		fname.close()
	
	@staticmethod
	def DeleteLine(filepath, str_target):
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
		
'''
DatetimeUtil class for format handle between datatime and string
'''
class DatetimeUtil(object):
	#switch datatime object to format string
	@staticmethod
	def datetime_string(_datetime, _format="%Y-%m-%d %H:%M:%S"):
		str_datetime=_datetime.strftime(_format)
		return str_datetime
		
	#switch format string to datatime object
	@staticmethod
	def string_datetime(_strtime, _format="%Y-%m-%d %H:%M:%S"):
		_datetime=datetime.strptime(_strtime, "%Y-%m-%d %H:%M:%S")
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
