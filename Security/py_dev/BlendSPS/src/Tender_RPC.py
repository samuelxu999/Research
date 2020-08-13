#!/usr/bin/env python3

'''
========================
Tender_RPC module
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

class Tender_RPC(object):

    '''
    Get abci_info:     curl -s 'localhost:26657/abci_info'
    '''
    @staticmethod
    def abci_info():
        headers = {'Content-Type' : 'application/json'}
        response = requests.get('http://localhost:26657/abci_info', headers=headers)

        #get response json
        json_response = response.json()      

        return json_response
    

    '''
    Execute abci_query: curl -s 'localhost:26657/abci_query?data="abcd"'
    '''
    # @staticmethod
    def abci_query(params_json={}):            
        headers = {'Content-Type' : 'application/json'}
        api_url='http://localhost:26657/abci_query'
 
        response = requests.get(api_url, params=params_json, headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response

    '''
    Send transaction to network
    curl -s 'localhost:26657/broadcast_tx_commit?tx="sam"'
    '''
    @staticmethod
    def broadcast_tx_commit(params_json={}):          
        headers = {'Content-Type' : 'application/json'}
        api_url='http://localhost:26657/broadcast_tx_commit'

        response = requests.post(api_url, params=params_json, headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response

