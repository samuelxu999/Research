'''
========================
efficient_vdf module
========================
Created on Feb.6, 2022
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide efficient verifiable delay function implementation.
@Reference: Efficient Verifiable Delay Functions (By Wesolowski)
			C++ prototype: https://github.com/iotaledger/vdf/tree/master/src

'''
import os
import time
import hashlib
import gmpy2
from gmpy2 import mpz

'''
======================== Internal functions ========================
'''
## integer to hex
def int_to_hex(int_data):
	return hex(int_data)
	
## hex to integer
def hex_to_int(hex_data):
	return int(hex_data, 16)

## hash function with 2*k length:
def hash_message(hex_message, _k):
	if(_k==128):
		hash_hex = hashlib.sha256(hex_message.encode('utf-8')).hexdigest()
	else:
		hash_hex = hashlib.sha1(hex_message.encode('utf-8')).hexdigest()
	
	return hash_hex

'''
======================= Efficient VDF class ========================
'''
class E_VDF(object):
	def __init__(self, seed_type=0):
		'''
		Initialize parameters
		@Input
		seed_type:	seed generaton method.
		'''

		if(seed_type ==1):
			## 1) use random number as seed
			r_seed = int(os.urandom(32).hex(), 16)
		else:
			## 2) use hash of random_state as seed
			r_seed = hash(gmpy2.random_state())

		## set random state
		self.r_state = gmpy2.random_state(r_seed)

	@staticmethod
	def generate_prime(r_state, bitLen):
		'''
		generate a random prime number
		@Input
			r_state: 	generate by gmpy2.random_state(r_seed)
		    bitLen: 	bit length of the prime number
		@Output
		    mpz_prime: 	an uniformly distributed random integer between 0 and 2**bitLen - 1

		'''
		## generate a random number
		mpz_random = gmpy2.mpz_urandomb(r_state, bitLen)	

		## get prime bumber that close to mpz_random
		mpz_prime = gmpy2.next_prime(mpz_random)
	
		## return prime number.
		return mpz_prime

	def hash_prime(self, mpz_prime):
		'''
		generate a next_prime given the output of H(current_prime)
		@Input
		    mpz_prime: current mpz_prime used to calculate hash_prime
		@Output
		    next_mpz_prime (l): the closet prime number to H(mpz_prime)
		'''

		## 1) convert mpz_prime to hex format
		hex_mpz_prime = int_to_hex(mpz_prime)

		## 2) get hex format hash value that is output of H(mpz_prime)
		hash_data = hash_message(hex_mpz_prime, self._k)

		## 3) convert hash_data to mpz format
		hash_mpz_prime = mpz(hex_to_int(hash_data))
		
		## 4) get next prime that is closed to hash_mpz_prime
		next_mpz_prime = gmpy2.next_prime(hash_mpz_prime)
		return next_mpz_prime

	def set_up(self, _lambda, _k,):
		'''
		VDF setup procedure to configurate parameters
		@Input
			_lambda:	This is used to generate RSA prime N with ength p_lambda/2
			_k:			Security parameter _k defines length of hash string l.
		'''
		## set security parameters
		self._lambda = _lambda
		self._k = _k

		## create big prime N
		self.p = E_VDF.generate_prime(self.r_state, int(self._lambda/2))
		self.q = E_VDF.generate_prime(self.r_state, int(self._lambda/2))

		mpz_N = gmpy2.mul(self.p, self.q)
		# self.phi_N = gmpy2.mul(self.p-1, self.q-1)

		return mpz_N

	def evaluate_proof(self, _message, _tau ,_N):
		'''
		VDF evaluation to solve challenge and calculate proof pairs for verification
		@Input
			_message:		data (x) that is used to feed evaluatation
			_tau:			challenge (task difficuly) that requires y=x^(2**tau) mod N
			_N:				modulus N
		@Output
			proof_pair:		Return [pi, l]	
		'''
		## ---------------------- evaluation -----------------------------
		## 1) perform H(m)
		hash_m = hash_message(_message, self._k)
		x = hex_to_int(hash_m)

		## 2) calculate 2^tau
		exp_tau = pow(2, _tau)

		## 3) calculate y=x^(2**t) mod N
		y = gmpy2.powmod(x, exp_tau, _N)

		## ---------------------------- proof -----------------------------
		## 1) calculate  l= H_prime(x+y)		
		l = self.hash_prime(gmpy2.add(x,y))

		## 2) calculate floor(2^tau/l)
		exp_tau_div = gmpy2.f_div(exp_tau,l)

		## 3) calculate pi=x^exp_tau_div mod N
		pi = gmpy2.powmod(x, exp_tau_div, _N)

		## return proof pair
		proof_pair=[pi,l]
		return proof_pair

	def verify_proof(self, _message, _tau ,_N, proof_pair):
		'''
		VDF verification to check if proof is correct
		@Input
			_message:		data (x) that is used to feed evaluatation
			_tau:			challenge (task difficuly) that requires y=x^2**t mod N
			_N:				modulus N
			proof_pair:		[pi, l]
		@Output
			verify_ret:		Return true or false	
		'''
		pi = proof_pair[0]
		l = proof_pair[1]

		## 1) perform H(m)
		hash_m = hash_message(_message, self._k)
		x = hex_to_int(hash_m)

		## 2) calculate 2^tau mod l
		r = gmpy2.powmod(2, _tau, l)

		## 3) use proof pair to calculate y 
		## optimized method: y=((pi^l mod N) * (x^r mod N)) mod N
		pi_l_mod = gmpy2.powmod(pi, l, _N)
		pi_x_r = gmpy2.powmod(x, r, _N)
		y = gmpy2.mul(pi_l_mod, pi_x_r) % _N

		## 4) calculate l_verify = H_prime(x+y)
		l_verify = self.hash_prime(gmpy2.add(x,y))

		## 5) return verify result
		return l==l_verify
