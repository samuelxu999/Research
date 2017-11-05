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
from filter_list import FilterManager, FilterList


# Define IP set source type 
class IPSetSRC(object): 
	Unknown = 0
	Database = 1
	File = 2 
			
'''
PolicyManager class for manage policy task
'''
class PolicyManager(object):	
	#new IPset based on specified src_type
	@staticmethod
	def setup_IPset(db_path, tb_name, src_type=IPSetSRC.Unknown):
		if(src_type==IPSetSRC.File):
			#extract ipset name from file path
			f_name=db_path.split('/')[-1]
			ipset_name=f_name.split('.')[0]
		elif(src_type==IPSetSRC.Database):
			ipset_name=tb_name
		else:
			print('Not supported ipset source')
			return
		
		#create ipset
		IPSets.create(ipset_name+'_Net','hash:net')
		IPSets.create(ipset_name+'_IP','hash:ip')
		
		if(src_type==IPSetSRC.File):
			#load filter list from file
			ls_records=FilterList.getList(db_path)
		elif(src_type==IPSetSRC.Database):
			#load filter list from db
			ls_records=FilterManager.select_entry(db_path, tb_name)
		else:
			print('Not supported ipset source')
			return
		
		#write net list to ipset
		for record in ls_records:
			if(record[0]=='Net'):
				IPSets.add(ipset_name+'_Net',record[1])
			elif(record[0]=='IP'):
				IPSets.add(ipset_name+'_IP',record[1])
			else:
				continue
		
	#update IPset based on specified src_type and condition
	@staticmethod
	def update_IPset(db_path, tb_name, src_type=IPSetSRC.Unknown):		
		if(src_type==IPSetSRC.File):
			#extract ipset name from file path
			f_name=db_path.split('/')[-1]
			ipset_name=f_name.split('.')[0]
		elif(src_type==IPSetSRC.Database):
			ipset_name=tb_name
		else:
			print('Not supported ipset source')
			return
		
		#First clear all ipset list
		IPSets.flush(ipset_name+'_Net')
		IPSets.flush(ipset_name+'_IP')
		
		if(src_type==IPSetSRC.File):
			#load filter list from file
			ls_records=FilterList.getList(db_path)
		elif(src_type==IPSetSRC.Database):
			#load filter list from db
			ls_records=FilterManager.select_entry(db_path, tb_name)
		else:
			print('Not supported ipset source')
			return
		
		#rewrite net list to ipset
		for record in ls_records:
			if(record[0]=='Net'):
				IPSets.add(ipset_name+'_Net',record[1])
			elif(record[0]=='IP'):
				IPSets.add(ipset_name+'_IP',record[1])
			else:
				continue
	
	#teardown IPset by using 'ipset destroy'
	@staticmethod
	def teardown_IPset():
		#destory all ipset
		IPSets.destroy()
	
	
	#setup iptables for policy management
	@staticmethod
	def setup_IPTables(db_path, chain_name, tb_name, src_type=IPSetSRC.Unknown):
		if(src_type==IPSetSRC.File):
			#extract ipset name from file path
			f_name=db_path.split('/')[-1]
			ipset_name=f_name.split('.')[0]
		elif(src_type==IPSetSRC.Database):
			ipset_name=tb_name
		else:
			print('Not supported ipset source')
			return
		
		#setup network filter for prerouting
		if(chain_name=='PREROUTING'):
			IPTables.create_PreRouting('eth0', '9080', [(ipset_name+'_IP'), 'src'], '172.16.202.8:80')
			IPTables.create_PreRouting('eth0', '9080', [(ipset_name+'_Net'), 'src'], '172.16.202.8:80')
			IPTables.create_PreRouting('eth0', '9022', [(ipset_name+'_IP'), 'src'], '172.16.202.8:22')
			IPTables.create_PreRouting('eth0', '9022', [(ipset_name+'_Net'), 'src'], '172.16.202.8:22')
		#setup network filter for input
		elif(chain_name=='INPUT'):
			#setup whitelist network filter for input
			IPTables.create_Rule('FILTER', 'INPUT', 'eth0', 'DROP')
			IPTables.create_RulePort('FILTER', 'INPUT','eth0', '80', 'NEW,ESTABLISHED', 'ACCEPT')
			IPTables.create_Rulestate('FILTER', 'INPUT', 'eth0', 'RELATED,ESTABLISHED', 'ACCEPT')
			IPTables.create_Ruleset('FILTER', 'INPUT', 'eth0', [(ipset_name+'_IP'), 'src'], 'ACCEPT')
			IPTables.create_Ruleset('FILTER', 'INPUT', 'eth0', [(ipset_name+'_Net'), 'src'], 'ACCEPT')
		#setup network filter for forward
		elif(chain_name=='FORWARD'):
			IPTables.create_Forward( 'wlan0', 'eth0', '', 'ACCEPT')
			IPTables.create_Forward( 'eth0', 'wlan0', 'RELATED,ESTABLISHED', 'ACCEPT')
		#setup network filter for output
		elif(chain_name=='OUTPUT'):
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'eth0', [(ipset_name+'_IP'), 'dst'], 'DROP')
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'eth0', [(ipset_name+'_Net'), 'dst'], 'DROP')
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'wlan0', [(ipset_name+'_IP'), 'dst'], 'DROP')
			IPTables.create_Ruleset('FILTER', 'OUTPUT', 'wlan0', [(ipset_name+'_Net'), 'dst'], 'DROP')
		#setup network filter for postrouting
		elif(chain_name=='POSTROUTING'):
			IPTables.create_PostRouting('eth0', 'MASQUERADE')
		else:
			pass
			
	#teardown iptables for policy management
	@staticmethod
	def teardown_IPTables():
		#extract ipset name from file path
		#f_name=file_path.split('/')[-1]
		#ipset_name=f_name.split('.')[0]
		
		#IPTables.delete_Ruleset('FILTER', 'INPUT', [(ipset_name+'_IP'), 'src'], 'ACCEPT')
		#IPTables.delete_Ruleset('FILTER', 'INPUT', [(ipset_name+'_Net'), 'src'], 'ACCEPT')
		#IPTables.delete_Rules('FILTER', chain_name)
		
		IPTables.flush('nat')
		IPTables.flush('filter')
	
	#setup iptables for policy management
	@staticmethod
	def setup_PreRouting(file_path, in_interface, dport, to_dst):
		#extract ipset name from file path
		f_name=file_path.split('/')[-1]
		ipset_name=f_name.split('.')[0]
		
		IPTables.create_PreRouting(in_interface, dport, [(ipset_name+'_IP'), 'src'], to_dst)
		IPTables.create_PreRouting(in_interface, dport, [(ipset_name+'_Net'), 'src'], to_dst)
		
	#teardown iptables for policy management
	@staticmethod
	def teardown_PreRouting(to_dst):
		IPTables.delete_PreRouting(to_dst)

