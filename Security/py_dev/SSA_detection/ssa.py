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
import numpy as np
from sklearn.preprocessing import MinMaxScaler


logger = logging.getLogger(__name__)

def _create_hankel(ts_vect, win_length, hankel_order, start_id):
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

def _spd_svd(hankel_base, hankel_test, n_eofs):
	'''
	Run svd algorithm for single point detection
	'''
	U_base, _, _ = np.linalg.svd(hankel_base, full_matrices=False)
	U_test, _, _ = np.linalg.svd(hankel_test, full_matrices=False)
	_, s, _ = np.linalg.svd(U_test[:, :n_eofs].T @
	    U_base[:, :n_eofs], full_matrices=False)
	return 1 - s[0]


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
	        interval between base matrix and test matrix (l).      
		'''
		self.win_len = win_len
		self.n_eofs = n_eofs
		self.hankel_order = hankel_order
		self.test_lag = test_lag

	def score_ssa(self, ts_vect):
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
			# logger.info(tid + self.win_len + self.hankel_order + self.test_lag )

			# get Hankel matrix
			base_id = tid
			X_base = _create_hankel(ts_scaled, 
									self.win_len, 
									self.hankel_order,
									base_id)

			test_id = tid + self.test_lag
			X_test = _create_hankel(ts_scaled, 
									self.win_len,
									self.hankel_order,
									test_id)
			
			score_id = tid + self.test_lag + self.hankel_order
			score[score_id-1] = _spd_svd(X_base, X_test, self.n_eofs)
		return score

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


	# @staticmethod
	# def reconstruct(hankel_matrix, n_eofs):
	# 	U_vect, sigma, V_vect = np.linalg.svd(hankel_matrix, full_matrices=False)
	# 	vect_restruct = (U_vect[:,0:n_eofs]).dot(np.diag(sigma[0:n_eofs])).dot(V_vect[0:n_eofs,:])
	# 	return vect_restruct

