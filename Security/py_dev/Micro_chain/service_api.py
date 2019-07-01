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

from utilities import TypesUtil

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
    def broadcast(peer_nodes, msg_data, ws_url):
        '''
         broadcast message to peer nodes
         @ msg_data: input message as json format
         @ peer_nodes: peer node set()
        '''
        headers = {'Content-Type' : 'application/json'}
        for node in list(peer_nodes):
            json_node = TypesUtil.string_to_json(node)
            api_url = 'http://' + json_node['node_url'] + ws_url
            #SrvAPI.POST(api_url, msg_data)
            requests.post(api_url, data=json.dumps(msg_data), headers=headers)
