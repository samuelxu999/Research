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

from wallet import Wallet
from transaction import Transaction
from nodes import PeerNodes
from utilities import FileUtil, TypesUtil, DatetimeUtil

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

print_config()



	
#========================================== Request handler ===============================================
#GET req
@app.route('/test/transaction', methods=['POST'])
def verify_transaction():
	#Token missing, deny access
	req_data=TypesUtil.bytes_to_string(request.data)
	#transaction_data = TypesUtil.string_to_json(req_data)
	transaction_data=json.loads(req_data)
	
	if(transaction_data=='{}'):
		abort(401, {'message': 'Token missing, deny access'})
	
	#print(transaction_data)

	# ====================== verify transaction ==========================
	dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
										transaction_data['recipient_address'],
										transaction_data['value'])
	
	sign_data = TypesUtil.hex_to_string(transaction_data['signature'])
	#print(dict_transaction)
	#print(sign_data)

	sender_node = peer_nodes.get_node(transaction_data['sender_address'])
	if(sender_node!={}):
		sender_pk= sender_node['public_key']
		verify_data = Transaction.verify(sender_pk, sign_data, dict_transaction)
	else:
		verify_data = False

	#print('verify transaction:', verify_data)

	return jsonify({'verify_transaction': verify_data}), 201
	
if __name__ == '__main__':
	'''from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=8042, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port'''

	app.run(host='0.0.0.0', port=8042, debug=True)

