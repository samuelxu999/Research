#This is used for test code

from wallet import Wallet
from nodes import *
from transaction import Transaction
from block import Block
from Sim_validator import Validator as SimValidator
from validator import Validator
from consensus import *
from utilities import FileUtil, TypesUtil
from configuration import *
from db_adapter import DataManager
from vote import VoteCheckPoint

from time import time
import random
import copy

def test_transaction():
    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    #list account address
    print(mywallet.list_address())

    #----------------- test transaction --------------------
    sender = mywallet.accounts[0]
    recipient = mywallet.accounts[-1]
    attacker = mywallet.accounts[1]

    # generate transaction
    sender_address = sender['address']
    sender_private_key = sender['private_key']
    recipient_address = recipient['address']
    time_stamp = time()
    value = 12

    mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, value)

    '''print(mytransaction.sender_address)
    print(mytransaction.sender_private_key)
    print(mytransaction.recipient_address)
    print(mytransaction.value)'''
    #print(mytransaction.to_dict())
    #print(mytransaction.to_json())

    # sign transaction
    sign_data = mytransaction.sign('samuelxu999')

    # verify transaction
    dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
                                            mytransaction.recipient_address,
                                            mytransaction.time_stamp,
                                            mytransaction.value)
    verify_data = Transaction.verify(sender['public_key'], sign_data, dict_transaction)
    print('verify transaction:', verify_data)

def build_transaction():
	# Instantiate the Wallet
	mywallet = Wallet()

	# load accounts
	mywallet.load_accounts()

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

def build_block():
	# Instantiate the Wallet
	mywallet = Wallet()
	# Instantiate the PeerNodes
	peer_nodes = PeerNodes()

	# load accounts
	mywallet.load_accounts()

	#----------------- test account --------------------
	sender = mywallet.accounts[0]
	recipient = mywallet.accounts[-1]
	attacker = mywallet.accounts[1]

	# generate transaction
	sender_address = sender['address']
	sender_private_key = sender['private_key']

	root_block=Block()
	transaction_json = build_transaction()

	new_block=Block(root_block, [transaction_json])
	new_block.print_data()
	print('OrderedDict format: \n', new_block.to_dict())
	json_block = new_block.to_json()
	print('Json format: \n', json_block)

	# rebuild block object given json data
	obj_block = Block.json_to_block(new_block.to_json())
	print('obj_block.transactions: \n', obj_block.transactions)

	sign_data = new_block.sign(sender_private_key, 'samuelxu999')
	json_block['sender_address'] = sender_address
	json_block['signature'] = TypesUtil.string_to_hex(sign_data)

	return json_block


def test_block():
	# Instantiate the PeerNodes
	peer_nodes = PeerNodes()

	json_block = build_block()
	print('Receive block: \n', json_block)
	# ====================== rebuild transaction ==========================
	#transaction_data = new_block.transactions[0]
	transaction_data = json_block['transactions'][0]
	dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
											transaction_data['recipient_address'],
											transaction_data['time_stamp'],
											transaction_data['value'])
	sign_data = TypesUtil.hex_to_string(transaction_data['signature'])
	#peer_nodes.load_ByAddress(transaction_data['sender_address'])
	peer_nodes.load_ByAddress(json_block['sender_address'])
	ls_nodes = list(peer_nodes.get_nodelist())
	# ====================== verify transaction ==========================
	if(ls_nodes!=[]):
		sender_node = TypesUtil.string_to_json(ls_nodes[0])
	else:
		sender_node = None

	if(sender_node!=None):
		sender_pk= sender_node['public_key']
		verify_trans = Transaction.verify(sender_pk, sign_data, dict_transaction)
		
		# rebuild block object given json data
		obj_block = Block.json_to_block(json_block)
		verify_block = obj_block.verify(sender_pk, TypesUtil.hex_to_string(json_block['signature']))
	else:
		verify_trans = False
		verify_block = False
	
	print('Verify transaction:', verify_trans)
	print('Verify block:', verify_block)


def test_PoW():
	"""
	Mining task to find new block
	"""
	root_block=Block()
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
	root_block=Block()
	chain_data = []
	chain_data.append(root_block.to_json())

	last_block = chain_data[-1]
	print(last_block)
	print('get proof value:', POS.get_proof(Transaction.json_to_dict(last_block['transactions']), last_block['previous_hash'], last_block['nonce'],TEST_STAKE_SUM))
	
	sum_hit = 0
	test_run = 1000
	ran_nonce = random.randint(1, 2**256)

	for n in range(1, test_run):
		i=1
		while(POS.proof_of_stake(last_block, [build_transaction()], ran_nonce, TEST_STAKE_WEIGHT, TEST_STAKE_SUM )==0):
			i+=1
		#print('Try %d until succeed!' %(i))
		sum_hit+=i
	print('hit rate:', sum_hit/test_run)

