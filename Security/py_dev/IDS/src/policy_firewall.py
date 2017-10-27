#!/usr/bin/env python

'''
========================
policy_firewall.py
========================
Created on Oct.20, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide network firewall policy function, such as ipset, iptables.
@Reference: 
'''

import time
from datetime import datetime
from utilities import FileUtil, DatetimeUtil
from wrapper_ipset import IPSets
from wrapper_iptables import IPTables
		
'''
FilterList class for manage filter list files
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
	
		#Read filter list information
	
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
PolicyManager class for manage policy task
'''
class PolicyManager(object):
	#new IPset from selected filterlist.txt
	@staticmethod
	def setup_IPset(file_path):
		#extract ipset name from file path
		f_name=file_path.split('/')[-1]
		ipset_name=f_name.split('.')[0]

		#create ipset
		IPSets.create(ipset_name+'_Net','hash:net')
		IPSets.create(ipset_name+'_IP','hash:ip')
		
		#load filter list from file
		ls_records=FilterList.getList(file_path)
		#write net list to ipset
		for record in ls_records:
			if(record[0]=='Net'):
				IPSets.add(ipset_name+'_Net',record[1])
			elif(record[0]=='IP'):
				IPSets.add(ipset_name+'_IP',record[1])
			else:
				continue
		
	#update IPset based on selected filterlist.txt
	@staticmethod
	def update_IPset(file_path):		
		#extract ipset name from file path
		f_name=file_path.split('/')[-1]
		ipset_name=f_name.split('.')[0]
		
		#First clear all ipset list
		IPSets.flush(ipset_name+'_Net')
		IPSets.flush(ipset_name+'_IP')
		
		#load filter list from file
		ls_records=FilterList.getList(file_path)
		#rewrite net list to ipset
		for record in ls_records:
			if(record[0]=='Net'):
				IPSets.add(ipset_name+'_Net',record[1])
			elif(record[0]=='IP'):
				IPSets.add(ipset_name+'_IP',record[1])
			else:
				continue
	
	#update IPset based on selected filterlist.txt
	@staticmethod
	def teardown_IPset():
		#destory all ipset
		IPSets.destroy()
		
	#setup iptables for policy management
	@staticmethod
	def setup_IPTables(file_path, chain_name):
		#extract ipset name from file path
		f_name=file_path.split('/')[-1]
		ipset_name=f_name.split('.')[0]
		
		#setup network filter for input
		if(chain_name=='INPUT'):
			#setup whitelist network filter for input
			IPTables.create_Rule('FILTER', 'INPUT', 'eth0', 'DROP')
			IPTables.create_Rulestate('FILTER', 'INPUT', 'eth0', 'RELATED,ESTABLISHED', 'ACCEPT')
			IPTables.create_Ruleset('FILTER', 'INPUT', 'eth0', [(ipset_name+'_IP'), 'src'], 'ACCEPT')
			IPTables.create_Ruleset('FILTER', 'INPUT', 'eth0', [(ipset_name+'_Net'), 'src'], 'ACCEPT')
		#setup blacklist network filter for output
		elif(chain_name=='OUTPUT'):
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'eth0', [(ipset_name+'_IP'), 'dst'], 'DROP')
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'eth0', [(ipset_name+'_Net'), 'dst'], 'DROP')
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'wlan0', [(ipset_name+'_IP'), 'dst'], 'DROP')
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'wlan0', [(ipset_name+'_Net'), 'dst'], 'DROP')
		else:
			pass
		
		
	#teardown iptables for policy management
	@staticmethod
	def teardown_IPTables(file_path, chain_name):
		#extract ipset name from file path
		f_name=file_path.split('/')[-1]
		ipset_name=f_name.split('.')[0]
		
		#IPTables.delete_Ruleset('FILTER', 'INPUT', [(ipset_name+'_IP'), 'src'], 'ACCEPT')
		#IPTables.delete_Ruleset('FILTER', 'INPUT', [(ipset_name+'_Net'), 'src'], 'ACCEPT')
		IPTables.delete_Rules('FILTER', chain_name)
		

if __name__ == '__main__':
	#display_iptc_table() 
	#FilterList.display('ipset_config/whitelist.txt')
	#print(FilterList.getRecord('ipset_config/whitelist.txt','172.16.201.0/24'))
	#FilterList.addRecord('ipset_config/whitelist.txt','Net','172.16.203.0/24',[0,0,0,10])
	#FilterList.addRecord('ipset_config/whitelist.txt','IP','172.16.202.5',[0,0,0,10])
	#FilterList.updateRecord('ipset_config/whitelist.txt','172.16.202.5')
	#FilterList.updateRecord('ipset_config/whitelist.txt','172.16.203.0/24')
	#FilterList.deleteRecord('ipset_config/whitelist.txt','172.16.203.0/24')
	#FilterList.deleteRecord('ipset_config/whitelist.txt','172.16.202.5')
	#FilterList.removeExpiredRecord('ipset_config/blacklist.txt')
	#IPSets.create('myset1','hash:ip')
	#IPSets.list()
	
	#IPTables.list_iptables() 
	pass