'''
PolicyTask class for executing policy rule
'''
class PolicyTask(object):
	filter_db='ipset_config/ipset_filter.db'
	tb_name=['Whitelist','Blacklist']
	
	@staticmethod
	def setup_Filter():
		#new filter databased *.db and create table
		for tb in PolicyTask.tb_name:
			FilterManager.create_table(PolicyTask.filter_db, tb)
		
		#add default list in Whitelist
		FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[0], 'Net', '172.16.201.0/24', [0,1,0,10])
		FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[0], 'IP', '128.226.79.117', [0,0,1,10])
		FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[0], 'IP', '128.226.79.11', [0,0,1,10])
		
			
		#add default list in Blacklist
		#FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[1], 'Net', '172.16.201.0/24', [0,1,0,10])
		FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[1], 'IP', '128.226.88.147', [0,0,1,10])
		#FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[1], 'IP', '128.226.79.117', [0,0,1,10])
		
		#list all
		print(FilterManager.select_entry(PolicyTask.filter_db, PolicyTask.tb_name[0]))
		print(FilterManager.select_entry(PolicyTask.filter_db, PolicyTask.tb_name[1]))
	
	@staticmethod
	def setup_IPset(op_type):
		#setup using file
		if(op_type==IPSetSRC.File):
			PolicyManager.setup_IPset('ipset_config/Whitelist.txt', '', op_type)
			PolicyManager.setup_IPset('ipset_config/Blacklist.txt', '', op_type)
		#setup using db
		elif(op_type==IPSetSRC.Database):
			for tb in PolicyTask.tb_name:
				PolicyManager.setup_IPset(PolicyTask.filter_db, tb, op_type)
		else:
			print('Not supported ipset source')
			return

	
	@staticmethod
	def update_IPset(op_type):
		#setup using file
		if(op_type==IPSetSRC.File):
			PolicyManager.update_IPset('ipset_config/Whitelist.txt', '', op_type)
			PolicyManager.update_IPset('ipset_config/Blacklist.txt', '', op_type)
		#setup using db
		elif(op_type==IPSetSRC.Database):
			for tb in PolicyTask.tb_name:
				PolicyManager.update_IPset(PolicyTask.filter_db, tb, op_type)
		else:
			print('Not supported ipset source')
			return
	
	@staticmethod
	def teardown_IPset():
		PolicyManager.teardown_IPset()
	
	@staticmethod	
	def setup_IPtables(op_type):
		#setup using file
		if(op_type==IPSetSRC.File):		
			PolicyManager.setup_IPTables('ipset_config/Whitelist.txt', 'PREROUTING', '', op_type)
			PolicyManager.setup_IPTables('ipset_config/Whitelist.txt', 'INPUT', '', op_type)
			PolicyManager.setup_IPTables('', 'FORWARD', '', op_type)
			PolicyManager.setup_IPTables('ipset_config/Blacklist.txt', 'OUTPUT', '', op_type)
			PolicyManager.setup_IPTables('ipset_config/Whitelist.txt', 'POSTROUTING', '', op_type)
		elif(op_type==IPSetSRC.Database):		
			PolicyManager.setup_IPTables('', 'PREROUTING', PolicyTask.tb_name[0], op_type)
			PolicyManager.setup_IPTables('', 'INPUT', PolicyTask.tb_name[0], op_type)
			PolicyManager.setup_IPTables('', 'FORWARD', '', op_type)
			PolicyManager.setup_IPTables('', 'OUTPUT', PolicyTask.tb_name[1], op_type)
			PolicyManager.setup_IPTables('', 'POSTROUTING', PolicyTask.tb_name[0], op_type)
		else:
			print('Not supported ipset source')
			return
			
	
	@staticmethod
	def teardown_IPtables():
		PolicyManager.teardown_IPTables()
	
	@staticmethod
	def restore_IPtables():
		#PolicyManager.teardown_IPTables('ipset_config/whitelist.txt','INPUT')
		#PolicyManager.teardown_IPTables('ipset_config/blacklist.txt','OUTPUT')
		IPTables.restore('/etc/iptables.ipv4.nat')

