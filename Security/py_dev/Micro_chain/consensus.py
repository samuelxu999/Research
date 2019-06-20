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

import hashlib
from enum import Enum
from configuration import *
from block import Block

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
	def valid_proof(transactions, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		"""
		guess_str = (str(transactions)+str(previous_hash)+str(nonce)).encode()
		guess_hash = hashlib.sha256(guess_str).hexdigest()
		#print(guess_hash[:difficulty])
		return guess_hash[:difficulty] == '0'*difficulty

	@staticmethod
	def proof_of_work(last_block, transactions):
		"""
		Proof of work algorithm
		"""
		#last_block = chain_data[-1]
		last_hash = Block.hash_block(last_block)
		#print(transactions)
		nonce = 0
		while POW.valid_proof(transactions, last_hash, nonce) is False:
		    nonce += 1

		# return mined nonce
		return nonce

class POS():
	''' 
	Proof-of-Stake consenses mechanism
	'''

	@staticmethod
	def valid_proof(transactions, previous_hash, nonce, stake_weight=1, sum_stake=1):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ nonce: the stake deposit value 
		"""
		guess_str = (str(transactions)+str(previous_hash)+str(nonce)).encode()
		guess_hash = hashlib.sha256(guess_str).hexdigest()
		#print(guess_hash)
		difficulty =1
		while(int('f'*difficulty, 16) < sum_stake):
			difficulty+=1

		guess_weight = int(guess_hash[:difficulty], 16)/int('f'*difficulty, 16) 

		# The hit rate is related to P(nonce/sum_stake)
		return guess_weight < (stake_weight/sum_stake)

	@staticmethod
	def proof_of_stake(parent_block, commit_transactions, nonce, stake_weight, sum_stake):
		"""
		Proof of work algorithm
		@ parent_block: parent block data without 'hash' value
		@ commit_transactions: commited transactions list when new block
		"""
		#last_block = chain_data[-1]
		last_hash = Block.hash_block(parent_block)

		if( not POS.valid_proof(commit_transactions, last_hash, nonce, stake_weight, sum_stake) ):
			return 0
		return nonce

		


