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

import hashlib
from utilities import TypesUtil
from collections import OrderedDict
from crypto_rsa import Crypto_RSA

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
			hash_data = hashlib.sha1(str(self.to_dict()).encode('utf8')).hexdigest()
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
			hash_data = hashlib.sha1(str(dict_vote).encode('utf8')).hexdigest()
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