def test_ipset():
	'''IPSets.create('myset1','hash:ip')
	IPSets.add('myset1','172.16.203.2')
	IPSets.create('myset2','hash:net')
	IPSets.add('myset2','172.16.204.0/24')'''
	#IPSets.destroy()
	#IPSets.destroy('myset2')
	#IPSets.flush()
	#IPSets.flush('myset2')
	#IPSets.rename('test', 'myset2')
	#IPSets.add('bkset1','172.16.203.0/24')
	#IPSets.delete('bkset1','172.16.203.2')
	#IPSets.delete('bkset2','172.16.204.0/24')
	#IPSets.save('myset1','ipset_config/all.save')
	#IPSets.restore('ipset_config/all.save')
	#IPSets.list()
	pass
		
def test_iptables():
	'''IPTables.save('', 'iptables_config/all.rule')
	IPTables.save('nat', 'iptables_config/nat.rule')
	IPTables.save('filter', 'iptables_config/filter.rule')'''	
	#IPTables.flush('')
	#IPTables.flush('nat')
	#IPTables.flush('filter')
	
	#IPTables.restore('iptables_config/nat.rule')
	#IPTables.restore('iptables_config/filter.rule')	
	#IPTables.restore('iptables_config/all.rule')
	
	#IPTables.list_iptables('NAT') 
	pass	

def test_FileList():
	FilterList.display('ipset_config/Whitelist.txt')
	#print(FilterList.getRecord('ipset_config/whitelist.txt','172.16.201.0/24'))
	#FilterList.addRecord('ipset_config/whitelist.txt','Net','172.16.203.0/24',[0,0,0,10])
	#FilterList.addRecord('ipset_config/whitelist.txt','IP','172.16.202.5',[0,0,0,10])
	#FilterList.updateRecord('ipset_config/whitelist.txt','172.16.202.5')
	#FilterList.updateRecord('ipset_config/whitelist.txt','172.16.203.0/24')
	#FilterList.deleteRecord('ipset_config/whitelist.txt','172.16.203.0/24')
	#FilterList.deleteRecord('ipset_config/whitelist.txt','172.16.202.5')
	#FilterList.removeExpiredRecord('ipset_config/blacklist.txt')
	pass
	
def test_Filter():	
	#new filter databased *.db and create table
	'''for tb in PolicyTask.tb_name:
		FilterManager.create_table(PolicyTask.filter_db, tb)'''
	
	#FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[0], 'Net', '172.16.201.0/24', [0,1,0,10])	
	#FilterManager.addRecord(PolicyTask.filter_db, PolicyTask.tb_name[1], 'Net', '172.16.202.0/24', [0,0,1,10])
	
	#FilterManager.updateRecord(PolicyTask.filter_db, PolicyTask.tb_name[0], '172.16.201.0/24', [0,0,0,10])
	
	#FilterManager.delete_ByAddress(PolicyTask.filter_db, PolicyTask.tb_name[1], '172.16.201.0/24')
	#FilterManager.delete_ByType(PolicyTask.filter_db, PolicyTask.tb_name[0], 'IP')
	
	#list all
	FilterManager.DisplayByTable(PolicyTask.filter_db, PolicyTask.tb_name[0])
	FilterManager.DisplayByTable(PolicyTask.filter_db, PolicyTask.tb_name[1])
	
if __name__ == '__main__': 
	test_FileList()
	test_Filter()
	test_ipset()
	test_iptables()
	pass
