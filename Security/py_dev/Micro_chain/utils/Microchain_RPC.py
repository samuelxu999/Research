'''
========================
Microchain_RPC module
========================
Created on Feb.13, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of client APIs that access to Microchain_server node.
                  Mainly used to client test and demo
'''
import random
import time
import logging
import threading
import copy
import asyncio

from network.wallet import Wallet
from network.nodes import *
from consensus.transaction import Transaction
from utils.utilities import TypesUtil, FileUtil
from utils.service_api import SrvAPI
from utils.configuration import *
from randomness.randshare import RandShare, RandOP

logger = logging.getLogger(__name__)

## ---------------------- Internal function and class -----------------------------
class TxsThread(threading.Thread):
	'''
	Threading class to handle multiple txs threads pool
	'''
	def __init__(self, argv):
		threading.Thread.__init__(self)
		self.argv = argv

	#The run() method is the entry point for a thread.
	def run(self):
		## set parameters based on argv
		tx_sender = self.argv[0]
		mypeer_nodes = self.argv[1]
		tx_size = self.argv[2]

		sender_address = tx_sender['address']
		sender_private_key = tx_sender['private_key']
		## set recipient_address as default value: 0
		recipient_address = '0'
		time_stamp = time.time()

		# using random byte string for value of tx
		hex_value = TypesUtil.string_to_hex(os.urandom(tx_size))

		mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, hex_value)

		# sign transaction
		sign_data = mytransaction.sign('samuelxu999')

		# verify transaction
		dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
		                                        mytransaction.recipient_address,
		                                        mytransaction.time_stamp,
		                                        mytransaction.value)

		## --------------------- send transaction --------------------------------------
		transaction_json = mytransaction.to_json()
		transaction_json['signature']=TypesUtil.string_to_hex(sign_data)

		node_info = mypeer_nodes.load_ByAddress(sender_address)
		json_nodes = TypesUtil.string_to_json(list(mypeer_nodes.get_nodelist())[0])

		## trigger broadcast_tx on tx_sender
		SrvAPI.POST('http://'+json_nodes['node_url']+'/test/transaction/broadcast', 
								transaction_json)

