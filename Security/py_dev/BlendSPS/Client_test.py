import time
import logging
import argparse
import sys
import os
import threading

from wrapper_pyca import Crypto_DSA, Crypto_Hash
from utilities import FileUtil, TypesUtil
from service_utils import TenderUtils, ContractUtils, MonoClient

LOG_INTERVAL = 25

logger = logging.getLogger(__name__)

#global variable

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
		# Launch service request given opType-1-AuthID, 2-CapAC, 3-IndexAuth;
		if(self.opType==1):
			srv_ret = ContractUtils.isValidID(self.argv[0])
			logger.info("thread-{}: {}".format(self.threadID, srv_ret))
		elif(self.opType==2):
			srv_ret = ContractUtils.isValidAccess(self.argv[0])
			logger.info("thread-{}: {}".format(self.threadID, srv_ret))
		elif(self.opType==3):
			srv_ret = ContractUtils.verify_indexToken(self.argv[0], self.argv[1], self.argv[2])
			logger.info("thread-{}: {}".format(self.threadID, srv_ret))
		else:
			srv_ret = MonoClient.Get_DataByID(self.argv[0])
			logger.info("thread-{}: {}".format(self.threadID, srv_ret))


def define_and_get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Run websocket client test."
    )

    parser.add_argument("--test_func", type=int, default=0, 
                        help="Execute test function: 0-function test, \
                        							1-Asyn_KeyGen(), \
                        							2-ENF_test(), \
                        							3-Service_test")
    parser.add_argument("--tx_round", type=int, default=1, help="tx evaluation round")
    parser.add_argument("--thread_count", type=int, default=1, help="service threads count for test")
    parser.add_argument("--wait_interval", type=int, default=1, 
                        help="break time between tx evaluate step.")
    parser.add_argument("--keygen_op", type=int, default=0, 
                        help="Asyn_KeyGen operation: 0-Generate key pairs, \
                        							1-Load key pairs, then Sign and verify test.")
    parser.add_argument("--query_tx", type=int, default=0, 
                        help="Query tx or commit tx: 0-Query, 1-Commit")
    parser.add_argument("--service_op", type=int, default=0, 
                        help="Service operation: 0-MonoService, 1-AuthID, 2-CapAC, 3-IndexAuth")
    args = parser.parse_args(args=args)
    return args

def ENF_test(args):
	ENF_file = "./data/ENF_sample.log"
	for i in range(args.tx_round):
		logger.info("Test run:{}".format(i+1))
		# -------------------------- Tendermint test ----------------------------------
		if(args.query_tx==0):
			# verify hash model
			logger.info("Verify ENF: '{}' --- {}\n".format(ENF_file, 
			                                            TenderUtils.verify_ENF(ENF_file)) )
		else:
			# call tx_evaluate() and record tx_commit time
			logger.info("Tx commit ENF '{}' --- {}\n".format(ENF_file, 
			                                            TenderUtils.tx_evaluate(ENF_file)))
		time.sleep(args.wait_interval)

def Asyn_KeyGen(args):
	logger.info('Asyn_KeyGen() running...')
	if(args.keygen_op==0):
		logger.info('Generate key pairs')
		key_pairs = Crypto_DSA.generate_key_pairs()
		# Crypto_DSA.display_key_pairs(key_pairs)

		public_key = Crypto_DSA.get_public_key(key_pairs['public_key'])
		# logger.info(public_key.public_numbers())

		private_key = Crypto_DSA.get_private_key(key_pairs['private_key'], public_key)
		# logger.info(private_key.private_numbers().x)

		public_key_bytes = Crypto_DSA.get_public_key_bytes(public_key)
		logger.info(public_key_bytes)

		private_key_bytes = Crypto_DSA.get_private_key_bytes(private_key, encryp_pw=b'samuelxu999')
		logger.info(private_key_bytes)

		# save key bytes to files
		Crypto_DSA.save_key_bytes(public_key_bytes, 'public_key_file')
		Crypto_DSA.save_key_bytes(private_key_bytes, 'private_key_file')

	else:
		logger.info('Load key pairs')

		load_public_key_bytes = Crypto_DSA.load_key_bytes('public_key_file')
		load_private_key_bytes = Crypto_DSA.load_key_bytes('private_key_file')

		reload_public_key = Crypto_DSA.load_public_key_bytes(load_public_key_bytes)
		logger.info(reload_public_key.public_numbers())

		reload_private_key = Crypto_DSA.load_private_key_bytes(load_private_key_bytes, encryp_pw=b'samuelxu999')
		logger.info(reload_private_key.private_numbers().x)

		# logger.info('Sign and verify test')
		#sing message
		message_data = b'samuel'
		sign_value = Crypto_DSA.sign(reload_private_key, message_data)

		# #verify signature
		verify_sign=Crypto_DSA.verify(reload_public_key,sign_value,message_data)
		logger.info("Sign verification: {}".format(verify_sign))

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
		# build parameters list based on opType
		if(opType==3):
			param_args = [ls_service_nodes[service_nodes_id], fun_args['index_id'], fun_args['filepath']]
		else:
			data_args = fun_args
			data_args['service_addr'] = ls_service_nodes[service_nodes_id]
			param_args = [data_args]
		# print(param_args)

		# Create new threads
		p_thread = ServiceThread(i, opType, param_args)

		# append to threads pool
		threads_pool.append(p_thread)

		# The start() method starts a thread by calling the run method.
		p_thread.start()

	# The join() waits for all threads to terminate.
	for p_thread in threads_pool:
		p_thread.join()