def test_SimValidator():
    # Instantiate the Blockchain
    myblockchain = SimValidator(ConsensusType.PoW)
    print('Chain information:')
    print('    uuid:          ', myblockchain.node_id)
    print('    chain length: ', len(myblockchain.chain))

    print(myblockchain.chain[0])
    print('Mining....')
    for i in range(1, 6):
        new_block=myblockchain.mine_block()
        myblockchain.chain.append(new_block)
        print(new_block)

    #print(blockchain.chain[-1])
    print('    chain length: ', len(myblockchain.chain))

    print('Valid chain: ', SimValidator.valid_chain(myblockchain.chain))

    new_block = myblockchain.mine_block()
    print('Valid block: ', SimValidator.valid_block(new_block, myblockchain.chain))

def test_Node():
	# Instantiate the PeerNodes
	peer_nodes = PeerNodes()

	# ----------------------- register node -------------------------------
	peer_nodes.register_node('ceeebaa052718c0a00adb87de857ba63608260e9',
	    '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414b396a6a6e486e332f70492f596c6e4175454c492b35574b34394c397776510a5950346471516e514a7a66312f634d34416a726835484e706f5974622b326a6c33336a6b684850662f2b784f694f52346b4a685658526b434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
	    'http://128.226.77.51:8080')
	peer_nodes.register_node('1699600976ec6fc0fe35d54174eb6094e671d2fd',
	    '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414d58736e354f706b57706e3359695a386257753749397168363873784439370a2b2f4f5374616270305a464e365745475a415452316f397051684273727041416f656f4d4876717871784d2f645a636e7a43377a4f394d434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
	    'http://128.226.77.51:8081')
	peer_nodes.register_node('f55af09f40768ca05505767cd013b6b9a78579c4',
	    '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414e393072576d52506b6e46446b6d51536368414f74594434686f675a4d57330a6f4b4d77626559306a322f4966705a642b614447414863754c317534463443314d712b426354765239336b4b34573657346b6e59383145434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
	    'http://128.226.77.51:8082')
	peer_nodes.register_node('e416c382f8ff6d883dec61a12a2ced1b80905992',
	    '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414c3146677174546e7941393154586d5134656c7a4f2b334578486232716f450a6d454b4c52697830794e386772634d4a31493776413161315937416c4957437745644e69583956486c7654772f346c5a2b64374f356a38434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
	    'http://128.226.77.51:8083')

	peer_nodes.load_ByAddress()
	nodes = peer_nodes.get_nodelist()    
	#nodes = copy.copy(peer_nodes.nodes)
	print('List nodes by address:')
	for node in nodes:
	    json_node = TypesUtil.string_to_json(node)
	    print('    ' + json_node['address'] + '    ' + json_node['node_url'] )

	# ------------------ update and remove test -------------------
	json_data = {}
	#peer_nodes.update_node('ceeebaa052718c0a00adb87de857ba63608260e9', TypesUtil.json_to_string('{}'))
	peer_nodes.update_status('ceeebaa052718c0a00adb87de857ba63608260e9', 1)
	#peer_nodes.remove_node('ceeebaa052718c0a00adb87de857ba63608260e9')

	node_status = 1
	peer_nodes.load_ByStatus(node_status)
	nodes = peer_nodes.get_nodelist()  
	print('List nodes by status %d:' %(node_status))
	for node in nodes:
		json_node = TypesUtil.string_to_json(node)
		print('    ' + json_node['address'] + '    ' + json_node['node_url'] )

	#peer_nodes.save_node(PEER_NODES)
	'''peer_nodes.load_node(PEER_NODES)
	reload_nodes = peer_nodes.nodes
	#print(reload_nodes)

	print('List loaded nodes:')
	for node in list(reload_nodes):
	    json_node = TypesUtil.string_to_json(node)
	    print('    ' + json_node['address'] + '    ' + json_node['node_url'])

	# ---------------------- search node ----------------------
	node_address = '1699600976ec6fc0fe35d54174eb6094e671d2fd'
	print('Search nodes:' + node_address)
	print(peer_nodes.get_node(node_address))'''

