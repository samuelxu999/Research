#!/usr/bin/env python3.5

'''
========================
Register Token module
========================
Created on Feb.20, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of web3.py API to interact with RegisterToken.sol smart contract.
'''

from web3 import Web3, HTTPProvider, IPCProvider
from utilities import DatetimeUtil, TypesUtil
import json, datetime, time

class RegisterToken(object):
	def __init__(self, http_provider, contract_addr, contract_config):
		# configuration initialization
		self.web3 = Web3(HTTPProvider(http_provider))
		self.contract_address=Web3.toChecksumAddress(contract_addr)
		self.contract_config = json.load(open(contract_config))

		# new contract object
		self.contract=self.web3.eth.contract()
		self.contract.address=self.contract_address
		self.contract.abi=self.contract_config['abi']

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


	#get user data by call getUserInfo()
	def getUserInfo(self, addr_user):
		checksumAddr_user=Web3.toChecksumAddress(addr_user)
		user_data = []
		'''
		Call a contract function, executing the transaction locally using the eth_call API. 
		This will not create a new public transaction.
		'''

		# get token status
		user_data=self.contract.call({'from': self.web3.eth.coinbase}).getUserInfo(checksumAddr_user)

		return user_data

	#set user data by sending transact to call setUserInfo()
	def setUserInfo(self, addr_user, str_UserID, addr_Summary):
		checksumAddr_user=Web3.toChecksumAddress(addr_user)
		checksumAddr_summary=Web3.toChecksumAddress(addr_Summary)

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setUserInfo(checksumAddr_user, str_UserID, checksumAddr_summary)

	#clear user data by sending transact to call clearUserInfo()
	def clearUserInfo(self, addr_user):
		checksumAddr_user=Web3.toChecksumAddress(addr_user)

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).clearUserInfo(checksumAddr_user)


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
	contract_addr = RegisterToken.getAddress('RegisterToken', './addr_list.json')
	contract_config = '../contracts/build/contracts/RegisterToken.json'

	#new RegisterToken object
	myUserToken=RegisterToken(http_provider, contract_addr, contract_config)

	#------------------------- test contract API ---------------------------------
	#getAccounts
	accounts = myUserToken.getAccounts()
	balance = myUserToken.getBalance(accounts[0])
	print("Host accounts: %s" %(accounts))
	print("coinbase balance:%d" %(balance))
	print("--------------------------------------------------------------------")

	user_address = RegisterToken.getAddress('sam_ubuntu', '../contracts/test/addr_list.json')
	sum_address = RegisterToken.getAddress('SummaryToken', '../contracts/test/addr_list.json')

	#------------------------------ call functions test -------------------------
	#Read valid master data using call
	token_data=myUserToken.getUserInfo(user_address)
	RegisterToken.print_tokendata(token_data)
	print("--------------------------------------------------------------------")


	#---------------------------------- Send transact test ----------------------
	#myUserToken.setUserInfo(user_address, 'Samuel', sum_address)
	#myUserToken.clearUserInfo(user_address)

	
	pass