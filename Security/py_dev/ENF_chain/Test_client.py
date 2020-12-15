'''
========================
WS_Client module
========================
Created on Dec.10, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of client API that access to Web service.
                  Mainly used to test and demo
'''
import argparse
import sys
import random
import requests
import json
import time
import logging

from network.wallet import Wallet
from network.nodes import *
from consensus.transaction import Transaction
from consensus.block import Block
from consensus.vote import VoteCheckPoint
from consensus.validator import Validator
from consensus.consensus import POW, POE
from utils.utilities import TypesUtil, FileUtil
from utils.service_api import SrvAPI
from utils.Swarm_RPC import Swarm_RPC
from randomness.randshare import RandShare, RandOP

logger = logging.getLogger(__name__)

## Instantiate the PeerNodes
peer_nodes = PeerNodes()
peer_nodes.load_ByAddress()

## Load ENF samples database for test
ENF_file = "./data/one_day_enf.csv"
ENF_data = FileUtil.csv_read(ENF_file)

# ====================================== client side REST API ==================================
def run_consensus(target_address, exec_consensus, isBroadcast=False):
	json_msg={}
	json_msg['consensus_run']=exec_consensus

	if(not isBroadcast):
		json_response=SrvAPI.POST('http://'+target_address+'/test/consensus/run', json_msg)
		json_response = {'run_consensus': target_address, 'status': json_msg['consensus_run']}
	else:
		SrvAPI.broadcast_POST(peer_nodes.get_nodelist(), json_msg, '/test/consensus/run', True)
		json_response = {'run_consensus': 'broadcast', 'status': json_msg['consensus_run']}
	logger.info(json_response)

def validator_getinfo(target_address, isBroadcast=False):
	info_list = []
	if(not isBroadcast):
		json_response = SrvAPI.GET('http://'+target_address+'/test/validator/getinfo')
		info_list.append(json_response)
	else:
		for node in peer_nodes.get_nodelist():
			json_node = TypesUtil.string_to_json(node)
			json_response = SrvAPI.GET('http://'+json_node['node_url']+'/test/validator/getinfo')
			info_list.append(json_response)
	return info_list

def getSwarmhash(samples_id, samples_head, samples_size, is_random=False):
	if(is_random==True):
		head_pos = random.randint(0,7200) 
	else:
		head_pos = samples_head 

	ls_ENF = TypesUtil.np2list(ENF_data[head_pos:(head_pos+samples_size), 1]) 

	## ******************** upload ENF samples **********************
	## build json ENF data for transaction
	tx_json = {}

	json_ENF={}
	json_ENF['id']=samples_id
	json_ENF['enf']=ls_ENF
	tx_data = TypesUtil.json_to_string(json_ENF)  

	## save ENF data in transaction
	tx_json['data']=tx_data
	# print(tx_json)

	## random choose a swarm server
	target_address = Swarm_RPC.get_service_address()
	post_ret = Swarm_RPC.upload_data(target_address, tx_json)	

	return post_ret['data']

def send_transaction(target_address, samples_head, samples_size, isBroadcast=False):
    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    ##----------------- build test transaction --------------------
    sender = mywallet.accounts[0]
    sender_address = sender['address']
    sender_private_key = sender['private_key']
    ## set recipient_address as default value: 0
    recipient_address = '0'
    time_stamp = time.time()
    
    ## value comes from hash value to indicate address that ENF samples are saved on swarm network.
    json_value={}
    json_value['sender_address'] = sender_address
    json_value['swarm_hash'] = getSwarmhash(sender_address, samples_head, samples_size)
    ## convert json_value to string to ensure consistency in tx verification.
    str_value = TypesUtil.json_to_string(json_value)

    mytransaction = Transaction(sender_address, sender_private_key, recipient_address, time_stamp, str_value)

    # sign transaction
    sign_data = mytransaction.sign('samuelxu999')

    # verify transaction
    dict_transaction = Transaction.get_dict(mytransaction.sender_address, 
                                            mytransaction.recipient_address,
                                            mytransaction.time_stamp,
                                            mytransaction.value)
    
    ## --------------------- send transaction --------------------------------------
    transaction_json = mytransaction.to_json()
    transaction_json['signature']=TypesUtil.string_to_hex(sign_data)
    # print(transaction_json)
    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/transaction/verify', 
        						transaction_json)
    else:
        json_response=SrvAPI.POST('http://'+target_address+'/test/transaction/broadcast', 
                                transaction_json)
    logger.info(json_response)

