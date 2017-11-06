#!/usr/bin/env python

'''
========================
WS_Client module
========================
Created on Nov.2, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of client API that access to Web service.
'''
import time
import requests
import datetime
import json

from CapAC_Policy import CapToken

import sys
sys.path.append('../SGW_API/')
from utilities import DatetimeUtil

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")
    
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

	print(WSClient.Get_Datasets('http://128.226.78.217/test/api/v1.0/dt', data_args))
	print(WSClient.Get_DataByID('http://128.226.78.217/test/api/v1.0/dt/project', params, data_args))
    
def test_add(data_args={}):
	project = {
		'title': 'post_new',
		'description': 'post_description',
		'date': datestr,
		'time': timestr
	}
	project_data = {'project_data':project}
	
	if(bool(data_args)):
		project_data['token_data']=data_args['token_data']
	json_response=WSClient.Create_Data('http://128.226.78.217/test/api/v1.0/dt/create',project_data)
	#print(json_response['project_data'])
	print(json_response)
    
def test_update(data_args={}):
	project = {
		'id': 2,
		'title': 'update_test',
		'description': 'update_description',
		'date': datestr,
		'time': timestr
	}		
	project_data = {'project_data':project}

	if(bool(data_args)):
		project_data['token_data']=data_args['token_data']
		
	json_response=WSClient.Update_Data('http://128.226.78.217/test/api/v1.0/dt/update',project_data)
	print(json_response)
    
def test_delete(data_args={}):
	project_data = {'id': 3}

	if(bool(data_args)):
		project_data['token_data']=data_args['token_data']

	json_response=WSClient.Delete_Data('http://128.226.78.217/test/api/v1.0/dt/delete',project_data)
	print(json_response)

def test_token():
	#assign access based on authorization policy
	ac_data=[]
	ac_data.append(CapToken.new_access('GET', 'http://128.226.78.217/test/api/v1.0/dt'))
	ac_data.append(CapToken.new_access('PUT', 'http://128.226.78.217/test/api/v1.0/dt/update'))
	
	#calculate start time and end time
	starttime=DatetimeUtil.datetime_string(now)
	_duration=[0,1,0,10]
	duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
	endtime = DatetimeUtil.datetime_string(now+duration)
	
	#generate token
	token_data=CapToken.new_token('edere0129', 'Admin', DatetimeUtil.datetime_string(now), 'signature_code', \
				'Samuel:128.226.76.37', 'http://128.226.78.217', [starttime, endtime], ac_data) 
	#print(token_data)
	CapToken.display_token(token_data)

def generate_token():
	#assign access based on authorization policy
	ac_data=[]
	
	#define condition
	cond_data1={}
	cond_data1['type']='Timespan'
	cond_data1['value']={'start':'10:12:32','end':'18:32:32'}
	ac_data.append(CapToken.new_access('GET', '/test/api/v1.0/dt', cond_data1))
	
	cond_data2={}
	cond_data2['type']='Timespan'
	cond_data2['value']={'start':'14:12:32','end':'19:32:32'}
	ac_data.append(CapToken.new_access('GET', '/test/api/v1.0/dt/project', cond_data2))
	
	cond_data3={}
	cond_data3['type']='Timespan'
	cond_data3['value']={'start':'17:12:32','end':'19:32:32'}
	ac_data.append(CapToken.new_access('POST', '/test/api/v1.0/dt/create', cond_data3))
	
	cond_data4={}
	cond_data4['type']='Timespan'
	cond_data4['value']={'start':'17:12:32','end':'20:32:32'}
	ac_data.append(CapToken.new_access('PUT', '/test/api/v1.0/dt/update', cond_data4))
	
	cond_data5={}
	cond_data5['type']='Timespan'
	cond_data5['value']={'start':'17:02:32','end':'20:32:32'}
	ac_data.append(CapToken.new_access('DELETE', '/test/api/v1.0/dt/delete', cond_data5))
	
	#calculate start time and end time
	'''starttime=DatetimeUtil.datetime_string(now)
	_duration=[0,1,0,10]
	duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
	endtime = DatetimeUtil.datetime_string(now+duration)'''
	starttime='2017-11-05 18:12:32'
	endtime='2017-11-07 16:12:32'
	#issuetime=DatetimeUtil.datetime_string(now)
	issuetime='2017-11-05 20:12:32'
	
	#generate token
	token_data=CapToken.new_token('edere0129', 'Admin', issuetime, 'signature_code', \
				'Samuel:128.226.76.37', 'http://128.226.78.217', [starttime, endtime], ac_data) 
	return token_data
	
def test_CapAC():
	token_data=generate_token()
	#CapToken.display_token(token_data)
	
	#params = {'project_id':'2'}
	data_args = {'project_id':'2', 'token_data': token_data}
	
	start_time=time.time()
	
	#print token_data	
	#test_add(data_args)
	#test_update(data_args)
	#test_delete(data_args)	
	test_search(data_args)
	
	end_time=time.time()
	exec_time=end_time-start_time
	
	print("Execution time is:%2.6f" %(exec_time))
	'''print WSClient.Get_Datasets('http://128.226.78.217/test/api/v1.0/dt', data_args)
	print WSClient.Get_DataByID('http://128.226.78.217/test/api/v1.0/dt/project',params, data_args)'''

if __name__ == "__main__":
	'''test_search()
	test_add()
	test_update()
	test_delete()
	test_token()'''
	test_CapAC()
	pass
