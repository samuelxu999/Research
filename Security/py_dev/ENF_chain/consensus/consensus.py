'''
========================
consensus.py
========================
Created on Dec.10, 2020
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
from utils.Swarm_RPC import Swarm_RPC
from consensus.ENF_consensus import ENFUtil

class ConsensusType(Enum):
	'''
	Define consensus enum type
	@ PoW :  Proof-of-Work
	@ PoS :  Proof-of-Stake
	@ PoE :  Proof-of-ENF 
	'''
	PoW = 0
	PoS = 1
	PoE = 2

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

class POE():
	''' 
	Proof-of-ENF consenses mechanism
	'''
	@staticmethod
	def proof_of_enf(commit_transactions, validator_id):
		"""
		Proof of ENF algorithm
		@ commit_transactions: 	commited transactions list when new block is generated
		@ validator_id: 		the address of validator 
		"""
		ENF_samples = []
		## internal id for sort score
		ENF_id = 0
		for transaction in commit_transactions:
			json_value = TypesUtil.string_to_json(transaction['value'])
			swarm_hash = json_value['swarm_hash']
			target_address = Swarm_RPC.get_service_address()
			query_data = Swarm_RPC.download_data(target_address,swarm_hash)['data']
			json_data = TypesUtil.string_to_json(query_data)

			ENF_samples.append( [ENF_id, json_data['enf'], json_data['id'] ])
			ENF_id=ENF_id+1

		# For byzantine tolerant: 3f+1, at least 4 samples points are required. 
		if(len(ENF_samples)<4):
			return False
		
		##  calculate ENF score for each node 
		# print(ENF_samples)
		ls_ENF_score = []
		for ENF_id in range(len(ENF_samples)):
			# print(sample_data['enf'])
			sorted_ENF_sqr_dist=ENFUtil.sort_ENF_sqr_dist(ENF_samples, ENF_id)
			ENF_score = ENFUtil.ENF_score(sorted_ENF_sqr_dist)
			ls_ENF_score.append([ENF_id, ENF_score])

		## get sorted ENF score 
		sorted_score = sorted(ls_ENF_score, key=lambda x:x[1])
		# print(sorted_score)

		winner_id = ENF_samples[sorted_score[0][0]][2]
		# print("winer: {}    sender: {}   result: {}".format(winner_id, validator_id,
		# 													validator_id==winner_id))

		## return if validator_id has proposed the least score among all nodes
		return validator_id==winner_id