def test_Wallet():
    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    # new account
    #mywallet.create_account('samuelxu999')

    #print(mywallet.accounts)
    
    if(len(mywallet.accounts)!=0):
        account = mywallet.accounts[0]
        print(TypesUtil.hex_to_string(account['public_key']))
        print(len(account['address']))
    
    #list account address
    print(mywallet.list_address())

def test_database():
	myDB_manager = DataManager(CHAIN_DATA_DIR, 'testdb')

	# new table 
	myDB_manager.create_table('processed')
	#myDB_manager.remove_table('processed')

	#build test data
	transaction = build_transaction()
	json_data = {}
	json_data['hash']='ed6d03786f790508ae752f5190432bca4d9cc017c5835c1c6e470a9936d88015'
	json_data['nonce']= 34567
	json_data['transactions'] = [transaction]

	# CRUD test
	#myDB_manager.insert_block('processed', json_data['hash'], TypesUtil.json_to_string(json_data))
	#myDB_manager.update_block('processed', json_data['hash'], TypesUtil.json_to_string('{}'))
	#myDB_manager.update_status('processed', json_data['hash'], 1)
	#myDB_manager.delete_block('processed', json_data['hash'])

	#Display data
	ls_result = myDB_manager.select_block('processed', json_data['hash'])
	#ls_result = myDB_manager.select_status('processed', 1)	
	#print(ls_result)

	if(len(ls_result)>0):
		print('ID:           ', ls_result[0][0] )
		print('Block_hash:   ', ls_result[0][1] )
		print('Block_status: ', ls_result[0][3] )
		json_data = TypesUtil.string_to_json(ls_result[0][2])
		if(json_data !={}):
			print(json_data['transactions'])
			print(json_data['hash']==ls_result[0][1])		


def test_Validator():
	# Instantiate the Blockchain
	myblockchain = Validator(ConsensusType.PoW)
	myblockchain.load_chain()

	print('Chain information:')
	print('    uuid:          ', myblockchain.node_id)
	print('    chain length: ', len(myblockchain.chain))

	#print(myblockchain.chain[-1])
	#print(myblockchain.chain_db.select_block(CHAIN_TABLE))

	'''print('Mining....')
	for i in range(1, 6):
		new_block=myblockchain.mine_block()
		myblockchain.chain.append(new_block)
		print(new_block)

	#print(blockchain.chain[-1])
	print('    chain length: ', len(myblockchain.chain))

	new_block = myblockchain.mine_block()
	print('Valid block: ', myblockchain.valid_block(new_block))'''

	print(myblockchain.get_parent(myblockchain.chain[1]))

	print(myblockchain.is_ancestor(myblockchain.chain[0], myblockchain.chain[1]))

def test_Vote():
	# Instantiate the Wallet
	mywallet = Wallet()

	# load accounts
	mywallet.load_accounts()

	#list account address
	print(mywallet.list_address())

	#----------------- test transaction --------------------
	sender = mywallet.accounts[0]
	recipient = mywallet.accounts[-1]
	attacker = mywallet.accounts[1]

	my_vote = VoteCheckPoint('src_h', 'tar_h', 1, 2, sender['address'])

	dict_vote = my_vote.to_dict()
	json_vote = my_vote.to_json()

	print('dict vote data:', dict_vote)

	# sign vote
	sign_data = my_vote.sign(sender['private_key'], 'samuelxu999')
	json_vote['signature'] = TypesUtil.string_to_hex(sign_data)

	print('json vote data:', json_vote)

	#rebuild vote object given json data
	new_vote = VoteCheckPoint.json_to_vote(json_vote)

	#verify vote
	verify_data = VoteCheckPoint.verify(sender['public_key'], 
						TypesUtil.hex_to_string(json_vote['signature']), new_vote.to_dict())

	print('verify vote:', verify_data)

	voter = VoteCheckPoint.new_voter(json_vote)
	#voter = VoteCheckPoint.remove_voter(json_vote)
	votes_db={}
	votes_db[json_vote['sender_address']]=voter

	VoteCheckPoint.add_voter_data(votes_db[json_vote['sender_address']], json_vote)
	vote_data = VoteCheckPoint.get_voter_data(votes_db[json_vote['sender_address']], json_vote)

	print(vote_data)


if __name__ == '__main__':
	#test_block()
	#test_PoW()
	#test_PoS()
	#test_SimValidator()
	#test_transaction()
	#test_Node()
	#test_Wallet()
	#test_database()
	#test_Validator()
	#test_Vote()

	pass


