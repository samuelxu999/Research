#This is used for test code

from wallet import Wallet
from nodes import PeerNodes
from transaction import Transaction
from block import Block
from consensus import POW
from utilities import FileUtil, TypesUtil

from time import time

def test_block():

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

	#myblock=Block(root_block, [transaction_json])
	#myblock.print_data()

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
	print(verify_data)

	"""
	Mining task to find new block
	"""
	chain_data = []
	chain_data.append(root_block.to_json())
	#chain_data.append(myblock.to_json())

	#print(chain_data[-1])
	#print(myblock.to_dict())

	#obj_block = Block.json_to_block(myblock.to_json())
	#print(obj_block.transactions)

	last_block = chain_data[-1]
	print(last_block)
	parent_block = Block.json_to_block(last_block)

	# mining new block
	nonce = POW.proof_of_work(last_block, [transaction_json])
	new_block = Block(parent_block, [transaction_json], nonce)
	new_block.print_data()

	chain_data.append(new_block.to_json())

	print(chain_data)


# Instantiate the Wallet
mywallet = Wallet()

# load accounts
mywallet.load_accounts()

# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_node()

root_block=Block()

if __name__ == '__main__':
	root_block.print_data()
	test_block()
	pass


