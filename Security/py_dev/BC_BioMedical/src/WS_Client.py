#!/usr/bin/env python3.5

'''
========================
WS_Client module
========================
Created on Sep.15, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of client API that access to Web service.
'''
import time
import requests
import datetime
import json

from PatientACToken import PatientACToken

import sys
from utilities import DatetimeUtil, TypesUtil, FileUtil

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

#global variable
http_provider = 'http://localhost:8042'
contract_addr = PatientACToken.getAddress('PatientACToken', './addr_list.json')
contract_config = '../contracts/build/contracts/PatientACToken.json'

#new PatientACToken object
myPatientACToken=PatientACToken(http_provider, contract_addr, contract_config)

 
class WSClient(object):
    
    '''
    Get all dataset
    '''
    @staticmethod
    def Get_Datasets(api_url, data_args={}):          
        headers = {'Content-Type' : 'application/json'}
        response = requests.get(api_url, data=json.dumps(data_args), headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Get record by id
    '''
    @staticmethod
    def Get_DataByID(api_url, params, data_args={} ):          
        headers = {'Content-Type' : 'application/json'}
        response = requests.get(api_url,params=params, data=json.dumps(data_args), headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Post data to add record
    '''
    @staticmethod
    def Create_Data(api_url, data):          
        headers = {'Content-Type' : 'application/json'}
        response = requests.post(api_url, data=json.dumps(data), headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Put updated data
    '''
    @staticmethod
    def Update_Data(api_url, data):          
        headers = {'Content-Type' : 'application/json'}
        response = requests.put(api_url, data=json.dumps(data), headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Put id to delete data
    '''
    @staticmethod
    def Delete_Data(api_url, data):          
        headers = {'Content-Type' : 'application/json'}
        response = requests.delete(api_url, data=json.dumps(data), headers=headers)
        
        #get response json
        json_response = response.json()      

        return json_response

def test_search(data_args={}):
	params={}
	if('project_id' in data_args):
		params['project_id']=data_args['project_id']
	else:
		params['project_id']=0

	SP_ipaddress = data_args['host_ip']
	print(WSClient.Get_Datasets('http://' + SP_ipaddress + '/test/api/v1.0/dt', data_args))
	#print(WSClient.Get_DataByID('http://' + SP_ipaddress + '/test/api/v1.0/dt/project', params, data_args))
    
def test_add(data_args={}):
	project = {
		'title': 'post_new',
		'description': 'post_description',
		'date': datestr,
		'time': timestr
	}
	project_data = {'project_data':project}
	project_data['host_address'] = data_args['host_address']	

	SP_ipaddress = data_args['host_ip']
	json_response=WSClient.Create_Data('http://' + SP_ipaddress + '/test/api/v1.0/dt/create',project_data)

	print(json_response)
    
def test_update(data_args={}):
	project = {
		'title': 'update_test',
		'description': 'update_description',
		'date': datestr,
		'time': timestr
	}	
	project['id'] = data_args['project_id']
	project_data = {'project_data':project}
	project_data['host_address'] = data_args['host_address']

	SP_ipaddress = data_args['host_ip']
	json_response=WSClient.Update_Data('http://' + SP_ipaddress + '/test/api/v1.0/dt/update',project_data)
	print(json_response)
    
def test_delete(data_args={}):
	#project_data = {'id': 5}
	project_data = {}
	project_data['id'] = data_args['project_id']
	project_data['host_address'] = data_args['host_address']

	SP_ipaddress = data_args['host_ip']
	json_response=WSClient.Delete_Data('http://' + SP_ipaddress + '/test/api/v1.0/dt/delete',project_data)
	print(json_response)

	
def test_CapAC():
	# set host id address
	host_ip = '128.226.77.237'
	#host_ip = '128.226.77.51'
	test_address = PatientACToken.getAddress('sam_ubuntu', './addr_list.json')
	
	# get host account
	accounts = myPatientACToken.getAccounts()
	# set project id
	project_id = 3

	# construct data argument
	data_args = {}
	data_args ['project_id'] = project_id
	data_args ['host_ip'] = host_ip
	data_args ['host_address'] = test_address
	
	start_time=time.time()
	
	#------------------ test data access service API ------------------	
	#test_add(data_args)
	#test_update(data_args)
	#test_delete(data_args)	
	test_search(data_args)
	
	end_time=time.time()
	exec_time=end_time-start_time
	
	time_exec=format(exec_time*1000, '.3f')
	print("Execution time is:%2.6f" %(exec_time))

	FileUtil.AddLine('exec_time_client.log', time_exec)

if __name__ == "__main__":
	test_run = 1
	wait_interval = 1
	for x in range(test_run):
		test_CapAC()
		time.sleep(wait_interval)
	pass