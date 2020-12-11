'''
========================
ENF_consensus.py
========================
Created on Dec.8, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide mathmatical functions to support ENF consensus algorithm.
@Reference: 
'''

import math
import numpy as np
from utils.utilities import TypesUtil

'''
EnfProcess class for handling ENF signal squire distance calculation and verification, etc.
'''
class ENFUtil(object):
	@staticmethod
	def sqr_distance(ENF_dataset, scale=1):
		'''
		Function: Calculate squire distance of two ENF singal
		@arguments: 
		(out) sqr_dist:   	return squire distance value of ENF signals
		(in) ENF_data:   	ENF list dataset that can input two ENF signals
		'''
		np_ENF0=TypesUtil.list2np(ENF_dataset[0])
		np_ENF1=TypesUtil.list2np(ENF_dataset[1])
		# print(type(np_ENF0[0]))

		# 1) np_ENF0 - np_ENF0. The difference of np_ENF0 and np_ENF0, element-wise.
		diff_ENF = np.subtract(np_ENF0, np_ENF1) * scale

		# 2) calculate squire of diff_ENF
		sqr_diff = np.square(diff_ENF)

		# 3) calculate sum of sqr_diff to get squire distance of two ENF signals
		sqr_dist = np.sum(sqr_diff)

		return sqr_dist

	@staticmethod
	def sort_ENF_sqr_dist(ENF_samples, benchmark_node):
		'''
		Function: Calculate squire distance of two ENF singal
		@arguments: 
		(out) sorted_sqr_dist:   	return sorted ENF_sqr_dist of neighboring nodes
		(in) ENF_samples:   		ENF samples of neighboring nodes
		(in) benchmark_node:   		benchmark node that works as local validator
		'''
		ENF_sqr_dist = []
		for ENF_node in ENF_samples:
			ENF_dataset = []

			## skip benchmark node
			if(ENF_node[0]==benchmark_node):
				continue
			
			## 1) set benchmark sample data
			ENF_dataset.append(ENF_samples[benchmark_node][1])
			## 2) choose other node
			ENF_dataset.append(ENF_node[1])

			sqr_dist = ENFUtil.sqr_distance(ENF_dataset, scale=100)

			ENF_sqr_dist.append([ENF_node[0], sqr_dist])

		sorted_ENF_sqr_dist = sorted(ENF_sqr_dist, key=lambda x:x[1])

		return sorted_ENF_sqr_dist

	@staticmethod
	def ENF_score(sorted_ENF_sqr_dist):
		'''
		Function: Calculate score that sum n-f-2 of sorted ENF sqr_dist list based on n nodes  
		@arguments: 
		(out) sum_sorted_ENF:   	return sum of sorted_ENF_sqr_dist as ENf score
		(in) sorted_ENF_sqr_dist:   sorted ENF squire distances that ENF samples of neighboring nodes.
		'''
		## calculate byzantine node f let n>=2f+3
		n_count = len(sorted_ENF_sqr_dist)
		byz_count = math.ceil( (n_count-3)/2)

		np_sorted_ENF_sqr_dist = TypesUtil.list2np(sorted_ENF_sqr_dist)

		## calculate sum of ENF_sqr_dist that are from n-f-2 neighboring nodes. 
		sum_sorted_ENF = np.sum(np_sorted_ENF_sqr_dist[:(n_count-byz_count-1),1])

		return sum_sorted_ENF
