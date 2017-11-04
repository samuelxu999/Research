#!/usr/bin/env python

'''
========================
filter_list.py
========================
Created on Nov.3, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide filter list management.
@Reference: https://www.sqlite.org/
'''

import sqlite3
import time
from datetime import datetime
from utilities import FileUtil, DatetimeUtil

'''
FilterList class for manage filter list by using file I/O API
'''
class FilterList(object):
	#Display filter list information
	@staticmethod
	def display(f_name):
		ls_line=FileUtil.ReadLines(f_name)
		print("Type\t Target\t\t\t Start from\t\t\t Valid before")
		for line in ls_line:
			line=line.replace('\n','')	
			#skip empty line
			if(line==''):
				continue			
			ls_data=line.split('; ')
			print("%-5s\t %-20s\t %s\t\t %s" %(ls_data[0], ls_data[1],ls_data[2],ls_data[3]))
	
	#Read filter list information
	@staticmethod
	def getList(f_name):
		ls_line=FileUtil.ReadLines(f_name)
		ls_record=[]
		for line in ls_line:
			line=line.replace('\n','')	
			#skip empty line
			if(line==''):
				continue			
			ls_data=line.split('; ')
			ls_record.append(ls_data)
		return ls_record
	
	#Get selected record in filter list
	@staticmethod
	def getRecord(f_name, r_name):
		ls_line=FileUtil.ReadLines(f_name)
		ls_record=[]
		for line in ls_line:
			line=line.replace('\n','')			
			ls_data=line.split('; ')
			if(ls_data[1]==r_name):
				ls_record=ls_data
				break
		return ls_record
		
	#add record to filter list
	@staticmethod
	def addRecord(f_name, _type, _target, _duration=[0,0,1,0]):
		ls_record=[]
		
		#calculate start time and end time
		starttime=DatetimeUtil.datetime_string(datetime.now())
		duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
		endtime = DatetimeUtil.datetime_string(datetime.now()+duration)
		
		newline=''
		newline+=_type+'; '
		newline+=_target+'; '
		newline+=starttime+'; '
		newline+=endtime
		
		FileUtil.AddLine(f_name, newline)
		
	#remove selected record from filter list
	@staticmethod
	def deleteRecord(f_name, target):
		#remove ls_data from the file
		FileUtil.DeleteLine(f_name,target)
		
	#update selected record from filter list
	@staticmethod
	def updateRecord(f_name, _target, _duration=[0,0,1,0]):
		ls_data=FilterList.getRecord(f_name,_target)
		if(ls_data==[]):
			print("Target:%s is not exist, update fail1" %(_target))
			return
	
		#calculate start time and end time
		starttime=DatetimeUtil.datetime_string(datetime.now())
		duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
		endtime = DatetimeUtil.datetime_string(datetime.now()+duration)
		
		updateline=''
		updateline+=ls_data[0]+'; '
		updateline+=ls_data[1]+'; '
		updateline+=starttime+'; '
		updateline+=endtime+'\n'
		
		#rewrite updateline to file
		FileUtil.UpdateLine(f_name,_target,updateline)
	
	@staticmethod
	def removeExpiredRecord(f_name):
		ls_line=FileUtil.ReadLines(f_name)
		ls_record=[]
		for line in ls_line:
			line=line.replace('\n','')	
			#skip empty line
			if(line==''):
				continue			
			#split line to get each filed data as 
			ls_data=line.split('; ')
			
			#check if end-time expired
			if(DatetimeUtil.IsExpired(ls_data[3])):
				continue
			ls_record.append(line)
		#return ls_record
		#print ls_record
		FileUtil.AddDataByLine(f_name, ls_record)

