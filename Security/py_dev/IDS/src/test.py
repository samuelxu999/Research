import sys
from scapy.all import *

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
        
if __name__ == '__main__':
    #test_demo()
    #test_fun() 
    pkts = sniff(prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}{Raw:%Raw.load%\n}"))
    
    