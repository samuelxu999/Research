'''
========================
ENF_analyze.py
========================
Created on Oct.10, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide analysis functions to support ENF-based deepfake detection.
@Reference: 
'''

import os
import logging
from consensus.block import Block
from utils.db_adapter import DataManager
from utils.configuration import *
from utils.utilities import FileUtil, TypesUtil

logger = logging.getLogger(__name__)

def load_chainInfo():
	"""
	Config file operation: load validator information from static json file
	"""
	if(os.path.isfile(CHAIN_DATA_DIR+'/'+CHAIN_INFO)):
	    return FileUtil.JSON_load(CHAIN_DATA_DIR+'/'+CHAIN_INFO)
	else:
		return None

class ENF_analyzer(object):
	'''
	--------------------------- A analyzer contains the following arguments: ----------------------------------
	self.chain_db: 				local chain database adapter	
	self.chain_info				chain information object
	self.vote_info				vote information for chain finality
	--------------------------------------------------------------------------------------------------------------
	''' 

	def __init__(self):
		## New database manager to manage chain data
		self.chain_db = DataManager(CHAIN_DATA_DIR, BLOCKCHAIN_DATA)
		self.chain_db.create_table(CHAIN_TABLE)

		## Create genesis block
		genesis_block = Block()
		json_data = genesis_block.to_json()

		## no local chain data, generate a new validator information
		if( self.chain_db.select_block(CHAIN_TABLE)==[] ):
			#add genesis_block as 2-finalized
			self.chain_db.insert_block(CHAIN_TABLE,	json_data['hash'], 
					TypesUtil.json_to_string(json_data), 2)

		## -------------- load chain info ---------------
		self.chain_info = load_chainInfo()

		## -------------- get vote info ---------------
		self.vote_info = self.chain_info['vote_count']

	def print_chaininfo(self):
		'''
		Printout chain information.
		'''
		logger.info("Chain information:")
		logger.info("    uuid:                         {}".format(self.chain_info['node_id']))
		logger.info("    processed head:               {}    height: {}".format(self.chain_info['processed_head']['hash'],
																				self.chain_info['processed_head']['height']))
		logger.info("    highest justified checkpoint: {}    height: {}".format(self.chain_info['highest_justified_checkpoint']['hash'],
																				self.chain_info['highest_justified_checkpoint']['height']) )
		logger.info("    highest finalized checkpoint: {}    height: {}".format(self.chain_info['highest_finalized_checkpoint']['hash'],
																				self.chain_info['highest_finalized_checkpoint']['height']) )
	def print_voteinfo(self):
		'''
		Printout vote information.
		'''
		logger.info("Vote information:")

		## for each vote data to get source hash
		for src_hash in self.vote_info:
			## for each attributes to get destination hash and vote value.
			for des_hash, vote_value in self.vote_info[src_hash].items():
				logger.info("source hash: {} ----> target hash: {}   vote:{}".format(src_hash,des_hash, vote_value))

	def getBlock(self, block_hash):
		'''
		get block data given bloch hash.
		Args:			
			@block_hash: hash value refered to a block			
			@return: block data (json)
		'''
		ls_block = self.chain_db.select_block(CHAIN_TABLE, block_hash)
		if( ls_block==[] ):
			return {}
		else:
			return TypesUtil.string_to_json(ls_block[0][2])
