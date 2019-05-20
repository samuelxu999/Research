'''
========================
Crypto_RSA module
========================
Created on May.19, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide RSA cryptography function based on pyca API.
@Reference:https://cryptography.io/en/latest/
'''

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, BestAvailableEncryption
from cryptography.hazmat.primitives import serialization

class Crypto_RSA(object): 
	'''
	Generate key pairs as json fromat
		@in: key_size
		@out: key_pairs={'private_key':x,'public_key':{'y':y,'p':p,'q':q,'g':g}}
	'''
	@staticmethod
	def generate_key_numbers(public_exponent=65537, key_size=1024):
		#define key_pairs dictionary
		key_numbers={}

		#generate private key
		private_key = rsa.generate_private_key(public_exponent, key_size, backend=default_backend())
		# genereate key pairs numbers
		private_numbers = private_key.private_numbers()
		public_key = private_key.public_key()
		public_numbers = public_key.public_numbers()

		#add private key value - x
		key_numbers['n']=public_numbers.n
		key_numbers['e']=public_numbers.e
		key_numbers['d']=private_numbers.d
		key_numbers['key_size']=private_key.key_size

		return key_numbers

	'''
	Get public key object given public key numbers
		@in: public_key_numbers={'public_key':{'n':n,'e':e,}}
		@out: public_key object
	'''
	@staticmethod
	def get_public_key(n, e):
		
		#construct public key based on public_key_numbers
		public_key = rsa.RSAPublicNumbers(e,n).public_key(default_backend())
		#print(publick_number)
		return public_key

	'''
	Get private key object given private key numbers
		@in: key_numbers={'n':n, 'e':e,'d':d,} 
		@out: private_key object
	'''	
	@staticmethod
	def get_private_key(n,e,d):
		#reconstruct private key
		p, q = rsa.rsa_recover_prime_factors(n, e, d)
		iqmp = rsa.rsa_crt_iqmp(p, q)
		dmp1 = rsa.rsa_crt_dmp1(d, p)
		dmq1 = rsa.rsa_crt_dmq1(d, q)

		#call RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, public_numbers)
		private_numbers = rsa.RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, rsa.RSAPublicNumbers(e,n))
		# get private key object
		private_key=private_numbers.private_key(default_backend())
		
		return private_key


	'''
	Generate public key bytes
		@in: public_key object
		@out: public_key_bytes
	'''		
	@staticmethod
	def get_public_key_bytes(public_key):
		public_key_bytes=public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
		return public_key_bytes

	'''
	Generate private key bytes
		@in: private_key object
		@in: encryp_pw- password for encryption private_key_bytes
		@out: private_key_bytes
	'''		
	@staticmethod
	def get_private_key_bytes(private_key, encryp_pw='rootpasswd'):
		private_key_bytes=private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, 
													BestAvailableEncryption(encryp_pw.encode(encoding='UTF-8')))
		return private_key_bytes

	'''
	Generate public_key object by loading public key bytes, Encoding.PEM
		@in: public_key_bytes 
		@out: public_key object
	'''	
	@staticmethod
	def load_public_key(public_key_bytes):
		public_key=serialization.load_pem_public_key(public_key_bytes, default_backend())
		return public_key

	'''
	Generate private_key object by loading public key bytes, Encoding.PEM
		@in: private_key_bytes 
		@in: encryp_pw- password for decryption private_key_bytes
		@out: private_key object
	'''		
	@staticmethod
	def load_private_key(private_key_bytes, encryp_pw='rootpasswd', encoding=Encoding.PEM):
		private_key=serialization.load_pem_private_key(private_key_bytes, encryp_pw.encode(encoding='UTF-8'), default_backend())
		return private_key


	'''
	Save key bytes data in key_file
		@in: key_bytes 
		@in: key_file
	'''	
	@staticmethod
	def save_key_bytes(key_bytes, key_file):
		fname=open(key_file, 'w') 
		fname.write("%s" %(key_bytes.decode(encoding='UTF-8')))
		fname.close()

	'''
	Load key bytes data from key_file 
		@in: key_file
		@out: key_bytes
	'''		
	@staticmethod
	def load_key_bytes(key_file):
		fname=open(key_file, 'r') 
		key_bytes=fname.read().encode(encoding='UTF-8')
		fname.close()
		return key_bytes

if __name__ == "__main__":
	#test_func()
	#test_ecc()
	#test_DSA()
	keys_numbers = Crypto_RSA.generate_key_numbers()
	#print(keys_numbers)

	publick_key = Crypto_RSA.get_public_key(keys_numbers['n'], keys_numbers['e'])
	#print(publick_key.public_numbers())

	private_key = Crypto_RSA.get_private_key(keys_numbers['n'], keys_numbers['e'], keys_numbers['d'])
	#print(private_key.private_numbers().d)

	public_key_bytes = Crypto_RSA.get_public_key_bytes(publick_key)
	#print(public_key_bytes)

	private_key_bytes = Crypto_RSA.get_private_key_bytes(private_key, 'samuelxu999')
	#print(private_key_bytes)

	load_publick_key = Crypto_RSA.load_public_key(public_key_bytes)
	#print(load_publick_key.public_numbers())

	load_private_key = Crypto_RSA.load_private_key(private_key_bytes, 'samuelxu999')
	#print(load_private_key.private_numbers().d)

	Crypto_RSA.save_key_bytes(public_key_bytes, 'public_key_file')
	Crypto_RSA.save_key_bytes(private_key_bytes, 'private_key_file')
	
	load_public_key_bytes = Crypto_RSA.load_key_bytes('public_key_file')
	load_private_key_bytes = Crypto_RSA.load_key_bytes('private_key_file')

	reload_publick_key = Crypto_RSA.load_public_key(load_public_key_bytes)
	print(reload_publick_key.public_numbers())

	reload_private_key = Crypto_RSA.load_private_key(load_private_key_bytes, 'samuelxu999')
	print(reload_private_key.private_numbers().d)

	pass