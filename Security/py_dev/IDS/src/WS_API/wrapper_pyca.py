'''
========================
Wrapper_pyca module
========================
Created on Nov.7, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide cryptography function based on pyca API.
@Reference:https://cryptography.io/en/latest/
'''

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, dsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, BestAvailableEncryption
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

class Crypto_DSA(object):
	'''
	Generate key pairs as json fromat
		@in: key_size
		@out: key_pairs={'private_key':x,'public_key':{'y':y,'p':p,'q':q,'g':g}}
	'''
	@staticmethod
	def generate_key_pairs(key_size=1024):
		#define key_pairs dictionary
		key_pairs={}
		
		#generate private key
		private_key = dsa.generate_private_key(key_size=key_size, backend=default_backend())
		private_number=private_key.private_numbers()
		
		#add private key value - x
		key_pairs['private_key']=private_number.x
		
		#get private key from private_key
		public_key = private_key.public_key()
		
		#get public number
		public_numbers=public_key.public_numbers()		
		y=public_numbers.y
		p=public_numbers.parameter_numbers.p
		q=public_numbers.parameter_numbers.q
		g=public_numbers.parameter_numbers.g
		
		#add public_key_numbers value - y, p, q, g
		public_keys_numbers={'y':y, 'p':p, 'q':q, 'g':g}
		key_pairs['public_key']=public_keys_numbers
		
		return key_pairs
	
	'''
	Display out key pairs data on screen
		@in: key_pairs={'private_key':x,'public_key':{'y':y,'p':p,'q':q,'g':g}}
		@out: print out key pairs data on screen
	'''
	@staticmethod
	def display_key_pairs(key_pairs):
		print("private key value x:%d" %(key_pairs['private_key']))
		
		public_keys_numbers=key_pairs['public_key']
		
		print("public key value y:%d" %(public_keys_numbers['y']))
		print("public key value p:%d" %(public_keys_numbers['p']))
		print("public key value q:%d" %(public_keys_numbers['q']))
		print("public key value g:%d" %(public_keys_numbers['g']))
	
	'''
	Get public key object given public key numbers
		@in: public_key_numbers={'public_key':{'y':y,'p':p,'q':q,'g':g}}
		@out: public_key object
	'''
	@staticmethod
	def get_public_key(public_key_numbers):
		y=public_key_numbers['y']
		p=public_key_numbers['p']
		q=public_key_numbers['q']
		g=public_key_numbers['g']
		
		#construct public key based on public_key_numbers
		parameter_numbers=dsa.DSAParameterNumbers(p,q,g)
		publick_number=dsa.DSAPublicNumbers(y,parameter_numbers)			
		public_key=publick_number.public_key(default_backend())
		#print(publick_number)
		return public_key

	'''
	Get private key object given private key numbers
		@in: private_key_numbers={'publicprivate_key':x}
		@in: public_key_numbers={'public_key':{'y':y,'p':p,'q':q,'g':g}}
		@out: private_key object
	'''	
	@staticmethod
	def get_private_key(x, public_key_numbers):
		#reconstruct private key
		private_numbers=dsa.DSAPrivateNumbers(x, public_key_numbers)
			
		#construct private_key based on private_numbers
		private_key=private_numbers.private_key(default_backend())
		
		return private_key

	'''
	Generate signature by signing data
		@in: private_key object
		@in: sign_data
		@out: signature
	'''	
	@staticmethod
	def sign(private_key, sign_data):
		signature=private_key.sign(sign_data,hashes.SHA256())
		return signature

	'''
	Verify signature by using public_key
		@in: public_key object
		@in: signature
		@in: sign_data
		@out: True or False
	'''		
	@staticmethod
	def verify(public_key, signature, sign_data):
		try:
			public_key.verify(signature, sign_data, hashes.SHA256())
		except InvalidSignature: 
			return False
		except:
			return False
		return True

	'''
	Generate public key bytes
		@in: public_key object
		@in: encoding- Encoding.PEM or Encoding.DER
		@out: public_key_bytes
	'''		
	@staticmethod
	def get_public_key_bytes(public_key, encoding=Encoding.PEM):
		public_key_bytes=public_key.public_bytes(encoding, PublicFormat.SubjectPublicKeyInfo)
		return public_key_bytes

	'''
	Generate public_key object by loading public key bytes
		@in: public_key_bytes 
		@in: encoding- Encoding.PEM or Encoding.DER
		@out: public_key object
	'''	
	@staticmethod
	def load_public_key_bytes(public_key_bytes,encoding=Encoding.PEM):
		if(encoding==Encoding.PEM):
			public_key=serialization.load_pem_public_key(public_key_bytes, default_backend())
		elif(encoding==Encoding.DER):
			public_key=serialization.load_der_public_key(public_key_bytes, default_backend())
		else:
			public_key=''
		return public_key

	'''
	Generate private key bytes
		@in: private_key object
		@in: encryp_pw- password for encryption private_key_bytes
		@in: encoding- Encoding.PEM or Encoding.DER
		@in: private_format- PrivateFormat.PKCS8 or PrivateFormat.TraditionalOpenSSL
		@out: private_key_bytes
	'''		
	@staticmethod
	def get_private_key_bytes(private_key, encryp_pw=b'rootpasswd', encoding=Encoding.PEM, private_format=PrivateFormat.PKCS8):
		private_key_bytes=private_key.private_bytes(encoding, private_format, BestAvailableEncryption(bytes(encryp_pw)))
		return private_key_bytes

	'''
	Generate private_key object by loading public key bytes
		@in: private_key_bytes 
		@in: encryp_pw- password for encryption private_key_bytes
		@in: encoding- Encoding.PEM or Encoding.DER
		@out: private_key object
	'''		
	@staticmethod
	def load_private_key_bytes(private_key_bytes, encryp_pw=b'rootpasswd', encoding=Encoding.PEM):
		if(encoding==Encoding.PEM):
			private_key=serialization.load_pem_private_key(private_key_bytes, encryp_pw, default_backend())
		elif(encoding==Encoding.DER):
			private_key=serialization.load_der_private_key(private_key_bytes, encryp_pw, default_backend())
		else:
			private_key=''
		return private_key

	'''
	Save key bytes data in key_file
		@in: key_bytes 
		@in: key_file
	'''	
	@staticmethod
	def save_key_bytes(key_bytes, key_file):
		fname = open(key_file, 'w') 
		fname.write("%s" %(key_bytes.decode(encoding='UTF-8')))
		fname.close()

	'''
	Load key bytes data from key_file 
		@in: key_file
		@out: key_bytes
	'''		
	@staticmethod
	def load_key_bytes(key_file):
		fname = open(key_file, 'r') 
		key_bytes=fname.read().encode(encoding='UTF-8')
		fname.close()
		return key_bytes
		
