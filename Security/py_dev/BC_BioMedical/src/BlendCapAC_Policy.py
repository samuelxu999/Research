#!/usr/bin/env python3.5

'''
========================
BlendCapAC_Policy module
========================
Created on September.17, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide Capability token struct model and encapsulation of access control policy.
'''

import time
import datetime
import json
import sys
from RegisterToken import RegisterToken
from SummaryToken import SummaryToken
from PatientACToken import PatientACToken
from utilities import DatetimeUtil, TypesUtil, FileUtil
from flask import request

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

#global variable

global_config = {}
global_config['http_provider'] = 'http://localhost:8042'
global_config['Register_addr'] = RegisterToken.getAddress('RegisterToken', './addr_list.json')
global_config['Register_contract'] = '../contracts/build/contracts/RegisterToken.json'
global_config['Summary_addr'] = SummaryToken.getAddress('SummaryToken', './addr_list.json')
global_config['Summary_contract'] = '../contracts/build/contracts/SummaryToken.json'
global_config['Patient_addr'] = PatientACToken.getAddress('PatientACToken', './addr_list.json')
global_config['Patient_contract'] = '../contracts/build/contracts/PatientACToken.json'
global_config['address_0'] = '0x0000000000000000000000000000000000000000'


'''
Identity information management
'''
class IdentityInfo(object):
	# New IdentityInfo object
	def __init__(self, config_json):
		self.global_config = config_json
		self.myUserToken = RegisterToken(self.global_config['http_provider'], self.global_config['Register_addr'], self.global_config['Register_contract'])
		self.mySummaryToken=SummaryToken(self.global_config['http_provider'], self.global_config['Summary_addr'], self.global_config['Summary_contract'])
		self.myPatientACToken=PatientACToken(self.global_config['http_provider'], self.global_config['Patient_addr'], self.global_config['Patient_contract'])

	def ShowIdentity(self, user_address):
		#new RegisterToken object
		self.myUserToken=RegisterToken(self.global_config['http_provider'], self.global_config['Register_addr'], self.global_config['Register_contract'])
		user_data=self.myUserToken.getUserInfo(user_address)

		user_info={}
		user_info['UserID'] = user_data[0] 
		user_info['User_address'] = user_address
		user_info['SummaryAddress'] = user_data[1] 

		if(user_info['SummaryAddress']!= self.global_config['address_0']):
			#new SummaryToken object
			self.mySummaryToken=SummaryToken(self.global_config['http_provider'], user_info['SummaryAddress'], self.global_config['Summary_contract'])
			summary_data=self.mySummaryToken.getSummaryInfo(user_address)
			user_info['PatientACAddress'] = summary_data[0] 
		else:
			user_info['PatientACAddress'] = self.global_config['address_0']

		if(user_info['PatientACAddress']!= self.global_config['address_0']):
			#new SummaryToken object
			self.myPatientACToken=PatientACToken(self.global_config['http_provider'], user_info['PatientACAddress'], self.global_config['Patient_contract'])			
		
		token_data=self.myPatientACToken.getCapTokenStatus(user_address)

		json_token={}
		#Add status information
		tokenStatus = token_data
		json_token['id'] = tokenStatus[0]
		json_token['VZone_master'] = tokenStatus[1]
		json_token['initialized'] = tokenStatus[2]
		json_token['isValid'] = tokenStatus[3]
		json_token['issuedate'] = tokenStatus[4]
		json_token['expireddate'] = tokenStatus[5]
		json_token['authorization'] = tokenStatus[6]

		user_info['CapACToken'] = json_token


		return user_info



