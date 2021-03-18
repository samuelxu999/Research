'''
========================
SrvExchange_Server module
========================
Created on March.17, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of Fed-DDM Server API that handle and response client's request.
'''

import time
import sys
import logging
from argparse import ArgumentParser

from flask import Flask, jsonify
from flask import abort,make_response,request

from utils.utilities import FileUtil, TypesUtil
from utils.SrvExchangeToken import SrvExchangeToken

app = Flask(__name__)

## --------------------------- global variable ----------------------------
addr_list = './addr_list.json'
http_provider = 'http://localhost:8042'
contract_addr = SrvExchangeToken.getAddress('SrvExchangeToken', addr_list)
contract_config = '../contract_dev/build/contracts/SrvExchange.json'


## create SrvExchangeToken object to support contract interface
mySrvExchange=SrvExchangeToken(http_provider, contract_addr, contract_config)

#========================================== Error handler ===============================================
#Error handler for abort(404) 
@app.errorhandler(404)
def not_found(error):
    #return make_response(jsonify({'error': 'Not found'}), 404)
	response = jsonify({'result': 'Failed', 'message':  error.description['message']})
	response.status_code = 404
	return response

#Error handler for abort(400) 
@app.errorhandler(400)
def type_error(error):
    #return make_response(jsonify({'error': 'type error'}), 400)
    response = jsonify({'result': 'Failed', 'message':  error.description['message']})
    response.status_code = 400
    return response
	
#Error handler for abort(401) 
@app.errorhandler(401)
def access_deny(error):
    response = jsonify({'result': 'Failed', 'message':  error.description['message']})
    response.status_code = 401
    return response

	
#========================================== Request handler ===============================================	
## GET query broker information: publisher and subscriber
@app.route('/Fed-DDM/api/v1.0/getBroker', methods=['GET'])
def getBroker():

	start_time=time.time()
	publisher_info = mySrvExchange.getPublisher()
	subscriber_info = mySrvExchange.getSubscriber()
	exec_time=time.time()-start_time
	FileUtil.save_testlog('test_results', 'exec_getBroker.log', format(exec_time*1000, '.3f'))

	host_account = mySrvExchange.getHostAccounts()[0]
	host_balance = mySrvExchange.getHostBalance(host_account)

	json_data={}

	json_data['host']={}
	json_data['host']['account']=host_account
	json_data['host']['balance']=format(host_balance, '.3f')

	json_data['publisher']={}
	json_data['publisher']['vid']=publisher_info[0]
	json_data['publisher']['zid']=publisher_info[1]
	json_data['publisher']['status']=publisher_info[2]
	json_data['publisher']['balance']=publisher_info[3]
	json_data['publisher']['txs']=publisher_info[4]

	json_data['subscriber']={}
	json_data['subscriber']['vid']=subscriber_info[0]
	json_data['subscriber']['zid']=subscriber_info[1]
	json_data['subscriber']['status']=subscriber_info[2]
	json_data['subscriber']['balance']=subscriber_info[3]
	json_data['subscriber']['txs']=subscriber_info[4]

	return jsonify({'result': 'Succeed', 'data': json_data}), 201

## POST: initialize publisher (or subscriber) data in broker
@app.route('/Fed-DDM/api/v1.0/initalizeBroker', methods=['POST'])
def initalizeBroker():

	mySrvExchange.initBroker()

	return jsonify({'initalizeBroker': 'Finish'}), 201

## POST: set publisher (or subscriber) to delegate seller (or buyer) 
@app.route('/Fed-DDM/api/v1.0/delegateBroker', methods=['POST'])
def delegateBroker():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_data = TypesUtil.string_to_json(req_data)

	client_addr = json_data['client_addr']
	op_state = json_data['op_state']
	zone_id = json_data['zid']
	str_txs = json_data['txs']

	if(op_state==1):
		mySrvExchange.setSubscriber(client_addr, zone_id, str_txs)
	else:
		mySrvExchange.setPublisher(client_addr, zone_id, str_txs)

	return jsonify({'delegateBroker': 'Succeed'}), 201

## POST: update publisher (or subscriber) for delegated seller (or buyer)
@app.route('/Fed-DDM/api/v1.0/updateBroker', methods=['POST'])
def updateBroker():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_data = TypesUtil.string_to_json(req_data)

	client_addr = json_data['client_addr']
	op_state = json_data['op_state']
	zone_id = json_data['zid']

	if(op_state==1):
		mySrvExchange.updateSubscriber(client_addr, zone_id)
	else:
		mySrvExchange.updatePublisher(client_addr, zone_id)

	return jsonify({'updateBroker': 'Succeed'}), 201

## POST: change publisher (or subscriber) to commitmemt
@app.route('/Fed-DDM/api/v1.0/commitService', methods=['POST'])
def commitService():
	# parse data from request.data
	req_data=TypesUtil.bytes_to_string(request.data)
	json_data = TypesUtil.string_to_json(req_data)

	op_state = json_data['op_state']
	balance = json_data['balance']

	if(op_state==1):
		mySrvExchange.subscriber_commit(balance)
	else:
		mySrvExchange.publisher_commit()

	return jsonify({'commitService': 'Succeed'}), 201

## POST: change publisher (or subscriber) to payment
@app.route('/Fed-DDM/api/v1.0/paymentService', methods=['POST'])
def paymentService():

	mySrvExchange.service_payment()

	return jsonify({'paymentService': 'Succeed'}), 201

def define_and_get_arguments(args=sys.argv[1:]):
	parser = ArgumentParser(description="Run Fed-DDM Broker websocket server.")

	parser.add_argument('-p', '--port', default=80, type=int, 
						help="port to listen on.")
	parser.add_argument("--debug", action="store_true", 
						help="if set, debug model will be used.")
	parser.add_argument("--threaded", action="store_true", 
						help="if set, support threading request.")

	args = parser.parse_args()
	return args
	
if __name__ == '__main__':
	## get arguments
	args = define_and_get_arguments()

	app.run(host='0.0.0.0', port=args.port, debug=args.debug, threaded=args.threaded)
