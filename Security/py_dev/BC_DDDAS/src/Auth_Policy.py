#!/usr/bin/env python3.5

'''
========================
Authentiation Policy module
========================
Created on September.16, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide identity authentication policy for DDDAS and SSA using Blockchain
'''

import time
from utilities import DatetimeUtil, TypesUtil, FileUtil
from wrapper_pyca import Crypto_Hash
from AuthToken import AuthToken


#global variable
http_provider = 'http://localhost:8042'
contract_addr = '0x7d2a0199bc5ce701f21c94f8b80219bbfe33258e'
contract_config = '../Contracts/build/contracts/AuthToken.json'

#new AuthToken object
myAuthToken=AuthToken(http_provider, contract_addr, contract_config)


'''
Identity authentication policy management
'''
class AuthPolicy(object):

	# get token data from smart contract, return json fromat
	@staticmethod
	def get_VTrustZone(str_VZoneID):
		token_data=myAuthToken.getVTrustZone(str_VZoneID);
		json_token={}

		#Add status information
		json_token['id'] = str_VZoneID
		json_token['master'] = token_data

		return json_token

	# get Vnode information from smart contract, return json fromat
	@staticmethod
	def get_VNodeInfo(addr_node):
		token_data=myAuthToken.getNode(addr_node);
		json_token={}

		#Add status information
		json_token['Node_type'] = token_data[0]
		json_token['VZoneID'] = token_data[1]

		return json_token


	# verify authToken by comparing Vzone data in smart contract.
	@staticmethod
	def verify_AuthToken(addr_client):
		# Define ls_time_exec to save executing time to log
		ls_time_exec=[]

		# get host Vnode data
		accounts = myAuthToken.getAccounts()
		json_VNode_host = AuthPolicy.get_VNodeInfo(accounts[0])

		# mark the start time
		start_time=time.time()

		#1) read data in contract\
		json_VNode_client=AuthPolicy.get_VNodeInfo(addr_client);
		#print(json_VNode_host)
		#print(json_VNode_client)

		#2) authicate identity based on token
		# compare 
		ret_indexAuth = (json_VNode_host['VZoneID']==json_VNode_client['VZoneID'])

		# calculate computational cost
		exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of identity authentication is:%2.6f" %(exec_time))

		#transfer list to string
		str_time_exec=" ".join(ls_time_exec)
		print(str_time_exec)
		#FileUtil.AddLine('exec_time_server.log', str_time_exec)

		#return index authentication result
		return ret_indexAuth



def test_pyca():
	# transfer string data to bytes block
	bytes_block=TypesUtil.string_to_bytes('RF1');

	hash_value=Crypto_Hash.generate_hash(bytes_block)
	#print(hash_value)
	print(Crypto_Hash.verify_hash(hash_value, b'RF1'))
	pass

def test_Auth():
	
	#1) read token data
	VZoneID = 'NA1'
	#VZone = AuthPolicy.get_VTrustZone(VZoneID)
	#print(VZone)

	node1_address = myAuthToken.getAddress('sam_miner_ubuntu_0', '../Contracts/test/addr_list.json')
	node2_address = myAuthToken.getAddress('RPi2_node_0', '../Contracts/test/addr_list.json')
	VNode1 = AuthPolicy.get_VNodeInfo(node1_address)
	VNode2 = AuthPolicy.get_VNodeInfo(node2_address)
	#print(VNode1)
	#print(VNode2)
	
	print(AuthPolicy.verify_AuthToken(node1_address))
	
	
if __name__ == "__main__":
	test_Auth()
	#test_pyca()
	pass
