'''
========================
service utilities module
========================
Created on March.18, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of test API to interact with RPC exposed by service node.
'''

import logging
import sys
import time
import threading

from account.wallet import Wallet
from account.transaction import Transaction
from utils.utilities import FileUtil, TypesUtil, FuncUtil
from utils.brokerClient_RPC import SrvExchangeClient
from utils.Tender_RPC import Tender_RPC

logger = logging.getLogger(__name__)

#global variable
addr_list = './addr_list.json'

class ServiceThread(threading.Thread):
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

	@staticmethod
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

class BrokerUtils(object):
	@staticmethod 
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
	@staticmethod 
	def test_initalizeBroker(args):
		logger.info("Initalize broker data.")
		# construct data argument
		data_args = {} 
		data_args['host_ip'] = args.host_ip

		SrvExchangeClient.initalizeBroker(data_args) 

	@staticmethod 
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

	@staticmethod 
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

	@staticmethod 
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

	@staticmethod 
	def test_paymentService(args):
		logger.info("Service payment.")
		# construct data argument
		data_args = {}
		data_args ['host_ip'] = args.host_ip     

		SrvExchangeClient.paymentService(data_args)

class AccountUtils(object):
	@staticmethod
	def new_account():
		## Instantiate the Wallet
		mywallet = Wallet()

		## load accounts
		mywallet.load_accounts()

		## new account
		mywallet.create_account('samuelxu999')

		if(len(mywallet.accounts)!=0):
			account = mywallet.accounts[0]
			print(TypesUtil.hex_to_string(account['public_key']))
			print(len(account['address']))

		#list account address
		print(mywallet.list_address())
	
	@staticmethod
	def build_tx(broker_op):
		## Instantiate the Wallet
		mywallet = Wallet()

		## load accounts
		mywallet.load_accounts()

		#----------------- test transaction --------------------
		sender = mywallet.accounts[0]

		# generate transaction
		sender_address = sender['address']
		sender_private_key = sender['private_key']

		if(broker_op==1): 
			## subscriber deposit token
			recipient_address = SrvExchangeClient.getAddress("rack1_PI_Plus_2", addr_list)
			# tx_str = '100'
			value = 100
		else:
			## publisher set description and requirement.
			recipient_address = SrvExchangeClient.getAddress("rack1_PI_Plus_1", addr_list)
			json_data = {}
			json_data['name'] = "samuel"
			json_data['resource'] = "/test/api/v1.0/dt"
			json_data['action'] = "GET"
			json_data['price'] = 80
			json_data['conditions'] = {}
			json_data['conditions']['value'] = {}
			json_data['conditions']['value']['start']="8:30"
			json_data['conditions']['value']['end']="19:25"
			json_data['conditions']['value']['week']="M|T|F"
			json_data['conditions']['type'] = "Timespan"
			# tx_str = TypesUtil.json_to_string(json_data)	
			value = json_data

		# set time stamp
		time_stamp = time.time()

		mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, value)

		# sign transaction
		sign_data = mytransaction.sign('samuelxu999')

		# verify transaction
		dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
		                                        mytransaction.recipient_address,
		                                        mytransaction.time_stamp,
		                                        mytransaction.value)
		#send transaction
		transaction_json = mytransaction.to_json()
		transaction_json['signature']=TypesUtil.string_to_hex(sign_data)

		return transaction_json 

