'''
========================
Test_Client module
========================
Created on March.17, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide FEd-DDM Client app that access to web service of FEd-DDM Server.
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
		srv_ret = SrvExchangeClient.getBroker(self.argv[0])['data']
		logger.info("thread-{}: {}".format(self.threadID, srv_ret))

   
def test_getBroker(args):
	logger.info("Get broker information.")
	# construct data argument
	data_args = {}
	data_args['host_ip'] = args.host_ip
	# data_args ['host_address'] = node_address


	broker_info = SrvExchangeClient.getBroker(data_args)['data']

	logger.info("Host: account:{} balance:{}".format(broker_info['host']['account'],
                                                    broker_info['host']['balance']) )

	logger.info("Publisher: vid:{} zid: {} status: {} balance:{} txs: {}".format(broker_info['publisher']['vid'], 
	                                                                    broker_info['publisher']['zid'], 
	                                                                    broker_info['publisher']['status'],
	                                                                    broker_info['publisher']['balance'],
	                                                                    broker_info['publisher']['txs']) )

	logger.info("Subscriber: vid:{} zid: {} status: {} balance:{} txs: {}".format(broker_info['subscriber']['vid'], 
	                                                                        broker_info['subscriber']['zid'],
	                                                                        broker_info['subscriber']['status'],
	                                                                        broker_info['subscriber']['balance'],
	                                                                        broker_info['subscriber']['txs']) )

def test_initalizeBroker(args):
	logger.info("Initalize broker data.")
	# construct data argument
	data_args = {} 
	data_args['host_ip'] = args.host_ip

	SrvExchangeClient.initalizeBroker(data_args) 

def test_delegateBroker(args):
	logger.info("Delegate broker for service.")
	# construct data argument
	data_args = {}
	data_args['host_ip'] = args.host_ip
	data_args['op_state'] = args.broker_op

	if(args.broker_op==1):
		node_address = SrvExchangeClient.getAddress("rack1_PI_Plus_2", addr_list)
		data_args['host_address'] = node_address
		data_args['zone_id'] = "zone-2"
		data_args['tx_ref'] = "0xd67b57e6ae47623f"
	else:
		node_address = SrvExchangeClient.getAddress("rack1_PI_Plus_1", addr_list)
		data_args['host_address'] = node_address
		data_args['zone_id'] = "zone-1"  
		data_args['tx_ref'] = "0xea12421586661067"     

	SrvExchangeClient.delegateBroker(data_args)  

def test_updateBroker(args):
	logger.info("Update broker information.")
	# construct data argument
	data_args = {}
	data_args ['host_ip'] = args.host_ip
	data_args['op_state'] = args.broker_op 
	if(args.broker_op==1):
		node_address = SrvExchangeClient.getAddress("rack1_PI_Plus_4", addr_list)
		data_args ['host_address'] = node_address
		data_args['zone_id'] = "zone-4" 
	else:
		node_address = SrvExchangeClient.getAddress("rack1_PI_Plus_3", addr_list)
		data_args['host_address'] = node_address
		data_args['zone_id'] = "zone-3" 
	    

	SrvExchangeClient.updateBroker(data_args) 

def test_commitService(args):
	logger.info("Commit service.")
	# construct data argument
	data_args = {}
	data_args ['host_ip'] = args.host_ip
	data_args['op_state'] = args.broker_op 
	if(args.broker_op==1):
		## subscriber deposit balance
	    data_args['balance'] = 100
	else:
	    data_args['balance'] = 0     

	SrvExchangeClient.commitService(data_args) 

def test_paymentService(args):
	logger.info("Service payment.")
	# construct data argument
	data_args = {}
	data_args ['host_ip'] = args.host_ip     

	SrvExchangeClient.paymentService(data_args)      

  
def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(
	    description="Run websocket client test."
	)

	parser.add_argument("--test_func", type=int, default=0, 
	                    help="Execute test function: 0-Services_demo, \
	                                                1-Services_test")
	parser.add_argument("--service_op", type=int, default=0, 
	                    help="Execute test function: 0-test_getBroker(), \
	                                                1-test_initalizeBroker(), \
	                                                2-test_delegateBroker, \
	                                                3-test_updateBroker \
	                                                4-test_commitService, \
	                                                5-test_paymentService")
	parser.add_argument("--broker_op", type=int, default=0, 
	                    help="broker for service operation: 0-publisher, \
	                                                1-subscriber.")
	parser.add_argument("--host_ip", default='0.0.0.0:8088', type=str, 
						help="server node address format[ip:port].")
	parser.add_argument("--tx_round", type=int, default=1, help="tx evaluation round")
	parser.add_argument("--thread_count", type=int, default=1, help="service threads count for test")
	parser.add_argument("--wait_interval", type=int, default=1, 
	                    help="break time between tx evaluate step.")
	args = parser.parse_args(args=args)
	return args

def Services_demo(args):

    if(args.service_op==1):
        test_initalizeBroker(args)
    elif(args.service_op==2):
        test_delegateBroker(args)
    elif(args.service_op==3):
        test_updateBroker(args)
    elif(args.service_op==4):
        test_commitService(args)
    elif(args.service_op==5):
        test_paymentService(args)
    else:
        test_getBroker(args)

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

	# if(args.broker_op==1):
	#     node_address = SrvExchangeClient.getAddress("rack1_PI_Plus_2", addr_list)
	# else:
	#     node_address = SrvExchangeClient.getAddress("rack1_PI_Plus_1", addr_list)

	for i in range(args.tx_round):
		logger.info("Test run:{}".format(i+1))
		data_args['service_addr'] = services_host['docker_nodes']
		# data_args['host_address'] = node_address

		start_time=time.time()
		# call threads pooling
		threads_pooling(args.thread_count, args.service_op, data_args)
		end_time=time.time()

		exec_time=end_time-start_time

		time_exec=format(exec_time, '.3f')
		logger.info("Execution time is:{}".format(time_exec))

		FileUtil.save_testlog('test_results', 'exec_FedDDM_client.log', time_exec)

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
	
