#!/usr/bin/env python

import sys
import subprocess
from scapy.all import *
from wrapper_ipset import IPSets
from wrapper_iptables import IPTables
from policy_firewall import *

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

def test_ipset():
	'''FwallPolicy.IPSets.create('myset1','hash:ip')
	FwallPolicy.IPSets.add('myset1','172.16.203.2')
	FwallPolicy.IPSets.create('myset2','hash:net')
	FwallPolicy.IPSets.add('myset2','172.16.204.0/24')'''
	#FwallPolicy.IPSets.destroy()
	#FwallPolicy.IPSets.destroy('myset2')
	#FwallPolicy.IPSets.flush()
	#FwallPolicy.IPSets.flush('myset2')
	#FwallPolicy.IPSets.rename('test', 'myset2')
	#FwallPolicy.IPSets.add('bkset1','172.16.203.0/24')
	#FwallPolicy.IPSets.delete('bkset1','172.16.203.2')
	#FwallPolicy.IPSets.delete('bkset2','172.16.204.0/24')
	#FwallPolicy.IPSets.save('myset1','ipset_config/all.save')
	#FwallPolicy.IPSets.restore('ipset_config/all.save')
	#FwallPolicy.IPSets.list()
	pass

def test_iptables():
	'''FwallPolicy.IPTables.save('', 'iptables_config/all.rule')
	FwallPolicy.IPTables.save('nat', 'iptables_config/nat.rule')
	FwallPolicy.IPTables.save('filter', 'iptables_config/filter.rule')'''	
	#FwallPolicy.IPTables.flush('')
	#FwallPolicy.IPTables.flush('nat')
	#FwallPolicy.IPTables.flush('filter')
	
	#FwallPolicy.IPTables.restore('iptables_config/nat.rule')
	#FwallPolicy.IPTables.restore('iptables_config/filter.rule')	
	#FwallPolicy.IPTables.restore('iptables_config/all.rule')
	pass

def setup_IPset():
	PolicyManager.setup_IPset('ipset_config/whitelist.txt')
	PolicyManager.setup_IPset('ipset_config/blacklist.txt')

def update_IPset():
	PolicyManager.update_IPset('ipset_config/whitelist.txt')
	PolicyManager.update_IPset('ipset_config/blacklist.txt')
	
def setup_IPtables():
	PolicyManager.setup_IPTables('ipset_config/whitelist.txt', 'INPUT')
	PolicyManager.setup_IPTables('ipset_config/blacklist.txt', 'OUTPUT')
	
def teardown_IPtables():
	#PolicyManager.teardown_IPTables('ipset_config/whitelist.txt','INPUT')
	#PolicyManager.teardown_IPTables('ipset_config/blacklist.txt','OUTPUT')
	IPTables.restore('/etc/iptables.ipv4.nat')
	
if __name__ == '__main__':
    #test_demo()
    #test_fun() 
    #pkts = sniff(prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"))
	
	#setup_IPset()
	#update_IPset()
	#PolicyManager.teardown_IPset()
	
	#setup_IPtables()
	#teardown_IPtables()
	
	IPTables.list_iptables() 
	pass
