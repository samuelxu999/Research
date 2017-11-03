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

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")
    
class WSClient(object):
    
    '''
    Get all dataset
    '''
    @staticmethod
    def Get_Datasets(api_url):          
        
        response = requests.get(api_url)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Get record by id
    '''
    @staticmethod
    def Get_DataByID(api_url, params):          
        
        response = requests.get(api_url,params)
        
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
    print(WSClient.Get_Datasets('http://128.226.76.37/test/api/v1.0/dt'))
    print(WSClient.Get_DataByID('http://128.226.76.37/test/api/v1.0/dt/project',params))
    
def test_add():
    project = {
        'title': 'post_new',
        'description': 'post_description',
        'date': datestr,
        'time': timestr
    }
    project_data = {'project_data':project}
    json_response=WSClient.Create_Data('http://128.226.76.37/test/api/v1.0/dt/create',project_data)
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
    json_response=WSClient.Update_Data('http://128.226.76.37/test/api/v1.0/dt/update',project_data)
    print(json_response)
    
def test_delete():
    param = {'id': 2}
    json_response=WSClient.Delete_Data('http://128.226.76.37/test/api/v1.0/dt/delete',param)
    print(json_response)
    
if __name__ == "__main__":
    #test_search()
    #test_add()
    #test_update()
    #test_delete()
    test_search()
    pass