class TenderUtils(object):
	@staticmethod
	def tx_verify(tx_hash):
		'''
		Verify tx data by querying from blockchain
		Args:
		    tx_hash: hash value of tx
		Returns:
		    Verified result: True or False
		'''
		# 1) Read token data using call
		ls_time_exec = []

		query_json = {}
		query_json['data']='"' + tx_hash +'"'
		start_time=time.time()

		query_ret=Tender_RPC.abci_query(query_json)

		# -------- parse value from response and display it ------------
		key_str=query_ret['result']['response']['key']
		value_str=query_ret['result']['response']['value']
		# print(query_ret)
		logger.info("Fetched transaction:")
		logger.info("key: {}".format(TypesUtil.base64_to_ascii(key_str)) )
		if( value_str!= None):
			query_tx_value = TypesUtil.base64_to_ascii(value_str)
		else:
			query_tx_value = ''
		# convert tx to json format
		# logger.info("value: {}".format(query_tx_value))
		if(query_tx_value==''):
			logger.info("Not valid value. verify fail.")
			return False
		
		query_tx_json = TypesUtil.tx_to_json(query_tx_value)
		logger.info("value: {}".format(query_tx_json))		

		# 2) verify signature
		## Instantiate the Wallet
		mywallet = Wallet()

		## load accounts
		mywallet.load_accounts()

		sender = mywallet.accounts[0]

		sender_pk = sender['public_key']

		# ====================== rebuild transaction ==========================
		dict_transaction = Transaction.get_dict(query_tx_json['sender_address'], 
												query_tx_json['recipient_address'],
												query_tx_json['time_stamp'],
												query_tx_json['value'])

		sign_data = TypesUtil.hex_to_string(query_tx_json['signature'])

		verify_result = Transaction.verify(sender_pk, sign_data, dict_transaction)

		logger.info("verify transaction: {}".format(verify_result))

		exec_time=time.time()-start_time
		ls_time_exec.append( format( exec_time*1000, '.3f' ) ) 

		# Prepare log messgae
		str_time_exec=" ".join(ls_time_exec)
		FileUtil.save_testlog('test_results', 'exec_tx_verify.log', str_time_exec)

	@staticmethod
	def tx_commit(tx_data):
		'''
		Launch tx and evaluate tx committed time
		Args:
		    tx_data: tx json format data
		Returns:
		    tx_summary: tx committed reulst including block_hash, height and tx_hash
		'''
		## 1) calculate tx_hash given tx_data
		logger.info("tx value:{}".format(tx_data))
		dict_tx = Transaction.json_to_hash(tx_data)
		# test_data = {'sender_address': '670a8061427285962a4715954c54411ecb9ccc95', 'recipient_address': '0xea12421586661067abe5b8b7222f2bef79d69b8c', 'time_stamp': 1616101416.2954514, 'value': '100', 'signature': '84843dbf1a990c8b6ea5c2763605781e47159eb66e3f1072158d18011c5a5f24a5144a19069ab031e822c0cb4ad961c095d356e56bae3f4b7b87ce60e595ed8e'}
		# dict_tx = Transaction.json_to_hash(test_data)
		tx_hash = FuncUtil.hashfunc_sha1(str(dict_tx).encode('utf8'))
		# logger.info("tx hash:{}".format(tx_hash))

		# 2) evaluate tx committed time
		start_time=time.time()
		logger.info("commit tx_hash:{} to blockchain...\n".format(tx_hash)) 

		# -------- prepare parameter for tx ------------
		tx_json = {}
		key_str = str(tx_hash)
		# value_json = {}
		# value_json['ENF']=json_ENF['ENF']
		# value_json['sign_ENF']=TypesUtil.string_to_hex(sign_ENF)

		# convert json to tx format
		value_str = TypesUtil.json_to_tx(tx_data)
		tx_data = key_str + "=" + value_str 
		# --------- build parameter string: tx=? --------
		tx_json['tx']='"' + tx_data +'"' 
		# print(tx_json)
		tx_ret=Tender_RPC.broadcast_tx_commit(tx_json)
		exec_time=time.time()-start_time
		logger.info("tx committed time: {:.3f}\n".format(exec_time, '.3f')) 
		FileUtil.save_testlog('test_results', 'exec_tx_commit.log', format(exec_time, '.3f'))
		# print(tx_ret)

		## build summary of tx commitment
		tx_summary={}
		tx_summary['hash'] = tx_ret['result']['hash']
		tx_summary['height'] = tx_ret['result']['height']
		tx_summary['tx_hash'] = key_str
		FileUtil.save_testlog('test_results', 'tx_summary.log', tx_summary)
		return tx_summary
