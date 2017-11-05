#!/usr/bin/env python

import sys
import subprocess
from scapy.all import *
from utilities import FileUtil, DatetimeUtil
from wrapper_ipset import IPSets
from wrapper_iptables import IPTables
from policy_firewall import *
from vtAPI import vtAPI
#from filter_list import FilterManager

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
	
def test_vtAPI():
	#print vtAPI.url_Scan('http://www.virustotal.com')
	#vtAPI.url_Scan('http://www.virustotal.com')
	#response=vtAPI.url_Report('http://www.baidu.com')
	#print(vtAPI.file_Scan('number.txt'))
	#print(vtAPI.file_Rescan('721250fc401e820a662fc76720b9f63a'))
	#print(vtAPI.file_Report('721250fc401e820a662fc76720b9f63a'))
	#response=vtAPI.file_Report('721250fc401e820a662fc76720b9f63a')
	#print(vtAPI.getPositiveRate(response))
	json_data = vtAPI.url_Report('http://wwww.google.com')
	for e in json_data:
		print e+' : '+str(json_data[e])
	'''json_scans=json_data['scans']
	for e in json_scans:
		print e+' : '+str(json_scans[e])
	#print json_data['scans'][0]'''
	'''if(json_data['response_code']==1):
		print(vtAPI.getPositiveRate(json_data))'''
	pass


	
if __name__ == '__main__':
    #test_demo()
    #test_fun() 
    #pkts = sniff(prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"))
	
	#db_src=IPSetSRC.Database
	
	#PolicyTask.setup_Filter()
	#PolicyTask.setup_IPset(db_src)
	#PolicyTask.update_IPset(db_src)
	#PolicyTask.teardown_IPset()
	
	'''PolicyTask.teardown_IPtables()
	PolicyTask.setup_IPtables(db_src)'''
	#PolicyTask.restore_IPtables()
	
	#PolicyManager.setup_PreRouting('ipset_config/whitelist.txt', 'eth0', '9080', '172.16.202.8:80')
	#PolicyManager.teardown_PreRouting('172.16.202.8:80')
	#IPTables.list_iptables('NAT') 
	
	
	#test_vtAPI()
	pass
