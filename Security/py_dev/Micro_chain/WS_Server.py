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

import time
import datetime
import json
import threading
from flask import Flask, jsonify
from flask import abort,make_response,request

from utilities import FileUtil, TypesUtil, DatetimeUtil
from transaction import Transaction
from block import Block
from validator import Validator
from consensus import *
from service_api import SrvAPI
from randshare import RandShare


# ================================= Instantiate the server =====================================
app = Flask(__name__)
#CORS(app)

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
	
	start_time=time.time()
	verify_data = myblockchain.on_receive(transaction_data, 0)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_verify_tx.log', format(exec_time*1000, '.3f'))
	
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
	#myblockchain.peer_nodes.load_ByAddress()
	SrvAPI.broadcast_POST(myblockchain.peer_nodes.get_nodelist(), transaction_data, '/test/transaction/verify')

	return jsonify({'broadcast_transaction': 'Succeed!'}), 201

@app.route('/test/transactions/get', methods=['GET'])
def get_transactions():
    # Get transactions from transactions pool
    transactions = myblockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

@app.route('/test/chain/get', methods=['GET'])
def full_chain():
	myblockchain.load_chain()
	response = {
	    'chain': myblockchain.chain,
	    'length': len(myblockchain.chain),
	}
	return jsonify(response), 200

@app.route('/test/chain/checkhead', methods=['GET'])
def check_head():
	myblockchain.fix_processed_head()

	return jsonify({'Reorganize processed_head': myblockchain.processed_head}), 200

@app.route('/test/mining', methods=['GET'])
def mine_block():
	start_time=time.time()
	new_block=myblockchain.mine_block()
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_mining.log', format(exec_time*1000, '.3f'))
	
	#broadcast proposed block
	if( (myblockchain.consensus==ConsensusType.PoW) or (not Block.isEmptyBlock(new_block)) ):
		#broadcast new block to peer nodes
		#myblockchain.peer_nodes.load_ByAddress()
		SrvAPI.broadcast_POST(myblockchain.peer_nodes.get_nodelist(), new_block, '/test/block/verify')

		response = {
			'message': "New Block Forged",
			'sender_address': new_block['sender_address'],
			'signature': new_block['signature'],
			'hash': new_block['hash'],
			'height': new_block['height'],
			'transactions': new_block['transactions'],
			'nonce': new_block['nonce'],
			'previous_hash': new_block['previous_hash'],
		}
	else:
		response = { 'message': "Empty Block Forged, not broadcast."}		
	
	return jsonify(response), 200

@app.route('/test/nodes/get', methods=['GET'])
def get_nodes():
	myblockchain.peer_nodes.load_ByAddress()
	nodes = myblockchain.peer_nodes.nodes
	response = {'nodes': nodes}
	return jsonify(response), 200

@app.route('/test/nodes/add', methods=['POST'])
def add_node():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_node=json.loads(req_data)

	if(json_node=='{}'):
		abort(401, {'error': 'No node data'})

	myblockchain.peer_nodes.register_node(json_node['address'], json_node['public_key'], json_node['node_url'])
	myblockchain.peer_nodes.load_ByAddress()
	return jsonify({'add peer node': json_node['address']}), 201

@app.route('/test/nodes/remove', methods=['POST'])
def remove_node():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_node=json.loads(req_data)
	
	if(json_node=='{}'):
		abort(401, {'error': 'No node data'})
		
	myblockchain.peer_nodes.remove_node(json_node['address'])
	myblockchain.peer_nodes.load_ByAddress()
	return jsonify({'remove peer node': json_node['address']}), 201

@app.route('/test/block/verify', methods=['POST'])
def verify_block():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	block_data=json.loads(req_data)
	
	if(block_data=='{}'):
		abort(401, {'error': 'No block data'})

	start_time=time.time()
	verify_result = myblockchain.on_receive(block_data, 1)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_verify_block.log', format(exec_time*1000, '.3f'))

	return jsonify({'verify_block': verify_result}), 201

@app.route('/test/block/vote', methods=['GET'])
def vote_block():
	json_block = myblockchain.processed_head

	ret_msg = "Not valid for voting epoch"
	if( (json_block['height'] % EPOCH_SIZE) == 0):
		vote_data = myblockchain.vote_checkpoint(json_block)	
		SrvAPI.broadcast_POST(myblockchain.peer_nodes.get_nodelist(), vote_data, '/test/vote/verify')
		ret_msg = vote_data

	return jsonify({'Vote block': ret_msg}), 201

@app.route('/test/vote/verify', methods=['POST'])
def verify_vote():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	vote_data=json.loads(req_data)
	
	if(vote_data=='{}'):
		abort(401, {'error': 'No vote data'})

	start_time=time.time()
	verify_result = myblockchain.on_receive(vote_data, 2)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_verify_vote.log', format(exec_time*1000, '.3f'))

	print('verify_vote:', verify_result)

	return jsonify({'verify_vote': verify_result}), 201

#GET req
@app.route('/test/vote/broadcast', methods=['POST'])
def broadcast_vote():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	vote_data=json.loads(req_data)

	if(vote_data=='{}'):
		abort(401, {'error': 'No vote data'})

	# broadcast transaction to peer nodes
	#myblockchain.peer_nodes.load_ByAddress()
	SrvAPI.broadcast_POST(myblockchain.peer_nodes.get_nodelist(), vote_data, '/test/vote/verify')

	return jsonify({'broadcast_vote': 'Succeed!'}), 201

@app.route('/test/randshare/fetch', methods=['POST'])
def fetch_randshare():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_node=json.loads(req_data)

	if(json_node=='{}'):
		abort(401, {'error': 'No node data'})

	load_json_shares=RandShare.load_sharesInfo()
	node_shares = load_json_shares['node_shares']

	if json_node['address'] in node_shares:
		shares=node_shares[json_node['address']]
	else:
		shares={}
	host_node=myblockchain.wallet.list_address()[0]
	response = {host_node: shares}
	return jsonify(response), 200

def disp_randomshare(json_shares):
	''' randshare function'''	
	print('poly_secrets:')
	poly_secrets = json_shares['poly_secrets']
	if poly_secrets:
	    for poly_secret in poly_secrets:
	        print('  ', poly_secret)	

	print('node_shares:')
	node_shares = json_shares['node_shares']
	nodes = myrandshare.peer_nodes.get_nodelist()
	if node_shares:
		shares=[]
		for node in nodes:
			json_node = TypesUtil.string_to_json(node)
			shares.append(node_shares[json_node['address']])
			print('  ', json_node['address'], ': ', node_shares[json_node['address']])

if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port

	# Instantiate the Blockchain
	myblockchain = Validator(ConsensusType.PoS)
	myblockchain.load_chain()

	myblockchain.print_config()

	# Instantiate RandShare 
	myrandshare = RandShare()
	load_json_shares=RandShare.load_sharesInfo()
	# display random shares
	disp_randomshare(load_json_shares);

	app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

