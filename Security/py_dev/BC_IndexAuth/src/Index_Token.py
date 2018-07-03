#!/usr/bin/env python3.5

'''
========================
Index token module
========================
Created on July.02, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of web3.py API to interact with IndexToken.sol smart contract.
'''

from web3 import Web3, HTTPProvider, IPCProvider
from utilities import DatetimeUtil, TypesUtil
import json, datetime, time

class IndexToken(object):
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

	#get token data by call getIndexToken()
	def getIndexToken(self, str_index):

		token_data = []
		'''
		Call a contract function, executing the transaction locally using the eth_call API. 
		This will not create a new public transaction.
		'''

		# get token status
		token_data=self.contract.call({'from': self.web3.eth.coinbase}).getIndexToken(str_index)

		return token_data

	#get token data by call getIndexToken()
	def getAuthorizedNodes(self):

		node_data = []
		'''
		Call a contract function, executing the transaction locally using the eth_call API. 
		This will not create a new public transaction.
		'''

		# get token status
		node_data=self.contract.call({'from': self.web3.eth.coinbase}).getAuthorizedNodes()

		return node_data

	#initialized token by sending transact to call initIndexToken()
	def initIndexToken(self, str_index):

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).initIndexToken(self.web3.eth.coinbase, str_index)

	# set isValid flag in token
	def setIndexToken(self, str_index, hash_index):

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setIndexToken(self.web3.eth.coinbase, str_index, hash_index)

	# set authorizaed nodes
	def addAuthorizedNodes(self, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)
		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).addAuthorizedNodes(checksumAddr)

	# remove authorizaed nodes
	def removeAuthorizedNodes(self, node_addr):
		checksumAddr=Web3.toChecksumAddress(node_addr)
		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).removeAuthorizedNodes(checksumAddr)

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
	contract_addr = '0xb7e549d21afa4c6fc672a37ef00bfab0ca6d81a8'
	contract_config = '../IndexAuthContract/build/contracts/IndexToken.json'

	#Get account address
	accountAddr=IndexToken.getAddress('sam_miner_win7_0', '../IndexAuthContract/test/addr_list.json')
	print("Account: " + accountAddr)
	#new ABACToken object
	mytoken=IndexToken(http_provider, contract_addr, contract_config)
	#mytoken.Show_ContractInfo()


	#------------------------- test contract API ---------------------------------
	#getAccounts
	accounts = mytoken.getAccounts()
	balance = mytoken.getBalance('0x950d8eb4825c597534027638c862496ea0d7cf43')
	print(accounts)
	print(balance)

	#Read token data using call
	token_data=mytoken.getIndexToken('1')
	IndexToken.print_tokendata(token_data)

	#read node data using call
	token_data=mytoken.getAuthorizedNodes()
	print(token_data)

	#Send transact
	#mytoken.initIndexToken('1');
	#mytoken.setIndexToken('1', 'dave')

	node_address = IndexToken.getAddress('sam_miner_ubuntu_0', '../IndexAuthContract/test/addr_list.json')
	#mytoken.addAuthorizedNodes(node_address)
	#mytoken.removeAuthorizedNodes(node_address)

	pass