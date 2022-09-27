'''
========================
UAV_Server module
========================
Created on Sep.26, 2022
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide server API that handle and response client's request.
'''

import sys
import time, datetime
import json
import threading
import logging
import random
from argparse import ArgumentParser

from flask import Flask, jsonify
from flask import abort,make_response,request

from utils.utilities import TypesUtil, FileUtil, DatetimeUtil
from utils.Client_RPC import Client_RPC

logger = logging.getLogger(__name__)

app = Flask(__name__)

class UAV_Service():
	'''
	UAV service class handle blockchain nodes
	'''
	def __init__(self, bootstrapnode, refresh_rate):
		## Instantiate the Client_RPC
		self.bootstrapnode = bootstrapnode
		self.refresh_rate = refresh_rate
		self.alive_nodes = []
		self.client_rpc =  Client_RPC(self.bootstrapnode)
		
		## new a thread to refresh nodes
		self.nodes_thread = threading.Thread(target=self.refresh_nodes, args=())
		self.nodes_thread.daemon = True
		self.nodes_thread.start()

	def refresh_nodes(self):
		'''
		daemon thread function: refresh nodes in blockchain
		'''
		while(True):
			logger.info("Refresh alive nodes' information")
			try:
				self.alive_nodes = self.client_rpc.query_neighbors(self.bootstrapnode)['neighbors']
			except:
				logger.info('\n! Some error happen in refresh_nodes.\n')
			finally:		
				## wait for next refresh time line
				time.sleep(self.refresh_rate)

##========================================== Error handler ===============================================
##Error handler for abort(404) 
@app.errorhandler(404)
def not_found(error):
	#return make_response(jsonify({'error': 'Not found'}), 404)
	response = jsonify({'result': 'Failed', 'message':  error.description['message']})
	response.status_code = 404
	return response

##Error handler for abort(400) 
@app.errorhandler(400)
def type_error(error):
	#return make_response(jsonify({'error': 'type error'}), 400)
	response = jsonify({'result': 'Failed', 'message':  error.description['message']})
	response.status_code = 400
	return response
	
##Error handler for abort(401) 
@app.errorhandler(401)
def access_deny(error):
	response = jsonify({'result': 'Failed', 'message':  error.description['message']})
	response.status_code = 401
	return response


## ============================== AC verify procedures =======================
def is_token_expired(json_token):
	## sexpire time
	now_stamp = DatetimeUtil.datetime_timestamp(datetime.datetime.now())
	if(  now_stamp > json_token['expire_time'] ):
		print("expire_time validation fail!")
		return False
	return True	

def is_ac_valid(json_token, access_args):
	if(json_token['resource']!=str(access_args['url_rule'])):
		print("resource validation fail!")
		return False

	## check if timespan condition is valid
	starttime = DatetimeUtil.string_datetime(json_token['start_time'], "%H:%M:%S")
	endtime = DatetimeUtil.string_datetime(json_token['end_time'], "%H:%M:%S")
	nowtime=DatetimeUtil.string_datetime(datetime.datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")

	if(not (starttime<nowtime<endtime) ):
		print("condition validation fail!")
		return False	
	return True

#========================================== Request handler ===============================================	
#GET req for specific ID
@app.route('/drone/api/v1.0/uav/data', methods=['GET'])
def get_data():
	req_data=TypesUtil.bytes_to_string(request.data)
	json_data=json.loads(req_data)
	if(json_data == '{}'):
		abort(401, {'message': 'AC Token receipt missing, deny access'})

	if( json_data['ac_receipt']!="" ):	
		## random choose a peer node. 
		node_idx = random.randint(0,len(uav_service.alive_nodes)-1)
		node_url = uav_service.alive_nodes[node_idx][0]+':808'+str(uav_service.alive_nodes[node_idx][1])[-1]
		
		## query capAC
		list_tx = uav_service.client_rpc.query_tx(node_url, json_data['ac_receipt'])

		if(len(list_tx)==0):
			abort(401, {'message': 'cannot find AC token, deny access'})
		
		token_data = TypesUtil.string_to_json(list_tx[0][2])['value']
		capAC_token = TypesUtil.string_to_json(token_data)
		print(capAC_token)

		## verify if token has been expired
		if(not is_token_expired(capAC_token)):
			abort(401, {'message': 'AC token has been expired, deny access'})

		## verify access right
		acess_args={}
		acess_args['url_rule']=request.url_rule
		if(not is_ac_valid(capAC_token['access_right'], acess_args)):
			abort(401, {'message': 'acccess right is not valid, deny access'})
	
	## finally, grand access to data query
	uav_data = FileUtil.List_load("data/MAVLink_message_data.pkl")

	ret_data = {}
	for e in uav_data['_fieldnames']:
		ret_data[e]= uav_data[e]
	return jsonify({'result': 'Succeed', 'data': ret_data}), 201

def define_and_get_arguments(args=sys.argv[1:]):
	parser = ArgumentParser(description="Run uav_server websocket server.")
	parser.add_argument('-p', '--port', default=8088, type=int, 
						help="port to listen on.")
	parser.add_argument("--debug", action="store_true", 
						help="if set, debug model will be used.")
	parser.add_argument("--threaded", action="store_true", 
						help="if set, support threading request.")
	parser.add_argument("--bootstrapnode", default='128.226.88.250:8080', type=str, 
						help="bootstrap node address format[ip:port] to join the network.")
	parser.add_argument('--refresh_nodes', default=60, type=int, 
							help="frequency for refresh_nodes().")
	args = parser.parse_args()

	return args

if __name__ == '__main__':
	FORMAT = "%(asctime)s %(levelname)s %(filename)s(l:%(lineno)d) - %(message)s"
	# FORMAT = "%(asctime)s %(levelname)s | %(message)s"
	LOG_LEVEL = logging.INFO
	logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

	## get arguments
	args = define_and_get_arguments()

	## ------------------------ Instantiate the Client_RPC ----------------------------------
	uav_service = UAV_Service(args.bootstrapnode, args.refresh_nodes)

	## -------------------------------- run app server ----------------------------------------
	app.run(host='0.0.0.0', port=args.port, debug=args.debug, threaded=args.threaded)