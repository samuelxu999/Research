#!/usr/bin/env python

'''
========================
WS_Server module
========================
Created on May.21, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of server API that handle and response client's request.
                  This can be used as microchain validator server.
'''

import time
import datetime
import json
import threading
import logging
from flask import Flask, jsonify
from flask import abort,make_response,request
from argparse import ArgumentParser

from utilities import FileUtil, TypesUtil, DatetimeUtil
from transaction import Transaction
from block import Block
from validator import Validator
from consensus import *
from service_api import SrvAPI
from randshare import RandShare, RandOP

logger = logging.getLogger(__name__)

# ================================= Instantiate the server =====================================
app = Flask(__name__)
#CORS(app)

#===================================== Validator RPC handler ===================================
@app.route('/test/consensus/run', methods=['POST'])
def consensus_run():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_data=json.loads(req_data)

	if(json_data=='{}'):
		abort(401, {'error': 'No node data'})

	myblockchain.runConsensus = json_data['consensus_run']

	return jsonify({'consensus_run': myblockchain.runConsensus}), 201


@app.route('/test/validator/getinfo', methods=['GET'])
def validator_info():
	response = myblockchain.get_info()
	return jsonify(response), 200

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
	# if( (json_block['height'] % EPOCH_SIZE) == 0):
	if( (json_block['height'] % myblockchain.block_epoch) == 0):
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

	# print('verify_vote:', verify_result)

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

# ====================================== Random share RPC handler==================================
@app.route('/test/randshare/create', methods=['GET'])
def create_randshare():
	myrandshare = RandShare()

	# get host node address
	# host_node=myblockchain.wallet.list_address()[0]
	# int_share = TypesUtil.hex_to_int(host_node)
	start_time=time.time()
	json_shares=myrandshare.create_shares()
	RandShare.save_sharesInfo(json_shares)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_create_shares.log', format(exec_time*1000, '.3f'))

	return jsonify({'create_randshare': 'Succeed!'}), 201

# request for share from peers
@app.route('/test/randshare/fetch', methods=['POST'])
def fetch_randshare():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_node=json.loads(req_data)

	if(json_node=='{}'):
		abort(401, {'error': 'No node data'})

	# used to save share data including node_shares, poly_commitments and share_proofs
	# 1) get node_shares
	load_json_shares=RandShare.load_sharesInfo()
	node_shares = load_json_shares['node_shares']

	# 2) get poly_commitments
	poly_commitments = load_json_shares['poly_commitments']

	# 3) get share_proofs
	node_proofs = load_json_shares['node_proofs']


	# prepare return json_share
	json_share = {}
	if json_node['address'] in node_shares:
		# shares=node_shares[json_node['address']]
		json_share['poly_commitments'] = poly_commitments
		json_share['node_shares'] = node_shares[json_node['address']]
		json_share['node_proofs'] = node_proofs[json_node['address']]
		json_share['status'] = 0

	host_node=myblockchain.wallet.list_address()[0]
	response = {host_node: json_share}
	return jsonify(response), 200

# request for share from peers and cache to local
@app.route('/test/randshare/cachefetched', methods=['GET'])
def cachefetched_randshare():
	start_time=time.time()
	# 1) read cached host_shares
	host_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)
	if( host_shares == None):
		host_shares = {}
	# get host address
	host_node=myblockchain.wallet.list_address()[0]
	# 2) for each peer node to fetch host share information
	for peer_node in list(myblockchain.peer_nodes.get_nodelist()):
		json_peer = TypesUtil.string_to_json(peer_node)
		# fetch_share=fetch_randshare(target_address)
		json_node={}
		json_node['address'] = host_node
		# print(json_node)
		fetch_share=SrvAPI.POST('http://'+json_peer['node_url']+'/test/randshare/fetch', json_node)

		for (node_name, share_data) in fetch_share.items():
			host_shares[node_name]=share_data
	# 3) update host shares 
	RandShare.save_sharesInfo(host_shares, RandOP.RandDistribute)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_cachefetched_shares.log', format(exec_time*1000, '.3f'))
	return jsonify({'cachefetched_randshare': 'Succeed!'}), 200

