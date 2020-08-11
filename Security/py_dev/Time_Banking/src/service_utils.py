#!/usr/bin/env python3.5

'''
========================
Test_Client module
========================
Created on August.11, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of TB SrvExchangeClient API that access to Web service.
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
    Get service exchange information
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def getService(data_args={}):
        #construct api_url
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/TB/api/v1.0/getService"
        headers = {'Content-Type' : 'application/json'}

        response = requests.get(api_url,data=json.dumps(data_args), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Get account data based on address
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def getAccount(data_args={}):
        #construct api_url
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/TB/api/v1.0/getAccount"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']

        response = requests.get(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response
    
    '''
    Send register service transaction
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def registerService(data_args={}):
        #construct api_url
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/TB/api/v1.0/registerService"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']
        data_json['op_state'] = data_args['op_state']
        data_json['service_info'] = data_args['service_info']

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send negotiate service transaction
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def negotiateService(data_args={}):
        #construct api_url
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/TB/api/v1.0/negotiateService"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']
        data_json['op_state'] = data_args['op_state']
        data_json['time_currency'] = data_args['time_currency']

        response = requests.post(api_url,data=json.dumps(data_json), headers=headers)

        #get response json
        json_response = response.json()

        return json_response

    '''
    Send commit service transaction
    @host_addr: ip_address:port_num
    '''
    @staticmethod
    def commitService(data_args={}):
        #construct api_url
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/TB/api/v1.0/commitService"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']

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
        #construct api_url
        host_addr = data_args['host_ip']
        api_url = "http://" + host_addr + "/TB/api/v1.0/paymentService"
        headers = {'Content-Type' : 'application/json'}

        data_json={}
        data_json['client_addr']=data_args['host_address']

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

