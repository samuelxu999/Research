#!/usr/bin/env python

'''
========================
WS_Server module
========================
Created on Nov.2, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of server API that handle and response client's request.
'''

import datetime
import json
from flask import Flask, jsonify
from flask import abort,make_response,request

from utilities import FileUtil, TypesUtil, DatetimeUtil
from wallet import Wallet
from transaction import Transaction
from nodes import PeerNodes
from blockchain import Blockchain
from service_api import SrvAPI

def print_config():
	#list account address
	accounts = mywallet.list_address()
	print('Current accounts:')
	if accounts:
		i=0
		for account in accounts:
		    print(i, '  ', account)
		    i+=1

	print('Peer nodes:')
	for node in list(peer_nodes.nodes):
		json_node = TypesUtil.string_to_json(node)
		print('    ', json_node['address'] + '    ' + json_node['node_url'])

	# Instantiate the Blockchain
	myblockchain = Blockchain()
	print('Chain information:')
	print('    uuid:          ', myblockchain.node_id)
	print('    chain length: ', len(myblockchain.chain))

# ================================= Instantiate the server =====================================
app = Flask(__name__)
#CORS(app)

# Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_node()

# Instantiate the Wallet
mywallet = Wallet()
# load accounts
mywallet.load_accounts()

# Instantiate the Blockchain
myblockchain = Blockchain()

print_config()


def broadcast_block(block_data):
	# broadcast transaction to peer nodes
	for node in list(peer_nodes.nodes):
		json_node = TypesUtil.string_to_json(node)
		api_url = 'http://' + json_node['node_url'] + '/test/block/verify'
		json_response = SrvAPI.POST(api_url, block_data)


	
#========================================== Request handler ===============================================
#GET req
@app.route('/test/transaction/verify', methods=['POST'])
def verify_transaction():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	#transaction_data = TypesUtil.string_to_json(req_data)
	transaction_data=json.loads(req_data)
	
	if(transaction_data=='{}'):
		abort(401, {'error': 'No transaction data'})
	
	#print(transaction_data)

	# ====================== rebuild transaction ==========================
	dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
										transaction_data['recipient_address'],
										transaction_data['value'])
	
	sign_data = TypesUtil.hex_to_string(transaction_data['signature'])
	#print(dict_transaction)
	#print(sign_data)

	sender_node = peer_nodes.get_node(transaction_data['sender_address'])

	# ====================== verify transaction ==========================
	if(sender_node!={}):
		sender_pk= sender_node['public_key']
		#verify_data = Transaction.verify(sender_pk, sign_data, dict_transaction)
		verify_data = myblockchain.verify_transaction(dict_transaction, sender_pk, sign_data)
	else:
		verify_data = False

	return jsonify({'verify_transaction': verify_data}), 201

#GET req
@app.route('/test/transaction/broadcast', methods=['POST'])
def broadcast_transaction():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	#transaction_data = TypesUtil.string_to_json(req_data)
	transaction_data=json.loads(req_data)

	if(transaction_data=='{}'):
		abort(401, {'error': 'No transaction data'})

	# broadcast transaction to peer nodes
	for node in list(peer_nodes.nodes):
		json_node = TypesUtil.string_to_json(node)
		api_url = 'http://' + json_node['node_url'] + '/test/transaction/verify'
		json_response = SrvAPI.POST(api_url, transaction_data)
		#print(api_url)

	return jsonify({'broadcast_transaction': 'Succeed!'}), 201

@app.route('/test/transactions/get', methods=['GET'])
def get_transactions():
    # Get transactions from transactions pool
    transactions = myblockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

@app.route('/test/chain/get', methods=['GET'])
def full_chain():
    response = {
        'chain': myblockchain.chain,
        'length': len(myblockchain.chain),
    }
    return jsonify(response), 200

@app.route('/test/mining', methods=['GET'])
def mine_block():
	new_block=myblockchain.mine_block()
	#print(new_block)
	broadcast_block(new_block)

	response = {
	    'message': "New Block Forged",
	    'block_number': new_block['block_number'],
	    'transactions': new_block['transactions'],
	    'nonce': new_block['nonce'],
	    'previous_hash': new_block['previous_hash'],
	}
	return jsonify(response), 200

@app.route('/test/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(peer_nodes.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200

@app.route('/test/block/verify', methods=['POST'])
def verify_block():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	#transaction_data = TypesUtil.string_to_json(req_data)
	block_data=json.loads(req_data)
	
	if(block_data=='{}'):
		abort(401, {'error': 'No block data'})

	# verify block
	if(Blockchain.valid_block(block_data, myblockchain.chain)):
		verify_result = True
		for transaction_data in block_data['transactions']:
		    #print(transaction_data)
		    # ====================== rebuild transaction ==========================
		    dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
		                                        transaction_data['recipient_address'],
		                                        transaction_data['value'])
		    
		    sign_str = TypesUtil.hex_to_string(transaction_data['signature'])
		    #print(dict_transaction)
		    #print(sign_str)

		    sender_node = peer_nodes.get_node(transaction_data['sender_address'])
		    #print(sender_node)
		    # ====================== verify transaction ==========================
		    if(sender_node!={}):
		        sender_pk= sender_node['public_key']
		        verify_result = Transaction.verify(sender_pk, sign_str, dict_transaction)
		    else:
		        verify_result = False
		        #print('1')
		        break
	else:
		verify_result = False
		#print('2')

	if(verify_result):
		# remove committed transactions
		for transaction in block_data['transactions']:
			myblockchain.transactions.remove(transaction)
		# append verified block to local chain
		myblockchain.chain.append(block_data)
	#print(verify_result)
	return jsonify({'verify_block': verify_result}), 201
	
if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port

	app.run(host='0.0.0.0', port=port, debug=True)

