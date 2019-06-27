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
	self.highest_justified_checkpoint: the block with higest justified checkpoint
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
			#set processed_head and highest_justified_checkpoint as genesis_block
			self.processed_head = json_data
			self.highest_justified_checkpoint = json_data

			#self.chain.append(genesis_block.to_json())
			self.add_block(json_data)
		
		# new chain buffer
		self.chain = []

		# new transaction pool
		self.transactions = []

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
			# update chain info
			self.save_chainInfo()
		else:
			#Generate random number to be used as node_id
			self.node_id = chain_info['node_id']
			self.block_dependencies = chain_info['block_dependencies']
			self.vote_dependencies = chain_info['vote_dependencies']
			self.processed_head = chain_info['processed_head']
			self.highest_justified_checkpoint = chain_info['highest_justified_checkpoint']
	
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
		print('    consensus: 	 ', self.consensus.name)


	def add_block(self, json_block, status=0):
		'''
		add verified block to local chain data
		'''
		# if block not existed, add block to database
		if( self.chain_db.select_block(CHAIN_TABLE, json_block['hash'])==[] ):
			self.chain_db.insert_block(CHAIN_TABLE,	json_block['hash'], 
								TypesUtil.json_to_string(json_block), status)

	def load_chain(self):
		'''
		load chain data from local database
		'''
		ls_chain=self.chain_db.select_block(CHAIN_TABLE)
		self.chain = []
		for block in ls_chain:
			json_data = TypesUtil.string_to_json(block[2])
			if( json_data['hash'] not in self.chain):
				self.chain.append(json_data)

	def save_chainInfo(self):
			"""
			Save the validator information to static json file
			"""
			chain_info = {}
			chain_info['node_id'] = self.node_id
			chain_info['processed_head'] = self.processed_head
			chain_info['highest_justified_checkpoint'] = self.highest_justified_checkpoint
			chain_info['block_dependencies'] = self.block_dependencies
			chain_info['vote_dependencies'] = self.vote_dependencies

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

	def verify_transaction(self, transaction, sender_pk, signature):
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

		commit_transactions = []
		if( len(self.transactions)<=COMMIT_TRANS ):
			commit_transactions = copy.copy(self.transactions)

		else:
			commit_transactions = copy.copy(self.transactions[:COMMIT_TRANS])


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

		return new_block.to_json()

	def valid_block(self, new_block):
		"""
		check if a new block from other miners is valid
		"""
		#last_block = self.chain[-1]
		current_block = new_block
		#print(previous_block)
		#print(current_block)

		'''block_data = {'height': last_block['height'],
					'previous_hash': last_block['previous_hash'],
					'transactions': last_block['transactions'],
					'nonce': last_block['nonce']}'''

		# Check that the hash of the block is correct
		'''if( current_block['previous_hash'] != Block.hash_block(block_data) ):
			print('v1')
			return False

		# Check that the hash of the block is correct
		if( current_block['height'] <= last_block['height'] ):
			print('v2')
			return False'''

		# Check that the Proof of Work is correct given current block data
		dict_transactions = Transaction.json_to_dict(current_block['transactions'])

		# execute valid proof task given consensus algorithm
		if(self.consensus==ConsensusType.PoW):
			if( not POW.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce']) ):
				print('v3')
				return False
		elif(self.consensus==ConsensusType.PoS):
			if( not POS.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce'], 
									TEST_STAKE_WEIGHT, TEST_STAKE_SUM) ):
				print('v3')
				return False
		else:
			return False

		return True

	def valid_transactions(self, transactions):
		"""
		check if transactions in a new block are valid
		"""
		verify_result = True
		for transaction_data in transactions:
			#print(transaction_data)
			# ====================== rebuild transaction ==========================
			dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
			                                    transaction_data['recipient_address'],
			                                    transaction_data['time_stamp'],
			                                    transaction_data['value'])

			sign_str = TypesUtil.hex_to_string(transaction_data['signature'])
			#print(dict_transaction)
			#print(sign_str)

			self.peer_nodes.load_ByAddress(transaction_data['sender_address'])
			sender_node = TypesUtil.string_to_json(list(self.peer_nodes.get_nodelist())[0])
			#print(sender_node)
			# ====================== verify transaction ==========================
			if(sender_node!={}):
			    sender_pk= sender_node['public_key']
			    verify_result = Transaction.verify(sender_pk, sign_str, dict_transaction)
			else:
				verify_result = False
			if(not verify_result):
				break
		return verify_result

	# Get the parent block of a given block
	def get_parent(self, json_block):
		# root block, return None
	    if json_block['height'] == 0:
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
		@ json_msg: json message
		@ op_type: operation type given different message
		'''
		# transaction message processing
		if(op_type ==0):
			return self.accept_transaction(json_msg)
		# block message processing
		elif(op_type ==1):
			return self.accept_block(json_msg)
		#vote message processing
		else:
			return True

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

		self.peer_nodes.load_ByAddress(json_tran['sender_address'])
		sender_node = TypesUtil.string_to_json(list(self.peer_nodes.get_nodelist())[0])

		# ====================== verify transaction ==========================
		if(sender_node!={}):
			sender_pk= sender_node['public_key']
			#verify_data = Transaction.verify(sender_pk, sign_data, dict_transaction)
			verify_result = self.verify_transaction(dict_transaction, sender_pk, sign_data)
		else:
			verify_result = False	
		return verify_result

	def accept_block(self, json_block):
		'''
		Called on processing a block message.
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

		# remove committed transactions
		for transaction in json_block['transactions']:
			self.transactions.remove(transaction)
		
		# append verified block to local chain, status = 0, processed
		self.add_block(json_block, 0)
		self.check_processed_head(json_block)
		self.save_chainInfo()
		return True

	def check_processed_head(self, new_block):
		'''Reorganize the processed_head to stay on the chain with the highest
		justified checkpoint.

		If we are on wrong chain, reset the head to be the highest descendent
		among the chains containing the highest justified checkpoint.

		Args:
		    block: latest block processed.'''

		# we are on the right chain, the head is simply the latest block
		if self.is_ancestor(self.highest_justified_checkpoint, new_block):
			self.processed_head = new_block
			#self.main_chain_size += 1


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


'''	@staticmethod
	def valid_chain(chain_data, consensus=ConsensusType.PoW):
		"""
		check if a bockchain data is valid
		""" 
		# start from chain tail
		previous_block = chain_data[0]
		current_index = 1   
		while current_index < len(chain_data): 
			current_block = chain_data[current_index]

			block_data = {'height': previous_block['height'],
						'previous_hash': previous_block['previous_hash'],
						'transactions': previous_block['transactions'],
						'nonce': previous_block['nonce']}

			# Check that the hash of the block is correct
			if( current_block['previous_hash'] != Block.hash_block(block_data) ):
				print('C1')
				return False

			# Check that the Proof of Work is correct given current block data
			transactions = current_block['transactions']

			# Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
			transaction_elements = ['sender_address', 'recipient_address', 'time_stamp', 'value', 'signature']
			transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]
			
			# execute valid proof task given consensus algorithm
			if(consensus==ConsensusType.PoW):
				if( not POW.valid_proof(transactions, current_block['previous_hash'], current_block['nonce']) ):
					print('C2')
					return False
			elif(consensus==ConsensusType.PoS):
				if( not POS.valid_proof(transactions, current_block['previous_hash'], current_block['nonce'], 
										TEST_STAKE_WEIGHT, TEST_STAKE_SUM) ):
					print('C2')
					return False
			else:
				return False

			previous_block = current_block
			current_index += 1

			return True'''


