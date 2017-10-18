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

import pkt_analysis as PktAna
    
#callback function for binding sniff
def network_monitor_callback(pkt):
    #print pkt.command()
    ''''a=pkt.sprintf("{IP:%IP.src%\n}{Raw:%Raw.load%\n}")
    print a'''
    
    pkt_data=PktAna.extract_data_from_packet(pkt,1)

    #print pkt_data
    PktAna.display_data(pkt_data,1)
        
if __name__ == '__main__':
    #start sniff
    sniff(prn=network_monitor_callback, filter="", store=0)
    
    