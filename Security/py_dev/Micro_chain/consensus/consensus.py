'''
========================
consensus.py
========================
Created on June.18, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide consensus algorithm implementation.
@Reference: 
'''

from enum import Enum

from merklelib import MerkleTree, jsonify as merkle_jsonify

from utils.configuration import *
from utils.utilities import TypesUtil, FuncUtil
from consensus.transaction import Transaction

class ConsensusType(Enum):
	'''
	Define consensus enum type
	@ PoW :  Proof-of-Work
	@ PoS :  Proof-of-Stake
	@ BFT :  Byzantine Fault Tolerant
	'''
	PoW = 0
	PoS = 1
	BFT = 2

class POW():
	''' 
	Proof-of-Work consenses mechanism
	'''

	@staticmethod
	def valid_proof(merkle_root, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ previous_hash:	The hash of parent block
		@ nonce: 			the random number used in PoW guess 
		@ merkle_root: 		merkle tree root of transactions in block 
		"""
		guess_str = (str(merkle_root)+str(previous_hash)+str(nonce)).encode('utf8')
		guess_hash = FuncUtil.hashfunc_sha256(guess_str)
		#print(guess_hash[:difficulty])
		return guess_hash[:difficulty] == '0'*difficulty

	@staticmethod
	def proof_of_work(last_block, transactions):
		"""
		Proof of work algorithm
		@ last_block: 	parent block data without 'hash' value
		@ transactions: commited transactions list when new block is generated
		"""
		#last_block = chain_data[-1]
		last_hash = TypesUtil.hash_json(last_block)
		#print(transactions)

		# build a Merkle tree for transactions list
		tx_HMT = MerkleTree(transactions, FuncUtil.hashfunc_sha256)

		# calculate merkle tree root hash
		if(len(tx_HMT)==0):
			merkle_root = 0
		else:
			tree_struct=merkle_jsonify(tx_HMT)
			json_tree = TypesUtil.string_to_json(tree_struct)
			merkle_root = json_tree['name']

		nonce = 0
		while POW.valid_proof(merkle_root, last_hash, nonce) is False:
		    nonce += 1

		# return mined nonce
		return nonce

class POS():
	''' 
	Proof-of-Stake consenses mechanism
	'''

	@staticmethod
	def valid_proof(merkle_root, previous_hash, nonce, stake_weight=1, sum_stake=1):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ previous_hash:	The hash of parent block
		@ nonce: 			the stake deposit value 
		@ merkle_root: 		merkle tree root of transactions in block 
		"""
		guess_str = (str(merkle_root)+str(previous_hash)+str(nonce)).encode('utf8')
		guess_hash = FuncUtil.hashfunc_sha256(guess_str)
		#print(guess_hash)
		difficulty =1
		while(int('f'*difficulty, 16) < sum_stake):
			difficulty+=1

		guess_weight = int(guess_hash[:difficulty], 16)/int('f'*difficulty, 16) 

		# The hit rate is related to P(nonce/sum_stake)
		return guess_weight < (stake_weight/sum_stake)

	@staticmethod
	def get_proof(merkle_root, previous_hash, nonce, sum_stake=1):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ nonce: 		the stake deposit value 
		@ merkle_root: 	merkle tree root of transactions in block 
		"""
		guess_str = (str(merkle_root)+str(previous_hash)+str(nonce)).encode('utf8')
		guess_hash = FuncUtil.hashfunc_sha256(guess_str)
		#print(guess_hash)
		difficulty =1
		while(int('f'*difficulty, 16) < sum_stake):
			difficulty+=1

		guess_weight = int(guess_hash[:difficulty], 16)

		return guess_weight

	@staticmethod
	def proof_of_stake(parent_block, commit_transactions, nonce, stake_weight, sum_stake):
		"""
		Proof of work algorithm
		@ parent_block: 		parent block data without 'hash' value
		@ commit_transactions: 	commited transactions list when new block is generated
		@ nonce: 				the stake deposit value 
		"""
		#last_block = chain_data[-1]
		last_hash = TypesUtil.hash_json(parent_block)

		# convert to a order-dict transactions list
		dict_transactions = Transaction.json_to_dict(commit_transactions)

		# build a Merkle tree for that list
		tx_HMT = MerkleTree(dict_transactions, FuncUtil.hashfunc_sha256)

		# calculate merkle tree root hash
		if(len(tx_HMT)==0):
			merkle_root = 0
		else:
			tree_struct=merkle_jsonify(tx_HMT)
			json_tree = TypesUtil.string_to_json(tree_struct)
			merkle_root = json_tree['name']

		if( not POS.valid_proof(merkle_root, last_hash, nonce, stake_weight, sum_stake) ):
			return 0
		return nonce

		


