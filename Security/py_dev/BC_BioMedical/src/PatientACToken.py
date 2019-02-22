#!/usr/bin/env python3.5

'''
========================
Patient access control token module
========================
Created on Feb.20, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of web3.py API to interact with PatientACToken.sol smart contract.
'''

from web3 import Web3, HTTPProvider, IPCProvider
from utilities import DatetimeUtil, TypesUtil
import json, datetime, time

class PatientACToken(object):
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
	contract_addr = PatientACToken.getAddress('PatientACToken', './addr_list.json')
	contract_config = '../contracts/build/contracts/PatientACToken.json'

	#new PatientACToken object
	myPatientACtoken=PatientACToken(http_provider, contract_addr, contract_config)


	#------------------------- test contract API ---------------------------------
	#getAccounts
	accounts = myPatientACtoken.getAccounts()
	balance = myPatientACtoken.getBalance(accounts[0])
	print("Host accounts: %s" %(accounts))
	print("coinbase balance:%d" %(balance))
	print("--------------------------------------------------------------------")

	user_address = PatientACToken.getAddress('sam_ubuntu', './addr_list.json')
	patientACToken_address = PatientACToken.getAddress('PatientACToken', './addr_list.json')

	#------------------------------ call functions test -------------------------
	#Read token data using call
	token_data=myPatientACtoken.getCapTokenStatus(user_address)
	PatientACToken.print_tokendata(token_data)	
	print("--------------------------------------------------------------------")

	# list Access control
	'''json_data=TypesUtil.string_to_json(token_data[-1])
	print("resource: %s" %(json_data['resource']))
	print("action: %s" %(json_data['action']))
	print("conditions: %s" %(json_data['conditions']))'''

	# ----------------------------------- Send transact --------------------------
	#========== set master of domain ========
	#myPatientACtoken.assignVZoneMaster(user_address);
	#myPatientACtoken.revokeVZoneMaster()

	# ========= set capability flag ========
	#myPatientACtoken.initCapToken(user_address);
	#myPatientACtoken.setCapToken_isValid(user_address, True)

	# ============= set issue date and expired date ==========
	nowtime = datetime.datetime.now()
	#calculate issue_time and expire_time
	issue_time = DatetimeUtil.datetime_timestamp(nowtime)
	duration = DatetimeUtil.datetime_duration(0, 1, 0, 0)
	expire_time = DatetimeUtil.datetime_timestamp(nowtime + duration)
	#myPatientACtoken.setCapToken_expireddate(user_address, issue_time, expire_time)

	#set access right
	access_right='{"resource":"/test/api/v1.0/dt", "action":"GET", "conditions":{"value": {"start": "08:12:32", "end": "22:32:32"},"type": "Timespan"}}';
	#myPatientACtoken.setCapToken_authorization(user_address, access_right)


	pass