# verify share and proof 
@app.route('/test/randshare/verify', methods=['GET'])
def verify_randshare():
	start_time=time.time()
	# 1) read cached randshare 
	host_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)
	if( host_shares == None):
		host_shares = {}
	# 2) for each peer node to verify shares
	for peer_node in list(myblockchain.peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		# get public numbers given peer's pk
		public_numbers = RandShare.get_public_numbers(json_node['public_key'])
		host_address = json_node['address']
		# get share information
		shares = host_shares[host_address]
		poly_commits = shares['poly_commitments']
		share_proofs = shares['node_proofs']
		# print(poly_commits)
		# print(share_proofs)

		# instantiate RandShare to verify share proof.
		myrandshare = RandShare()
		myrandshare.p = public_numbers.n
		share_index = share_proofs[0]
		verify_S = myrandshare.verify_S(poly_commits, share_index)
		# print('verify S', share_index, ':', verify_S==share_proofs[1])
		if(verify_S==share_proofs[1]):
			host_shares[host_address]['status']=1
			# update host shares 
	RandShare.save_sharesInfo(host_shares, RandOP.RandDistribute)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_verify_shares.log', format(exec_time*1000, '.3f'))
	return jsonify({'verify_randshare': 'Succeed!'}), 200

@app.route('/test/randshare/recovered', methods=['GET'])
def recovered_randshare():
	# used to save share data including node_shares, poly_commitments and share_proofs
	# 1) get node_shares
	load_json_shares=RandShare.load_sharesInfo()
	node_shares = load_json_shares['node_shares']

	# get host node address
	host_node=myblockchain.wallet.list_address()[0]

	# prepare return json_share
	ls_shares = []
	for (node_name, node_data) in node_shares.items():
		ls_shares.append(node_data)
	response = {host_node: ls_shares}
	return jsonify(response), 200

# request for vote shares from peers
@app.route('/test/randshare/fetchvote', methods=['GET'])
def fetch_vote_randshare():
	# used to get vote shares of peer
	# 1) get shares host
	load_json_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)

	# get host node address
	host_node=myblockchain.wallet.list_address()[0]

	# prepare return json_share
	host_shares = {}
	for (node_name, node_data) in load_json_shares.items():
		host_shares[node_name]=node_data['status']
	response = {host_node: host_shares}
	return jsonify(response), 200

# retrive vote shares from peers and locally cache for verify vote 
@app.route('/test/randshare/cachevote', methods=['GET'])
def cache_vote_randshare():
	start_time=time.time()
	# 1) read cached vote shares
	vote_shares=RandShare.load_sharesInfo(RandOP.RandVote)
	if( vote_shares == None):
		vote_shares = {}
	# 2) for each peer node to fetch vote information
	for peer_node in list(myblockchain.peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		# cache_vote_shares(json_node['node_url'])
		# host_vote_shares=fetchvote_randshare(json_node['node_url'])
		host_vote_shares = SrvAPI.GET('http://'+json_node['node_url']+'/test/randshare/fetchvote')
		for (node_name, share_data) in host_vote_shares.items():
			vote_shares[node_name]=share_data
	# 3) update vote shares 
	RandShare.save_sharesInfo(vote_shares, RandOP.RandVote)
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_cachevote_shares.log', format(exec_time*1000, '.3f'))
	return jsonify({'vote_randshare': 'Succeed!'}), 200

def disp_randomshare(json_shares):
	''' randshare function'''	
	logger.info("poly_secrets:")
	poly_secrets = json_shares['poly_secrets']
	if poly_secrets:
	    for poly_secret in poly_secrets:
	        logger.info('    {}'.format(poly_secret))

	logger.info("node_shares:")
	node_shares = json_shares['node_shares']
	nodes = myrandshare.peer_nodes.get_nodelist()
	if node_shares:
		shares=[]
		for node in nodes:
			json_node = TypesUtil.string_to_json(node)
			shares.append(node_shares[json_node['address']])
			logger.info('    {}: {}'.format(json_node['address'], node_shares[json_node['address']]))
	
	# get poly_commits
	poly_commits = myrandshare.poly_commits(poly_secrets)
	logger.info("poly_commitments:")
	if poly_commits:
		for poly_commit in poly_commits:
			logger.info('    {}'.format(poly_commit))

	# get share_proofs
	share_proofs = myrandshare.share_proofs(shares)
	logger.info("share_proofs:")
	share_proofs.sort(key=lambda tup: tup[0])
	if share_proofs:
		for share_proof in share_proofs:
			logger.info('    {}'.format(share_proof))

if __name__ == '__main__':
	# FORMAT = "%(asctime)s %(levelname)s %(filename)s(l:%(lineno)d) - %(message)s"
	FORMAT = "%(asctime)s %(levelname)s | %(message)s"
	LOG_LEVEL = logging.INFO
	logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

	parser = ArgumentParser(description="Run microchain websocket server.")
	parser.add_argument('-p', '--port', default=8080, type=int, 
						help="port to listen on.")
	parser.add_argument('--blockepoch', default=2, type=int, 
						help="Block proposal round epoch size.")
	parser.add_argument('--pauseepoch', default=2, type=int, 
						help="Checkpoint epoch size for pending consensus and synchronization.")
	parser.add_argument('--phasedelay', default=3, type=int, 
						help="Delay time between operations of consensus protocol.")
	parser.add_argument("--debug", action="store_true", 
						help="if set, debug model will be used.")
	parser.add_argument("--threaded", action="store_true", 
						help="if set, support threading requests.")
	args = parser.parse_args()

	# ------------------------ Instantiate the Validator ----------------------------------
	myblockchain = Validator(consensus=ConsensusType.PoS, 
							block_epoch=args.blockepoch,
							pause_epoch=args.pauseepoch,
							phase_delay=args.phasedelay)
	myblockchain.load_chain()

	myblockchain.print_config()

	# # -------------------------- Instantiate RandShare -------------------------------------
	# myrandshare = RandShare()
	# json_sharesInfo=RandShare.load_sharesInfo()
	# # display random shares
	# disp_randomshare(json_sharesInfo)

	app.run(host='0.0.0.0', port=args.port, debug=args.debug, threaded=args.threaded)

