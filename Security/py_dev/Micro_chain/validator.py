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

import hashlib
import json
from time import time
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


class Validator(object):
	'''A Validator contains the following arguments:
	self.node_id: GUID 
	self.consensus: consensus algorithm
	self.chain_db: local chain database adapter
	self.consensus: consensus algorithm
	self.wallet: wallet account management
	self.peer_nodes: peer nodes management 

	self.transactions: local transaction pool
	self.chain: local chain data buffer
	self.block_dependencies: used to save blocks need for dependency
	self.vote_dependencies: used to save pending vote need for dependency
	self.processed_head: the latest processed descendant of the highest justified checkpoint
	self.current_head: the current received descendant of the highest justified checkpoint
	self.highest_justified_checkpoint: the block with higest justified checkpoint
	self.highest_finalized_checkpoint: the block with higest finalized checkpoint
	self.votes: Map {sender -> vote_db object} which contains all the votes data for check
	self.vote_count: Map {source_hash -> {target_hash -> count}} to count the votes
	'''

	def __init__(self, consensus=ConsensusType.PoW):

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
	
	def print_config(self):
		#list account address
		accounts = self.wallet.list_address()
		print('Current accounts:')
		if accounts:
			i=0
			for account in accounts:
			    print(i, '  ', account)
			    i+=1

		print('Peer nodes:')
		nodes = self.peer_nodes.get_nodelist()
		for node in nodes:
			json_node = TypesUtil.string_to_json(node)
			print('    ', json_node['address'] + '    ' + json_node['node_url'])

		# Instantiate the Blockchain
		print('Chain information:')
		print('    uuid:         ', self.node_id)
		print('    main chain size: ', self.processed_head['height']+1)
		print('    processed head: ', self.processed_head['hash'])
		print('    highest justified checkpoint: ', self.highest_justified_checkpoint['hash'])
		print('    highest finalized checkpoint: ', self.highest_finalized_checkpoint['hash'])
		print('    consensus: 	 ', self.consensus.name)


	def add_block(self, json_block, status=0):
		'''
		add verified block to local chain data
		'''
		# if block not existed, add block to database
		if( self.chain_db.select_block(CHAIN_TABLE, json_block['hash'])==[] ):
			self.chain_db.insert_block(CHAIN_TABLE,	json_block['hash'], 
								TypesUtil.json_to_string(json_block), status)

	def update_blockStatus(self, block_hash, status):
		'''
		update block status
		'''
		self.chain_db.update_status(CHAIN_TABLE, block_hash, status)

	def get_block(self, block_hash):
		'''
		select a block as json given block_hash
		'''
		str_block = self.chain_db.select_block(CHAIN_TABLE, block_hash)[0][2]
		return TypesUtil.string_to_json(str_block)

	def get_node(self, node_address):
		'''
		select a node from peer_nodes buffer given node address
		'''
		ls_nodes=list(self.peer_nodes.get_nodelist())
		json_node = None
		for node in ls_nodes:
			json_node = TypesUtil.string_to_json(node)
			if(json_node['address']==node_address):
				break				
		return json_node


	def load_chain(self):
		'''
		load chain data from local database
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
			Save the validator information to static json file
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
			load validator information from static json file
			"""
			if(os.path.isfile(CHAIN_DATA_DIR+'/'+CHAIN_INFO)):
			    return FileUtil.JSON_load(CHAIN_DATA_DIR+'/'+CHAIN_INFO)
			else:
				return None

	def valid_transaction(self, transaction, sender_pk, signature):
		"""
		Verify a received transaction and append to local transactions pool
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
		Mining task to propose new block
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
									TEST_STAKE_WEIGHT, TEST_STAKE_SUM )!=0 ):
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
		check if a new block from other miners is valid of proof work
		"""
		current_block = new_block

		# get node data from self.peer_nodes buffer
		sender_node = self.get_node(current_block['sender_address'])

		# ======================1: verify block signature ==========================
		if(sender_node==None):
			# unknown sender, drop block
			print('v_sender')
			return False

		# rebuild block object given json data
		obj_block = Block.json_to_block(current_block)
		# if check signature failed, drop block
		if( not obj_block.verify(sender_node['public_key'], 
							TypesUtil.hex_to_string(current_block['signature']) ) ):
			print('v_sign')
			return

		#=========2: Check that the Proof of Work is correct given current block data =========
		dict_transactions = Transaction.json_to_dict(current_block['transactions'])

		# execute valid proof task given consensus algorithm
		if(self.consensus==ConsensusType.PoW):
			if( not POW.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce']) ):
				print('v_pow')
				return False
		elif(self.consensus==ConsensusType.PoS):
			if( not POS.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce'], 
									TEST_STAKE_WEIGHT, TEST_STAKE_SUM) ):
				print('v_pos')
				return False
		else:
			return False

		return True

	def valid_vote(self, json_vote):
		'''
		check if a vote from other voters is valid
		'''
		# ------------------- verify vote before accept it ------------------
		verify_result = False

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
		check if transactions in a new block are valid
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
		# transaction message processing
		if(op_type ==0):
			ret = self.accept_transaction(json_msg)
		# block message processing
		elif(op_type ==1):
			ret = self.accept_block(json_msg)
		#vote message processing
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
			Input:
				@json_block: received block (json)
			Output:
				@[Ret, json_vote]: return operation result and a vote json message
		'''
		# ------------------- verify block before accept it ------------------
		verify_result = False
		if(self.valid_block(json_block)):
			verify_result = self.valid_transactions(json_block['transactions'])

		if(not verify_result):
			return [False, None]
		
		# ---------------- accept block given processed status ----------------
		# If the block's parent has not received, add to dependency list
		if(self.get_parent(json_block) == None):
			self.add_dependency(json_block['previous_hash'], json_block)
			return [False, None]

		
		# append verified block to local chain, status = 0, processed
		self.add_block(json_block, 0)
		self.check_processed_head(json_block)
		#self.save_chainInfo()

		return True

	def vote_checkpoint(self, json_block):
		"""
		Called after receiving a block.
		Args:
			Input:
				@json_block: last processed block
			Output:
				@json_vote: return a vote json message
		"""
		print('vote for ', json_block['hash'])
		if( (json_block['height'] % EPOCH_SIZE) != 0):
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
		if(target_obj.epoch <= source_obj.epoch):
			#return None
			source_block = self.highest_finalized_checkpoint
			source_obj = Block.json_to_block(source_block)

		# if the target_block is a descendent of the source_block, build a vote
		if(self.is_ancestor(source_block, target_block)):
			# get sender information
			sender_node = self.wallet.accounts[0]

			new_vote = VoteCheckPoint(source_block['hash'], target_block['hash'], 
			                        source_obj.epoch, target_obj.epoch, sender_node['address'])
			json_vote = new_vote.to_json()

			# sign vote
			sign_data = new_vote.sign(sender_node['private_key'], 'samuelxu999')
			json_vote['signature'] = TypesUtil.string_to_hex(sign_data)

			return json_vote
		
	def accept_vote(self, json_vote):
		'''
		Called on processing a vote message.
		'''
		# ------------------- verify vote before accept it ------------------
		verify_result = self.valid_vote(json_vote)
		if(not verify_result):
			print('v')
			return False

		#--------------------- check if source block is valid---------
		ls_block = self.chain_db.select_block(CHAIN_TABLE, json_vote['source_hash'])
		# If the block has not yet been processed, add to vote_dependencies
		if(ls_block==[]):
			self.add_dependency(json_vote['source_hash'], json_vote, 1)
			print('s1')
			return False
		
		source_block = ls_block[0]
		# If the source block is not justified, discard vote
		if(source_block[3]==0):
			print('s2')
			return False

		#--------------------- check if target block is valid---------
		ls_block = self.chain_db.select_block(CHAIN_TABLE, json_vote['target_hash'])
		# If the block has not yet been processed, add to vote_dependencies
		if(ls_block==[]):
			self.add_dependency(json_vote['target_hash'], json_vote, 1)
			print('t1')
			return False
		
		target_block = ls_block[0]

		# Initialize self.votes[vote.sender] if necessary
		if(json_vote['sender_address'] not in self.votes):
			#self.votes[json_vote['sender_address']] = []
			self.votes[json_vote['sender_address']] = VoteCheckPoint.new_voter(json_vote)

		# Check the slashing conditions
		vote_data = VoteCheckPoint.get_voter_data(self.votes[json_vote['sender_address']], json_vote)
		#for past_vote in self.votes[json_vote['sender_address']]:
		for past_vote in vote_data:
			if past_vote['epoch_target'] == json_vote['epoch_target']:
				# TODO: SLASH
				print('You just got slashed. R1')
				return False

			if ((past_vote['epoch_source'] < json_vote['epoch_source'] and
				past_vote['epoch_target'] > json_vote['epoch_target']) or
				(past_vote['epoch_source'] > json_vote['epoch_source'] and
				past_vote['epoch_target'] < json_vote['epoch_target'])):
				print('You just got slashed. R2')
				return False

		# Add the vote to the map of votes['sender']
		#self.votes[json_vote['sender_address']].append(json_vote)
		VoteCheckPoint.add_voter_data(self.votes[json_vote['sender_address']], json_vote)

		# Add to the vote count
		if json_vote['source_hash'] not in self.vote_count:
			self.vote_count[json_vote['source_hash']] = {}
		self.vote_count[json_vote['source_hash']][json_vote['target_hash']] = \
		self.vote_count[json_vote['source_hash']].get(json_vote['target_hash'], 0) + 1

		# If there are enough votes, set block as justified
		if (self.vote_count[json_vote['source_hash']][json_vote['target_hash']] > (NUM_VALIDATORS * 2) // 3):
			target_status = target_block[3]
			# 1) if target was processed, set justified block
			if( target_status==0 ):
				# Mark the target block as 1-justified
				print('justified target:', json_vote['target_hash'])
				self.update_blockStatus(json_vote['target_hash'], 1)
				target_status = 1
			# 2) update highest_justified_checkpoint as target
			if( json_vote['epoch_target'] > Block.json_to_block(self.highest_justified_checkpoint).epoch ):
				print('update highest_justified_checkpoint:', json_vote['target_hash'])
				self.highest_justified_checkpoint = self.get_block(json_vote['target_hash'])

			# If the source was a direct parent of the target, the source is finalized block
			source_status = source_block[3]
			if( json_vote['epoch_source'] == (json_vote['epoch_target'] - 1) and target_status==1 and source_status!=2):
				# Mark the source block as 2-finalized
				print('finalized source:', json_vote['source_hash'])
				self.highest_finalized_checkpoint = self.get_block(json_vote['source_hash'])
				self.update_blockStatus(json_vote['source_hash'], 2)

		return True

	def check_processed_head(self, new_block):
		'''Reorganize the processed_head to stay on the chain with the highest
		justified checkpoint.

		If we are on wrong chain, reset the head to be the highest descendent
		among the chains containing the highest justified checkpoint.

		Args:
		    block: latest block processed.'''
		head_block = self.current_head 
		# we are on the right chain, the head is simply the latest block
		if self.is_ancestor(self.highest_justified_checkpoint, head_block):
			if(self.consensus==ConsensusType.PoS):
				# get proof value used for choose current_head
				new_proof=POS.get_proof(Transaction.json_to_dict(new_block['transactions']), 
								new_block['previous_hash'], new_block['nonce'],TEST_STAKE_SUM)
				head_proof=POS.get_proof(Transaction.json_to_dict(head_block['transactions']), 
								head_block['previous_hash'], head_block['nonce'],TEST_STAKE_SUM)
				# head is genesis block or new_block have smaller proof value than current head
				print(new_proof, "--", head_proof)
				print(head_block['height'], "--", new_block['height'])
				if(new_proof<head_proof or head_block['height']<new_block['height']):
					self.current_head = new_block
					print("Update current_head:", self.current_head['hash'])
			else:
				self.processed_head = new_block
				print("Fix processed_head:", self.processed_head['hash'])
			#self.main_chain_size += 1

	def fix_processed_head(self):
		# set processed_head when block proposal epoch finish 
		if(self.consensus==ConsensusType.PoS):
			self.processed_head = self.current_head
			print("Fix processed_head:", self.processed_head['hash'])

	def add_dependency(self, hash_value, json_data, op_type=0):
		'''
		If we processed an object but did not receive some dependencies
		needed to process it, save it to be processed later
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

