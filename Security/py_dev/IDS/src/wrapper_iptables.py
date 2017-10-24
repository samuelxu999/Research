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

import iptc
import sys
import subprocess

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
			print "Chain ", chain.name
			for rule in chain.rules:
				print "Rule", "proto:", rule.protocol, "src:", rule.src, "dst:", \
					rule.dst, "in:", rule.in_interface, "out:", rule.out_interface,
				print "Matches:",
				for match in rule.matches:
					if(match.name=='state'):
						print match.name, '-', match.state
					else:
						print match.name
				print "Target:",
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