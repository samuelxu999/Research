#!/usr/bin/env python

'''
========================
VirusTotal API module
========================
Created on Oct.29, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation for VirusTotal API.
@Reference: https://developers.virustotal.com/v2.0/reference
'''

import requests

class vtAPI(object):
    #Key for access right to API function 
    API_Key='a4048f555f5c47e5100f3a68eb65ee60134bc1f7aa3c78a5fb8c461158568ced'
    
    '''
    Sending and scanning URLs
    '''
    @staticmethod
    def url_Scan(test_url):
        api_url='https://www.virustotal.com/vtapi/v2/url/scan'     
        
        params = {'apikey': vtAPI.API_Key, 'url':test_url}
        
        response = requests.post(api_url, data=params)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Retrieving URL scan reports
    '''
    @staticmethod
    def url_Report(test_res):
        api_url = 'https://www.virustotal.com/vtapi/v2/url/report'

        params = {'apikey': vtAPI.API_Key, 'resource':test_res}
        
        response = requests.get(api_url, params=params)
        
        #get response json
        json_response = response.json()
        
        return json_response
    
    '''
    Sending and scanning files
    '''
    @staticmethod
    def file_Scan(test_file):
        api_url='https://www.virustotal.com/vtapi/v2/file/scan'     
        
        params = {'apikey': vtAPI.API_Key}
        
        files = {'file': (test_file, open(test_file, 'rb'))}
        
        response = requests.post(api_url, files=files, params=params)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Rescanning already submitted files
    '''
    @staticmethod
    def file_Rescan(_res):
        api_url='https://www.virustotal.com/vtapi/v2/file/rescan'     
        
        params = {'apikey': vtAPI.API_Key, 'resource': _res}
        
        
        response = requests.post(api_url, params=params)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    Retrieving file scan reports
    '''
    @staticmethod
    def file_Report(_res):
        api_url='https://www.virustotal.com/vtapi/v2/file/report'     
        
        params = {'apikey': vtAPI.API_Key, 'resource': _res}
        
        
        response = requests.post(api_url, params=params)
        
        #get response json
        json_response = response.json()      

        return json_response
    
    '''
    get positive rate based on response from scan report
    '''
    @staticmethod
    def getPositiveRate(report_response):
        positives=report_response['positives']
        total=report_response['total']
        
        #print(str(positives)+'/'+str(total))
        return round(positives/total, 2)