'''
Capability access control policy management
'''
class CapPolicy(object):

	# get token data from smart contract, return json fromat
	@staticmethod
	def get_token(accountAddr):
		myIdentityInfo=IdentityInfo(global_config)
		User_data = myIdentityInfo.ShowIdentity(accountAddr)
		# get CapACToken data
		json_token = User_data['CapACToken'] 
		
		return json_token

	# check identity status
	@staticmethod
	def is_identity_valid(user_data):
		ret = True
		#check enable flag
		if(user_data['UserID']=='' or 
			user_data['SummaryAddress']==global_config['address_0'] or
			user_data['PatientACAddress']==global_config['address_0']):
			ret = False

		return ret

	# check token status, like status flag, issue and expire time.
	@staticmethod
	def is_token_valid(token_data):
		ret = True
		#check enable flag
		if( token_data['initialized']!=True or token_data['isValid']!=True):
			ret = False

		#check issue time and expire time
		now_stamp = DatetimeUtil.datetime_timestamp(datetime.datetime.now())
		if( (token_data['issuedate'] > now_stamp) or (now_stamp > token_data['expireddate']) ):
			ret = False
		return ret

	# verify acccess right
	@staticmethod
	def is_access_valid(token_data, acess_args=''):
		ret = True
		if(token_data['authorization'] == ''):
			ret = False
		else:
			#token_authorization = token_data[2][1]
			ac_data=TypesUtil.string_to_json(token_data['authorization'])
			#print(ac_data)

			if(ac_data['action']!=acess_args['method'] or 
				ac_data['resource']!=str(acess_args['url_rule']) or 
				not CapPolicy.is_condition_valid(ac_data['conditions'])):
				'''print(ac_data['action']!=acess_args['method'])
				print(ac_data['resource']==str(acess_args['url_rule']))
				print(CapPolicy.is_condition_valid(ac_data['conditions']))'''
				ret = False

		return ret

	# check condition status to verify context requirement
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
			'''print(starttime)
			print(endtime)
			print(nowtime)'''
			#check if timespan condition is valid
			if(not (starttime<nowtime<endtime) ):
				print("condition validation fail!")
				return False
		return True

	'''
	Valid access request based on policy, call by interposing service API
	'''	
	@staticmethod	
	def is_valid_access_request(req_args):
		#Get account address
		addr_client = req_args.json['host_address']

		#Define ls_time_exec to save executing time to log
		ls_time_exec=[]

		# define branch control flag
		query_src = 0 # smart contract:0, local cache:1 
		is_cachetoken = 0 # cache data:1, not cache data:0

		# ======================= get smart contract data =======================
		start_time=time.time()
		
		if(query_src == 0):
			# ----------a) query token from smart contract ------------
			myIdentityInfo=IdentityInfo(global_config)
			User_data = myIdentityInfo.ShowIdentity(addr_client)
			# get CapACToken data
			#token_data = User_data['CapACToken'] 
			#token_data=CapPolicy.get_token(addr_client)
			#print(token_data)

			if(is_cachetoken == 1):				
				# 2) Save token data to local token.dat
				FileUtil.AddLine('IdentityInfo.dat', TypesUtil.json_to_string(User_data))
		else:
			# ----------b) read authToken from local cached file ------------
			read_token=FileUtil.ReadLines('IdentityInfo.dat')
			User_data = TypesUtil.string_to_json(read_token[0])
		
		token_data=User_data['CapACToken'] 
		#print(token_data)

		exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of get UserData is:%2.6f" %(exec_time))

		#extract access action from request
		access_data={}
		access_data['url_rule']=req_args.url_rule
		access_data['method']=req_args.method
		#print(access_data)

		# ======================= AC process =======================
		start_time=time.time()

		if(not CapPolicy.is_identity_valid(User_data)):
			print('Identity valid fail')
			return False

		if(not CapPolicy.is_token_valid(token_data)):
			print('Token valid fail')
			return False

		'''exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of is_token_valid is:%2.6f" %(exec_time))'''

		#start_time=time.time()
		if(not CapPolicy.is_access_valid(token_data, access_data)):
			print('access valid fail')
			return False
		exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))		
		print("Execution time of is_access_valid is:%2.6f" %(exec_time))

		#transfer list to string
		str_time_exec=" ".join(ls_time_exec)
		#print(str_time_exec)
		FileUtil.AddLine('capac_exec_time_server.log', str_time_exec)

		return True

def test_CapACToken():

	myIdentityInfo=IdentityInfo(global_config)

	myUserToken=myIdentityInfo.myUserToken
	# ========== get host account =========
	accounts = myUserToken.getAccounts()
	balance = myUserToken.getBalance(accounts[0])
	print("Host accounts: %s" %(accounts))
	print("coinbase balance:%d" %(balance))
	print("--------------------------------------------------------------------")

	# ========== Get account address =========
	user_address = PatientACToken.getAddress('sam_ubuntu', './addr_list.json')
	#patientACToken_address = PatientACToken.getAddress('PatientACToken', '../contracts/test/addr_list.json')
	print("User Account: " + user_address)

	# ============== Read token data using ShowIdentity  ========
	User_data = myIdentityInfo.ShowIdentity(user_address)
	print(User_data)

	# =========  Read token data using CapPolicy function get_token() =============
	token_data=User_data['CapACToken']
	'''print(token_data['VZone_master'])
	ac = TypesUtil.string_to_json(token_data['authorization'])
	print(ac['resource'])'''

	# =========  Write token data to 'token.dat' =============
	#FileUtil.AddLine('token.dat', TypesUtil.json_to_string(token_data))

	# =========  Read token data from 'token.dat' =============
	'''read_token=FileUtil.ReadLines('token.dat')
	json_token=TypesUtil.string_to_json(read_token[0])
	print(json_token['initialized'])
	print(json_token['issuedate'])'''

	if(token_data!={}):
		print(CapPolicy.is_token_valid(token_data))		
	else:
		print(False)


	#ret=CapPolicy.is_valid_access_request()
	

if __name__ == "__main__":

	test_CapACToken()
	pass
