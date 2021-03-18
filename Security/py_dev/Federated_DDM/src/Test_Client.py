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

from utils.utilities import FileUtil, TypesUtil
from utils.service_utils import ServiceThread, BrokerUtils, AccountUtils, TenderUtils


logger = logging.getLogger(__name__)

  
def Services_demo(args):
	if(args.service_op==1):
		BrokerUtils.test_initalizeBroker(args)
	elif(args.service_op==2):
		BrokerUtils.test_delegateBroker(args)
	elif(args.service_op==3):
		BrokerUtils.test_updateBroker(args)
	elif(args.service_op==4):
		BrokerUtils.test_commitService(args)
	elif(args.service_op==5):
		BrokerUtils.test_paymentService(args)
	else:
		BrokerUtils.test_getBroker(args)

def Services_test(args):
	data_args = {}
	services_host = FileUtil.JSON_load("services_list.json")

	for i in range(args.tx_round):
		logger.info("Test run:{}".format(i+1))
		data_args['service_addr'] = services_host['server_nodes']
		# data_args['host_address'] = node_address

		start_time=time.time()
		# call threads pooling
		ServiceThread.threads_pooling(args.thread_count, args.service_op, data_args)
		end_time=time.time()

		exec_time=end_time-start_time

		time_exec=format(exec_time, '.3f')
		logger.info("Execution time is:{}".format(time_exec))

		FileUtil.save_testlog('test_results', 'exec_FedDDM_client.log', time_exec)

		time.sleep(args.wait_interval)

def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(
	    description="Run websocket client test."
	)

	parser.add_argument("--test_func", type=int, default=0, 
	                    help="Execute test function: 0-Services_demo, \
	                                                1-Services_test, \
	                                                2-new_account(), \
	                                                3-tx_verify(), \
	                                                4-tx_commit()")
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
	parser.add_argument("--tx_hash", default='0x00', type=str, 
						help="hash value of tx, used for querying tx data.")
	parser.add_argument("--tx_round", type=int, default=1, help="tx evaluation round")
	parser.add_argument("--thread_count", type=int, default=1, help="service threads count for test")
	parser.add_argument("--wait_interval", type=int, default=1, 
	                    help="break time between tx evaluate step.")
	args = parser.parse_args(args=args)
	return args

if __name__ == "__main__":
	# Logging setup
	FORMAT = "%(asctime)s | %(message)s"
	logging.basicConfig(format=FORMAT)
	logger.setLevel(level=logging.DEBUG)

	serviceUtils_logger = logging.getLogger("utils.service_utils")
	serviceUtils_logger.setLevel(logging.INFO)

	args = define_and_get_arguments()

	if(args.test_func==1): 
		Services_test(args)
	elif(args.test_func==2): 
		AccountUtils.new_account()
	elif(args.test_func==3):
		TenderUtils.tx_verify(args.tx_hash)
	elif(args.test_func==4):
		json_tx = AccountUtils.build_tx(args.broker_op)
		tx_ret = TenderUtils.tx_commit(json_tx)
		print(tx_ret)
	else:
		Services_demo(args)
		pass
	