'''
FilterList class for manage filter list by using SQLite
'''
class FilterManager(object):
	
	#new db file based on db_path
	@staticmethod
	def new_db(db_path):
		conn = sqlite3.connect(db_path)
		print "New database successfully at: " + db_path;
		conn.close()
	
	#Create table in db file
	@staticmethod	
	def create_table(db_path, tb_name):
		conn = sqlite3.connect(db_path)
		
		#create table
		conn.execute('CREATE TABLE %s \
				 (ID INTEGER PRIMARY KEY AUTOINCREMENT, \
				 Type           		TEXT    	NOT NULL, \
				 Address        		TEXT    	NOT NULL, \
				 StartTime        		TEXT    	NOT NULL, \
				 ExpireTime         	TEXT    	NOT NULL);' %(tb_name))
				 
	
	#Insert record into table
	@staticmethod	
	def insert_entry(path_db, tb_name, arg_list):	
		conn = sqlite3.connect(path_db)
			  
		conn.execute("INSERT INTO %s (Type, Address, StartTime, ExpireTime) VALUES ('%s', '%s', '%s','%s');" \
			%(tb_name, arg_list[0], arg_list[1], arg_list[2], arg_list[3]));

		conn.commit()
		conn.close()
	
	#Update record of table based on condition
	@staticmethod	
	def update_entry(path_db, tb_name, value_list):
		conn = sqlite3.connect(path_db)
		
		conn.execute("UPDATE %s set StartTime='%s',ExpireTime='%s' where Address='%s';" \
					%(tb_name, value_list[2], value_list[3], value_list[1]))
		
		conn.commit()
		conn.close()
	
	#Delete record from table based on Type
	@staticmethod		
	def delete_ByType(path_db, tb_name, type_name):
		conn = sqlite3.connect(path_db)

		conn.execute("DELETE from %s where Type = '%s';" %(tb_name, type_name))
		conn.commit()
		
		conn.close()
		
	#Delete record from table based on Address
	@staticmethod		
	def delete_ByAddress(path_db, tb_name, address_name):
		conn = sqlite3.connect(path_db)

		conn.execute("DELETE from %s where Address = '%s';" %(tb_name, address_name))
		conn.commit()
		
		conn.close()
	
	#Select all record from table
	@staticmethod		
	def select_entry(path_db, tb_name):
		conn = sqlite3.connect(path_db)	
	
		cursor = conn.execute("SELECT Type, Address, StartTime, ExpireTime from %s;" %(tb_name))
		
		ls_result=[]
		for row in cursor:			
		   '''print "Type = ", row[0]
		   print "ADDRESS = ", row[1]
		   print "StartTime = ", row[2]
		   print "ExpireTime = ", row[3], "\n"'''
		   ls_result.append(row)

		conn.close()
		
		return ls_result
		
	#Select record from table based on Type
	@staticmethod		
	def select_ByType(path_db, tb_name, type_name):
		conn = sqlite3.connect(path_db)	
	
		cursor = conn.execute("SELECT Type, Address, StartTime, ExpireTime from %s where Type='%s';" %(tb_name, type_name))
		
		ls_result=[]		
		for row in cursor:
			ls_result.append(row)
			
		conn.close()
		
		return ls_result
		
	#Select record from table based on Type
	@staticmethod		
	def select_ByAddress(path_db, tb_name, address_name):
		conn = sqlite3.connect(path_db)	
	
		cursor = conn.execute("SELECT Type, Address, StartTime, ExpireTime from %s where Address='%s';" %(tb_name, address_name))
		
		ls_result=[]		
		for row in cursor:
			ls_result.append(row)
			
		conn.close()
		
		return ls_result
		
	#add record to filter.db
	@staticmethod
	def addRecord(path_db, tb_name, _type, _target, _duration=[0,0,1,0]):
		#calculate start time and end time
		starttime=DatetimeUtil.datetime_string(datetime.now())
		duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
		endtime = DatetimeUtil.datetime_string(datetime.now()+duration)
		
		#build arg list
		ls_arg=[]
		ls_arg.append(_type)
		ls_arg.append(_target)
		ls_arg.append(starttime)
		ls_arg.append(endtime)
		
		#insert record into table
		FilterManager.insert_entry(path_db,tb_name,ls_arg)
		
	#update selected record from filter list
	@staticmethod
	def updateRecord(path_db, tb_name, _target, _duration=[0,0,1,0]):
		ls_data=FilterManager.select_ByAddress(path_db, tb_name, _target)
		
		if(ls_data==[]):
			return
		
		#calculate start time and end time
		starttime=DatetimeUtil.datetime_string(datetime.now())
		duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
		endtime = DatetimeUtil.datetime_string(datetime.now()+duration)
		
		#build arg list
		ls_arg=[]
		ls_arg.append(ls_data[0][0])
		ls_arg.append(ls_data[0][1])
		ls_arg.append(starttime)
		ls_arg.append(endtime)
		
		#rewrite updateline to file
		FilterManager.update_entry(path_db, tb_name, ls_arg)

def test_FilterManager():		
	path_db='ipset_config/ipset_filter.db'
	tb_name1='Whitelist'
	tb_name2='Blacklist'
	ls_arg1=['Net', '172.16.201.0/24', '2016-10-15 10:29:42', '2016-11-28 11:29:42']
	ls_arg2=['IP', '128.226.79.117', '2017-10-19 12:29:42', '2017-11-9 16:29:42']

	#FilterManager.new_db(path_db)
	#FilterManager.create_table(path_db, tb_name1)
	#FilterManager.create_table(path_db, tb_name2)
	#FilterManager.insert_entry(path_db, tb_name1, ls_arg1)
	#FilterManager.update_entry(path_db, tb_name, ls_arg1)
	#FilterManager.delete_entry(path_db, tb_name, ls_arg2)
	#print(FilterManager.select_entry(path_db, tb_name1))
	#print(FilterManager.select_ByType(path_db, tb_name1, 'Net'))
	#print(FilterManager.select_ByAddress(path_db, tb_name1, '128.226.79.117'))
	
if __name__ == '__main__': 
	test_FilterManager()
	pass