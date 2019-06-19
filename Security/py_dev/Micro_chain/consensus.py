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
from configuration import *
from block import Block

class POW():

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

