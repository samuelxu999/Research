#!/usr/bin/env python3.5

'''
========================
Authentication token module
========================
Created on September.15, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of web3.py API to interact with AuthToken.sol smart contract.
'''

from web3 import Web3, HTTPProvider, IPCProvider
from utilities import DatetimeUtil, TypesUtil
import json, datetime, time

class AuthToken(object):
	def __init__(self, http_provider, contract_addr, contract_config):
		# configuration initialization
		self.web3 = Web3(HTTPProvider(http_provider))
		self.contract_address=Web3.toChecksumAddress(contract_addr)
		self.contract_config = json.load(open(contract_config))

		# new contract object
		self.contract=self.web3.eth.contract()
		self.contract.address=self.contract_address
		self.contract.abi=self.contract_config['abi']

	def Show_ContractInfo(self):  
		print(self.web3.eth.blockNumber)
		print(self.web3.eth.accounts)
		print(self.web3.fromWei(self.web3.eth.getBalance(self.web3.eth.accounts[0]), 'ether'))

		print(self.contract.address)

	# return accounts address
	def getAccounts(self):
		return self.web3.eth.accounts

	# return accounts balance
	def getBalance(self, account_addr=''):
		if(account_addr==''):
			# get accounts[0] balance
			checksumAddr=self.web3.eth.coinbase
		else:
			#Change account address to EIP checksum format
			checksumAddr=Web3.toChecksumAddress(account_addr)	
		return self.web3.fromWei(self.web3.eth.getBalance(checksumAddr), 'ether')

	#get ValidMaster data by call getValidMaster()
	def getValidMaster(self):

		ValidMaster_data = []
		'''
		Call a contract function, executing the transaction locally using the eth_call API. 
		This will not create a new public transaction.
		'''

		# get token status
		ValidMaster_data = self.contract.call({'from': self.web3.eth.coinbase}).getValidMaster()

		return ValidMaster_data

	#get VZone data by call getVTrustZone()
	def getVTrustZone(self, str_VzoneID):

		Vzone_data = []
		'''
		Call a contract function, executing the transaction locally using the eth_call API. 
		This will not create a new public transaction.
		'''

		# get token status
		Vzone_data = self.contract.call({'from': self.web3.eth.coinbase}).getVTrustZone(str_VzoneID)

		return Vzone_data

	#get Vnode data by call getNode()
	def getNode(self, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)
		node_data = []
		'''
		Call a contract function, executing the transaction locally using the eth_call API. 
		This will not create a new public transaction.
		'''

		# get token status
		node_data=self.contract.call({'from': self.web3.eth.coinbase}).getNode(checksumAddr)

		return node_data

	#initialized VZone data by sending transact to call initVTrustZone()
	def initVTrustZone(self, str_VzoneID):

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).initVTrustZone(self.web3.eth.coinbase, str_VzoneID)


	# Add master node to ValidMaster
	def addMasterNode(self, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)
		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).addMasterNode(checksumAddr)

	# remove master node from ValidMaster
	def removeMasterNode(self, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)
		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).removeMasterNode(checksumAddr)

	# Create VZone data by sending transact to call createVZone()
	def createVZone(self, str_VzoneID):

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).createVZone(str_VzoneID)

	# Create VZone data by sending transact to call changeVZoneMaster()
	def changeVZoneMaster(self, str_VzoneID, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)
		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).changeVZoneMaster(str_VzoneID, checksumAddr)

	# Remove VZone data by sending transact to call removeVZone()
	def removeVZone(self, str_VzoneID):

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).removeVZone(str_VzoneID)

	# Join VZone by sending transact to call joinVZone()
	def joinVZone(self, str_VzoneID, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).joinVZone(str_VzoneID, checksumAddr)

	# Remove VZone data by sending transact to call leaveVZone()
	def leaveVZone(self, str_VzoneID, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).leaveVZone(str_VzoneID, checksumAddr)

	# Print token date
	@staticmethod
	def print_tokendata(token_data):
		#print token status
		for i in range(0,len(token_data)):
				print(token_data[i])


	# get address from json file
	@staticmethod
	def getAddress(node_name, datafile):
		address_json = json.load(open(datafile))
		return address_json[node_name]


if __name__ == "__main__":
	http_provider = 'http://localhost:8042'
	contract_addr = '0x7d2a0199bc5ce701f21c94f8b80219bbfe33258e'
	contract_config = '../Contracts/build/contracts/AuthToken.json'

	#new ABACToken object
	myAuthToken=AuthToken(http_provider, contract_addr, contract_config)
	#mytoken.Show_ContractInfo()


	#------------------------- test contract API ---------------------------------
	#getAccounts
	accounts = myAuthToken.getAccounts()
	balance = myAuthToken.getBalance(accounts[0])
	print("Host accounts: %s" %(accounts))
	print("coinbase balance:%d" %(balance))
	print("--------------------------------------------------------------------")

	#------------------------------ call functions test -------------------------
	#Read valid master data using call
	token_data=myAuthToken.getValidMaster()
	AuthToken.print_tokendata(token_data)
	print("--------------------------------------------------------------------")

	#read Vzone data using call
	VZone_ID = 'AF1'
	token_data=myAuthToken.getVTrustZone(VZone_ID)
	print(token_data)
	print("--------------------------------------------------------------------")

	#read Vnode data using call
	node_address = AuthToken.getAddress('sam_miner_ubuntu_0', '../Contracts/test/addr_list.json')
	token_data=myAuthToken.getNode(node_address)
	#token_data=myAuthToken.getNode(accounts[0])
	print(token_data)
	print("--------------------------------------------------------------------")

	#---------------------------------- Send transact test ----------------------
	#myAuthToken.initVTrustZone(VZone_ID);

	node_address = AuthToken.getAddress('RPi1_node_0', '../Contracts/test/addr_list.json')
	#myAuthToken.addMasterNode(node_address)
	#myAuthToken.removeMasterNode(node_address)

	
	#myAuthToken.createVZone(VZone_ID)
	#myAuthToken.changeVZoneMaster(VZone_ID, node_address)
	#myAuthToken.removeVZone(VZone_ID)

	node_address = AuthToken.getAddress('RPi2_node_0', '../Contracts/test/addr_list.json')
	#myAuthToken.joinVZone(VZone_ID, node_address)
	#myAuthToken.leaveVZone(VZone_ID, node_address)

	pass