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
from PatientACToken import PatientACToken
from utilities import DatetimeUtil, TypesUtil, FileUtil
from flask import request

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

#global variable
http_provider = 'http://localhost:8042'
contract_addr = PatientACToken.getAddress('PatientACToken', './addr_list.json')
contract_config = '../contracts/build/contracts/PatientACToken.json'

#new PatientACToken object
myPatientACtoken=PatientACToken(http_provider, contract_addr, contract_config)

'''
Capability access control policy management
'''
class CapPolicy(object):

	# get token data from smart contract, return json fromat
	@staticmethod
	def get_token(accountAddr):
		token_data=myPatientACtoken.getCapTokenStatus(accountAddr);
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

		return json_token

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

		#get token data
		start_time=time.time()
		
		if(query_src == 0):
			# ----------a) query token from smart contract ------------
			token_data=CapPolicy.get_token(addr_client)
			#print(token_data)

			if(is_cachetoken == 1):				
				# 2) Save token data to local token.dat
				FileUtil.AddLine('ACtoken.dat', TypesUtil.json_to_string(token_data))
		else:
			# ----------b) read authToken from local cached file ------------
			read_token=FileUtil.ReadLines('ACtoken.dat')
			token_data=TypesUtil.string_to_json(read_token[0])
			#print(token_data)

		'''exec_time=time.time()-start_time
		ls_time_exec.append(format(exec_time*1000, '.3f'))	
		print("Execution time of get_token is:%2.6f" %(exec_time))'''

		#extract access action from request
		access_data={}
		access_data['url_rule']=req_args.url_rule
		access_data['method']=req_args.method
		#print(access_data)

		#start_time=time.time()
		if(not CapPolicy.is_token_valid(token_data)):
			print('token valid fail')
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

	# ========== get host account =========
	accounts = myPatientACtoken.getAccounts()
	balance = myPatientACtoken.getBalance(accounts[0])
	print("Host accounts: %s" %(accounts))
	print("coinbase balance:%d" %(balance))
	print("--------------------------------------------------------------------")

	# ========== Get account address =========
	user_address = PatientACToken.getAddress('sam_ubuntu', '../contracts/test/addr_list.json')
	patientACToken_address = PatientACToken.getAddress('PatientACToken', '../contracts/test/addr_list.json')
	print("User Account: " + user_address)

	# ============== Read token data using CapACToken call getCapTokenStatus() ========
	'''token_data=myCapACToken.getCapTokenStatus(node1_address);
	CapACToken.print_tokendata(token_data)'''

	# =========  Read token data using CapPolicy function get_token() =============
	token_data=CapPolicy.get_token(user_address)
	print(token_data['VZone_master'])
	ac = TypesUtil.string_to_json(token_data['authorization'])
	print(ac['resource'])

	# =========  Write token data to 'token.dat' =============
	#FileUtil.AddLine('token.dat', TypesUtil.json_to_string(token_data))

	# =========  Read token data from 'token.dat' =============
	'''read_token=FileUtil.ReadLines('token.dat')
	json_token=TypesUtil.string_to_json(read_token[0])
	print(json_token['initialized'])
	print(json_token['issuedate'])'''

	print(CapPolicy.is_token_valid(token_data))

	#ret=CapPolicy.is_valid_access_request()
	

if __name__ == "__main__":

	test_CapACToken()
	pass
