#!/usr/bin/env python

'''
========================
service_api module
========================
Created on Nov.2, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide web service url API that access to Web service.
'''

import requests
import json
import threading
from utilities import TypesUtil

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

        # Launch request given ReqType-0: GET; 1: POST;
        if(self.ReqType==1):
            requests.post(self.argv[0], data=json.dumps(self.argv[1]), headers=self.argv[2])
        else:
            requests.get(self.argv[0], data=json.dumps({}), headers=self.argv[1])

        # print ("Exiting ReqThread:{}".format(self.threadID))

class SrvAPI(object):
    '''
    Post data to add record
    '''
    @staticmethod
    def POST(api_url, transaction):          
    	headers = {'Content-Type' : 'application/json'}
    	response = requests.post(api_url, data=json.dumps(transaction), headers=headers)

    	#get response json
    	json_response = response.json()      

    	return json_response

    @staticmethod
    def GET(api_url, data_args={}):          
        headers = {'Content-Type' : 'application/json'}
        response = requests.get(api_url, data=json.dumps(data_args), headers=headers)

        #get response json
        json_response = response.json()      

        return json_response

    @staticmethod
    def broadcast_POST(peer_nodes, msg_data, ws_url):
        '''
         broadcast message to peer nodes
         @ msg_data: input message as json format
         @ peer_nodes: peer node set()
        '''
        headers = {'Content-Type' : 'application/json'}

        # Create thread pool
        threads_pool = []
        i=0
        for node in list(peer_nodes):
            json_node = TypesUtil.string_to_json(node)
            api_url = 'http://' + json_node['node_url'] + ws_url
            #SrvAPI.POST(api_url, msg_data)
            # requests.post(api_url, data=json.dumps(msg_data), headers=headers)

            i+=1
            # Create new threads
            p_thread = ReqThread(i, 1, [api_url, msg_data, headers])

            # append to threads pool
            threads_pool.append(p_thread)

            # The start() method starts a thread by calling the run method.
            p_thread.start()

        # The join() waits for all threads to terminate.
        for p_thread in threads_pool:
                p_thread.join()

    @staticmethod
    def broadcast_GET(peer_nodes, ws_url):
        '''
         broadcast message to peer nodes using GET
         @ msg_data: input message as json format
         @ peer_nodes: peer node set()
        '''
        headers = {'Content-Type' : 'application/json'}

        # Create thread pool
        threads_pool = []
        i=0
        for node in list(peer_nodes):
            json_node = TypesUtil.string_to_json(node)
            api_url = 'http://' + json_node['node_url'] + ws_url
            #SrvAPI.POST(api_url, msg_data)
            # requests.get(api_url, data=json.dumps({}), headers=headers)

            i+=1
            # Create new threads
            p_thread = ReqThread(i, 0, [api_url, headers])

            # append to threads pool
            threads_pool.append(p_thread)

            # The start() method starts a thread by calling the run method.
            p_thread.start()

        # The join() waits for all threads to terminate.
        for p_thread in threads_pool:
                p_thread.join()
