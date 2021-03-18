#!/usr/bin/env python3.5

'''
========================
Test_Client module
========================
Created on March.17, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of Fed-DDM client RESTful APIs that access to broker server.
'''
import time
import requests
import datetime
import json
import logging

LOG_INTERVAL = 25


logger = logging.getLogger(__name__)
    
class SrvExchangeClient(object):
    '''
    Get broker information: [host, publisher, subscriber]
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def getBroker(data_args={}):
        ## -------------- construct api_url ------------------------
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/Fed-DDM/api/v1.0/getBroker"
        headers = {'Content-Type' : 'application/json'}

        response = requests.get(api_url,data=json.dumps(data_args), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send payment service transaction
    '''
    @staticmethod
    def initalizeBroker(data_args={}):
        ## -------------- construct api_url ------------------------
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/Fed-DDM/api/v1.0/initalizeBroker"
        headers = {'Content-Type' : 'application/json'}

        data_json={}

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send delegate broker transaction
    '''
    @staticmethod
    def delegateBroker(data_args={}):
        ## -------------- construct api_url ------------------------
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/Fed-DDM/api/v1.0/delegateBroker"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']
        data_json['op_state'] = data_args['op_state']
        data_json['zid'] = data_args['zone_id']
        data_json['txs'] = data_args['tx_ref']

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send update broke transaction
    '''
    @staticmethod
    def updateBroker(data_args={}):
        ## -------------- construct api_url ------------------------
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/Fed-DDM/api/v1.0/updateBroker"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']
        data_json['op_state'] = data_args['op_state']
        data_json['zid'] = data_args['zone_id']

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send commit service transaction
    '''
    @staticmethod
    def commitService(data_args={}):
        ## -------------- construct api_url ------------------------
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/Fed-DDM/api/v1.0/commitService"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['op_state'] = data_args['op_state']
        data_json['balance'] = data_args['balance']

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send payment service transaction
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def paymentService(data_args={}):
        ## -------------- construct api_url ------------------------
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/Fed-DDM/api/v1.0/paymentService"
        headers = {'Content-Type' : 'application/json'}

        data_json={}

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Get BC_account given node_name
    @node_name: ip_address:port_num
    @datafile: node account datafile path
    '''
    @staticmethod
    def getAddress(node_name, datafile):
        address_json = json.load(open(datafile))
        return address_json[node_name]

