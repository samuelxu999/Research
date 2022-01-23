'''
========================
ssa.py
========================
Created on Dec.17, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide Singluar Spectrum Analysis functions.
@Reference: 
'''

import logging
import math
import numpy as np
from sklearn.preprocessing import MinMaxScaler


logger = logging.getLogger(__name__)

def _create_hankel(ts_vect, win_length, hankel_order, start_id):
	'''Create Hankel matrix.
	input
		ts_vect : 			full time series vector
		win_length:			window length of Hankel matrix
		hankel_order : 		order of Hankel matrix
		start_id : 			start index of ts_vect
	returns
		hankel_X:			hankel matrix, 2d array shape (win_len, hankel_order)
	'''
	end_id = start_id + hankel_order
	hankel_X = np.empty((win_length, hankel_order))
	for i in range(hankel_order):
	    hankel_X[:, i] = ts_vect[(start_id + i):(start_id + i + win_length)]
	return hankel_X

def _score_svd(hankel_base, hankel_test, n_eofs):
	'''
	Run singular spectrum analysis algorithm for change point detection (cpd)
	'''
	## apply svd to decompose hankel_base
	U_base, _, _ = np.linalg.svd(hankel_base, full_matrices=False)

	## apply svd to decompose hankel_test
	U_test, _, _ = np.linalg.svd(hankel_test, full_matrices=False)

	## perform the svd of lag-covariance matrix R=X*X.T 
	## given a particular group I including sorted n_eofs eigenvectors.
	## s is a list of scores that indicate the largest eigenvalue
	_, s, _ = np.linalg.svd(U_test[:, :n_eofs].T @
	    U_base[:, :n_eofs], full_matrices=False)

	## return the largest one as score.
	return 1 - s[0]

def _Edist_svd(hankel_base, hankel_test, n_eofs):
	'''
	Run svd to get Euclidean distances of hankel_base and hankel_test
	'''
	## apply svd to decompose hankel_base
	U_base, _, _ = np.linalg.svd(hankel_base, full_matrices=False)

	## calculate Euclidean distance between test matrix and space matrix
	Euc_dist = np.linalg.norm(hankel_test.T @ hankel_test - 
		hankel_test.T @ U_base[:, :n_eofs] @ U_base[:, :n_eofs].T @ hankel_test)

	## return the lEuclidean distance.
	return Euc_dist


