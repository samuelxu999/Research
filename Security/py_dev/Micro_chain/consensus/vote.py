'''
========================
vote.py
========================
Created on June.27, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide vote message implementation.
@Reference: 
'''

from collections import OrderedDict

from cryptolib.crypto_rsa import Crypto_RSA
from utils.utilities import TypesUtil, FuncUtil
from utils.db_adapter import DataManager
from utils.configuration import *

class VoteCheckPoint(object):
	"""Vote check point message

	Args:
		self.hash: hash of the vote message
	    source_hash: hash of the source block
	    target_hash: hash of the target block
	    epoch_source: epoch of the source block
	    epoch_target: epoch of the target block
	    sender_address: node address of sending the VOTE message
	"""
	def __init__(self, source_hash, target_hash, epoch_source, epoch_target, sender_address):
		self.source_hash = source_hash
		self.target_hash = target_hash
		self.epoch_source = epoch_source
		self.epoch_target = epoch_target
		self.sender_address = sender_address

		block = {'source_hash': self.source_hash,
				'target_hash': self.target_hash,
				'epoch_source': self.epoch_source,
				'epoch_target': self.epoch_target,
				'sender_address': self.sender_address}
		# calculate hash of block 
		self.hash = TypesUtil.hash_json(block)

	def to_dict(self):
		"""
		Output as dict data structure. 
		"""
		order_dict = OrderedDict()
		order_dict['hash'] = self.hash
		order_dict['source_hash'] = self.source_hash
		order_dict['target_hash'] = self.target_hash
		order_dict['epoch_source'] = self.epoch_source
		order_dict['epoch_target'] = self.epoch_target
		order_dict['sender_address'] = self.sender_address
		return order_dict

	def to_json(self):
		"""
		Output as json data structure. 
		"""
		return {'hash': self.hash,
		        'source_hash': self.source_hash,
		        'target_hash': self.target_hash,
		        'epoch_source': self.epoch_source,
		        'epoch_target': self.epoch_target,
		        'sender_address': self.sender_address }

	def sign(self, sender_private_key, sk_pw):
		'''
		Sign vote by using sender's private key and password
		'''
		try:
			private_key_byte = TypesUtil.hex_to_string(sender_private_key)
			private_key = Crypto_RSA.load_private_key(private_key_byte, sk_pw)

			# generate hashed dict_vote
			hash_data = FuncUtil.hashfunc_sha1(str(self.to_dict()).encode('utf8'))
			sign_value = Crypto_RSA.sign(private_key, hash_data)
		except:
			sign_value=''
		return sign_value

	@staticmethod
	def verify(sender_public_key, signature, dict_vote):
		"""
		Verify vote by using sender's public key
		"""
		try:
			public_key_byte = TypesUtil.hex_to_string(sender_public_key)
			publick_key = Crypto_RSA.load_public_key(public_key_byte)

			# generate hashed dict_vote
			hash_data = FuncUtil.hashfunc_sha1(str(dict_vote).encode('utf8'))
			verify_sign=Crypto_RSA.verify(publick_key,signature,hash_data)
		except:
			verify_sign=False
		return verify_sign

	@staticmethod
	def json_to_vote(json_vote):
		"""
		Output vote object given json vote data structure. 
		"""
		return VoteCheckPoint(json_vote['source_hash'], json_vote['target_hash'],
								json_vote['epoch_source'], json_vote['epoch_target'], 
								json_vote['sender_address'])

	# ------------------------ voter database function--------------------
	@staticmethod
	def new_voter(voter_block):
		"""
		Output voter_db object given voter's hash address. 
		"""	
		voter_name = 'voter_' + voter_block['sender_address']
		# New database manager to manage chain data
		voter_db = DataManager(CHAIN_DATA_DIR, VOTER_DATA)
		voter_db.create_table(voter_name)
		return voter_db

	@staticmethod
	def remove_voter(voter_block):
		"""
		remove voter table given voter's hash address. 
		"""	
		voter_name = 'voter_' + voter_block['sender_address']
		# New database manager to manage chain data
		voter_db = DataManager(CHAIN_DATA_DIR, VOTER_DATA)
		voter_db.remove_table(voter_name)

	@staticmethod
	def get_voter_data(voter_db, voter_block, block_hash=''):
		"""
		Output all vote data as json list given voter's hash address . 
		"""	
		voter_name = 'voter_' + voter_block['sender_address']
		#select a block as json given block_hash
		ls_blocks = voter_db.select_block(voter_name, block_hash)
		ls_json = []
		for str_block in ls_blocks:
			ls_json.append(TypesUtil.string_to_json(str_block[2]))
		return ls_json

	@staticmethod
	def add_voter_data(voter_db, voter_block):
		"""
		Add voter_block to database . 
		"""	
		voter_name = 'voter_' + voter_block['sender_address']
		# if block not existed, add block to database
		if( VoteCheckPoint.get_voter_data(voter_db, voter_block, voter_block['hash'])==[] ):
			voter_db.insert_block(voter_name, voter_block['hash'], 
								TypesUtil.json_to_string(voter_block))



