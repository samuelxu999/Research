#!/usr/bin/env python

'''
========================
network_monitor
========================
Created on Oct.18, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide network monitoring function, such as sniff packets.
@Reference: 
'''

import sys
from scapy.all import *
from pkt_analysis import PktData
    
#callback function for binding sniff
def network_monitor_callback(pkt):
	#print pkt.command()
	''''a=pkt.sprintf("{IP:%IP.src%\n}{Raw:%Raw.load%\n}")
	print a'''
    
	pkt_data=PktData.extract_data_from_packet(pkt,1)
	
    #print pkt_data
	#PktData.display_data(pkt_data,1)
	PktData.log_data('logdata', pkt_data)
	print(PktData.read_log('logdata')[-1])

'''
ARP ping to test alive IP target in Lan
@dest: "192.168.2.0/24"
'''
def ARP_ping(dest):
	conf.verb=0
	ans,unans=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=dest),timeout=2)
	for s, r in ans :
		print r.sprintf("%Ether.src% : %ARP.psrc%")
	'''ans,unans=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.2.0/24"),timeout=2)
	ans.summary(lambda (s,r): r.sprintf("%Ether.src% %ARP.psrc%") )'''

if __name__ == '__main__':
    #start sniff
	str_filter='tcp and (src 128.226.79.117)'
	sniff(prn=network_monitor_callback, filter=str_filter, store=0)
	
	'''if len (sys.argv )!= 2 :
		print "Usage: arping <net >\n eg :arping 192.168.1.0/24"
		sys.exit(1)
	ARP_ping(sys.argv[1]) '''
    
    
