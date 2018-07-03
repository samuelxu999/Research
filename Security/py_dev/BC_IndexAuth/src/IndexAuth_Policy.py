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
from Index_Token import IndexToken


#global variable
http_provider = 'http://localhost:8042'
contract_addr = '0xb71e920f014cddc0064ed166e10a0126ef76f537'
contract_config = '../IndexAuthContract/build/contracts/IndexToken.json'

#new CapACToken object
mytoken=IndexToken(http_provider, contract_addr, contract_config)


'''
Index authentication policy management
'''
class IndexPolicy(object):

	# get token data from smart contract, return json fromat
	@staticmethod
	def get_indexToken(str_index):
		token_data=mytoken.getIndexToken(str_index);
		json_token={}

		#Add status information
		json_token['id'] = token_data[0]
		json_token['HashValue'] = token_data[1]

		return json_token

def test_pyca():
	# transfer string data to bytes block
	bytes_block=TypesUtil.string_to_bytes('samuel');

	hash_value=Crypto_Hash.generate_hash(bytes_block)
	print(Crypto_Hash.verify_hash(hash_value, b'samuelx'))
	pass
	
	
if __name__ == "__main__":
	#set sample record 
	record_block={}
	record_block['id']='1'
	record_block['value']='samuelxu'

	#1) read token data
	token_data=mytoken.getIndexToken(record_block['id']);
	print(token_data)

	#2) get hash value for index
	# transfer string data to bytes block
	bytes_block = TypesUtil.string_to_bytes(record_block['value']);

	hash_value = Crypto_Hash.generate_hash(bytes_block)
	#hash_str = TypesUtil.bytes_to_string(hash_value)
	print(hash_value)
	#print(hash_str)
	print(token_data[1])

	print(str(hash_value)==token_data[1])

	#3) set index token
	#mytoken.setIndexToken(record_block['id'], hash_str);

	#verify hash
	#hash_token = token_data[1]
	#print(Crypto_Hash.verify_hash(hash_value, bytes_block))

	#json_token = IndexPolicy.get_indexToken('1');
	#print(json_token)
	pass