class SingularSpectrumAnalysis():
	'''
	Singular Spectrum Analysis class
	'''
	def __init__(self, win_len, n_eofs=5, hankel_order=None, test_lag=None):
		'''
		win_len : int
	        window length (M) of Hankel matrix. This also specify how data of X_i vecter in Hankel matrix
		n_eofs : int
	        n components for EOFs. This also specify how many rank of Hankel matrix will be taken
		hankel_order : int
	        Hankel matrix length (K or Q). This also specify number of columns of Hankel matrix.  
		test_lag : int
	        interval between base matrix and test matrix (p).      
		'''
		self.win_len = win_len
		self.n_eofs = n_eofs
		self.hankel_order = hankel_order
		self.test_lag = test_lag

	def score_ssa(self, ts_vect):
		'''
		ts_vect : list
			time serial vector that used to build scores between base matrix and test matrix.
		'''
		if self.hankel_order is None:
			# rule of thumb
			self.hankel_order = self.win_len
		if self.test_lag is None:
			# rule of thumb
			self.test_lag = self.hankel_order // 2

		assert isinstance(ts_vect, np.ndarray), "input array must be numpy array."
		assert ts_vect.ndim == 1, "input array dimension must be 1."
		assert isinstance(self.win_len, int), "window length must be int."
		assert isinstance(self.n_eofs, int), "number of components must be int."
		assert isinstance(self.hankel_order, int), "order of partial time series must be int."
		assert isinstance(self.test_lag, int), "lag between test series and history series must be int."

		# ts_scaled = MinMaxScaler(feature_range=(1, 2))\
		# 			.fit_transform(ts_vect.reshape(-1, 1))[:, 0]
		ts_scaled = ts_vect

		score = np.zeros_like(ts_scaled)

		ts_size = ts_scaled.size

		end_p = ts_size - self.win_len - self.hankel_order - self.test_lag + 1

		for tid in range(1, end_p):
			## get base Hankel matrix
			base_id = tid -1
			hankel_base = _create_hankel(ts_scaled, 
									self.win_len, 
									self.hankel_order,
									base_id)

			## get test Hankel matrix
			test_id = tid + self.test_lag -1
			hankel_test = _create_hankel(ts_scaled, 
									self.win_len,
									self.hankel_order,
									test_id)
			
			## get score id
			score_id = tid + self.test_lag + self.win_len + self.hankel_order -1
			# score[score_id] = _score_svd(hankel_base, hankel_test, self.n_eofs)
			score[score_id] = _Edist_svd(hankel_base, hankel_test, self.n_eofs)
		return score

	def Sn_ssa(self, ssa_score):
		'''
		S : (list)
			Calculate list of normalized sum of squired distances S.
		'''
		## S is used to save the normalized sum of squired Euclidean distances Dn
		S = np.zeros_like(ssa_score)

		ts_size = ssa_score.size

		end_p = ts_size - self.win_len - self.hankel_order - self.test_lag + 1

		M = self.win_len
		Q = self.hankel_order

		for tid in range(1, end_p):
			## set start and end id of D
			start_id = tid + self.test_lag + self.hankel_order-1
			end_id = tid + self.win_len + self.test_lag + self.hankel_order-1

			## set start id of D
			S_id = tid + self.test_lag + self.win_len + self.hankel_order-1

			## calculate mu of D
			# mu_D = np.mean(ssa_score[tid-1:tid+self.win_len+self.hankel_order-1])
			mu_start = self.win_len + self.test_lag + self.hankel_order 
			mu_end = mu_start + Q
			mu_D = np.sum(ssa_score[mu_start:mu_end])/Q
			# print(mu_D)

			## the sum of squired distances is normalized to the number of elements in the test matrix  
			norm_D = np.sum(ssa_score[start_id:end_id])/(M*Q)

			## calculate normalized sum of squired distances S
			if(mu_D!=0):
				Sn = norm_D/mu_D
			else:
				Sn = norm_D

			S[S_id] = Sn

		return S

	def Wn_CUSUM(self, ssa_Sn):
		'''
		W : (list)
			Calculate CUSUM W of ssa_Sn.
		'''
		## W is used to save the cumulative sum of S 
		W = np.zeros_like(ssa_Sn)

		ts_size = ssa_Sn.size
		M = self.win_len
		Q = self.hankel_order

		## calculate CUSUM W
		W[0] = ssa_Sn[0]
		for tid in range(1, ts_size):
				temp_W = (W[tid-1] + ssa_Sn[tid]-ssa_Sn[tid-1]-1/(3*M*Q))
				W[tid] = max(0, temp_W)
		
		## calculate decision threshold
		# t_alpha = 1.6973	## alpha = 0.05, n=30
		t_alpha = 1.6839	## alpha = 0.05, n=40
		h = (2*t_alpha/(M*Q)) * math.sqrt((Q/3)*(3*M*Q-Q*Q+1))

		return W, h

	@staticmethod
	def create_hankel(ts_vect, win_length, hankel_order, start_id):
		'''Create Hankel matrix.
		input
			ts_vect : 		full time series vector
			win_length:		window length of Hankel matrix
			hankel_order : 	order of Hankel matrix
			start_id : 		start index of ts_vect
		returns
			X:				2d array shape (win_len, hankel_order)
		'''
		end_id = start_id + hankel_order
		X = np.empty((win_length, hankel_order))
		for i in range(hankel_order):
		    X[:, i] = ts_vect[(start_id + i):(start_id + i + win_length)]
		return X
	
	@staticmethod
	def sigma_svd(hankel_matrix, n_eofs):
		_, sigma, _ = np.linalg.svd(hankel_matrix, full_matrices=False)
		return sigma[:n_eofs] 


