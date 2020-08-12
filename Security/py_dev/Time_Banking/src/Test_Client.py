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
import time
import threading

from utilities import FileUtil
from service_utils import SrvExchangeClient

logger = logging.getLogger(__name__)

#global variable
addr_list = './addr_list.json'
host_ip = "128.226.79.137:8088"

class ServiceThread (threading.Thread):
	'''
	Threading class to handle service requests by multiple threads pool
	'''
	def __init__(self, threadID, opType, argv):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.opType = opType
		self.argv = argv

	#The run() method is the entry point for a thread.
	def run(self):
		# Add task operation here
		# Launch service request given opType: 0-getService, 1-getAccount.
		if(self.opType==1):
			srv_ret = SrvExchangeClient.getAccount(self.argv[0])['data']
			logger.info("thread-{}: {}".format(self.threadID, srv_ret))
		else:
			srv_ret = SrvExchangeClient.getService(self.argv[0])['data']
			logger.info("thread-{}: {}".format(self.threadID, srv_ret))

   
def test_getService(args):
	logger.info("Get service information.")
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
	logger.info("Get account information.")
	if(args.parter_op==1):
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
	else:
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)

	# construct data argument
	data_args = {}
	data_args['host_ip'] = host_ip
	data_args['host_address'] = node_address


	account_data = SrvExchangeClient.getAccount(data_args)['data']

	# # print account data: 
	logger.info("TB account:{}    uid:{}    balance:{}    status:{}".format(node_address,
	                                                                        account_data['uid'],
	                                                                        account_data['balance'],
	                                                                        account_data['status']) )

def test_registerService(args):
	logger.info("Register service.")
	# construct data argument
	data_args = {}
	data_args['host_ip'] = host_ip
	data_args['op_state'] = args.parter_op

	if(args.parter_op==1):
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
	    data_args['host_address'] = node_address
	    data_args['service_info'] = "Bob need house cleaning service."
	else:
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
	    data_args['host_address'] = node_address
	    data_args['service_info'] = "Samuel can provide house cleaning service."       

	SrvExchangeClient.registerService(data_args)  

def test_negotiateService(args):
	logger.info("Negotiate service.")
	# construct data argument
	data_args = {}
	data_args ['host_ip'] = host_ip
	data_args['time_currency'] = 3
	data_args['op_state'] = args.parter_op 
	if(args.parter_op==0):
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
	    data_args ['host_address'] = node_address
	else:
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
	    data_args['host_address'] = node_address
	    

	SrvExchangeClient.negotiateService(data_args) 

def test_commitService(args):
	logger.info("Commit service.")
	# construct data argument
	data_args = {}
	data_args ['host_ip'] = host_ip
	if(args.parter_op==0):
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)
	else:
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)

	data_args['host_address'] = node_address      

	SrvExchangeClient.commitService(data_args) 

def test_paymentService(args):
	logger.info("Service payment.")
	# construct data argument
	data_args = {}
	data_args ['host_ip'] = host_ip
	if(args.parter_op==0):
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
                        help="Execute test function: 0-Services_demo, \
                                                    1-Services_test")

    parser.add_argument("--service_op", type=int, default=0, 
                        help="Execute test function: 0-test_getService(), \
                                                    1-test_getAccount(), \
                                                    2-test_registerService, \
                                                    3-test_negotiateService \
                                                    4-test_commitService, \
                                                    5-test_paymentService")
    parser.add_argument("--parter_op", type=int, default=0, 
                        help="Register service operation: 0-provider, \
                                                    1-recipient.")
    parser.add_argument("--tx_round", type=int, default=1, help="tx evaluation round")
    parser.add_argument("--thread_count", type=int, default=1, help="service threads count for test")
    parser.add_argument("--wait_interval", type=int, default=1, 
                        help="break time between tx evaluate step.")
    args = parser.parse_args(args=args)
    return args

def Services_demo(args):

    if(args.service_op==1):
        test_getAccount(args)
    elif(args.service_op==2):
        test_registerService(args)
    elif(args.service_op==3):
        test_negotiateService(args)
    elif(args.service_op==4):
        test_commitService(args)
    elif(args.service_op==5):
        test_paymentService(args)
    else:
        test_getService(args)

def threads_pooling(thread_count, opType, fun_args):
	# Create thread pool
	threads_pool = []

	ls_service_nodes = fun_args['service_addr']
	service_nodes_count = len(ls_service_nodes)
	service_nodes_id = 0
	param_args = []

	i=0	
	for i in range(1,thread_count+1):
		# get service_nodes_id to assign service node
		service_nodes_id = i%service_nodes_count
		
		# build param_args list based on fun_args
		data_args = fun_args
		data_args['host_ip'] = ls_service_nodes[service_nodes_id]
		param_args = [data_args]

		# Create new threads
		p_thread = ServiceThread(i, opType, param_args)

		# append to threads pool
		threads_pool.append(p_thread)

		# The start() method starts a thread by calling the run method.
		p_thread.start()

	# The join() waits for all threads to terminate.
	for p_thread in threads_pool:
		p_thread.join()

def Services_test(args):
	data_args = {}
	services_host = FileUtil.JSON_load("services_list.json")

	if(args.parter_op==1):
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam2", addr_list)
	else:
	    node_address = SrvExchangeClient.getAddress("Desk_PI_Plus_Sam1", addr_list)

	for i in range(args.tx_round):
		logger.info("Test run:{}".format(i+1))
		data_args['service_addr'] = services_host['timebanking']
		data_args['host_address'] = node_address

		start_time=time.time()
		# call threads pooling
		threads_pooling(args.thread_count, args.service_op, data_args)
		end_time=time.time()

		exec_time=end_time-start_time

		time_exec=format(exec_time, '.3f')
		logger.info("Execution time is:{}".format(time_exec))

		FileUtil.save_testlog('test_results', 'exec_timebanking_client.log', time_exec)

		time.sleep(args.wait_interval)



if __name__ == "__main__":
    # Logging setup
    FORMAT = "%(asctime)s | %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(level=logging.DEBUG)

    # serviceUtils_logger = logging.getLogger("service_utils")
    # serviceUtils_logger.setLevel(logging.INFO)

    args = define_and_get_arguments()

    if(args.test_func==1): 
        Services_test(args)
    else:
        Services_demo(args)
        pass
	