## --------------------------------- Microchain_RPC ------------------------------------------
class Microchain_RPC(object):
	'''
	------------ A client instance of ENFchain_RPC contains the following arguments: -------
	self.wallet: 			local wallet account management
	self.wallet_net: 		network wallet accounts management, for test purpose
	self.peer_nodes: 		peer nodes management	
	'''
	def __init__(self, 	keystore="keystore", 
						keystore_net="keystore_net"):
		## Instantiate the local wallet and load all accounts information
		self.wallet = Wallet(keystore)
		self.wallet.load_accounts()

		## Instantiate the net wallet and load all accounts information
		self.wallet_net = Wallet(keystore_net)
		self.wallet_net.load_accounts()

		## Instantiate the Peer Nodes management adapter
		self.peer_nodes = Nodes(db_file = PEERS_DATABASE)
		self.peer_nodes.load_ByAddress()

		# Instantiate the verified Nodes management adapter
		self.verify_nodes = Nodes(db_file = VERIFY_DATABASE)
		self.verify_nodes.load_ByAddress()

	# =========================== client side REST API ==================================
	def run_consensus(self, target_address, exec_consensus, isBroadcast=False):
		json_msg={}
		json_msg['consensus_run']=exec_consensus

		if(not isBroadcast):
			json_response=SrvAPI.POST('http://'+target_address+'/test/consensus/run', json_msg)
			json_response = {'run_consensus': target_address, 'status': json_msg['consensus_run']}
		else:
			SrvAPI.broadcast_POST(self.peer_nodes.get_nodelist(), json_msg, '/test/consensus/run', True)
			json_response = {'run_consensus': 'broadcast', 'status': json_msg['consensus_run']}
		logger.info(json_response)

	def validator_getinfo(self, target_address, isBroadcast=False):
		info_list = []
		if(not isBroadcast):
			json_response = SrvAPI.GET('http://'+target_address+'/test/validator/getinfo')
			info_list.append(json_response)
		else:
			for node in self.peer_nodes.get_nodelist():
				json_node = TypesUtil.string_to_json(node)
				json_response = SrvAPI.GET('http://'+json_node['node_url']+'/test/validator/getinfo')
				info_list.append(json_response)
		return info_list

	def launch_txs(self, tx_size):
		## Instantiate mypeer_nodes using deepcopy of self.peer_nodes
		mypeer_nodes = copy.deepcopy(self.peer_nodes)

		# Create thread pool
		threads_pool = []

		## 1) for each account to send tx 
		for sender in self.wallet_net.accounts:
			## Create new threads for tx
			p_thread = TxsThread( [sender, mypeer_nodes, tx_size] )

			## append to threads pool
			threads_pool.append(p_thread)

			## The start() method starts a thread by calling the run method.
			p_thread.start()

		# 2) The join() waits for all threads to terminate.
		for p_thread in threads_pool:
			p_thread.join()

		tx_count = len(threads_pool)
		logger.info('launch transactions: tx size {}    total count: {}'.format(tx_size, tx_count))

	def send_transaction(self, target_address, tx_size=1, isBroadcast=False):
		##----------------- build test transaction --------------------
		sender = self.wallet.accounts[0]
		sender_address = sender['address']
		sender_private_key = sender['private_key']
		## set recipient_address as default value: 0
		recipient_address = '0'
		time_stamp = time.time()
		
		## using random byte string for value of tx; value can be any bytes string.
		hex_value = TypesUtil.string_to_hex(os.urandom(tx_size))

		mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, hex_value)

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
		# print(transaction_json)
		if(not isBroadcast):
		    json_response=SrvAPI.POST('http://'+target_address+'/test/transaction/verify', 
		    						transaction_json)
		else:
		    json_response=SrvAPI.POST('http://'+target_address+'/test/transaction/broadcast', 
		                            transaction_json)
		logger.info(json_response)

	def get_transactions(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/transactions/get')
		transactions = json_response['transactions']		
		return transactions

	def query_transaction(self, target_address, tx_json):
		json_response=SrvAPI.GET('http://'+target_address+'/test/transaction/query', tx_json)
		return json_response

	def start_mining(self, target_address, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.GET('http://'+target_address+'/test/mining')
		else:
			SrvAPI.broadcast_GET(self.peer_nodes.get_nodelist(), '/test/mining', True)
			json_response = {'start mining': 'broadcast'}

		logger.info(json_response)

	def start_voting(self, target_address, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.GET('http://'+target_address+'/test/block/vote')
		else:
			SrvAPI.broadcast_GET(self.peer_nodes.get_nodelist(), '/test/block/vote', True)
			json_response = {'verify_vote': 'broadcast'}
		logger.info(json_response)

	def get_neighbors(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/p2p/neighbors')
		return json_response

	def get_peers(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/p2p/peers')
		return json_response

	async def get_account(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/account/info')
		json_response['info']['node_url'] = target_address
		return json_response

	async def get_peers_info(self, target_address):
		## get p2p peers
		live_peers = self.get_peers(target_address)['peers']
		# print(live_peers)

		## set address list for each peer
		ls_peers = [peer[1]+":808"+str(peer[2])[-1] for peer in live_peers ]
		# print(ls_peers)	

		## async call get_account to query each peer's info
		cos = list(map(self.get_account, ls_peers))
		gathered = await asyncio.gather(*cos)
		info_peers = [node['info'] for node in gathered if node is not None]	

		return info_peers

	def get_peernodes(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/peernodes/get')
		return json_response

	def add_peernodes(self, target_address, json_node, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.POST('http://'+target_address+'/test/peernodes/add', json_node)
			logger.info(json_response)
		else:
			for target_node in target_address:
				try:
					SrvAPI.POST('http://'+target_node+'/test/peernodes/add', json_node)
				except:
					logger.info("access {} failed.".format(target_node))
					pass

	def remove_peernode(self, target_address, json_node, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.POST('http://'+target_address+'/test/peernodes/remove', json_node)
			logger.info(json_response)
		else:
			for target_node in target_address:
				try:
					SrvAPI.POST('http://'+target_node+'/test/peernodes/remove', json_node)
				except:
					logger.info("access {} failed.".format(target_node))
					pass

	def get_verifynodes(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/verifynodes/get')
		return json_response

	def check_verifynode(self, target_address, node_address):
		json_data = {}
		json_data['address'] = node_address
		json_response=SrvAPI.GET('http://'+target_address+'/test/verifynodes/check', json_data)
		return json_response

	def add_verifynode(self, target_address, json_node, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.POST('http://'+target_address+'/test/verifynodes/add', json_node)
			logger.info(json_response)
		else:
			for target_node in target_address:
				try:
					SrvAPI.POST('http://'+target_node+'/test/verifynodes/add', json_node)
				except:
					logger.info("access {} failed.".format(target_node))
					pass

	def remove_verifynode(self, target_address, json_node, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.POST('http://'+target_address+'/test/verifynodes/remove', json_node)
			logger.info(json_response)
		else:
			for target_node in target_address:
				try:
					SrvAPI.POST('http://'+target_node+'/test/verifynodes/remove', json_node)
				except:
					logger.info("access {} failed.".format(target_node))
					pass

	def get_chain(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
		return json_response

	def check_head(self):
		SrvAPI.broadcast_GET(self.peer_nodes.get_nodelist(), '/test/chain/checkhead')
		json_response = {'Reorganize processed_head': 'broadcast'}

	## ================================ randomshare client API =================================
	def create_randshare(self, target_address, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/create')
		else:
			SrvAPI.broadcast_GET(self.peer_nodes.get_nodelist(), '/test/randshare/create', True)
			json_response = {'broadcast_create_randshare': 'Succeed!'}
		return json_response

	def fetch_randshare(self, target_address, isBroadcast=False):
		if(not isBroadcast):
			# get host address
			json_node={}
			json_node['address'] = self.wallet.accounts[0]['address']
			json_response=SrvAPI.POST('http://'+target_address+'/test/randshare/fetch', json_node)
		else:
			SrvAPI.broadcast_GET(self.peer_nodes.get_nodelist(), '/test/randshare/cachefetched', True)
			json_response = {'broadcast fetch_randshare': 'Succeed!'}
		return json_response

	def verify_randshare(self, target_address, isBroadcast=False):
		if(not isBroadcast):
			json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/verify')
		else:
			SrvAPI.broadcast_GET(self.peer_nodes.get_nodelist(), '/test/randshare/verify', True)
			json_response = {'broadcast verify_randshare': 'Succeed!'}
		return json_response

	def recovered_randshare(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/recovered')
		return json_response

	def fetchvote_randshare(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/fetchvote')
		return json_response

	def vote_randshare(self, target_address):
		json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/cachevote')
		return json_response

	# ====================================== Random share test ==================================
	## request for share from peers and cache to local
	def cache_fetch_share(self, target_address):
		# read cached randshare
		host_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)
		if( host_shares == None):
			host_shares = {}
		fetch_share=self.fetch_randshare(target_address)
		# logging.info(fetch_share)
		for (node_name, share_data) in fetch_share.items():
			host_shares[node_name]=share_data
		# update host shares 
		RandShare.save_sharesInfo(host_shares, RandOP.RandDistribute)

	## request for recovered shares from peers and cache to local 
	def cache_recovered_shares(self, target_address):
		# read cached randshare
		recovered_shares=RandShare.load_sharesInfo(RandOP.RandRecovered)
		if( recovered_shares == None):
			recovered_shares = {}
		host_recovered_shares=self.recovered_randshare(target_address)
		for (node_name, share_data) in host_recovered_shares.items():
			recovered_shares[node_name]=share_data
		# update host shares 
		RandShare.save_sharesInfo(recovered_shares, RandOP.RandRecovered)

	# request for vote shares from peers and cache to local 
	def cache_vote_shares(self, target_address):
		# read cached randshare
		vote_shares=RandShare.load_sharesInfo(RandOP.RandVote)
		if( vote_shares == None):
			vote_shares = {}
		host_vote_shares=fetchvote_randshare(target_address)
		# logging.info(host_vote_shares)
		for (node_name, share_data) in host_vote_shares.items():
			vote_shares[node_name]=share_data
		# update host shares 
		RandShare.save_sharesInfo(vote_shares, RandOP.RandVote)

	# test recovered shares
	def recovered_shares(self, host_address):		
		# read cached randshare
		recovered_shares=RandShare.load_sharesInfo(RandOP.RandRecovered)
		if( recovered_shares == None):
			recovered_shares = {}
		# print(recovered_shares)

		## Instantiate mypeer_nodes using deepcopy of self.peer_nodes
		peer_nodes = copy.deepcopy(self.peer_nodes)
		peer_nodes.load_ByAddress(host_address)
		json_nodes = TypesUtil.string_to_json(list(peer_nodes.get_nodelist())[0])
		# get public numbers given peer's pk
		public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

		# get shares information
		shares = recovered_shares[host_address]
		# print(shares)
		# instantiate RandShare to verify share proof.
		myrandshare = RandShare()
		myrandshare.p = public_numbers.n

		secret=myrandshare.recover_secret(shares)
		# print('secret recovered from node shares:', secret)
		return secret

	# test new random generator
	def new_random(self, ls_secret):
		# get host account information
		json_nodes=self.wallet.accounts[0]
		# get public numbers given pk
		public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

		# instantiate RandShare to verify share proof.
		myrandshare = RandShare()
		myrandshare.p = public_numbers.n

		# calculate new random number
		random_secret = myrandshare.calculate_random(ls_secret)

		logger.info("New random secret: {}".format(random_secret))