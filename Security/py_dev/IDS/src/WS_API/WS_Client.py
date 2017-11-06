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
    def Get_Datasets(api_url, token):          
        
        response = requests.get(api_url, params=token)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Get record by id
    '''
    @staticmethod
    def Get_DataByID(api_url, params):          
        
        response = requests.get(api_url,params=params)
        
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

def test_search():
    params = {'project_id':'1'}
    print(WSClient.Get_Datasets('http://128.226.78.217/test/api/v1.0/dt'))
    print(WSClient.Get_DataByID('http://128.226.78.217/test/api/v1.0/dt/project',params))
    
def test_add():
    project = {
        'title': 'post_new',
        'description': 'post_description',
        'date': datestr,
        'time': timestr
    }
    project_data = {'project_data':project}
    json_response=WSClient.Create_Data('http://128.226.78.217/test/api/v1.0/dt/create',project_data)
    print(json_response['project_data'])
    
def test_update():
    project = {
        'id': 2,
        'title': 'update_test',
        'description': 'update_description',
        'date': datestr,
        'time': timestr
    }
    project_data = {'project_data':project}
    json_response=WSClient.Update_Data('http://128.226.78.217/test/api/v1.0/dt/update',project_data)
    print(json_response)
    
def test_delete():
    param = {'id': 2}
    json_response=WSClient.Delete_Data('http://128.226.78.217/test/api/v1.0/dt/delete',param)
    print(json_response)

def test_token():
	ac_data=[]
	ac_data.append(CapToken.new_access('GET', 'http://128.226.78.217/test/api/v1.0/dt'))
	ac_data.append(CapToken.new_access('PUT', 'http://128.226.78.217/test/api/v1.0/dt/update'))
	
	#calculate start time and end time
	starttime=DatetimeUtil.datetime_string(now)
	_duration=[0,1,0,10]
	duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
	endtime = DatetimeUtil.datetime_string(now+duration)
		
	token_data=CapToken.new_token('edere0129', 'Admin', DatetimeUtil.datetime_string(now), '@#$%^&*(', \
				'Samuel:128.226.76.37', 'http://128.226.78.217', [starttime, endtime], ac_data) 
	#print(token_data)
	CapToken.display_token(token_data)
def get_token():	
	ac_data=[]
	ac_data.append(CapToken.new_access('GET', 'http://128.226.78.217/test/api/v1.0/dt'))
	ac_data.append(CapToken.new_access('PUT', 'http://128.226.78.217/test/api/v1.0/dt/update'))
	
	#calculate start time and end time
	'''starttime=DatetimeUtil.datetime_string(now)
	_duration=[0,1,0,10]
	duration=DatetimeUtil.datetime_duration(_duration[0],_duration[1],_duration[2],_duration[3])
	endtime = DatetimeUtil.datetime_string(now+duration)'''
	starttime='2017-11-05 20:12:32'
	endtime='2017-11-06 20:12:32'
	#issuetime=DatetimeUtil.datetime_string(now)
	issuetime='2017-11-05 21:12:32'
	token_data=CapToken.new_token('edere0129', 'Admin', issuetime, '@#$%^&*(', \
				'Samuel:128.226.76.37', 'http://128.226.78.217', [starttime, endtime], ac_data) 
	return token_data

if __name__ == "__main__":
	#test_search()
	#test_add()
	#test_update()
	#test_delete()
	#test_token()
	token_data=get_token()
	print(WSClient.Get_Datasets('http://128.226.78.217/test/api/v1.0/dt', token_data))
	pass