def Service_test(args):
	addr_list = "./addr_list.json"
	node_name = "Desk_PI_Plus_Sam1"
	services_host = FileUtil.JSON_load("services_list.json")
	node_address = ContractUtils.getAddress(node_name, addr_list)
	data_args = {}

	for i in range(args.tx_round):
		logger.info("Test run:{}".format(i+1))	
		if(args.service_op==1):
			data_args['service_addr'] = services_host['authid']
			data_args['host_address'] = node_address

		elif(args.service_op==2):
			data_args['service_addr'] = services_host['blendcac']
			data_args['host_address'] = node_address
			data_args['url_rule'] = '/BlendCAC/api/v1.0/getCapToken'

		elif(args.service_op==3):
			data_args['service_addr'] = services_host['indexauth']
			data_args['index_id'] = "1"
			data_args['filepath'] = "./features/0_2_person1/13.2.52.txt"
		else:
			data_args['service_addr'] = services_host['mono_app']
			data_args['project_id'] = 1
			data = {}
			data['host_address'] = node_address
			data['url_rule'] = '/BlendCAC/api/v1.0/getCapToken'
			data['index_id'] = "1"
			data['filepath'] = "./features/0_2_person1/13.2.52.txt"
			data_args['data'] = data

		start_time=time.time()
		# call threads pooling
		threads_pooling(args.thread_count, args.service_op, data_args)
		end_time=time.time()

		exec_time=end_time-start_time

		time_exec=format(exec_time, '.3f')
		logger.info("Execution time is:{}".format(time_exec))

		FileUtil.save_testlog('test_results', 'exec_services_client.log', time_exec)

		time.sleep(args.wait_interval)



def Services_demo(args):
	services_host = FileUtil.JSON_load("services_list.json")
	addr_list = "./addr_list.json"
	data_args = {}

	start_time=time.time()

	if(args.service_op==1):
		logger.info("test AuthID service")
		node_name = "Desk_PI_Plus_Sam1"
		node_address = ContractUtils.getAddress(node_name, addr_list)
		# construct data argument
		data_args ['service_addr'] = services_host['authid'][0]
		data_args ['host_address'] = node_address
		

		logger.info(ContractUtils.getVNodeInfo(data_args))
		logger.info(ContractUtils.isValidID(data_args))
	elif(args.service_op==2):
		logger.info("test CapAC service")
		node_name = "Desk_PI_Plus_Sam1"
		node_address = ContractUtils.getAddress(node_name, addr_list)
		# construct data argument
		data_args ['service_addr'] = services_host['blendcac'][0]
		data_args ['host_address'] = node_address
		data_args ['url_rule'] = '/BlendCAC/api/v1.0/getCapToken'

		logger.info(ContractUtils.getCapToken(data_args))
		logger.info(ContractUtils.isValidAccess(data_args))
	elif(args.service_op==3):
		logger.info("test IndexAuth service")
		service_addr = services_host['indexauth'][0]
		index_id = "1"
		filepath = "./features/0_2_person1/13.2.52.txt"
		filepath0 = "./features/0_2_person1/13.4.53.txt"

		logger.info(ContractUtils.getIndexToken(service_addr, index_id))
		logger.info(ContractUtils.getAuthorizedNodes(service_addr))
		logger.info(ContractUtils.verify_indexToken(service_addr, index_id, filepath))
	else:
		node_name = "Desk_PI_Plus_Sam1"
		node_address = ContractUtils.getAddress(node_name, addr_list)
		logger.info("{} address is: {}.".format(node_name, node_address))

	end_time=time.time()

	exec_time=end_time-start_time

	time_exec=format(exec_time*1000, '.3f')
	logger.info("Execution time is:{}".format(time_exec))



if __name__ == "__main__":
	# Logging setup
	FORMAT = "%(asctime)s | %(message)s"
	logging.basicConfig(format=FORMAT)
	logger.setLevel(level=logging.DEBUG)

	serviceUtils_logger = logging.getLogger("service_utils")
	serviceUtils_logger.setLevel(logging.INFO)

	args = define_and_get_arguments()

	if(args.test_func==1):
		Asyn_KeyGen(args)
	elif(args.test_func==2):
		ENF_test(args)
	elif(args.test_func==3):
		Service_test(args)
	else:
		Services_demo(args)
