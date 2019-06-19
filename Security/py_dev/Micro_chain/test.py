#This is used for test code

from wallet import Wallet
from nodes import PeerNodes
from transaction import Transaction
from block import Block
from consensus import POW, POS
from utilities import FileUtil, TypesUtil

from time import time

def build_transaction():
	#----------------- test transaction --------------------
	sender = mywallet.accounts[0]
	recipient = mywallet.accounts[-1]
	attacker = mywallet.accounts[1]

	# generate transaction
	sender_address = sender['address']
	sender_private_key = sender['private_key']
	recipient_address = recipient['address']
	time_stamp = time()
	value = 15

	mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, value)

	# sign transaction
	sign_data = mytransaction.sign('samuelxu999')

	# verify transaction
	dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
	                                        mytransaction.recipient_address,
	                                        mytransaction.time_stamp,
	                                        mytransaction.value)
	#send transaction
	transaction_json = mytransaction.to_json()
	transaction_json['signature']=TypesUtil.string_to_hex(sign_data)

	return transaction_json

def test_block():

	transaction_json = build_transaction()

	myblock=Block(root_block, [transaction_json])
	myblock.print_data()
	print('OrderedDict format: \n', myblock.to_dict())
	print('Json format: \n', myblock.to_json())

	# rebuild block object given json data
	obj_block = Block.json_to_block(myblock.to_json())
	print('obj_block.transactions:', obj_block.transactions)

	# ====================== rebuild transaction ==========================
	#transaction_data = myblock.transactions[0]
	transaction_data = transaction_json
	dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
											transaction_data['recipient_address'],
											transaction_data['time_stamp'],
											transaction_data['value'])
	sign_data = TypesUtil.hex_to_string(transaction_data['signature'])
	sender_node = peer_nodes.get_node(transaction_data['sender_address'])

	# ====================== verify transaction ==========================
	if(sender_node!={}):
		sender_pk= sender_node['public_key']
		verify_data = Transaction.verify(sender_pk, sign_data, dict_transaction)
	else:
		verify_data = False
	print('Verify transaction:', verify_data)

def test_PoW():
	"""
	Mining task to find new block
	"""
	chain_data = []
	chain_data.append(root_block.to_json())

	last_block = chain_data[-1]
	#print(last_block)
	parent_block = Block.json_to_block(last_block)

	transaction_json = build_transaction()

	# mining new block
	nonce = POW.proof_of_work(last_block, [transaction_json])
	new_block = Block(parent_block, [transaction_json], nonce)
	new_block.print_data()

	chain_data.append(new_block.to_json())

	print(chain_data)


def test_PoS():
	# test PoS

	chain_data = []
	chain_data.append(root_block.to_json())

	last_block = chain_data[-1]
	print(last_block)

	sum_hit = 0
	test_run = 1000
	for n in range(1, test_run):
		i=1
		while(not POS.proof_of_stake(last_block, [build_transaction()], 1, 3 )):
			i+=1
		#print('Try %d until succeed!' %(i))
		sum_hit+=i
	print('hit rate:', sum_hit/test_run)



# Instantiate the Wallet
mywallet = Wallet()

# load accounts
mywallet.load_accounts()

# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_node()

root_block=Block()

if __name__ == '__main__':
	#test_block()
	#test_PoW()
	test_PoS()
	pass


