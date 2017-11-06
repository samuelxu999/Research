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

import datetime
import json
import sys
sys.path.append('../SGW_API/')
from utilities import DatetimeUtil


now = datetime.datetime.now()

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
		#validate issue time and token lift time
		if(now<starttime or now>endtime or ( not starttime<issue_time<endtime)):
			return False
		else:
			return True
		
	'''
	Check that the action is granted:
		check method and request-URL
	'''	
	@staticmethod
	def is_access_valid(token_data):
		pass
		
	'''
	Check that the conditions are fulfilled:
		check condition list
	'''	
	@staticmethod
	def is_condition_valid(token_data):
		pass
		
	'''
	Check that the signature is valid:
		make use of end user's public keys in token_data['issuer'] to verify signature
	'''	
	@staticmethod
	def is_signature_valid(token_data):
		pass
	
	'''
	Valid access request based on policy
	'''	
	@staticmethod	
	def is_valid_access_request(token_data):
		ret=True
		if(not CapPolicy.is_token_valid(token_data)):
			return False
		return ret
	
