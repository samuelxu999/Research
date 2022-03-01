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
	def valid_proof(parent_hash, merkle_root, nonce, difficulty=MINING_DIFFICULTY):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ parent_hash:	The hash of parent block 
		@ merkle_root: 		merkle tree root of transactions in block 
		@ nonce: 			the random number used in PoW guess
		"""
		guess_str = (str(parent_hash)+str(merkle_root)+str(nonce)).encode('utf8')
		guess_hash = FuncUtil.hashfunc_sha256(guess_str)
		#print(guess_hash[:difficulty])
		return guess_hash[:difficulty] == '0'*difficulty

	@staticmethod
	def proof_of_work(parent_hash, merkle_root):
		"""
		Proof of work algorithm
		@ parent_hash: 			parent block hash value
		@ merkle_root: 		merkle tree root of transactions in block
		"""
		nonce = 0
		while POW.valid_proof(parent_hash, merkle_root, nonce) is False:
		    nonce += 1

		# return mined nonce
		return nonce

class POS():
	''' 
	Proof-of-Stake consenses mechanism
	'''

	@staticmethod
	def valid_proof(parent_hash, merkle_root, nonce, stake_weight=1, sum_stake=1):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ parent_hash: 		parent block hash value	 
		@ merkle_root: 		merkle tree root of transactions in block 
		@ nonce: 			the stake deposit value
		"""
		guess_str = (str(parent_hash)+str(merkle_root)+str(nonce)).encode('utf8')
		guess_hash = FuncUtil.hashfunc_sha256(guess_str)
		#print(guess_hash)
		difficulty =1
		while(int('f'*difficulty, 16) < sum_stake):
			difficulty+=1

		guess_weight = int(guess_hash[:difficulty], 16)/int('f'*difficulty, 16) 

		# The hit rate is related to P(nonce/sum_stake)
		return guess_weight < (stake_weight/sum_stake)

	@staticmethod
	def get_proof(parent_hash, merkle_root, nonce, sum_stake=1):
		"""
		Check if a guessing hash value satisfies the mining difficulty conditions. 
		@ parent_hash: 		parent block hash value	
		@ nonce: 			random value from vdf proof 
		@ merkle_root: 		merkle tree root of transactions in block 
		"""
		guess_str = (str(parent_hash)+str(merkle_root)+str(nonce)).encode('utf8')
		guess_hash = FuncUtil.hashfunc_sha256(guess_str)
		#print(guess_hash)
		difficulty =1
		while(int('f'*difficulty, 16) < sum_stake):
			difficulty+=1

		guess_weight = int(guess_hash[:difficulty], 16)

		return guess_weight

	@staticmethod
	def proof_of_stake(parent_hash, merkle_root, nonce, stake_weight, sum_stake):
		"""
		Proof of work algorithm
		@ parent_hash: 		parent block hash value
		@ merkle_root: 		merkle tree root of transactions in block 
		@ nonce: 			the stake deposit value 
		"""

		if( not POS.valid_proof(parent_hash, merkle_root, nonce, stake_weight, sum_stake) ):
			return 0
		return nonce

		


