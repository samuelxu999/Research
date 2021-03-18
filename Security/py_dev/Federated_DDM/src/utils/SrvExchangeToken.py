'''
========================
SrvExchange token module
========================
Created on March.17, 2021
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

	def getPublisher(self):
		'''
		Get publisher data by call getPublisher()
		'''

		## return [vid, zid, status, balance, txs]
		publisher_info=self.contract.call({'from': self.web3.eth.coinbase}).getPublisher()
		return(publisher_info)

	def getSubscriber(self):
		'''
		Get subscriber data by call getSubscriber()
		'''

		## return [vid, zid, status, balance, txs]
		subscriber_info=self.contract.call({'from': self.web3.eth.coinbase}).getSubscriber()
		return(subscriber_info)

	def initBroker(self):
		'''
		Initialize broker info by call initBroker()
		'''

		# get service data: dealer, provider and recipient
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).initBroker()

	def setPublisher(self, account_addr, zone_id, str_txs):
		'''
		Set publisher info given delegation request [vid, zid, txs]
		'''
		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setPublisher(checksumAddr, zone_id, str_txs)

	def setSubscriber(self, account_addr, zone_id, str_txs):
		'''
		Set subscriber info given delegation request [vid, zid, txs]
		'''
		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).setSubscriber(checksumAddr, zone_id, str_txs)

	def updatePublisher(self, account_addr, zone_id):
		'''
		Update publisher by call updatePublisher()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).updatePublisher(checksumAddr, zone_id)

	def updateSubscriber(self, account_addr, zone_id):
		'''
		Update subscriber by call updateSubscriber()
		'''

		#Change account address to EIP checksum format
		checksumAddr=Web3.toChecksumAddress(account_addr)	

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).updateSubscriber(checksumAddr, zone_id)

	def publisher_commit(self):
		'''
		update publisher as Committed state by call publisher_commit()
		'''

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).publisher_commit()

	def subscriber_commit(self, balance):
		'''
		update subscriber as Committed state by call subscriber_commit()
		'''

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).subscriber_commit(balance)

	def service_payment(self):
		'''
		trigger service payment process by call service_payment()
		'''

		# Execute the specified function by sending a new public transaction
		ret=self.contract.transact({'from': self.web3.eth.coinbase}).service_payment()

	# Print token date
	@staticmethod
	def print_broker(broker_list):

		logger.info("Publisher: vid:{} zid: {} status: {} balance:{} txs: {}".format(broker_list[0][0], 
																			broker_list[0][1], 
																			broker_list[0][2], 
																			broker_list[0][3], 
																			broker_list[0][4]) )

		logger.info("Subscriber: vid:{} zid: {} status: {} balance:{} txs: {}".format(broker_list[1][0], 
																			broker_list[1][1], 
																			broker_list[1][2], 
																			broker_list[1][3], 
																			broker_list[1][4]) )

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

	addr_list = '../addr_list.json'

	http_provider = 'http://localhost:8042'
	contract_addr = SrvExchangeToken.getAddress('SrvExchangeToken', addr_list)
	contract_config = '../../contract_dev/build/contracts/SrvExchange.json'


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
	# mySrvExchange.initBroker()

	# # --------------------------------- service delegation -----------------------------------
	# publisher_address = SrvExchangeToken.getAddress('Desk_PI_Plus_Sam1', addr_list)
	# mySrvExchange.setPublisher(publisher_address, "zone-1", "0x983454")

	# subcriber_address = SrvExchangeToken.getAddress('Desk_PI_Plus_Sam2', addr_list)
	# mySrvExchange.setSubscriber(subcriber_address, "zone-2", "0xfefe")

	# --------------------------------- broker update -----------------------------------
	# new_publisher = SrvExchangeToken.getAddress('Desk_PI_Node_1', addr_list)
	# mySrvExchange.updatePublisher(new_publisher, "zone-3")

	# new_subcriber = SrvExchangeToken.getAddress('Desk_PI_Node_2', addr_list)
	# mySrvExchange.updateSubscriber(new_subcriber, "zone-4")

	# --------------------------------- service committment -----------------------------------
	# mySrvExchange.publisher_commit()
	# mySrvExchange.subscriber_commit(100)

	# --------------------------------- service payment -----------------------------------
	# mySrvExchange.service_payment()

	# # --------------------------------- list service status -----------------------------------
	publisher_info = mySrvExchange.getPublisher()
	subscriber_info = mySrvExchange.getSubscriber()
	SrvExchangeToken.print_broker([publisher_info, subscriber_info])

	pass
