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

import time
from utilities import DatetimeUtil, TypesUtil, FileUtil
from wrapper_pyca import Crypto_Hash
from Index_Token import IndexToken


#global variable
http_provider = 'http://localhost:8042'
contract_addr = '0xb7e549d21afa4c6fc672a37ef00bfab0ca6d81a8'
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

	# verify index by comparing index data in smart contract and calculated data block.
	@staticmethod
	def verify_indexToken(str_index, filepath):
		# Define ls_time_exec to save executing time to log
		ls_time_exec=[]

		# mark the start time
		start_time=time.time()

		#1) read index data in contract
		token_data=mytoken.getIndexToken(str_index);
		#print(token_data)

		# calculate computational cost
		exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of getIndexToken is:%2.6f" %(exec_time))

		
		# mark the start time
		start_time=time.time()

		#2) extract data from index file
		indexData=IndexPolicy.ExtractData(filepath)
		str_value=str(indexData)
		# calculate computational cost
		exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of extract Index is:%2.6f" %(exec_time))


		# mark the start time
		start_time=time.time()

		#3) calculate hash value of str_value
		# transfer string data to bytes block
		bytes_block = TypesUtil.string_to_bytes(str_value);
		hash_value = Crypto_Hash.generate_hash(bytes_block)

		# compare 
		ret_indexAuth = (str(hash_value)==token_data[1])

		# calculate computational cost
		exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of verifyIndex is:%2.6f" %(exec_time))

		#transfer list to string
		str_time_exec=" ".join(ls_time_exec)
		#print(str_time_exec)
		FileUtil.AddLine('exec_time_server.log', str_time_exec)

		#return index authentication result
		return ret_indexAuth

	# extract data from index files
	@staticmethod
	def ExtractData(filepath):
		ls_lines=FileUtil.ReadLines(filepath)
		ls_record=[]
		for line in ls_lines:
			#print(line[:-1].split(';'))
			ls_record.append(line[:-1].split(';'))

		return ls_record


def test_pyca():
	# transfer string data to bytes block
	bytes_block=TypesUtil.string_to_bytes('samuel');

	hash_value=Crypto_Hash.generate_hash(bytes_block)
	print(Crypto_Hash.verify_hash(hash_value, b'samuelx'))
	pass

def test_IndexAuth():
	#set sample record 
	record_block={}
	record_block['id']='1'
	#record_block['value']='samuelxu'

	#extract data from index file
	filepath = './features/0_2_people_features/Untitled_Folder/14.46.1.txt'
	filepath0 = './features/0_2_people_features/Untitled_Folder/14.47.31.txt'
	indexData=IndexPolicy.ExtractData(filepath)
	record_block['value']=str(indexData)

	#1) read token data
	token_data=mytoken.getIndexToken(record_block['id'])
	print(token_data)

	node_data=mytoken.getAuthorizedNodes();
	print(node_data)

	json_token = IndexPolicy.get_indexToken(record_block['id'])
	print(json_token)

	#2) get hash value for index
	# transfer string data to bytes block
	bytes_block = TypesUtil.string_to_bytes(record_block['value'])

	hash_value = Crypto_Hash.generate_hash(bytes_block)
	hash_str = str(hash_value)
	'''print(hash_value)
	print(hash_str)
	print(token_data[1])'''

	#3) set index token
	#mytoken.setIndexToken(record_block['id'], hash_str);

	#4) set authrozied nodes
	node_address = IndexToken.getAddress('RPi1_node_0', '../IndexAuthContract/test/addr_list.json')
	#mytoken.addAuthorizedNodes(node_address)
	#mytoken.removeAuthorizedNodes(node_address)

	#5) verify hash
	#hash_token = token_data[1]
	#print(Crypto_Hash.verify_hash(hash_value, bytes_block))

	print(IndexPolicy.verify_indexToken(record_block['id'],filepath))
	
	
if __name__ == "__main__":
	test_IndexAuth()
	#filepath = './features/0_2_people_features/Untitled_Folder/14.46.1.txt'
	#indexData=IndexPolicy.ExtractData(filepath)
	#print(indexData)
	pass
