'''
========================
SrvExchange token module
========================
Created on August.10, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of web3.py API to interact with SrvExchange.sol smart contract.
'''

from web3 import Web3, HTTPProvider, IPCProvider
# from utilities import DatetimeUtil, TypesUtil
import json, datetime, time
import logging

logger = logging.getLogger(__name__)

class SrvExchangeToken(object):
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
		logger.info(self.web3.eth.blockNumber)
		logger.info(self.web3.eth.accounts)
		logger.info(self.web3.fromWei(self.web3.eth.getBalance(self.web3.eth.accounts[0]), 'ether'))

		logger.info(self.contract.address)

	# return accounts address
	def getHostAccounts(self):
		return self.web3.eth.accounts

	# return accounts balance
	def getHostBalance(self, account_addr=''):
		if(account_addr==''):
			# get accounts[0] balance
			checksumAddr=self.web3.eth.coinbase
		else:
			#Change account address to EIP checksum format
			checksumAddr=Web3.toChecksumAddress(account_addr)	
		return self.web3.fromWei(self.web3.eth.getBalance(checksumAddr), 'ether')

	# # --------------------------- RPC functions to interact with smart contract ---------------------------

	def getAccount(self, account_addr):
		'''
		Get account  data by call getAccount()
		'''

		#Change account address to EIP checksum format
		checksumAddr = Web3.toChecksumAddress(account_addr)

		# get token status
		account_info=self.contract.call({'from': self.web3.eth.coinbase}).getAccount(checksumAddr)
		return(account_info)

	def initAccount(self, account_addr):
		'''
		Initialized account by sending transact to call initAccount()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).initAccount(checksumAddr)
	

	def setAccount(self, account_addr, account_status, account_balance):
		'''
		Set TB_account status and balance given address
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction.	
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setAccount(checksumAddr, 
																				account_status, 
																				account_balance)
	def getService(self):
		'''
		Get service  data by call getService()
		'''

		# get service data: dealer, provider and recipient
		service_list=self.contract.call({'from': self.web3.eth.coinbase}).getService()
		return(service_list)

	def initService(self):
		'''
		Initialize service  data by call initService()
		'''

		# get service data: dealer, provider and recipient
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).initService()

	def updateProvider(self, account_addr, service_info):
		'''
		Update provider by call updateProvider()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).updateProvider(checksumAddr, 
																				service_info)

	def updateRecipient(self, account_addr, service_info):
		'''
		Update recipient by call updateRecipient()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).updateRecipient(checksumAddr, 
																				service_info)


	def recipient_deposit(self, account_addr, time_currency):
		'''
		deposit recipient's time currency into dealer balance by call recipient_deposit()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).recipient_deposit(checksumAddr, 
																				time_currency)

	def recipient_withdraw(self, account_addr):
		'''
		remove recipient time currency from dealer balance by call recipient_withdraw()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).recipient_withdraw(checksumAddr)

	def provider_confirm(self, account_addr):
		'''
		set provider as Confirmed by call provider_confirm()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).provider_confirm(checksumAddr)

	def service_commit(self, account_addr):
		'''
		set service Committed state by call service_commit()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).service_commit(checksumAddr)

	def service_payment(self, account_addr):
		'''
		trigger service payment process by call service_payment()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).service_payment(checksumAddr)

	# Print token date
	@staticmethod
	def print_service(service_list):
		# print service list: 
		logger.info("Dealer:     uid:{}    balance: {}".format(service_list[0], 
																			service_list[1]) )

		logger.info("Provider:   vid:{}    service_info: {}    status: {}".format(service_list[2], 
																			service_list[3], 
																			service_list[4]) )

		logger.info("Recipient:  vid:{}    service_info: {}    status: {}".format(service_list[5], 
																				service_list[6],
																				service_list[7]) )

	# get address from json file
	@staticmethod
	def getAddress(node_name, datafile):
		address_json = json.load(open(datafile))
		return address_json[node_name]


if __name__ == "__main__":
	# Logging setup
	FORMAT = "%(asctime)s | %(message)s"
	logging.basicConfig(format=FORMAT)
	logger.setLevel(level=logging.DEBUG)

	addr_list = './addr_list.json'

	http_provider = 'http://localhost:8042'
	contract_addr = SrvExchangeToken.getAddress('SrvExchangeToken', addr_list)
	contract_config = '../contract_dev/build/contracts/SrvExchange.json'


	#new SrvExchangeToken object
	mySrvExchange=SrvExchangeToken(http_provider, contract_addr, contract_config)
	mySrvExchange.Show_ContractInfo()


	#------------------------- test contract API ---------------------------------
	#getAccounts
	accounts = mySrvExchange.getHostAccounts()
	balance = mySrvExchange.getHostBalance(accounts[0])
	logger.info("Host accounts:    {}".format(accounts) )
	logger.info("Coinbase balance: {}".format(balance))
	logger.info("--------------------------------------------------------------------")

	#------------------------------ RPC functions test -------------------------

	node_address = SrvExchangeToken.getAddress('Desk_PI_Plus_Sam1', addr_list)
	account_data=mySrvExchange.getAccount(node_address);
	# mySrvExchange.initAccount(node_address)
	# mySrvExchange.setAccount(node_address, 1, 10)
	logger.info("TB accounts:{}    uid:{}    balance:{}    status:{}".format(node_address,
																			account_data[0],
																			account_data[1],
																			account_data[2]) )

	# mySrvExchange.initService()

	# --------------------------------- service registration -----------------------------------
	provide_address = SrvExchangeToken.getAddress('Desk_PI_Plus_Sam1', addr_list)
	# mySrvExchange.updateProvider(provide_address, "Samuel can provide house cleaning service.")

	recipient_address = SrvExchangeToken.getAddress('Desk_PI_Plus_Sam2', addr_list)
	# mySrvExchange.updateRecipient(recipient_address, 'Bob need house cleaning service.')

	# --------------------------------- service negotiation -----------------------------------
	# mySrvExchange.recipient_deposit(recipient_address, 3)
	# mySrvExchange.recipient_withdraw(recipient_address)
	# mySrvExchange.provider_confirm(provide_address)

	# --------------------------------- service committment -----------------------------------
	# mySrvExchange.service_commit(provide_address)
	# mySrvExchange.service_commit(recipient_address)

	# --------------------------------- service payment -----------------------------------
	# mySrvExchange.service_payment(provide_address)

	# --------------------------------- list service status -----------------------------------
	service_data=mySrvExchange.getService()
	SrvExchangeToken.print_service(service_data)

	pass
