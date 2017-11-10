#!/usr/bin/env python

'''
========================
Cap_Token module
========================
Created on Nov.5, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide Capability token struct model and encapsulation of access control policy.
'''

import time
import datetime
import json
import sys
sys.path.append('../SGW_API/')
from utilities import DatetimeUtil, TypesUtil
from flask import request
from wrapper_pyca import Crypto_DSA

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

'''
Capability token data struct define and related API
'''
class CapToken(object):
	#Create access right object
	@staticmethod
	def new_access(action, resource, condition_args=[]):
		#new json data
		access_data = {}
		
		#Add access right list
		access_data['action'] = action
		access_data['resource'] = resource
		access_data['conditions'] = condition_args
		
		return access_data
	
	#Create token data based on input
	@staticmethod
	def new_token(identifier, issuer, issue_time, issuer_sign, subject, res_obj, lifetime, ac_args):
		#new json data
		token_data = {}
		
		#Add commen information
		token_data['id'] = identifier
		token_data['issuer'] = issuer
		token_data['issue_time'] = issue_time
		token_data['issuer_sign'] = issuer_sign
		
		#Add subject, resource(object)
		token_data['subject'] = subject
		token_data['resource'] = res_obj
		token_data['starttime'] = lifetime[0]
		token_data['endtime'] = lifetime[1]		
		
		#Add access right
		token_data['access_right'] = ac_args
		
		return token_data
		
	#Display token data
	@staticmethod
	def display_token(token_data):
		
		#Print commen information
		print("id:\t\t%s" %(token_data['id']))
		print("issuer:\t\t%s" %(token_data['issuer']))
		print("issue_time:\t%s" %(token_data['issue_time']))
		print("issuer_sign:\t%s" %(token_data['issuer_sign']))
		
		#Print subject, resource(object) and token_signature
		print("subject:\t%s" %(token_data['subject']))
		print("resource:\t%s" %(token_data['resource']))
		print("starttime:\t%s" %(token_data['starttime']))
		print("endtime:\t%s" %(token_data['endtime']))
		
		#Print access right
		print("access_right:")
		for ar in token_data['access_right']:
			print("\t\t%s" %(ar))
	
	#Save token data to file
	@staticmethod
	def save_token(token_data, token_file):
		token_file = open(token_file, 'w') 
		#json_str = json.dumps(token_data)
		json_str=TypesUtil.json_to_string(token_data)
		token_file.write("%s" %(json_str))
		token_file.close()
		
	#Load token data from file
	@staticmethod
	def load_token(token_file):
		token_file = open(token_file, 'r') 
		json_str=token_file.read()
		token_file.close()
		#token_data = json.loads(json_str)
		token_data=TypesUtil.string_to_json(json_str)
		return token_data


'''
Capability access control policy management
'''
class CapPolicy(object):
	'''
	Check that the token is valid: 
		compare issuetime and lifttime.
	'''
	@staticmethod
	def is_token_valid(token_data):
		issue_time=DatetimeUtil.string_datetime(token_data['issue_time'])
		starttime=DatetimeUtil.string_datetime(token_data['starttime'])
		endtime=DatetimeUtil.string_datetime(token_data['endtime'])
		nowtime=DatetimeUtil.string_datetime(DatetimeUtil.datetime_string(now))
		#validate issue time and token lift time
		'''print str(now) + "\t" + str(starttime)+ "\t" + str(endtime)
		print str(issue_time) + "\t" + str(starttime)+ "\t" + str(endtime)
		print now<starttime
		print now>endtime
		print(not starttime<issue_time<endtime)'''
		if(now<starttime or now>endtime or ( not starttime<issue_time<endtime)):
			return False
		else:
			return True
		
	'''
	Check that the action is granted:
		check method and request-URL
	'''	
	@staticmethod
	def is_access_valid(token_data, acess_args):
		for ar in token_data['access_right']:
			#print ar['action'] + ":" + ar['resource'] 
			#print acess_args['method'] + ":" + str(acess_args['url_rule']) 
			if(ar['action']==acess_args['method'] and ar['resource']==str(acess_args['url_rule']) \
				and CapPolicy.is_condition_valid(ar['conditions'])):
				return True
		return False
		
	'''
	Check that the conditions are fulfilled:
		check condition list
	'''	
	@staticmethod
	def is_condition_valid(condition_data):
		if(condition_data==[]):
			return True
		#handle Timespan
		if(condition_data['type']=='Timespan'):
			#print condition_data['value']['start']
			starttime = DatetimeUtil.string_datetime(condition_data['value']['start'], "%H:%M:%S")
			endtime = DatetimeUtil.string_datetime(condition_data['value']['end'], "%H:%M:%S")
			nowtime=DatetimeUtil.string_datetime(timestr, "%H:%M:%S")
			#check if timespan condition is valid
			if(not starttime<nowtime<endtime):
				return False
		return True
		
	'''
	Check that the signature is valid:
		make use of end user's public keys in token_data['issuer'] to verify signature
	'''	
	@staticmethod
	def is_signature_valid(token_data):
		#read signature
		signature_hex=token_data['issuer_sign']
		signature_str=TypesUtil.hex_to_string(signature_hex)
		#print(signature_str)
		
		#read public_key_byte
		public_key_bytes=TypesUtil.string_to_bytes(token_data['issuer'])
		#print(public_key_bytes)
		
		#get public_key
		public_key=Crypto_DSA.load_public_key_bytes(public_key_bytes)
		
		sign_data=b"This is some data I'd like to sign"
		verify_sign=Crypto_DSA.verify(public_key,signature_str,sign_data)
		#print(verify_sign)
		return verify_sign
	
	'''
	Valid access request based on policy
	'''	
	@staticmethod	
	def is_valid_access_request(req_args):
		#get token data
		token_data=req_args.json['token_data']
		
		'''print req_args.url
		print req_args.url_charset
		print req_args.url_root
		print req_args.url_rule
		print req_args.host_url
		print req_args.host
		print req_args.script_root
		print req_args.base_url
		print req_args.path
		print req_args.method'''
		#extract access action from request
		access_data={}
		access_data['url_rule']=req_args.url_rule
		access_data['method']=req_args.method
		#print access_data
		
		if(token_data=='{}'):
			return False
		
		start_time=time.time()
		if(not CapPolicy.is_token_valid(token_data)):
			print('token valid fail')
			return False
		exec_time=time.time()-start_time		
		print("Execution time of is_token_valid is:%2.6f" %(exec_time))
		
		start_time=time.time()
		if(not CapPolicy.is_access_valid(token_data, access_data)):
			print('access valid fail')
			return False
		exec_time=time.time()-start_time		
		print("Execution time of is_access_valid is:%2.6f" %(exec_time))
		
		start_time=time.time()
		if(not CapPolicy.is_signature_valid(token_data)):
			print('signature valid fail')
			return False
		exec_time=time.time()-start_time		
		print("Execution time of is_signature_valid is:%2.6f" %(exec_time))
		return True
	
