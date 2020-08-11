#!/usr/bin/env python3.5

'''
========================
Test_Client module
========================
Created on August.11, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of TB SrvExchangeClient API that access to Web service.
'''

import logging
import argparse
import sys


from service_utils import SrvExchangeClient


# addr_list = '../../node_data/addr_list.json'
addr_list = './addr_list.json'
host_ip = "128.226.88.210"

logger = logging.getLogger(__name__)
    
def test_getService(args):

    # construct data argument
    data_args = {}
    data_args['host_ip'] = host_ip
    # data_args ['host_address'] = node_address


    service_list = SrvExchangeClient.getService(data_args)['data']

    # print service list: 
    logger.info("Dealer:     uid:{}    balance: {}".format(service_list['dealer']['uid'], 
                                                            service_list['dealer']['balance']) )

    logger.info("Provider:   vid:{}    service_info: {}    status: {}".format(service_list['provider']['vid'], 
                                                                        service_list['provider']['serviceinfo'], 
                                                                        service_list['provider']['status']) )

    logger.info("Recipient:  vid:{}    service_info: {}    status: {}".format(service_list['recipient']['vid'], 
                                                                            service_list['recipient']['serviceinfo'],
                                                                            service_list['recipient']['status']) )

def test_getAccount(args):

    if(args.service_op==1):
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
    else:
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)

    # construct data argument
    data_args = {}
    data_args['host_ip'] = host_ip
    data_args['host_address'] = node_address


    account_data = SrvExchangeClient.getAccount(data_args)['data']

    # # print account data: 
    logger.info("TB accounts:{}    uid:{}    balance:{}    status:{}".format(node_address,
                                                                            account_data['uid'],
                                                                            account_data['balance'],
                                                                            account_data['status']) )

def test_registerService(args):

    # construct data argument
    data_args = {}
    data_args['host_ip'] = host_ip
    data_args['op_state'] = args.service_op

    if(args.service_op==1):
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
        data_args['host_address'] = node_address
        data_args['service_info'] = "Bob need house cleaning service."
    else:
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
        data_args['host_address'] = node_address
        data_args['service_info'] = "Samuel can provide house cleaning service."       

    SrvExchangeClient.registerService(data_args)  

def test_negotiateService(args):

    # construct data argument
    data_args = {}
    data_args ['host_ip'] = host_ip
    data_args['time_currency'] = 3
    data_args['op_state'] = args.service_op 
    if(args.service_op==0):
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
        data_args ['host_address'] = node_address
    else:
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
        data_args['host_address'] = node_address
        

    SrvExchangeClient.negotiateService(data_args) 

def test_commitService(args):

    # construct data argument
    data_args = {}
    data_args ['host_ip'] = host_ip
    if(args.service_op==0):
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
    else:
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)

    data_args['host_address'] = node_address      

    SrvExchangeClient.commitService(data_args) 

def test_paymentService(args):

    # construct data argument
    data_args = {}
    data_args ['host_ip'] = host_ip
    if(args.service_op==0):
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
    else:
        node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)

    data_args['host_address'] = node_address      

    SrvExchangeClient.paymentService(data_args)      

  
def define_and_get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Run websocket client test."
    )

    parser.add_argument("--test_func", type=int, default=0, 
                        help="Execute test function: 0-function test, \
                                                    1-test_getService(), \
                                                    2-test_getAccount(), \
                                                    3-test_registerService, \
                                                    4-test_negotiateService \
                                                    5-test_commitService, \
                                                    6-test_paymentService")
    parser.add_argument("--tx_round", type=int, default=1, help="tx evaluation round")
    parser.add_argument("--thread_count", type=int, default=1, help="service threads count for test")
    parser.add_argument("--wait_interval", type=int, default=1, 
                        help="break time between tx evaluate step.")
    parser.add_argument("--service_op", type=int, default=0, 
                        help="Register service operation: 0-provider, \
                                                    1-recipient.")
    args = parser.parse_args(args=args)
    return args
	
if __name__ == "__main__":
    # Logging setup
    FORMAT = "%(asctime)s | %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(level=logging.DEBUG)

    # serviceUtils_logger = logging.getLogger("service_utils")
    # serviceUtils_logger.setLevel(logging.INFO)

    args = define_and_get_arguments()

    if(args.test_func==1): 
        test_getService(args)
    elif(args.test_func==2):
        test_getAccount(args)
    elif(args.test_func==3):
        test_registerService(args)
    elif(args.test_func==4):
        test_negotiateService(args)
    elif(args.test_func==5):
        test_commitService(args)
    elif(args.test_func==6):
        test_paymentService(args)
    else:
        # Services_demo(args)
        pass
	
