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
import numpy as np
from consensus.block import Block
from consensus.ENF_consensus import ENFUtil
from utils.db_adapter import DataManager
from utils.configuration import *
from utils.utilities import FileUtil, TypesUtil
from utils.Swarm_RPC import Swarm_RPC

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
			@block_hash: 	hash value refered to a block			
			@return: 		block data (json)
		'''
		ls_block = self.chain_db.select_block(CHAIN_TABLE, block_hash)
		if( ls_block==[] ):
			return {}
		else:
			return TypesUtil.string_to_json(ls_block[0][2])

	def getENF_vectors(self, json_block):
		'''
		get ENF proof data given bloch data (json).
		Args:			
			@json_block: 	json fromat of a block	data		
			@return: 		ENF_vectors (list)
		'''
		ENF_id = 0
		ENF_vectors = []

		## for each tx to get enf_proof
		for tx in json_block['transactions']:
			json_value = TypesUtil.string_to_json(tx['value'])

			## get a swarm service node address
			swarm_node = Swarm_RPC.get_service_address()

			## query raw ENF proof from network
			enf_proof = Swarm_RPC.download_data(swarm_node, json_value['swarm_hash'])

			## add valid enf_proof data to ENF_vectors
			if(enf_proof['status'] == 200):
				enf_data = TypesUtil.string_to_json(enf_proof['data'])
				ENF_vectors.append([ENF_id, enf_data['enf'], json_value['sender_address']])
				ENF_id+=1

		return ENF_vectors

	def getENF_scores(self, ENF_vectors, Is_sorted=False):
		'''
		calculate ENF score list given ENF_vectors.
		Args:			
			@ENF_vectors: 	list fromat of ENF_vectors		
			@return: 		ENF_scores (list)
		'''

		ls_ENF_scores = []
		## calculate ENF score for each node 
		for ENF_id in range(len(ENF_vectors)):
			sorted_ENF_sqr_dist=ENFUtil.sort_ENF_sqr_dist(ENF_vectors, ENF_id)
			ENF_score = ENFUtil.ENF_score(sorted_ENF_sqr_dist)
			ls_ENF_scores.append([ENF_id, ENF_score, ENF_vectors[ENF_id][2]])

		## get sorted ENF scores list
		sorted_ENF_scores = sorted(ls_ENF_scores, key=lambda x:x[1])

		if(Is_sorted):
			return sorted_ENF_scores
		else:
			return ls_ENF_scores

	def getGroundtruthENF(self, ENF_vectors, ls_ENF_scores):
		'''
		calculate the ground truth ENF given ls_ENF_scores.
		Args:
			@ENF_vectors:	list fromat of ENF_vectors 			
			@ls_ENF_scores: 	list fromat of ENF_scores		
			@return: 		Ground truth ENF (list)
		'''
		
		## get sorted ENF scores list 
		sorted_ENF_scores = sorted(ls_ENF_scores, key=lambda x:x[1])

		## get ground truth ENF vector list
		G_ENF_vector = ENF_vectors[sorted_ENF_scores[0][0]]

		## convert list to float array
		np_ENF_vector=TypesUtil.list2np(G_ENF_vector[1])

		## calculate ground truth ENF value 
		G_ENF = np.average(np_ENF_vector)

		## return results with index and sender information.
		return [G_ENF_vector[0], G_ENF, G_ENF_vector[2]]
		

