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
from blockchain import Blockchain
from utilities import FileUtil, TypesUtil, DatetimeUtil

# Instantiate the server
app = Flask(__name__)
#CORS(app)


	
#========================================== Request handler ===============================================
#GET req
@app.route('/test/transaction', methods=['POST'])
def get_transaction():
	#Token missing, deny access
	req_data=TypesUtil.bytes_to_string(request.data)
	#transaction_data = TypesUtil.string_to_json(req_data)
	transaction_data=json.loads(req_data)
	
	if(transaction_data=='{}'):
		abort(401, {'message': 'Token missing, deny access'})
	
	#print(transaction_data)

	# Instantiate the Wallet
	mywallet = Wallet()

	# load accounts
	mywallet.load_accounts()

	#list account address
	#print(mywallet.list_address())

	#----------------- test transaction --------------------
	sender = mywallet.accounts[0]

	# verify transaction
	dict_transaction = Transaction.get_dict(transaction_data['sender_address'], 
										transaction_data['recipient_address'],
										transaction_data['value'])
	
	sign_data = TypesUtil.hex_to_string(transaction_data['signature'])
	#print(dict_transaction)
	#print(sign_data)

	verify_data = Transaction.verify(sender['public_key'], sign_data, dict_transaction)
	print('verify transaction:', verify_data)

	return jsonify({'verify_transaction': verify_data}), 201
	
if __name__ == '__main__':
	'''from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=8042, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port'''

	app.run(host='0.0.0.0', port=8042, debug=True)

