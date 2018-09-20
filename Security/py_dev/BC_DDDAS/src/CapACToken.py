#!/usr/bin/env python3.5

'''
========================
Authentication token module
========================
Created on September.17, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of web3.py API to interact with CapACToken.sol smart contract.
'''

from web3 import Web3, HTTPProvider, IPCProvider
from utilities import DatetimeUtil, TypesUtil
import json, datetime, time

class CapACToken(object):
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

	'''
	Call a contract function, executing the transaction locally using the eth_call API. 
	This will not create a new public transaction.
	'''
	#get token data by call getCapToken()
	def getCapTokenStatus(self, account_addr):
		#Change account address to EIP checksum format
		checksumAddr = Web3.toChecksumAddress(account_addr)

		# get token status
		tokenStatus=self.contract.call({'from': self.web3.eth.coinbase}).getCapTokenStatus(checksumAddr)
		return(tokenStatus)

	#initialized token by sending transact to call initCapToken()
	def initCapToken(self, account_addr):
		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)

		# Execute the specified function by sending a new public transaction.
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).initCapToken(checksumAddr)

	# set isValid flag in token
	def setCapToken_isValid(self, account_addr, flag_value):
		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setCapToken_isValid(checksumAddr, flag_value)

	# set issue date and expired date
	def setCapToken_expireddate(self, account_addr, issue_time, expire_time):
		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setCapToken_expireddate(checksumAddr, issue_time, expire_time)

	# set VZone master
	def assignVZoneMaster(self, account_addr):
		#Change account address to EIP checksum format
		checksumAddr = Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).assignVZoneMaster(checksumAddr)

	# revoke VZone master
	def revokeVZoneMaster(self):
		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).revokeVZoneMaster()

	# set issue date and expired date
	def setCapToken_authorization(self, account_addr, access_right):
		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setCapToken_authorization(checksumAddr, access_right)

	# Print token date
	@staticmethod
	def print_tokendata(tokenStatus):
		#print token status
		for i in range(0,len(tokenStatus)):
			if(i==4 or i==5):
				dt=DatetimeUtil.timestamp_datetime(tokenStatus[i])
				#dt=datetime.datetime.utcfromtimestamp(token_data[i]/1e3)
				print(DatetimeUtil.datetime_string(dt))
				#print(DatetimeUtil.datetime_timestamp(dt))
				#print(token_data[i])
			else:
				print(tokenStatus[i])

	# get address from json file
	@staticmethod
	def getAddress(node_name, datafile):
		address_json = json.load(open(datafile))
		return address_json[node_name]


if __name__ == "__main__":
	http_provider = 'http://localhost:8042'
	contract_addr = '0x2fd1ecaf8d6ca9a566161895ea6650b85e76eb93'
	contract_config = '../Contracts/build/contracts/CapACToken.json'

	#new CapACToken object
	myCapACtoken=CapACToken(http_provider, contract_addr, contract_config)
	#mytoken.Show_ContractInfo()


	#------------------------- test contract API ---------------------------------
	#getAccounts
	accounts = myCapACtoken.getAccounts()
	balance = myCapACtoken.getBalance(accounts[0])
	print("Host accounts: %s" %(accounts))
	print("coinbase balance:%d" %(balance))
	print("--------------------------------------------------------------------")

	#------------------------------ call functions test -------------------------
	#Read token data using call
	node_address = CapACToken.getAddress('sam_miner_ubuntu_0', '../Contracts/test/addr_list.json')
	#token_data=myCapACtoken.getCapTokenStatus(node_address)
	token_data=myCapACtoken.getCapTokenStatus(accounts[0]);
	CapACToken.print_tokendata(token_data)	
	print("--------------------------------------------------------------------")

	# list Access control
	json_data=TypesUtil.string_to_json(token_data[-1])
	print("resource: %s" %(json_data['resource']))
	print("action: %s" %(json_data['action']))
	print("conditions: %s" %(json_data['conditions']))

	# ----------------------------------- Send transact --------------------------
	#========== set master of domain ========
	#myCapACtoken.assignVZoneMaster(node_address);
	#myCapACtoken.revokeVZoneMaster()

	# ========= set capability flag ========
	#myCapACtoken.initCapToken(node_address);
	#myCapACtoken.setCapToken_isValid(node_address, True)

	# ============= set issue date and expired date ==========
	nowtime = datetime.datetime.now()
	#calculate issue_time and expire_time
	issue_time = DatetimeUtil.datetime_timestamp(nowtime)
	duration = DatetimeUtil.datetime_duration(0, 1, 0, 0)
	expire_time = DatetimeUtil.datetime_timestamp(nowtime + duration)
	#myCapACtoken.setCapToken_expireddate(node_address, issue_time, expire_time)

	#set access right
	access_right='{"resource":"/test/api/v1.0/dt", "action":"GET", "conditions":{"value": {"start": "8:12:32", "end": "14:32:32"},"type": "Timespan"}}';
	#myCapACtoken.setCapToken_authorization(node_address, access_right)


	pass