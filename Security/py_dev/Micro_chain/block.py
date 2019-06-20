'''
========================
block.py
========================
Created on June.18, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide block data struct and functions implementation.
@Reference: 
'''

import hashlib
import json
from collections import OrderedDict

from configuration import *

class Block():
	"""One node (roundrobin) adds a new block to the blockchain every
	BLOCK_PROPOSAL_TIME iterations.

	Args:
	    parent: parent block
	    finalized_dynasties: dynasties which have been finalized.
	                         Only a committed block's dynasty becomes finalized.
	"""

	def __init__(self, parent=None, transactions=[], nonce = 0):
		"""A block contains the following arguments:

		self.hash: hash of the block
		self.height: height of the block (genesis = 0)
		self.previous_hash: hash of the parent block
		self.transactions: transactions list
		"""
		# If we are genesis block, set initial values
		if not parent:
			self.height = 0
			self.previous_hash = 0
		else:
			self.height = parent.height+1
			self.previous_hash = parent.hash
		
		self.transactions = transactions
		self.nonce = nonce

		block = {'height': self.height,
			'previous_hash': self.previous_hash,
			'transactions': self.transactions,
			'nonce': self.nonce}
		# calculate hash of block 
		self.hash = Block.hash_block(block)
		return

	def to_dict(self):
		"""
		Output dict block data structure. 
		"""
		order_dict = OrderedDict()
		order_dict['hash'] = self.hash
		order_dict['height'] = self.height
		order_dict['previous_hash'] = self.previous_hash
		order_dict['transactions'] = self.transactions
		order_dict['nonce'] = self.nonce
		return order_dict
    
	def to_json(self):
		"""
		Output dict block data structure. 
		"""
		return {'hash': self.hash,
				'height': self.height,
				'previous_hash': self.previous_hash,
				'transactions': self.transactions,
				'nonce': self.nonce }

	def print_data(self):
		print('Block information:')
		print('    hash:',self.hash)
		print('    height:',self.height)
		print('    previous_hash:',self.previous_hash)
		print('    transactions:',self.transactions)
		print('    nonce:',self.nonce)

	@staticmethod
	def hash_block(block):
	    """
	    Create a SHA-256 hash of a block
	    """
	    # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
	    block_string = json.dumps(block, sort_keys=True).encode()
	    
	    return hashlib.sha256(block_string).hexdigest()

	@staticmethod
	def json_to_block(block_json):
		"""
		Output block object given json block data structure. 
		"""
		block = Block()
		block.hash = block_json['hash']
		block.height = block_json['height']
		block.previous_hash = block_json['previous_hash']
		block.transactions = block_json['transactions']
		block.nonce = block_json['nonce']
		return block

	@staticmethod
	def isEmptyBlock(block_json):
		"""
		check if block_json is empty block. 
		"""
		if( (block_json['height'] >0) and block_json['nonce']==0):
			return True
		return False



