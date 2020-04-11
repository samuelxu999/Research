#!/usr/bin/env python3

'''
========================
PRC_Client module
========================
Created on Feb.9, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of basic API that access to Tendermint RPC.
'''

import requests
import json
import time
import os
from utilities import TypesUtil,FileUtil
from RPC_Client import PRC_Client
import threading

class ReqThread (threading.Thread):
	'''
	Threading class to handle requests by multiple threads pool
	'''
	def __init__(self, threadID, ReqType, argv):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.ReqType = ReqType
		self.argv = argv

	#The run() method is the entry point for a thread.
	def run(self):
		# Add task operation here
		# print ("Starting ReqThread:{}".format(self.threadID))

		# Launch request given ReqType-0: query; 1: tx_commit;
		if(self.ReqType==1):
			# requests.post(self.argv[0], data=json.dumps(self.argv[1]), headers=self.argv[2])
			tx_ret=PRC_Client.broadcast_tx_commit(self.argv[0])
			# print(tx_ret)
		else:
			# requests.get(self.argv[0], data=json.dumps({}), headers=self.argv[1])
			query_ret=PRC_Client.abci_query(self.argv[0])
			print_query(query_ret)

		# print ("Exiting ReqThread:{}".format(self.threadID))


def print_query(query_ret):

	key_str = query_ret['result']['response']['key']
	if(key_str != None):
	    print("key:"+TypesUtil.base64_to_ascii(key_str))

	value_str = query_ret['result']['response']['value']
	if(value_str != None):
		str_ascii = TypesUtil.base64_to_ascii(value_str)
		print("value:"+str_ascii)   


def query_threads(thread_count=1, isjoin=True):
	# Create thread pool
	threads_pool = []
	i=0

	for i in range(1,thread_count+1):
		query_json = {}
		# ------------------------kvstore ----------------------
		key_str = str(i)
		# using key string to query data
		query_json['data']='"' + key_str +'"'

		# Create new threads
		p_thread = ReqThread(i, 0, [ query_json ])

		# append to threads pool
		threads_pool.append(p_thread)

		# The start() method starts a thread by calling the run method.
		p_thread.start()
	    
	if(isjoin):
		# The join() waits for all threads to terminate.
		for p_thread in threads_pool:
			p_thread.join()

def tx_threads(thread_count=1, isjoin=True):
	# Create thread pool
	threads_pool = []
	i=0

	for i in range(1,thread_count+1):
		# ------------------------kvstore ----------------------
		tx_json = {}
		tx_size = 128*1024
		# generate random data string given size
		tx_value = TypesUtil.string_to_hex(os.urandom(tx_size))
		
		# ----------------- 2) key:value --------------
		json_value={}
		json_value['name']="samuel" + str(i)
		# json_value['data']=36
		json_value['data']=tx_value
		
		# build key:value parameter
		key_str = str(i)
		value_str = TypesUtil.json_to_tx(json_value)  
		# print(value_str) 

		# In tx_data, " must replace with ', for json: 'id={\'address\':\'hamilton\'}' 
		tx_data = key_str + "=" + value_str 

		# --------- build parameter string: tx=? --------
		tx_json['tx']='"' + tx_data +'"' 
		# print(tx_json)

		# Create new threads
		p_thread = ReqThread(i, 1, [ tx_json ])

		# append to threads pool
		threads_pool.append(p_thread)

		# The start() method starts a thread by calling the run method.
		p_thread.start()
	    
	if(isjoin):
		# The join() waits for all threads to terminate.
		for p_thread in threads_pool:
			p_thread.join()

if __name__ == "__main__":
	thread_count = 1
	wait_interval = 1
	test_run = 5

	for x in range(test_run):
		print("Test run:", x+1)

		start_time=time.time()

		#==================== query data=========================
		# query_threads(thread_count)

		#==================== tx data=========================
		tx_threads(thread_count)

		exec_time=time.time()-start_time
		print(format(exec_time*1000, '.3f'))
		FileUtil.save_testlog('test_results', 'exec_time.log', format(exec_time*1000, '.3f'))

		time.sleep(wait_interval)

	pass
