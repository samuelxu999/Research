'''
========================
Swarm_RPC module
========================
Created on Dec.9, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of basic API that access to RPC server side of Swarm node.
'''

import requests
import json
import random
import threading
import queue
from utils.utilities import FileUtil, TypesUtil
from utils.configuration import *

# query swarm node tx timeout.
TX_TIMEOUT = 3.0
TX_INTERVAL = 0.1

class SwarmThread(threading.Thread):
	'''
	Threading class to query ENF samples from swarm nodes by multiple threads pool
	argv structure: [ ret_queue, [ENF_id, ENF_transaction] ]
	'''
	def __init__(self, argv):
		threading.Thread.__init__(self)
		self.argv = argv

	#The run() method is the entry point for a thread.
	def run(self):
		## set parameters based on argv
		ENF_id = self.argv[1][0]
		ENF_transaction = self.argv[1][1]

		## query ENF sample from a swarm node
		json_value = TypesUtil.string_to_json(ENF_transaction['value'])
		swarm_hash = json_value['swarm_hash']
		tx_time = 0.0
		while(True):
			## random choose a swarm server
			target_address = Swarm_RPC.get_service_address()
			query_data = Swarm_RPC.download_data(target_address,swarm_hash)['data']
			if(query_data!=""):
				json_data = TypesUtil.string_to_json(query_data)
				## save results into queue
				self.argv[0].put(  [ENF_id, json_data['enf'], json_data['id']] )
				break
			## query step incremental
			time.sleep(TX_INTERVAL)
			tx_time +=TX_INTERVAL
			## check timeout status.
			if(tx_time>=TX_TIMEOUT):
				break

class Swarm_RPC(object):
	'''
	Swarm RPC class to provide client-based RESTfull APIs
	'''
	@staticmethod
	def download_data(target_address, swarm_hash):
		'''
		fetch data from swarm node
		'''
		headers = {'Content-Type' : 'application/json'}
		api_url = 'http://'+target_address+'/swarm/data/download'
		data_args = {}
		data_args['hash']=swarm_hash

		response = requests.get(api_url, data=json.dumps(data_args), headers=headers)

		json_results = {}
		json_results['status']=response.status_code
		if(json_results['status']==200):
			json_results['data']=response.json()['data']
		else:
			json_results['data']=''

		return json_results


	def upload_data(target_address, tx_json):
		'''
		save data on swarm node
		'''
		headers = {'Content-Type' : 'application/json'}
		api_url = 'http://'+target_address+'/swarm/data/upload'
		data_args = {}
		data_args['data']=tx_json

		response = requests.post(api_url, data=json.dumps(data_args), headers=headers)

		json_results = {}
		json_results['status']=response.status_code
		if(json_results['status']==200):
			json_results['data']=response.json()['data']
		else:
			json_results['data']=''

		return json_results

	def get_service_address():
		'''
		random choose a swarm server from node list 
		'''
		services_host = FileUtil.JSON_load(SWARM_SERVER)
		server_id = random.randint(0,len(services_host['all_nodes'])-1)

		## get address of swarm server
		target_address = services_host['all_nodes'][server_id]

		return target_address

	def get_ENFsamples(ls_transactions):
		'''
		get ENFsamples given transactions list
		'''
		## Create queue to save results
		ret_queue = queue.Queue()
		# Create thread pool
		threads_pool = []
		## Create a list to save ENF samples from swarm node
		ENF_samples = []
		
		ENF_id=0
		## 1) For each transaction and assign querying task to a SwarmThread
		for str_transaction in ls_transactions:
			## Create new threads for tx
			p_thread = SwarmThread( [ret_queue, [ENF_id, str_transaction]] )

			## append to threads pool
			threads_pool.append(p_thread)

			## The start() method starts a thread by calling the run method.
			p_thread.start()

			ENF_id=ENF_id+1

		# 2) The join() waits for all threads to terminate.
		for p_thread in threads_pool:
			p_thread.join()

		# 3) get all results from queue
		while not ret_queue.empty():
			q_data = ret_queue.get()
			ENF_samples.append(q_data)

		# sorted ENF_samples before return
		sorted_ENF_samples = sorted(ENF_samples, key=lambda x:x[0])

		return sorted_ENF_samples

