#!/usr/bin/env python
''' 
======================== 
wrapper_iptables.py 
======================== 
Created on Oct.24, 2017 
@author: Xu Ronghua 
@Email: rxu22@binghamton.edu 
@TaskDescription: This module provide wrapper for iptables command
@Reference: http://ipset.netfilter.org/iptables.man.html
'''

import os
import sys
import subprocess

import iptc

'''
IPTables class for manage iptables rules
'''
class IPTables(object):
    
	#display iptables information
	@staticmethod
	def list_iptables(tb_name='FILTER'):
		if(tb_name=='NAT'):
			table = iptc.Table(iptc.Table.NAT)
		elif(tb_name=='FILTER'):
			table = iptc.Table(iptc.Table.FILTER)
		elif(tb_name=='MANGLE'):
			table = iptc.Table(iptc.Table.MANGLE)
		elif(tb_name=='RAW'):
			table = iptc.Table(iptc.Table.RAW)
		else:
			print("Not supported table.")
			return 
		print "-------Table:" + table.name + "--------"
		for chain in table.chains:
			print "======================="
			print "Chain: ", chain.name
			for rule in chain.rules:
				print "Rule:"
				print "\tproto:", rule.protocol, "src:", rule.src, "dst:", \
					rule.dst, "in:", rule.in_interface, "out:", rule.out_interface
				print "\tMatches:",
				for match in rule.matches:
					if(match.name=='state'):
						print match.name, '-', match.state
					elif(match.name=='set'):
						print match.name, '-', match.match_set
					else:
						print match.name
				print "\tTarget:",
				print rule.target.name
				table = iptc.Table(iptc.Table.FILTER)
		print "======================="
		
	#Save iptables to file
	@staticmethod
	def save(tb_name, f_name):
		if(tb_name==''):
			cmdline="iptables-save > " + f_name			
		else:
			cmdline="iptables-save -t " + tb_name + " > " + f_name
		os.system(cmdline)
		
	#Restore from iptables-save to current iptables
	@staticmethod
	def restore(f_name):	
		cmdline="iptables-restore < " + f_name
		os.system(cmdline)
		
	#Flush the selected chain
	@staticmethod
	def flush(tb_name):
		if(tb_name==''):
			cmdline="iptables -F"		
		else:
			cmdline="iptables -t " + tb_name + " -F"
		os.system(cmdline)
	
	#Create ipset based rule under [table-chain]
	@staticmethod
	def create_Ruleset(tb_name, chain_name, ipset_arg, target_name):	
		#get table
		if(tb_name=='NAT'):
			table = iptc.Table(iptc.Table.NAT)
		elif(tb_name=='FILTER'):
			table = iptc.Table(iptc.Table.FILTER)
		elif(tb_name=='MANGLE'):
			table = iptc.Table(iptc.Table.MANGLE)
		elif(tb_name=='RAW'):
			table = iptc.Table(iptc.Table.RAW)
		else:
			print("Not supported table.")
			return		
		
		#get chain
		chain = iptc.Chain(table, chain_name)
		
		#new rule
		rule = iptc.Rule()
		
		#create match for set
		match = rule.create_match("set")
		match.match_set = [ipset_arg[0], ipset_arg[1]]
		
		#create target
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
		
	#Create ipset based rule under [table-chain]
	@staticmethod
	def create_Rulestate(tb_name, chain_name, state_arg, target_name):	
		#get table
		if(tb_name=='NAT'):
			table = iptc.Table(iptc.Table.NAT)
		elif(tb_name=='FILTER'):
			table = iptc.Table(iptc.Table.FILTER)
		elif(tb_name=='MANGLE'):
			table = iptc.Table(iptc.Table.MANGLE)
		elif(tb_name=='RAW'):
			table = iptc.Table(iptc.Table.RAW)
		else:
			print("Not supported table.")
			return		
		
		#get chain
		chain = iptc.Chain(table, chain_name)
		
		#new rule
		rule = iptc.Rule()
		
		#create match for state
		match = rule.create_match("state")
		match.state = state_arg
		
		#create target
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
		
	#Create ipset based rule under [table-chain]
	@staticmethod
	def create_Rule(tb_name, chain_name, target_name):	
		#get table
		if(tb_name=='NAT'):
			table = iptc.Table(iptc.Table.NAT)
		elif(tb_name=='FILTER'):
			table = iptc.Table(iptc.Table.FILTER)
		elif(tb_name=='MANGLE'):
			table = iptc.Table(iptc.Table.MANGLE)
		elif(tb_name=='RAW'):
			table = iptc.Table(iptc.Table.RAW)
		else:
			print("Not supported table.")
			return		
		
		#get chain
		chain = iptc.Chain(table, chain_name)
		
		#new rule
		rule = iptc.Rule()
		
		#create target
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
		
	#Delete ipset based rule under [table-chain]
	@staticmethod
	def delete_Ruleset(tb_name, chain_name, ipset_arg, target_name):	
		#get table
		if(tb_name=='NAT'):
			table = iptc.Table(iptc.Table.NAT)
		elif(tb_name=='FILTER'):
			table = iptc.Table(iptc.Table.FILTER)
		elif(tb_name=='MANGLE'):
			table = iptc.Table(iptc.Table.MANGLE)
		elif(tb_name=='RAW'):
			table = iptc.Table(iptc.Table.RAW)
		else:
			print("Not supported table.")
			return		
		
		#get chain
		chain = iptc.Chain(table, chain_name)
		match_arg=ipset_arg[0]+' '+ipset_arg[1]
		for rule in chain.rules:
			for match in rule.matches:
				if(match.name=='set' and str(match.match_set)==match_arg and rule.target.name==target_name):
					#delete rule
					chain.delete_rule(rule)
					break
		
	#Delete all rules under [table-chain]
	@staticmethod
	def delete_Rules(tb_name, chain_name):	
		#get table
		if(tb_name=='NAT'):
			table = iptc.Table(iptc.Table.NAT)
		elif(tb_name=='FILTER'):
			table = iptc.Table(iptc.Table.FILTER)
		elif(tb_name=='MANGLE'):
			table = iptc.Table(iptc.Table.MANGLE)
		elif(tb_name=='RAW'):
			table = iptc.Table(iptc.Table.RAW)
		else:
			print("Not supported table.")
			return
		
		#disable autocommit
		table.autocommit = False
		
		#get chain
		chain = iptc.Chain(table, chain_name)
		for rule in chain.rules:
			#delete rule
			chain.delete_rule(rule)
		
		#commit change
		table.commit()
		#enable autocommit
		table.autocommit = True
		