def send_vote(target_address, isBroadcast=False):
    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    #list account address
    logger.info(mywallet.list_address())

    #----------------- test transaction --------------------
    sender = mywallet.accounts[0]
    # recipient = mywallet.accounts[-1]
    # attacker = mywallet.accounts[1]

    my_vote = VoteCheckPoint('385816343cc08cbc5350f4d1c92d2768e3be237ab364fb3bfc1dccde341205a2', 
                            'fc4341bb9867b7d389d84cd32a0e298cad595c806dd9477d0403ccc59f929138', 
                            1, 2, sender['address'])
    json_vote = my_vote.to_json()
    
    # sign vote
    sign_data = my_vote.sign(sender['private_key'], 'samuelxu999')
    json_vote['signature'] = TypesUtil.string_to_hex(sign_data)

    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/vote/verify', 
                                json_vote)
    else:
        json_response=SrvAPI.POST('http://'+target_address+'/test/vote/broadcast', 
                                json_vote)
    logger.info(json_response)


def get_transactions(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/transactions/get')
    transactions = json_response['transactions']
    logger.info(transactions)

    # print(POE.proof_of_enf(transactions, '1ad48ca78653f3f4b16b0622432db7d995613c42'))

def start_mining(target_address, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.GET('http://'+target_address+'/test/mining')
	#transactions = json_response['transactions']
	else:
		SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/mining', True)
		json_response = {'start mining': 'broadcast'}

	logger.info(json_response)

def start_voting(target_address, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.GET('http://'+target_address+'/test/block/vote')
	#transactions = json_response['transactions']
	else:
	#SrvAPI.broadcast(peer_nodes.get_nodelist(), {}, '/test/block/vote')
		SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/block/vote', True)
		json_response = {'verify_vote': 'broadcast'}
	logger.info(json_response)

def get_nodes(target_address):
    json_response=SrvAPI.GET('http://'+target_address+'/test/nodes/get')
    nodes = json_response['nodes']
    logger.info('Peer nodes:')
    for node in nodes:
        logger.info(node)

def add_node(target_address, json_node, isBroadcast=False):
    if(not isBroadcast):
        json_response=SrvAPI.POST('http://'+target_address+'/test/nodes/add', json_node)
        logger.info(json_response)
    else:
        #json_response=SrvAPI.broadcast_POST(peer_nodes.get_nodelist(), json_node, '/test/nodes/add')
        for target_node in target_address:
            try:
                SrvAPI.POST('http://'+target_node+'/test/nodes/add', json_node)
            except:
                pass

def remove_node(target_address, json_node, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.POST('http://'+target_address+'/test/nodes/remove', json_node)
		logger.info(json_response)
	else:
		#json_response=SrvAPI.broadcast_POST(peer_nodes.get_nodelist(), json_node, '/test/nodes/remove')
		for target_node in target_address:
			try:
				SrvAPI.POST('http://'+target_node+'/test/nodes/remove', json_node)
			except:
				pass

def get_chain(target_address, isDisplay=False):
	json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
	chain_data = json_response['chain']
	chain_length = json_response['length']
	logger.info('Chain length: {}'.format(chain_length))

	if( isDisplay ):
	    # only list latest 10 blocks
	    if(chain_length>10):
	        for block in chain_data[-10:]:
	            logger.info("{}\n".format(block))
	    else:
	        for block in chain_data:
	            logger.info("{}\n".format(block))

def check_head():
	SrvAPI.broadcast_GET(peer_nodes.get_nodelist(), '/test/chain/checkhead')
	json_response = {'Reorganize processed_head': 'broadcast'}

def set_peerNodes(target_name, op_status=0, isBroadcast=False):
    #--------------------------------------- load static nodes -------------------------------------
    static_nodes = StaticNodes()
    static_nodes.load_node()

    list_address = []
    print('List loaded static nodes:')
    for node in list(static_nodes.nodes):
        #json_node = TypesUtil.string_to_json(node)
        json_node = node
        list_address.append(json_node['node_url'])
        print(json_node['node_name'] + '    ' + json_node['node_address'] + '    ' + json_node['node_url'])

    #print(list_address)

    #-------------- localhost ----------------
    target_node = static_nodes.get_node(target_name)

    if( target_node=={}):
        return

    target_address = target_node['node_url']
    # print(target_address)

    # Instantiate the Wallet
    mywallet = Wallet()

    # load accounts
    mywallet.load_accounts()

    #list account address
    #print(mywallet.list_address())
    json_account = mywallet.get_account(target_node['node_address'])
    #print(json_account)

    # ---------------- add and remove peer node --------------------
    json_node = {}
    if(json_account!=None):
        json_node['address'] = json_account['address']
        json_node['public_key'] = json_account['public_key']
        json_node['node_url'] = target_node['node_url']
 
    if(op_status==1): 
        if(not isBroadcast):  
            add_node(target_address, json_node)
        else:
            add_node(list_address, json_node, True)
    if(op_status==2):
        if(not isBroadcast):
            remove_node(target_address, json_node)
        else:
            remove_node(list_address, json_node, True)
    
    get_nodes(target_address)

def fetch_randshare(target_address, isBroadcast=False):
	if(not isBroadcast):
		# Instantiate the Wallet
		mywallet = Wallet()
		mywallet.load_accounts()
		# get host address
		json_node={}
		json_node['address'] = mywallet.accounts[0]['address']
		json_response=SrvAPI.POST('http://'+target_address+'/test/randshare/fetch', json_node)
	else:
		SrvAPI.broadcast_GET(target_address, '/test/randshare/cachefetched', True)
		json_response = {'broadcast_fetch_randshare': 'Succeed!'}
	return json_response

def verify_randshare(target_address):
	json_response=SrvAPI.broadcast_GET(target_address, '/test/randshare/verify', True)
	return json_response

def recovered_randshare(target_address):
	json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/recovered')
	return json_response

def fetchvote_randshare(target_address):
	json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/fetchvote')
	return json_response

def vote_randshare(target_address):
	json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/cachevote')
	return json_response

def create_randshare(target_address, isBroadcast=False):
	if(not isBroadcast):
		json_response=SrvAPI.GET('http://'+target_address+'/test/randshare/create')
	else:
		SrvAPI.broadcast_GET(target_address, '/test/randshare/create', True)
		json_response = {'broadcast_create_randshare': 'Succeed!'}
	return json_response

'''def save_testlog(log_data):
	#save new key files
	test_dir = 'test_results'
	if(not os.path.exists(test_dir)):
	    os.makedirs(test_dir)
	test_file = test_dir + '/' + 'exec_time.log'
	FileUtil.AddLine(test_file, log_data)'''

# ====================================== validator test ==================================
def Epoch_validator(target_address, samples_head, samples_size, phase_delay=BOUNDED_TIME):
	'''
	This test network latency for one epoch life time:
	'''
	# Define ls_time_exec to save executing time to log
	ls_time_exec=[]

	# S1: send test transactions
	start_time=time.time()
	send_transaction(target_address, samples_head, samples_size, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# S2: start mining 
	start_time=time.time()   
	start_mining(target_address, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# S3: fix head of epoch 
	start_time=time.time()   
	check_head()
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# S4: voting block to finalize chain
	start_time=time.time() 
	start_voting(target_address, True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	logger.info("txs: {}    mining: {}    fix_head: {}    vote: {}\n".format(ls_time_exec[0],
										ls_time_exec[1], ls_time_exec[2], ls_time_exec[3]))
	# Prepare log messgae
	str_time_exec=" ".join(ls_time_exec)
	# Save to *.log file
	FileUtil.save_testlog('test_results', 'exec_time.log', str_time_exec)

# ====================================== Random share test ==================================
# # request for share from peers and cache to local
def cache_fetch_share(target_address):
	# read cached randshare
	host_shares=RandShare.load_sharesInfo(RandOP.RandDistribute)
	if( host_shares == None):
		host_shares = {}
	fetch_share=fetch_randshare(target_address)
	# logging.info(fetch_share)
	for (node_name, share_data) in fetch_share.items():
		host_shares[node_name]=share_data
	# update host shares 
	RandShare.save_sharesInfo(host_shares, RandOP.RandDistribute)

# request for recovered shares from peers and cache to local 
def cache_recovered_shares(target_address):
	# read cached randshare
	recovered_shares=RandShare.load_sharesInfo(RandOP.RandRecovered)
	if( recovered_shares == None):
		recovered_shares = {}
	host_recovered_shares=recovered_randshare(target_address)
	for (node_name, share_data) in host_recovered_shares.items():
		recovered_shares[node_name]=share_data
	# update host shares 
	RandShare.save_sharesInfo(recovered_shares, RandOP.RandRecovered)

# request for vote shares from peers and cache to local 
def cache_vote_shares(target_address):
	# read cached randshare
	vote_shares=RandShare.load_sharesInfo(RandOP.RandVote)
	if( vote_shares == None):
		vote_shares = {}
	host_vote_shares=fetchvote_randshare(target_address)
	# logging.info(host_vote_shares)
	for (node_name, share_data) in host_vote_shares.items():
		vote_shares[node_name]=share_data
	# update host shares 
	RandShare.save_sharesInfo(vote_shares, RandOP.RandVote)

# test recovered shares
def recovered_shares(host_address):		
	# read cached randshare
	recovered_shares=RandShare.load_sharesInfo(RandOP.RandRecovered)
	if( recovered_shares == None):
		recovered_shares = {}
	# print(recovered_shares)

	# get peer node information
	peer_nodes = PeerNodes()
	peer_nodes.load_ByAddress(host_address)
	json_nodes = TypesUtil.string_to_json(list(peer_nodes.get_nodelist())[0])
	# get public numbers given peer's pk
	public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

	# get shares information
	shares = recovered_shares[host_address]
	# print(shares)
	# instantiate RandShare to verify share proof.
	myrandshare = RandShare()
	myrandshare.p = public_numbers.n

	secret=myrandshare.recover_secret(shares)
	# print('secret recovered from node shares:', secret)
	return secret

# test new random generator
def new_random(ls_secret):
	# get host account information
	mywallet = Wallet()
	mywallet.load_accounts()
	json_nodes=mywallet.accounts[0]
	# get public numbers given pk
	public_numbers = RandShare.get_public_numbers(json_nodes['public_key'])

	# instantiate RandShare to verify share proof.
	myrandshare = RandShare()
	myrandshare.p = public_numbers.n

	# calculate new random number
	random_secret = myrandshare.calculate_random(ls_secret)

	logger.info("New random secret: {}".format(random_secret))


def Epoch_randomshare(phase_delay=BOUNDED_TIME):
	'''
	This test network latency for one epoch life time:
	'''
	# Define ls_time_exec to save executing time to log
	ls_time_exec=[]

	# get peer node information
	peer_nodes = PeerNodes()
	peer_nodes.load_ByAddress()

	# 1) create shares
	logger.info("1) Create shares")
	start_time=time.time()
	# for peer_node in list(peer_nodes.get_nodelist()):
	# 	json_node = TypesUtil.string_to_json(peer_node)
	# 	create_randshare(json_node['node_url'])
	create_randshare(peer_nodes.get_nodelist(), True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 2) fetch shares
	logger.info("2) Fetch shares")
	start_time=time.time()
	# for peer_node in list(peer_nodes.get_nodelist()):
	# 	json_node = TypesUtil.string_to_json(peer_node)
	# 	cache_fetch_share(json_node['node_url'])
	fetch_randshare(peer_nodes.get_nodelist(), True)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 3) verify received shares
	logger.info("3) Verify received shares")
	start_time=time.time()
	verify_randshare(peer_nodes.get_nodelist())
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 4) retrive vote shares from peers and verify them. need --threaded
	logger.info("4) Retrive vote shares from peers and verify them")
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		# cache_vote_shares(json_node['node_url'])
		vote_randshare(json_node['node_url'])
	# calculate voted shares 
	verify_vote = RandShare.verify_vote_shares()
	logging.info("verify_vote: {}".format(verify_vote))
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 5) retrive shares from peers for secret recover process
	logger.info("5) Retrive shares from peers for secret recovery process")
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		cache_recovered_shares(json_node['node_url'])
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 6) recover secret of each peer
	logger.info("6) Recover shared secret of each peer at local")
	ls_secret=[]
	start_time=time.time()
	for peer_node in list(peer_nodes.get_nodelist()):
		json_node = TypesUtil.string_to_json(peer_node)
		ls_secret.append(recovered_shares(json_node['address']))
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))

	time.sleep(phase_delay)

	# 7) calculate new random
	logger.info("7) Calculate new random")
	start_time=time.time()
	new_random(ls_secret)
	exec_time=time.time()-start_time
	ls_time_exec.append(format(exec_time*1000, '.3f'))
	

	# Prepare log messgae
	str_time_exec=" ".join(ls_time_exec)
	logging.info("{}\n".format(str_time_exec))
	# Save to *.log file
	FileUtil.save_testlog('test_results', 'exec_time_randshare.log', str_time_exec)

def checkpoint_netInfo(isDisplay=False):
	# get validators information in net.
	validator_info = validator_getinfo("0.0.0.0:8180", True)

	fininalized_count = {}
	justifized_count = {}
	processed_count = {}

	# Calculate all checkpoints count
	for validator in validator_info:
		# Calculate finalized checkpoint count
		if validator['highest_finalized_checkpoint']['hash'] not in fininalized_count:
			fininalized_count[validator['highest_finalized_checkpoint']['hash']] = 0
		fininalized_count[validator['highest_finalized_checkpoint']['hash']] += 1
		
		# Calculate justified checkpoint count
		if validator['highest_justified_checkpoint']['hash'] not in justifized_count:
			justifized_count[validator['highest_justified_checkpoint']['hash']] = 0
		justifized_count[validator['highest_justified_checkpoint']['hash']] += 1

		# Calculate processed checkpoint count
		if validator['processed_head']['hash'] not in processed_count:
			processed_count[validator['processed_head']['hash']] = 0
		processed_count[validator['processed_head']['hash']] += 1

	if(isDisplay):
		logger.info("")
		logger.info("Finalized checkpoints: {}\n".format(fininalized_count))
		logger.info("Justified checkpoints: {}\n".format(justifized_count))
		logger.info("Processed checkpoints: {}\n".format(processed_count))

	# search finalized checkpoint with maximum count
	checkpoint = ''
	max_acount = 0
	for _item, _value in fininalized_count.items():
		if(_value > max_acount):
			max_acount = _value
			checkpoint = _item	
	finalized_checkpoint = [checkpoint, max_acount]
	if(isDisplay):
		logger.info("Finalized checkpoint: {}    count: {}\n".format(finalized_checkpoint[0],
															   finalized_checkpoint[1]))

	# search finalized checkpoint with maximum count
	checkpoint = ''
	max_acount = 0
	for _item, _value in justifized_count.items():
		if(_value > max_acount):
			max_acount = _value
			checkpoint = _item	
	justified_checkpoint = [checkpoint, max_acount]
	if(isDisplay):
		logger.info("Justified checkpoint: {}    count: {}\n".format(justified_checkpoint[0],
															   justified_checkpoint[1]))

	# search finalized checkpoint with maximum count
	checkpoint = ''
	max_acount = 0
	for _item, _value in processed_count.items():
		if(_value > max_acount):
			max_acount = _value
			checkpoint = _item	
	processed_checkpoint = [checkpoint, max_acount]
	if(isDisplay):
		logger.info("Processed checkpoint: {}    count: {}\n".format(processed_checkpoint[0],
															   processed_checkpoint[1]))

	json_checkpoints={}
	json_checkpoints['finalized_checkpoint'] = finalized_checkpoint
	json_checkpoints['justified_checkpoint'] = justified_checkpoint
	json_checkpoints['processed_checkpoint'] = processed_checkpoint

	return json_checkpoints

def count_tx_size():
    json_response=SrvAPI.GET('http://'+target_address+'/test/chain/get')
    chain_data = json_response['chain']
    chain_length = json_response['length']
    logger.info('Chain length: {}'.format(chain_length))
    for block in chain_data:
        if(block['transactions']!=[]):          
            tx=block['transactions'][0]
            tx_str=TypesUtil.json_to_string(tx)
            logger.info('Tx size: {}'.format(len( tx_str.encode('utf-8') )))
            break

def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(
	    description="Run websocket client."
	)
	parser.add_argument("--test_func", type=int, default=2, help="test function: \
															0: set peer nodes \
															1: validator test \
															2: single step test \
															3: randshare test")
	parser.add_argument("--op_status", type=int, default=0, help="test case type.")
	parser.add_argument("--test_round", type=int, default=1, help="test evaluation round")
	parser.add_argument("--samples_head", type=int, default=0, help="Start point of ENF samples data for node.")
	parser.add_argument("--samples_size", type=int, default=60, help="Size of ENF samples list from node.")
	parser.add_argument("--wait_interval", type=int, default=1, help="break time between step.")
	parser.add_argument("--target_address", type=str, default="0.0.0.0:8180", 
						help="Test target address - ip:port.")
	parser.add_argument("--set_peer", type=str, default="", 
						help="set peer node. name@op")
	args = parser.parse_args(args=args)
	return args

if __name__ == "__main__":
    FORMAT = "%(asctime)s %(levelname)s | %(message)s"
    LOG_LEVEL = logging.INFO
    logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

    ## get arguments
    args = define_and_get_arguments()

    ## set parameters
    target_address = args.target_address
    test_func = args.test_func
    op_status = args.op_status
    wait_interval = args.wait_interval
    test_run = args.test_round
    samples_head = args.samples_head
    samples_size = args.samples_size

    ## |------------------------ test function type -----------------------------|
    ## | 0:set peer nodes | 1:round test | 2:single step test | 3:randshare test |
    ## |-------------------------------------------------------------------------|

    if(test_func == 0):
    	set_peer = args.set_peer
    	if(set_peer!=''):
    		name_op=set_peer.split('@')
    		# print(name_op[0], name_op[1])
    		# set_peerNodes('R2_pi4_4', 1, True)
    		set_peerNodes(name_op[0], int(name_op[1]), True)
    elif(test_func == 1):
    	for x in range(test_run):
    		logger.info("Test run:{}".format(x+1))
    		Epoch_validator(target_address, samples_head, samples_size, 5)
    		time.sleep(wait_interval)

    	# get checkpoint after execution
    	json_checkpoints = checkpoint_netInfo(False)
    	for _item, _value in json_checkpoints.items():
    		logger.info("{}: {}    {}".format(_item, _value[0], _value[1]))

    elif(test_func == 2):
        if(op_status == 1):
            send_transaction(target_address, samples_head, samples_size, True)
        elif(op_status == 2):
            start_mining(target_address, True)
        elif(op_status == 3):
            check_head()
        elif(op_status == 4):
            start_voting(target_address, True)
        elif(op_status == 11):
            get_transactions(target_address)
        elif(op_status == 12):
            get_chain(target_address, True)
        elif(op_status == 13):
            count_tx_size()
        elif(op_status == 9):
            run_consensus(target_address, True, True)
        else:
            json_checkpoints = checkpoint_netInfo(False)
            for _item, _value in json_checkpoints.items():
                logger.info("{}: {}    {}".format(_item, _value[0], _value[1])) 
    else:
        # host_address='ceeebaa052718c0a00adb87de857ba63608260e9'
        # cache_fetch_share(target_address)
        # verify_share(host_address)
        # cache_recovered_shares(target_address)
        # recovered_shares(host_address)
        # print(create_randshare(target_address))
        # cache_vote_shares(target_address)
        # print(verify_vote_shares())
        # vote_randshare(target_address)

        for x in range(test_run):
            logger.info("Test run:{}".format(x+1))
            Epoch_randomshare()
            time.sleep(wait_interval)