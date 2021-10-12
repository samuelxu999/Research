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
import random
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
		
	@staticmethod
	def loadENF_vectors(honest_file, bft_file, sample_head, 
						sample_length, head_seek, sample_nodes, BFT_rate, random_sample, show_info=False):
		'''
		load ENF vectors (list) given honest and bft ENF recordings
		Args:
		input
			@honest_file:		honest node ENF recording csv file 			
			@bft_file: 			bft node ENF recording csv file		
			@sample_head: 		head position of the sample data section 
			@sample_length: 	data length of a ENF vector. 
			@head_seek:			head seek that calculate head_pos for an ENF vector
			@sample_nodes:		Total number of sample nodes.
			@BFT_rate:			BFT node rate (%) of the whole committee.
			@random_sample:		True: use random head_position of an ENF vector.
		output
			@ENF_vectors:		return ENF vectors (list)
		'''
		## load ENF data
		honest_ENF_data = FileUtil.csv_read(honest_file)
		bft_ENF_data = FileUtil.csv_read(bft_file)	

		# get parameters
		ENF_vectors_head = sample_head
		ENF_length = sample_length
		ENF_head_seek = head_seek

		## get honest and BFT nodes
		total_node = sample_nodes

		bft_node = int(total_node*BFT_rate)
		honest_node = total_node - bft_node

		if(show_info):
			logger.info('Honest: {}    BFT: {}'.format(honest_node, bft_node))

		## define ENF_vectors to save selected ENF samples
		ENF_vectors = []

		## define ENF_id to index each node
		ENF_id = 0	

		## set head_pos as head of ENF_vectors.
		head_pos = ENF_vectors_head
		for ENF_id in range(honest_node):
			## 1) generate an ENF vector given head_pos and ENF_length
			ls_ENF = TypesUtil.np2list( np.array(honest_ENF_data[head_pos:(head_pos+ENF_length), 1], dtype=np.float32) )
			
			## 2) assign ls_ENF to ENF_id and append to ENF_vectors
			ENF_vectors.append([ENF_id, ls_ENF])

			## 3) calculate head_pos for next honest node
			if(random_sample):
				head_pos = random.randint(head_pos, head_pos+ENF_head_seek)
			else:
				head_pos = head_pos + ENF_head_seek

		## reset head_pos as head of ENF_vectors.
		head_pos = ENF_vectors_head
		for ENF_id in range(bft_node):
			## 1) generate an ENF vector given head_pos and ENF_length		
			ls_ENF = TypesUtil.np2list( np.array(bft_ENF_data[head_pos:(head_pos+ENF_length), 1], dtype=np.float32) )
			
			## 2) assign ls_ENF to ENF_id and append to ENF_vectors
			ENF_vectors.append([ENF_id+honest_node, ls_ENF])

			## 3) calculate head_pos for next bft node
			if(random_sample):
				head_pos = random.randint(head_pos, head_pos+ENF_head_seek)
			else:
				head_pos = head_pos + ENF_head_seek

		return ENF_vectors

	@staticmethod
	def sorted_ENF_scores(ENF_vectors, show_info=False):
		'''
		calculate ENF scores for all nodes and return sorted ENF_scores list
		Args:
		input
			@ENF_vectors:			ENF vectors (list) for all nodes			
		output
			@ls_ENF_scores_sorted:		return sorted ENF scores (list)
		'''

		## calculate ENF score for each node
		ls_ENF_score = []
		for ENF_id in range(len(ENF_vectors)):
			sorted_ENF_sqr_dist=ENFUtil.sort_ENF_sqr_dist(ENF_vectors, ENF_id)
			ENF_score = ENFUtil.ENF_score(sorted_ENF_sqr_dist)
			ls_ENF_score.append([ENF_id, ENF_score])

		ls_ENF_scores_sorted = sorted(ls_ENF_score, key=lambda x:x[1])

		if(show_info):
			logger.info("Sorted ENF score is: {}".format(ls_ENF_scores_sorted))

		## return sorted ENF scores
		return ls_ENF_scores_sorted
