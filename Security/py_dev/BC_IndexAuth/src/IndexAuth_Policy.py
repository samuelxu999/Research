#!/usr/bin/env python3.5

'''
========================
Index Authentiation Policy module
========================
Created on July.2, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide index authentication policy for Event-Oriented Surveillance Video Query using Blockchain
'''

from utilities import DatetimeUtil, TypesUtil, FileUtil
from wrapper_pyca import Crypto_Hash

'''
Get all dataset
'''
def test_func():
	# transfer string data to bytes block
	bytes_block=TypesUtil.string_to_bytes('samuel');

	hash_value=Crypto_Hash.generate_hash(bytes_block)
	print(Crypto_Hash.verify_hash(hash_value, b'samuelx'))
	pass
	
	
if __name__ == "__main__":
	test_func()
	pass