'''
Get all dataset
'''
def test_func():
	key = Fernet.generate_key()
	#print(key)
	f = Fernet(key)
	token = f.encrypt(b"my deep dark secret")
	print(token)
	print(f.decrypt(token))
	pass
	
'''
Elliptic curve cryptography
'''
def test_ecc():
	try:
		#generate private key
		private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
		testdata = b"this is some data I'd like to sign"
		signature = private_key.sign(testdata, ec.ECDSA(hashes.SHA256()))
		print(signature) 
		
		#signature=b"sdsds"
		public_key = private_key.public_key()
		public_key.verify(signature, testdata, ec.ECDSA(hashes.SHA256()))
	except InvalidSignature:
		print("signaure varify failed!")
	except:
		print("unknown error!")


def test_DSA():
	key_pairs=Crypto_DSA.generate_key_pairs(1024)
	Crypto_DSA.display_key_pairs(key_pairs)
	
	public_key=Crypto_DSA.get_public_key(key_pairs['public_key'])
	public_number=public_key.public_numbers()
	print(public_number.parameter_numbers.q)
	
	private_key=Crypto_DSA.get_private_key(key_pairs['private_key'], public_number)
	private_numbers=private_key.private_numbers()	
	print(private_numbers.x)
	
	sign_data=b"This is some data I'd like to sign"
	signature=Crypto_DSA.sign(private_key, sign_data)
	print(signature)
	
	#sign_data=b"This is some data I'd like to sig"
	verify_sign=Crypto_DSA.verify(public_key,signature,sign_data)
	print(verify_sign)
	
	#get public_key_byte
	public_key_bytes=Crypto_DSA.get_public_key_bytes(public_key)
	print(public_key_bytes)
	
	#save key bytes to key_file
	Crypto_DSA.save_key_bytes(public_key_bytes, 'public_key_file')
	#load key bytes
	load_public_key_bytes=Crypto_DSA.load_key_bytes('public_key_file')
	print(load_public_key_bytes)
		
	#load public_key_byte
	load_public_key=Crypto_DSA.load_public_key_bytes(load_public_key_bytes)
	print(load_public_key.public_numbers())
	
	#export private_key_byte
	private_key_bytes=Crypto_DSA.get_private_key_bytes(private_key)
	print(private_key_bytes)
	
	#save key bytes to key_file
	Crypto_DSA.save_key_bytes(private_key_bytes, 'private_key_file')
	#load key bytes
	load_private_key_bytes=Crypto_DSA.load_key_bytes('private_key_file')
	print(load_private_key_bytes)
	
	#load private_key_byte
	load_private_key=Crypto_DSA.load_private_key_bytes(load_private_key_bytes)
	print(load_private_key.private_numbers().x)
	
	
if __name__ == "__main__":
	#test_func()
	#test_ecc()
	test_DSA()
	pass

