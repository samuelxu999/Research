'''
========================
blockchain.py
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
from transaction import Transaction
from block import Block
from consensus import POW
from configuration import *


class Blockchain():

	def __init__(self):

		self.transactions = []
		self.chain = []

		#Generate random number to be used as node_id
		self.node_id = str(uuid4()).replace('-', '')

		#Create genesis block
		#genesis_block = self.genesis_block()
		genesis_block = Block()
		self.chain.append(genesis_block.to_json())

	def verify_transaction(self, transaction, sender_pk, signature):
		"""
		Verify a transaction and append to transactions list
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
		Mining task to find new block
		"""

		commit_transactions = []
		if(len(self.transactions)<=COMMIT_TRANS):
			commit_transactions = copy.copy(self.transactions)

		else:
			commit_transactions = copy.copy(self.transactions[:COMMIT_TRANS])


		last_block = self.chain[-1]

		block_data = {'height': last_block['height'],
					'previous_hash': last_block['previous_hash'],
					'transactions': last_block['transactions'],
					'nonce': last_block['nonce']}

		parent_block = Block.json_to_block(last_block)

		# mining new nonce
		nonce = POW.proof_of_work(block_data, commit_transactions)
		new_block = Block(parent_block, commit_transactions, nonce)

		return new_block.to_json()

	@staticmethod
	def valid_block(new_block, chain_data):
		"""
		check if a new block from other miners is valid
		"""
		last_block = chain_data[-1]
		current_block = new_block
		#print(previous_block)
		#print(current_block)

		block_data = {'height': last_block['height'],
					'previous_hash': last_block['previous_hash'],
					'transactions': last_block['transactions'],
					'nonce': last_block['nonce']}

		# Check that the hash of the block is correct
		if( current_block['previous_hash'] != Block.hash_block(block_data) ):
			print('v1')
			return False

		# Check that the hash of the block is correct
		if( current_block['height'] <= last_block['height'] ):
			print('v2')
			return False

		# Check that the Proof of Work is correct given current block data
		dict_transactions = Transaction.json_to_dict(current_block['transactions'])

		if(not POW.valid_proof(dict_transactions, current_block['previous_hash'], current_block['nonce'])):
			print('v3')
			return False

		return True

	@staticmethod
	def valid_chain(chain_data):
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

			if(not POW.valid_proof(transactions, current_block['previous_hash'], current_block['nonce'])):
				print('C2')
				return False
				#pass

			previous_block = current_block
			current_index += 1

			return True

def chain_test():
    # Instantiate the Blockchain
    myblockchain = Blockchain()
    print('Chain information:')
    print('    uuid:          ', myblockchain.node_id)
    print('    chain length: ', len(myblockchain.chain))

    print(myblockchain.chain[0])
    print('Mining....')
    for i in range(1, 6):
        new_block=myblockchain.mine_block()
        myblockchain.chain.append(new_block)
        print(new_block)

    #print(blockchain.chain[-1])
    print('    chain length: ', len(myblockchain.chain))

    print('Valid chain: ', Blockchain.valid_chain(myblockchain.chain))

    new_block = myblockchain.mine_block()
    print('Valid block: ', Blockchain.valid_block(new_block, myblockchain.chain))

if __name__ == '__main__':
    chain_test()
    pass








