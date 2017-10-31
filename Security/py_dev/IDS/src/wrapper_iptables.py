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
					elif(match.name=='tcp'):
						print match.name, '-', match.dport
					else:
						print match.name
				print "\tTarget:",
				if(rule.target.name=='DNAT'):
					print rule.target.name, '-', rule.target.to_destination
				else:
					print rule.target.name
				#table = iptc.Table(iptc.Table.FILTER)
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
	def create_Ruleset(tb_name, chain_name, io_interface, ipset_arg, target_name):	
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
		if(chain_name=='INPUT'):
			rule.in_interface = io_interface
		elif(chain_name=='OUTPUT'):
			rule.out_interface = io_interface
		else:
			pass

		#create match for set
		match = rule.create_match("set")
		match.match_set = [ipset_arg[0], ipset_arg[1]]
		
		#create target
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
		
	#Create ipset based rule under [table-chain]
	@staticmethod
	def create_Rulestate(tb_name, chain_name, io_interface, state_arg, target_name):	
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
		if(chain_name=='INPUT'):
			rule.in_interface = io_interface
		elif(chain_name=='OUTPUT'):
			rule.out_interface = io_interface
		else:
			pass
		
		#create match for state
		match = rule.create_match("state")
		match.state = state_arg
		
		#create target
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
		
	#Create ipset based rule under [table-chain]
	@staticmethod
	def create_Rule(tb_name, chain_name, io_interface, target_name):	
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
		if(chain_name=='INPUT'):
			rule.in_interface = io_interface
		elif(chain_name=='OUTPUT'):
			rule.out_interface = io_interface
		else:
			pass
		
		#create target
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
	
	#Create ipset based PreRouting rule under [table-chain]
	@staticmethod
	def create_PreRouting(in_interface, dst_port, ipset_arg, to_dst):	
		'''cmdline="iptables -A PREROUTING -t nat -i " + in_interface + \
				" -p tcp -m tcp --dport " +  dst_port + \
				" -m set --match-set " + ipset_arg[0] + " " + ipset_arg[1] + \
				" -j DNAT --to-destination " + to_dst
		os.system(cmdline)'''
		#get table
		table = iptc.Table(iptc.Table.NAT)
		
		#get chain
		chain = iptc.Chain(table, 'PREROUTING')
		
		#new rule
		rule = iptc.Rule()
		rule.in_interface = in_interface
		#set protocol: -p tcp
		rule.protocol = "tcp"
		
		#create match for tcp: -m tcp --dport 9080
		match = rule.create_match("tcp")
		match.dport = dst_port
		
		#create match for set: -m set --match-set whitelist_IP src
		match = rule.create_match("set")
		match.match_set = [ipset_arg[0], ipset_arg[1]]
		
		#create target: -j DNAT --to-destination 172.16.202.8:80
		target = rule.create_target("DNAT")
		target.to_destination=to_dst
		
		#insert rule to chain
		chain.insert_rule(rule)
	
	#Create ipset based PostRouting rule under [table-chain]
	@staticmethod
	def create_PostRouting(out_interface, target_name):	
		'''cmdline="iptables -A POSTROUTING -t nat -o " + out_interface + \
				" -j " + target_name
		os.system(cmdline)'''
		#get table
		table = iptc.Table(iptc.Table.NAT)	
		
		#get chain
		chain = iptc.Chain(table, 'POSTROUTING')
		
		#new rule
		rule = iptc.Rule()
		rule.out_interface = out_interface
		
		#create target: -j MASQUERADE
		target = rule.create_target(target_name)
		
		#insert rule to chain
		chain.insert_rule(rule)
		
	#Create ipset based rule under [table-chain]
	@staticmethod
	def create_Forward( in_interface, out_interface, state_arg, target_name):	
		#get table
		table = iptc.Table(iptc.Table.FILTER)			
		
		#get chain
		chain = iptc.Chain(table, 'FORWARD')
		
		#new rule
		rule = iptc.Rule()
		if(in_interface!=''):
			rule.in_interface = in_interface
		if(out_interface!=''):
			rule.out_interface = out_interface
		
		if(state_arg!=''):
			#create match for state
			match = rule.create_match("state")
			match.state = state_arg
		
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
		