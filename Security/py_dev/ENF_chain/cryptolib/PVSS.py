'''
Created on May 25, 2019

@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: Public Verifiable Security Sharing based on Shamir's Secret Sharing Scheme
Refer to Wiki for algorithm:
https://en.wikipedia.org/wiki/Shamir's_Secret_Sharing
'''

import random
import functools
import math

# default prime number
_PRIME = 2**511 - 1


def _extended_gcd(a, b):
    '''
    division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1) this can
    be computed via extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    '''
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a%b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def _divmod(num, den, p):
    '''compute num / den modulo prime p

    To explain what this means, the return value will be such that
    the following is true: den * _divmod(num, den, p) % p == num
    '''
    inv, _ = _extended_gcd(den, p)
    return num * inv

def _eval_at(poly, x, prime):
    '''evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    '''
    accum = 0
    # calculate f(x)=(a0*x^0 + a1*x^1 + a2*x^2) mod p
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def _eval_commit_at(poly_commits, x, prime):
    '''evaluates polynomial commitmemt (coefficient tuple) at x, 
    	used to verify a commitment proof
    '''
    accum = 1
    i = 0
    # calculate Sj(x)=II (Ajk ^ x^k) mod p
    for coeff in poly_commits:
        #accum ^= x
        exp = pow(x, i, prime)
        accum *= pow(coeff, exp, prime)
        accum %= prime
        i += 1
    return accum

def _lagrange_interpolate(x, x_s, y_s, p):
    '''
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order
    '''
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"
    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum *= v
        return accum
    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p)
               for i in range(k)])
    return (_divmod(num, den, p) + p) % p

'''
    Public Verifiable Security Share Class
'''
class PVSS(object):
	@staticmethod
	def randnt(poly_max):
		# random integer generator
		RINT = functools.partial(random.SystemRandom().randint, 0)
		return  RINT(poly_max)

	@staticmethod
	def split_shares(secret_s, minimum_t, shares_n, poly_max, prime=_PRIME):
		'''
		Random generates a random shamir pool to build poly function f(x),
		returns the share that split secret s0=f(0). 
		@Input:
			secret_s: 	secret s to be shared
			poly_prime: maximum of poly parameters
		    minimum_t: 	minimal shares for s0 recover - t
		    shares_n: 	available shares count - n
		    poly_max:	maximum value of poly parameter
		    prime: 		public prime number
		@Output:
		    poly: 		poly(j), where 0<=j<t
		    points: 	shared points f(i) where 1<=i<=n
		'''
		
		if minimum_t > shares_n:
		    raise ValueError("pool secret would be irrecoverable")

		# set poly[0]=s
		poly = [secret_s]

		# random choose poly no great than poly_max
		poly += [PVSS.randnt(poly_max) for i in range(minimum_t-1)]

		# calculate poly points for each i as format (i, s(i))
		points = [(i, _eval_at(poly, i, prime))
		          for i in range(1, shares_n + 1)]

		# return s0=poly[0] and point f(i) where i>=1 and i<shares_n
		return poly, points

	@staticmethod
	def recover_secret(shares, prime=_PRIME):
	    '''
	    Recover the secret from share points
	    (x,y points on the polynomial)
	    '''
	    if len(shares) < 2:
	        raise ValueError("need at least two shares")
	    x_s, y_s = zip(*shares)
	    
	    #perform lagrange interpolat to recover s(0) 
	    return _lagrange_interpolate(0, x_s, y_s, prime)

	@staticmethod
	def get_poly_commitment(g, poly, prime=_PRIME):
		'''
		Generate the poly commitment: (i, g^poly(i) mod prime)
		'''		
		#If the message representative g is not between 0 and n - 1,
		#output "message representative out of range" and stop.
		if not (0 <= g <= prime-1):
			raise Exception("g not within 0 and prime - 1")
		# Let poly_com = g^a mod n 
		poly_com = [pow(g, ai, prime) for ai in poly]

		# output commitment.
		return poly_com

	@staticmethod
	def get_share_proofs(g, shares, prime=_PRIME):
		'''
		Generate the consistency share proof: (i, g^s(i) mod prime)
		'''
		#If the message representative g is not between 0 and n - 1,
		#output "message representative out of range" and stop.
		if not (0 <= g <= prime-1):
			raise Exception("g not within 0 and prime - 1")

		# Let poly_com = g^a mod n 
		# calculate consistency proof
		share_proofs = [(share[0], pow(g, share[1], prime)) 
						for share in shares]

		# output commitment.
		return share_proofs

	@staticmethod
	def verify_shares(poly_commits, share_proofs, prime=_PRIME):
		'''
		verify consistency share proof given poly_commits
		'''
		# calculate S(x) by uisng 
		verify_points = [(i, _eval_commit_at(poly_commits, i, prime))
		          for i in range(1, len(share_proofs) + 1)]
		return verify_points

	@staticmethod
	def verify_S(poly_commits, share_index, prime=_PRIME):
		'''
		verify single share proof given share_index and poly_commits
		'''
		return _eval_commit_at(poly_commits, share_index, prime)
