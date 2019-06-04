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
