#!/usr/bin/env python

import sys
from scapy.all import *

import iptc

def test_demo():
    p=sr1(IP(dst=sys.argv[1])/ICMP())
    if p:
        p.show()
    
def arp_monitor_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1,2): #who-has or is-at
        return pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")


'''sniff(prn=arp_monitor_callback, filter="arp", store=0)'''
 
def test_fun():
    pkts=sniff(count=10)
    #print pkts[0].command()
    for pkt in pkts:
        extract_data_from_packet(pkts[0]);
        
def display_iptc_table():
	table = iptc.Table(iptc.Table.FILTER)
	for chain in table.chains:
		print "======================="
		print "Chain ", chain.name
		for rule in chain.rules:
			print "Rule", "proto:", rule.protocol, "src:", rule.src, "dst:", \
				rule.dst, "in:", rule.in_interface, "out:", rule.out_interface,
			print "Matches:",
			for match in rule.matches:
				print match.name,
			print "Target:",
			print rule.target.name
	print "======================="

if __name__ == '__main__':
    #test_demo()
    #test_fun() 
    #pkts = sniff(prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"))
	display_iptc_table() 
    