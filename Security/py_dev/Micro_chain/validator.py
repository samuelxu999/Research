'''
========================
validator.py
========================
Created on May.31, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide blockchain implementation.
@Reference: 
'''

from collections import OrderedDict
import os
import binascii
import threading
import logging
import time

import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4
import copy

from utilities import FileUtil, TypesUtil
from wallet import Wallet
from transaction import Transaction
from nodes import PeerNodes
from block import Block
from vote import VoteCheckPoint
from db_adapter import DataManager
from consensus import *
from configuration import *
from service_api import SrvAPI

logger = logging.getLogger(__name__)

class Validator(object):
	'''
	--------------------------- A Validator contains the following arguments: ----------------------------------
	self.node_id: 						GUID 
	self.consensus: 					Consensus algorithm
	self.chain_db: 						local chain database adapter
	self.consensus: 					consensus algorithm
	self.wallet: 						wallet account management
	self.peer_nodes: 					peer nodes management 

	self.transactions: 					local transaction pool
	self.chain: 						local chain data buffer
	self.block_dependencies: 			used to save blocks need for dependency
	self.vote_dependencies: 			used to save pending vote need for dependency
	self.processed_head: 				the latest processed descendant of the highest justified checkpoint
	self.current_head: 					the current received descendant of the highest justified checkpoint
	self.highest_justified_checkpoint: 	the block with higest justified checkpoint
	self.highest_finalized_checkpoint: 	the block with higest finalized checkpoint
	
	self.votes: 						Map {sender -> vote_db object} which contains all the votes data for check
	self.vote_count: 					Map {source_hash -> {target_hash -> count}} to count the votes

	self.sum_stake:						Summary of stake that all validators, used for PoS;
	self.committee_size:				Number of validators to participant the consensus committee;
	self.block_epoch:					Block proposal epoch size, used for set finalized checkpoint;
	
	self.msg_buf: 						Buffer messages which are procossed by daemon function process_msg(self)
	self.rev_thread: 					daemon thread object to handle process_msg(self)
	--------------------------------------------------------------------------------------------------------------
	''' 

	def __init__(self, 	consensus=ConsensusType.PoW, 
						block_epoch=EPOCH_SIZE, 
						pause_epoch=1, 
						phase_delay=BOUNDED_TIME):

		# Instantiate the Wallet
		self.wallet = Wallet()
		self.wallet.load_accounts()

		# Instantiate the PeerNodes
		self.peer_nodes = PeerNodes()
		self.peer_nodes.load_ByAddress()

		# New database manager to manage chain data
		self.chain_db = DataManager(CHAIN_DATA_DIR, BLOCKCHAIN_DATA)
		self.chain_db.create_table(CHAIN_TABLE)

		#Create genesis block
		genesis_block = Block()
		json_data = genesis_block.to_json()

		# no local chain data, generate a new validator information
		if( self.chain_db.select_block(CHAIN_TABLE)==[] ):
			#add genesis_block as 2-finalized
			self.add_block(json_data, 2)
		
		# new chain buffer
		self.chain = []

		# new transaction pool
		self.transactions = []                            

		# votes pool Map {sender -> vote_db object}
		self.votes = {}

		#choose consensus algorithm
		self.consensus = consensus

		#-------------- load chain info ---------------
		chain_info = self.load_chainInfo()
		if(chain_info == None):
			#Generate random number to be used as node_id
			self.node_id = str(uuid4()).replace('-', '')

			# initialize pending data buffer
			self.block_dependencies = {}
			self.vote_dependencies = {}
			self.processed_head = json_data
			self.highest_justified_checkpoint = json_data
			self.highest_finalized_checkpoint = json_data
			#self.votes = {}
			self.vote_count = {}
			# update chain info
			self.save_chainInfo()
		else:
			#Generate random number to be used as node_id
			self.node_id = chain_info['node_id']
			self.block_dependencies = chain_info['block_dependencies']
			self.vote_dependencies = chain_info['vote_dependencies']
			self.processed_head = chain_info['processed_head']
			self.highest_justified_checkpoint = chain_info['highest_justified_checkpoint']
			self.highest_finalized_checkpoint = chain_info['highest_finalized_checkpoint']
			#self.votes = chain_info['votes']
			self.vote_count = chain_info['vote_count']
		
		# point current head to processed_head
		self.current_head = self.processed_head

		# set total stake and number of validators
		ls_nodes=list(self.peer_nodes.get_nodelist())
		# set sum_stake is peer nodes count
		self.sum_stake = len(ls_nodes)
		# set committee_size as peer nodes count 
		self.committee_size = len(ls_nodes)
		# set block_epoch given args
		self.block_epoch = block_epoch;

		''' 
		Threading as daemon to process received message.
		The process_msg() method will be started and it will run in the background
		until the application exits.
		'''
		# new buffer list to process received message by on_receive().
		self.msg_buf = []
		# define a thread to handle received messages by executing process_msg()
		self.rev_thread = threading.Thread(target=self.process_msg, args=())
		# Set as daemon thread
		self.rev_thread.daemon = True
		# Start the daemonized method execution
		self.rev_thread.start()   

		''' 
		Threading as daemon to process consensus protocol.
		The exec_consensus() method will be started and it will run in the background
		until the application exits.
		'''
		# the flag used to trigger consensus protocol execution.
		self.runConsensus = False
		# set pause threshold for check synchronization
		self.pause_epoch = pause_epoch
		# set delay time between operations in consensus protocol.
		self.phase_delay = phase_delay
		# define a thread to handle received messages by executing process_msg()
		self.consensus_thread = threading.Thread(target=self.exec_consensus, args=())
		# Set as daemon thread
		self.consensus_thread.daemon = True
		# Start the daemonized method execution
		self.consensus_thread.start()   
	
	def process_msg(self):
		'''
		daemon thread function: handle message and save into local database
		'''
		# this variable is used as waiting time when there is no message for process.
		idle_time=0.0
		while(True):
			# ========= idle time incremental strategy, the maximum is 1 seconds ========
			if( len(self.msg_buf)==0 ):
				idle_time+=0.1
				if(idle_time>1.0):
					idle_time=1.0
				time.sleep(idle_time)
				continue
			
			# reset idle time as 0
			idle_time = 0.0

			# ============= Choose a message from buffer and process it ==================
			msg_data = self.msg_buf[0]
			if(msg_data[0]==1):
				self.add_block(msg_data[1], msg_data[2])
			
			if(msg_data[0]==2):
				VoteCheckPoint.add_voter_data(msg_data[1], msg_data[2])
			
			self.msg_buf.remove(msg_data)

	def exec_consensus(self):
		'''
		daemon thread function: execute consensus protocol
		'''
		# used as waiting time as pending consensus protocol execution.
		idle_time=0.0
		# Used to synchronization after certain epoch height.
		pause_epoch=0
		while(True):
			# ========= idle time incremental strategy, the maximum is 1 seconds ========
			if(not self.runConsensus):
				idle_time+=0.1
				if(idle_time>1.0):
					idle_time=1.0
				time.sleep(idle_time)
				pause_epoch=0
				continue

			# reset idle time as 0
			idle_time = 0.0

			# ========================== Run consensus protocol ==========================
			json_head=self.processed_head
			logger.info("Consensus run at height: {}    status: {}".format(json_head['height'], 
																		self.runConsensus))
			# ------------S1: execute proof-of-work to mine new block--------------------
			start_time=time.time()
			new_block=self.mine_block()
			exec_time=time.time()-start_time
			FileUtil.save_testlog('test_results', 'exec_mining.log', format(exec_time*1000, '.3f'))
			
			# broadcast proposed block to peer nodes
			if( (self.consensus==ConsensusType.PoW) or 
				(not Block.isEmptyBlock(new_block)) ):
				SrvAPI.broadcast_POST(self.peer_nodes.get_nodelist(), new_block, '/test/block/verify')
			time.sleep(self.phase_delay*2)

			# ------------S2: fix head of current block generation epoch ----------------
			self.fix_processed_head()
			time.sleep(self.phase_delay)

			# ------------S3: voting block to finalize chain ----------------------------
			json_head= self.processed_head

			# only vote if current height arrive multiple of EPOCH_SIZE
			if( (json_head['height'] % self.block_epoch) == 0):
				vote_data = self.vote_checkpoint(json_head)	
				SrvAPI.broadcast_POST(self.peer_nodes.get_nodelist(), vote_data, '/test/vote/verify')
				pause_epoch+=1
				time.sleep(self.phase_delay*4)
		
			# if pause_epoch arrives threshold. stop consensus for synchronization
			if(pause_epoch==self.pause_epoch):
				self.runConsensus=False
				logger.info("Consensus run status: {}".format(self.runConsensus))


	def print_config(self):
		'''
		Show validator configuration and information
		'''		
		accounts = self.wallet.list_address()
		logger.info("Current accounts: {}".format(len(accounts)))
		if accounts:
			i=0
			for account in accounts:
			    logger.info("[{}]: {}".format(i, account) )
			    i+=1

		nodes = self.peer_nodes.get_nodelist()
		logger.info("Peer nodes: {}".format(len(nodes)))
		for node in nodes:
			json_node = TypesUtil.string_to_json(node)
			logger.info('    {}    {}'.format(json_node['address'], json_node['node_url']) )

		# Instantiate the Blockchain
		logger.info("Chain information:")
		logger.info("    uuid:                         {}".format(self.node_id))
		logger.info("    main chain blocks:            {}".format(self.processed_head['height']+1))
		logger.info("    consensus:                    {}".format( self.consensus.name) )
		logger.info("    block proposal epoch:         {}".format( self.block_epoch) )
		logger.info("    pause epoch size:             {}".format( self.pause_epoch) )
		logger.info("    current head:                 {}    height: {}".format(self.current_head['hash'],
																				self.current_head['height']))
		logger.info("    processed head:               {}    height: {}".format(self.processed_head['hash'],
																				self.processed_head['height']))
		logger.info("    highest justified checkpoint: {}    height: {}".format(self.highest_justified_checkpoint['hash'],
																				self.highest_justified_checkpoint['height']) )
		logger.info("    highest finalized checkpoint: {}    height: {}".format(self.highest_finalized_checkpoint['hash'],
																				self.highest_finalized_checkpoint['height']) )


	def add_block(self, json_block, status=0):
		'''
		Database operation: add verified block to local chain data
		'''
		# if block not existed, add block to database
		if( self.chain_db.select_block(CHAIN_TABLE, json_block['hash'])==[] ):
			self.chain_db.insert_block(CHAIN_TABLE,	json_block['hash'], 
								TypesUtil.json_to_string(json_block), status)

	def update_blockStatus(self, block_hash, status):
		'''
		Database operation: update block status
		'''
		self.chain_db.update_status(CHAIN_TABLE, block_hash, status)

	def get_block(self, block_hash):
		'''
		Database operation: select a block as json given block_hash
		'''
		str_block = self.chain_db.select_block(CHAIN_TABLE, block_hash)[0][2]
		return TypesUtil.string_to_json(str_block)

	def get_node(self, node_address):
		'''
		Buffer operation: select a node from peer_nodes buffer given node address
		'''
		ls_nodes=list(self.peer_nodes.get_nodelist())

		# refresh sum_stake and committee_size as peer nodes change
		# set sum_stake is peer nodes count
		self.sum_stake = len(ls_nodes)
		# set committee size as peer nodes count 
		self.committee_size = len(ls_nodes)

		json_node = None
		for node in ls_nodes:
			json_node = TypesUtil.string_to_json(node)
			if(json_node['address']==node_address):
				break				
		return json_node


	def load_chain(self):
		'''
		Database operation: Load chain data from local database
		'''
		ls_chain=self.chain_db.select_block(CHAIN_TABLE)
		self.chain = []
		for block in ls_chain:
			json_data = TypesUtil.string_to_json(block[2])
			if( json_data['hash'] not in self.chain):
				json_data['status']=block[3]
				self.chain.append(json_data)

	def save_chainInfo(self):
		"""
		Config file operation: save the validator information to static json file
		"""
		chain_info = {}
		chain_info['node_id'] = self.node_id
		chain_info['processed_head'] = self.processed_head
		chain_info['highest_justified_checkpoint'] = self.highest_justified_checkpoint
		chain_info['highest_finalized_checkpoint'] = self.highest_finalized_checkpoint
		chain_info['block_dependencies'] = self.block_dependencies
		chain_info['vote_dependencies'] = self.vote_dependencies
		#chain_info['votes'] = self.votes
		chain_info['vote_count'] = self.vote_count

		if(not os.path.exists(CHAIN_DATA_DIR)):
		    os.makedirs(CHAIN_DATA_DIR)
		FileUtil.JSON_save(CHAIN_DATA_DIR+'/'+CHAIN_INFO, chain_info)

	def load_chainInfo(self):
		"""
		Config file operation: load validator information from static json file
		"""
		if(os.path.isfile(CHAIN_DATA_DIR+'/'+CHAIN_INFO)):
		    return FileUtil.JSON_load(CHAIN_DATA_DIR+'/'+CHAIN_INFO)
		else:
			return None

	def get_info(self):
		'''
		Get validator information for reference and synchronization
		'''
		validator_info = {}
		validator_info['node_id'] = self.node_id
		validator_info['committee_size'] = self.committee_size
		validator_info['processed_head'] = self.processed_head
		validator_info['highest_justified_checkpoint'] = self.highest_justified_checkpoint
		validator_info['highest_finalized_checkpoint'] = self.highest_finalized_checkpoint		
		validator_info['vote_count'] = self.vote_count

		return validator_info


	def valid_transaction(self, transaction, sender_pk, signature):
		"""
		Verify a received transaction and append to local transactions pool
		Args:
			@ transaction: transacton directionary data
			@ sender_pk: sender's public key
			@ signature: digital signature signed by sender
			@ return: True or False
		"""
		verified_transaction = transaction
		verify_result = Transaction.verify(sender_pk, signature, transaction)
		if(verify_result):
			verified_transaction['signature'] = TypesUtil.string_to_hex(signature)
			# discard duplicated tx
			if(verified_transaction not in self.transactions):
				self.transactions.append(verified_transaction)
			return True
		else:
			return False
 
	def mine_block(self):
		"""
		Mining task to calculate a valid proof and propose new block
		Args:
			@ json_block: return mined block
		"""
		# remove committed transactions in head block
		head_block = self.current_head
		for transaction in head_block['transactions']:
			if(transaction in self.transactions):
				self.transactions.remove(transaction)

		# commit transactions based on COMMIT_TRANS
		commit_transactions = []
		if( len(self.transactions)<=COMMIT_TRANS ):
			commit_transactions = copy.copy(self.transactions)

		else:
			commit_transactions = copy.copy(self.transactions[:COMMIT_TRANS])

		# set head as last block and used for new block proposal process
		last_block = self.processed_head

		block_data = {'height': last_block['height'],
					'previous_hash': last_block['previous_hash'],
					'transactions': last_block['transactions'],
					'nonce': last_block['nonce']}

		parent_block = Block.json_to_block(last_block)

		# execute mining task given consensus algorithm
		if(self.consensus==ConsensusType.PoW):
			# mining new nonce
			nonce = POW.proof_of_work(block_data, commit_transactions)
			new_block = Block(parent_block, commit_transactions, nonce)
		elif(self.consensus==ConsensusType.PoS):
			# propose new block given stake weight
			if( POS.proof_of_stake(block_data, commit_transactions, self.node_id, 
									TEST_STAKE_WEIGHT, self.sum_stake )!=0 ):
				new_block = Block(parent_block, commit_transactions, self.node_id)	
			else:
				# generate empty block without transactions
				new_block = Block(parent_block)	
		else:
			# generate empty block without transactions
			new_block = Block(parent_block)				

		json_block = new_block.to_json()

		# add sender address and signature
		if(self.wallet.accounts!=0):
			sender = self.wallet.accounts[0]
			sign_data = new_block.sign(sender['private_key'], 'samuelxu999')
			json_block['sender_address'] = sender['address']
			json_block['signature'] = TypesUtil.string_to_hex(sign_data)
		else:
			json_block['sender_address'] = 'Null'
			json_block['signature'] = 'Null'

		return json_block

	def valid_block(self, new_block):
		"""
		Check if a new block from other miner can show valid proof of work
		Args:
			@ new_block: vote json data
			@ return: True or False
		"""
		current_block = new_block

		# get node data from self.peer_nodes buffer
		sender_node = self.get_node(current_block['sender_address'])

		# ======================1: verify block signature ==========================
		if(sender_node==None):
			# unknown sender, drop block
			logger.info("Invalid sender: {}".format(current_block['sender_address']))
			return False

		# rebuild block object given json data
		obj_block = Block.json_to_block(current_block)
		# if check signature failed, drop block
		if( not obj_block.verify(sender_node['public_key'], 
							TypesUtil.hex_to_string(current_block['signature']) ) ):
			logger.info("Invalid signature from sender: {}".format(current_block['sender_address']))
			return

		#=========2: Check that the Proof of Work is correct given current block data =========
		# reject block with empty transactions
		if(current_block['transactions']==[]):
			logger.info("Invalid block with empty txs from sender: {}".format(current_block['sender_address']))
			return False

		dict_transactions = Transaction.json_to_dict(current_block['transactions'])

		# execute valid proof task given consensus algorithm
		if(self.consensus==ConsensusType.PoW):
			if( not POW.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce']) ):
				logger.info("PoW valid proof fail. Block: {}".format(current_block['hash']))
				return False
		elif(self.consensus==ConsensusType.PoS):
			if( not POS.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce'], 
									TEST_STAKE_WEIGHT, self.sum_stake) ):
				logger.info("PoS valid proof fail. Block: {}".format(current_block['hash']))
				return False
		else:
			return False

		return True

	def valid_vote(self, json_vote):
		'''
		Check if a vote from other validator is valid or not
		Args:
			@ json_vote: vote json data
			@ verify_result: True or False
		'''
		# ------------------- verify vote before accept it ------------------
		verify_result = False

		if(json_vote==None or json_vote=='{}'):
			return verify_result

		#rebuild vote object given json data
		new_vote = VoteCheckPoint.json_to_vote(json_vote)

		sign_data = TypesUtil.hex_to_string(json_vote['signature'])

		# get node data from self.peer_nodes buffer
		sender_node=self.get_node(new_vote.sender_address)

		# ====================== verify vote ==========================
		if(sender_node!=None):
			sender_pk = sender_node['public_key']
			verify_result = VoteCheckPoint.verify(sender_pk, sign_data, new_vote.to_dict())

		return verify_result

	def valid_transactions(self, transactions):
		'''
		check if all transactions that are committed in a new block are valid
		Args:
			@ transactions: transactions json list
			@ verify_result: True or False
		'''
		verify_result = True
		for transaction_data in transactions:
			#print(transaction_data)
			# ====================== rebuild transaction ==========================
			dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
			                                    transaction_data['recipient_address'],
			                                    transaction_data['time_stamp'],
			                                    transaction_data['value'])

			sign_str = TypesUtil.hex_to_string(transaction_data['signature'])

			# get node data from self.peer_nodes buffer
			sender_node=self.get_node(transaction_data['sender_address'])

			# ====================== verify transaction ==========================
			if(sender_node!={}):
			    sender_pk= sender_node['public_key']
			    verify_result = Transaction.verify(sender_pk, sign_str, dict_transaction)
			else:
				verify_result = False
			if(not verify_result):
				break
		return verify_result

	def get_parent(self, json_block):
		'''	
		Get the parent block of a given block (json)
		Args:
			@ json_block: block json data
			@ return: parent block json
		'''
		# root block, return None
		if(json_block['height'] == 0):
			return None
		ls_block = self.chain_db.select_block(CHAIN_TABLE, json_block['previous_hash'])
		
		if(ls_block==[]):
			return None
		else:
			return TypesUtil.string_to_json(ls_block[0][2])

	def is_ancestor(self, anc_block, desc_block):
		"""Is a given block an ancestor of another given block?
		Args:
		    anc_hash: ancestor block hash
		    desc_hash: descendant block hash
		"""	
		if(anc_block == None):
			return False

		# search parent
		while( True ):
			if desc_block is None:
			    return False
			if desc_block['hash'] == anc_block['hash']:
			    return True
			desc_block = self.get_parent(desc_block)

	def on_receive(self, json_msg, op_type=0):
		'''
		Call on receiving message: transactions, block and vote
		Args:
			@ json_msg: json message
			@ op_type: operation type given different message
		'''
		# ----------- 0: transaction message processing -----------
		if(op_type ==0):
			ret = self.accept_transaction(json_msg)
		# ----------- 1: block message processing -----------------
		elif(op_type ==1):
			ret = self.accept_block(json_msg)
		# ----------- 2: vote message processing ------------------
		else:
			ret = self.accept_vote(json_msg)

		# If the object was successfully processed, clear dependencies
		if(ret and op_type !=0):
			if(op_type ==1):
				if(json_msg['hash'] in self.block_dependencies):
					for dependency in self.block_dependencies[json_msg['hash']]:
						self.on_receive(dependency, 1)	
					self.remove_dependency(json_msg['hash'], 0)		
				if(json_msg['hash'] in self.vote_dependencies):
					for dependency in self.vote_dependencies[json_msg['hash']]:
						self.on_receive(dependency, 2)	
					self.remove_dependency(json_msg['hash'], 1)	
			else:
				if(json_msg['hash'] in self.vote_dependencies):
					for dependency in self.vote_dependencies[json_msg['hash']]:
						self.on_receive(dependency, 2)	
					self.remove_dependency(json_msg['hash'], 1)
		
		# save chain info to local
		self.save_chainInfo()
		return ret

	def accept_transaction(self, json_tran):
		'''
		Called on processing a transaction message.
		Args:
			@ json_tran: transaction json message
			@ verify_result: return True or False
		'''
		verify_result = False

		# ====================== rebuild transaction ==========================
		dict_transaction = Transaction.get_dict(json_tran['sender_address'], 
												json_tran['recipient_address'],
												json_tran['time_stamp'],
												json_tran['value'])

		sign_data = TypesUtil.hex_to_string(json_tran['signature'])
		#print(dict_transaction)
		#print(sign_data)

		# get node data from self.peer_nodes buffer
		sender_node=self.get_node(json_tran['sender_address'])

		# ====================== verify transaction ==========================
		if(sender_node!={}):
			sender_pk= sender_node['public_key']
			#verify_data = Transaction.verify(sender_pk, sign_data, dict_transaction)
			verify_result = self.valid_transaction(dict_transaction, sender_pk, sign_data)
		else:
			verify_result = False	
		return verify_result

	def accept_block(self, json_block):
		'''
		Called on processing a block message.
		Args:
			@json_block: received block (json)
			@return: True or False
		'''
		# ------------------- verify block before accept it ------------------
		verify_result = False
		if(self.valid_block(json_block)):
			verify_result = self.valid_transactions(json_block['transactions'])

		if(not verify_result):
			return False
		
		# ---------------- accept block given processed status ----------------
		# If the block's parent has not received, add to dependency list
		if(self.get_parent(json_block) == None):
			self.add_dependency(json_block['previous_hash'], json_block)
			return False

		
		# append verified block to local chain, status = 0, processed
		# ------------  add block to buffer --------------
		# self.add_block(json_block, 0)
		self.msg_buf.append([1, json_block, 0])
		self.check_processed_head(json_block)

		return True

	def vote_checkpoint(self, json_block):
		"""
		Called after receiving a block.
		Args:			
			@json_block: last processed block			
			@json_vote: return a vote json message
		"""
		logger.info('Vote for block: {}    height: {}'.format(json_block['hash'], json_block['height']))
		# if( (json_block['height'] % EPOCH_SIZE) != 0):
		if( (json_block['height'] % self.block_epoch) != 0):
			return None

		# get target block object as voting block
		target_block = json_block
		target_obj = Block.json_to_block(target_block)
		# get source block object as justified checkpoint with greatest height
		source_block = self.highest_justified_checkpoint
		source_obj = Block.json_to_block(source_block)

		# If the block is an epoch block of a higher epoch than what we've seen so far
		# This means that it's the first time we see a checkpoint at this height
		# It also means we never voted for any other checkpoint at this height (rule 1)
		if(target_obj.get_epoch(self.block_epoch) <= source_obj.get_epoch(self.block_epoch)):
			#return None
			source_block = self.highest_finalized_checkpoint
			source_obj = Block.json_to_block(source_block)

		# if the target_block is a descendent of the source_block, build a vote
		json_vote={}
		if(self.is_ancestor(source_block, target_block)):
			# get sender information
			sender_node = self.wallet.accounts[0]

			new_vote = VoteCheckPoint(source_block['hash'], target_block['hash'], 
			                        source_obj.get_epoch(self.block_epoch), target_obj.get_epoch(self.block_epoch), sender_node['address'])
			json_vote = new_vote.to_json()

			# sign vote
			sign_data = new_vote.sign(sender_node['private_key'], 'samuelxu999')
			json_vote['signature'] = TypesUtil.string_to_hex(sign_data)

		return json_vote
		
	def accept_vote(self, json_vote):
		'''
		Called on processing a vote message.
		Args:			
			@json_vote: a vote json message			
			@return: True or False
		'''
		# ============================ Check the vote conditions =================================

		# ---------------------------- verify vote before accept it ---------------------------
		verify_result = self.valid_vote(json_vote)
		if(not verify_result):
			logger.info("V:    invalid vote: {}    sender: {}".format(json_vote['hash'], json_vote['sender_address']))
			return False

		#-------------------------- check if source block is valid-----------------------------
		ls_block = self.chain_db.select_block(CHAIN_TABLE, json_vote['source_hash'])
		# If the block has not yet been processed, add to vote_dependencies
		if(ls_block==[]):
			self.add_dependency(json_vote['source_hash'], json_vote, 1)
			logger.info("S1:    not processed block: {}, add to vote_dependencies".format(json_vote['source_hash']))
			return False
		
		source_block = ls_block[0]
		# If the source block is not justified, discard vote
		if(source_block[3]==0):
			logger.info("S2:    not justified block: {}, discard vote".format(source_block[0]))
			return False

		#-------------------------- check if target block is valid-----------------------------
		ls_block = self.chain_db.select_block(CHAIN_TABLE, json_vote['target_hash'])
		# If the block has not yet been processed, add to vote_dependencies
		if(ls_block==[]):
			self.add_dependency(json_vote['target_hash'], json_vote, 1)
			logger.info("T1:    not processed block: {}, add to vote_dependencies".format(json_vote['target_hash']))
			return False
		
		target_block = ls_block[0]

		# -------- Initialize a voter_db for self.votes[vote.sender] if necessary -------------------
		# VoteCheckPoint.new_voter() will create a voter_db and return it.
		if(json_vote['sender_address'] not in self.votes):
			#self.votes[json_vote['sender_address']] = []
			logger.info("Create a voter_db handle for sender: {}".format(json_vote['sender_address']))
			self.votes[json_vote['sender_address']] = VoteCheckPoint.new_voter(json_vote)

		# ============================ Check the slashing conditions =================================
		# voter_db = self.votes[json_vote['sender_address']]
		# then get vote_data by execute voter_db.select_block(voter_name, block_hash)
		vote_data = VoteCheckPoint.get_voter_data(self.votes[json_vote['sender_address']], json_vote)
		# for each past_vote in vote_data to check
		for past_vote in vote_data:
			if past_vote['epoch_target'] == json_vote['epoch_target']:
				# TODO: SLASH
				logger.info("You just got slashed: R1   sender: {}    vote: {}".format(json_vote['sender_address'], 
																					json_vote['hash']))
				return False

			if ((past_vote['epoch_source'] < json_vote['epoch_source'] and
				past_vote['epoch_target'] > json_vote['epoch_target']) or
				(past_vote['epoch_source'] > json_vote['epoch_source'] and
				past_vote['epoch_target'] < json_vote['epoch_target'])):
				# TODO: SLASH
				logger.info("You just got slashed: R2   sender: {}    vote: {}".format(json_vote['sender_address'], 
																					json_vote['hash']))
				return False

		# Add the vote to the map of votes['sender']
		#self.votes[json_vote['sender_address']].append(json_vote)
		# ----------------------------- add vote data to buffer -------------------------------
		# VoteCheckPoint.add_voter_data(self.votes[json_vote['sender_address']], json_vote)
		self.msg_buf.append([2, self.votes[json_vote['sender_address']], json_vote])

		# Calculate votes count
		if json_vote['source_hash'] not in self.vote_count:
			self.vote_count[json_vote['source_hash']] = {}
		self.vote_count[json_vote['source_hash']][json_vote['target_hash']] = \
		self.vote_count[json_vote['source_hash']].get(json_vote['target_hash'], 0) + 1

		# If there are enough votes, set block as justified
		# if (self.vote_count[json_vote['source_hash']][json_vote['target_hash']] > (NUM_VALIDATORS * 2) // 3):
		if (self.vote_count[json_vote['source_hash']][json_vote['target_hash']] > (self.committee_size * 2) // 3):
			target_status = target_block[3]
			# 1) if target was processed, set justified block
			if( target_status==0 ):
				# Mark the target block as 1-justified
				logger.info("Justified target block: {}".format(json_vote['target_hash']))
				self.update_blockStatus(json_vote['target_hash'], 1)
				target_status = 1
			# 2) update highest_justified_checkpoint as target
			if( json_vote['epoch_target'] > Block.json_to_block(self.highest_justified_checkpoint).get_epoch(self.block_epoch) ):
				logger.info("Update highest_justified_checkpoint: {}".format(json_vote['target_hash']))
				self.highest_justified_checkpoint = self.get_block(json_vote['target_hash'])

			# If the source was a direct parent of the target, the source is finalized block
			source_status = source_block[3]
			if( json_vote['epoch_source'] == (json_vote['epoch_target'] - 1) and target_status==1 and source_status!=2):
				# Mark the source block as 2-finalized
				logger.info("Finalized source block: {}".format(json_vote['source_hash']))
				self.highest_finalized_checkpoint = self.get_block(json_vote['source_hash'])
				self.update_blockStatus(json_vote['source_hash'], 2)

		return True

	def check_processed_head(self, new_block):
		'''
		Reorganize the processed_head to stay on the chain with the highest justified checkpoint.

		If we are on wrong chain, reset the head to be the highest descendent
		among the chains containing the highest justified checkpoint.

		Args:
		    new_block: latest block processed.
		'''
		head_block = self.current_head 
		# we are on the right chain, the head is simply the latest block
		if self.is_ancestor(self.highest_justified_checkpoint, head_block):
			if(self.consensus==ConsensusType.PoS):
				# get proof value used for choose current_head
				new_proof=POS.get_proof(Transaction.json_to_dict(new_block['transactions']), 
								new_block['previous_hash'], new_block['nonce'],self.sum_stake)
				head_proof=POS.get_proof(Transaction.json_to_dict(head_block['transactions']), 
								head_block['previous_hash'], head_block['nonce'],self.sum_stake)
				# head is genesis block or new_block have smaller proof value than current head
				logger.info( "new block sender:  {}".format(new_block['sender_address']))
				logger.info( "head proof:        {} -- new proof:        {}".format(head_proof, new_proof) )
				logger.info( "head block height: {} -- new block height: {}".format(head_block['height'], new_block['height']) )
				
				# 1) new block is 1 larger height, then update current_head to new block 
				if( head_block['height'] == (new_block['height']-1) ):
					self.current_head = new_block
					logger.info("Update current_head: {}    height: {}".format(self.current_head['hash'], 
																				self.current_head['height']) )
					return

				# 2) new block has same height as current head
				if( head_block['height']==new_block['height'] ):
					# A) who holds smaller proof wins
					if(new_proof<head_proof):
						self.current_head = new_block
						logger.info("Update current_head: {}    height: {}".format(self.current_head['hash'], 
																					self.current_head['height']) )
						return

					# B) If they have same proof wins, who has larger nounce (credit) wins
					if( new_proof==head_proof and new_block['nonce']>head_block['nonce'] ):
						self.current_head = new_block
						logger.info("Update current_head: {}    height: {}".format(self.current_head['hash'], 
																					self.current_head['height']) )
			else:
				self.processed_head = new_block
				logger.info("Fix processed_head: {}    height: {}".format(self.processed_head['hash'],
																			self.processed_head['height']) )
			#self.main_chain_size += 1

	def fix_processed_head(self):
		'''
		Reset processed_head as each block proposal epoch finished:
		1) For no proposed block, generate empty block as current header
		2) otherwise, directly fixed processed_head
		3) remove committed transactions from local txs pool 
		4) update chaininfo and save into local file
		'''
		if(self.consensus==ConsensusType.PoS):
			# 1) if none of validator propose block, use empty block as header
			if(self.processed_head == self.current_head):
				#generate empty block
				last_block = self.processed_head
				parent_block = Block.json_to_block(last_block)
				json_block = Block(parent_block).to_json()
				json_block['sender_address'] = 'Null'
				json_block['signature'] = 'Null'
				# ------------  add block to buffer --------------
				# self.add_block(json_block, 0)
				self.msg_buf.append([1, json_block, 0])

				self.current_head = json_block
				logger.info("Set current_head as emptyblock: {}".format(self.current_head))
			
			# 2) set processed_head as current_head
			self.processed_head = self.current_head

			# 3) remove committed transactions in head block
			for transaction in self.processed_head['transactions']:
				if(transaction in self.transactions):
					self.transactions.remove(transaction)
			logger.info("Fix processed_head: {}    height: {}".format(self.processed_head['hash'],
																		self.processed_head['height']) )
			# 4) update chaininfo and save into local file
			self.save_chainInfo()	

	def add_dependency(self, hash_value, json_data, op_type=0):
		'''
		If we processed an object but did not receive some dependencies
		needed to process it, save it to be processed later
		Args:
			@ hash_value: hash value
			@ json_data: json data
			@ op_type: operation type given different message
		'''
		if(op_type ==0):
			if(hash_value not in self.block_dependencies):
				self.block_dependencies[hash_value] = []
			self.block_dependencies[hash_value].append(json_data)
		else:
			if(hash_value not in self.vote_dependencies):
				self.vote_dependencies[hash_value] = []
			self.vote_dependencies[hash_value].append(json_data)
	
	def remove_dependency(self, hash_value, op_type=0):
		'''
		If we processed an object, then remove it from dependencies
		Args:
			@ hash_value: hash value
			@ json_data: json data
			@ op_type: operation type given different message
		'''
		if(op_type ==0):
			if(hash_value in self.block_dependencies):
				del self.block_dependencies[hash_value]
		else:
			if(hash_value in self.vote_dependencies):
				del self.vote_dependencies[hash_value]

