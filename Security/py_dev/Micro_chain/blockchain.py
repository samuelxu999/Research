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

from utilities import FileUtil, TypesUtil
from transaction import Transaction

MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1
MINING_DIFFICULTY = 4


class Blockchain:

	def __init__(self):
	    
	    self.transactions = []
	    self.chain = []

	    #Generate random number to be used as node_id
	    self.node_id = str(uuid4()).replace('-', '')
	    #Create genesis block
	    self.create_block(0, '00')

	def create_block(self, nonce, previous_hash):
	    """
	    Add a block of transactions to the blockchain
	    """
	    block = {'block_number': len(self.chain) + 1,
	            'timestamp': time(),
	            'transactions': self.transactions,
	            'nonce': nonce,
	            'previous_hash': previous_hash}

	    # Reset the current list of transactions
	    self.transactions = []

	    self.chain.append(block)
	    return block

	def verify_transaction(self, transaction, sender_pk, signature):
		"""
		Verify a transaction and append to transactions list
		"""
		verify_result = Transaction.verify(sender_pk, signature, transaction)
		if(verify_result):
		    self.transactions.append(transaction)
		    return True
		else:
		    return False

 
	def mine_block(self):
	    """
	    Mining task to find new block
	    """
	    last_block = self.chain[-1]
	    #print(last_block)
	    block_hash = Blockchain.hash_block(last_block)
	    nonce = Blockchain.proof_of_work(last_block, self.transactions)
	    return self.create_block(nonce, block_hash)

	@staticmethod
	def hash_block(block):
	    """
	    Create a SHA-256 hash of a block
	    """
	    # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
	    block_string = json.dumps(block, sort_keys=True).encode()
	    
	    return hashlib.sha256(block_string).hexdigest()

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
	    last_hash = Blockchain.hash_block(last_block)

	    nonce = 0
	    while Blockchain.valid_proof(transactions, last_hash, nonce) is False:
	        nonce += 1

	    # return mined nonce
	    return nonce

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

	        # Check that the hash of the block is correct
	        if current_block['previous_hash'] != Blockchain.hash_block(previous_block):
	            return False

	        # Check that the Proof of Work is correct given current block data
	        transactions = current_block['transactions']

	        # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
	        transaction_elements = ['sender_address', 'recipient_address', 'value']
	        transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]
	        #print(transactions)

	        if(not Blockchain.valid_proof(transactions, current_block['previous_hash'], current_block['nonce'], MINING_DIFFICULTY)):
	            return False
	            #pass

	        previous_block = current_block
	        current_index += 1

	    return True

def chain_test():
    # Instantiate the Blockchain
    blockchain = Blockchain()
    print('Chain information:')
    print('    uuid:          ', blockchain.node_id)
    print('    chain length: ', len(blockchain.chain))

    print('Mining....')
    for i in range(1, 6):
        new_block=blockchain.mine_block()
        #print(blockchain.chain[-1])
        print(new_block)

    #print(blockchain.chain[-1])
    print('    chain length: ', len(blockchain.chain))

    print('Valid chain: ', blockchain.valid_chain(blockchain.chain))

if __name__ == '__main__':
    chain_test()
    pass








