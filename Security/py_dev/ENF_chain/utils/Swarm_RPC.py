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
from utils.utilities import FileUtil
from utils.configuration import *

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

