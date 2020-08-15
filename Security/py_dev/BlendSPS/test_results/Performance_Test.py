#!/usr/bin/env python

'''
========================
Perform measurement module
========================
Created on September.19, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide performance measure utilities.
'''
import sys
import logging
import argparse

import matplotlib
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np

'''
Data preparation class, such as merge data, calculate execute time
'''
class ExecTime(object):

	'''
	read execution time from log file
	'''
	@staticmethod
	def read_exec_time(client_log):
		#------------ read data from log file -------------
		f_client = open(client_log, 'r')
		ls_client=f_client.readlines()
		#close file
		f_client.close()

		line_len=len(ls_client)

		exec_time_data=[]

		for i in range(line_len):
			ls_client[i]=ls_client[i].replace('\n','')
			tmp_list=ls_client[i].split(' ')
			exec_time_data.append(tmp_list)

		return exec_time_data
		
	'''
	merge execution time from client and server
	'''
	@staticmethod
	def merge_exec_time(client_log, server_auth_log, server_ac_log):
		#------------ read data from log file -------------
		f_client = open(client_log, 'r')
		ls_client=f_client.readlines()
		#close file
		f_client.close()
		
		f_auth_server = open(server_auth_log, 'r')
		ls_auth_server=f_auth_server.readlines()
		#close file
		f_auth_server.close()
		
		f_ac_server = open(server_ac_log, 'r')
		ls_ac_server=f_ac_server.readlines()
		#close file
		f_ac_server.close()
		
		line_len=len(ls_client)
		
		exec_time_data=[]
		
		for i in range(line_len):
			ls_client[i]=ls_client[i].replace('\n','')
			ls_auth_server[i]=ls_auth_server[i].replace('\n','')
			ls_ac_server[i]=ls_ac_server[i].replace('\n','')
			if(ls_client[i]=='' or ls_auth_server[i]=='' or ls_ac_server[i]==''):
				continue
			tmp_str=ls_auth_server[i] +" " + ls_ac_server[i] +" " + ls_client[i]
			exec_time_data.append(tmp_str.split())
		
		return exec_time_data
    
	'''
	calculate execution time by using average
	'''
	@staticmethod
	def calc_exec_time_ave(ls_exec_time):  
		ave_exec_time = []
		for i in range(len(ls_exec_time[0])):  
			ave_exec_time.append(0.0)
		
		for exec_time in ls_exec_time:
			for i in range(len(exec_time)):
				ave_exec_time[i]+=float(exec_time[i])
		
		for i in range(len(ls_exec_time[0])):
			ave_exec_time[i]=format(ave_exec_time[i]/len(ls_exec_time), '.3f')
		
		#print(ave_exec_time)
		return ave_exec_time
		
	'''
	calculate execution time usng sum of each line
	'''
	@staticmethod
	def calc_exec_time_ave_sum(ls_exec_time):  
		sum_exec_time = []
		
		for exec_time in ls_exec_time:
			line_sum = 0.0
			for i in range(len(exec_time)):
				line_sum+=float(exec_time[i])
			sum_exec_time.append(format(line_sum, '.3f'))
		
		#print(sum_exec_time)
		return sum_exec_time

	'''
	merge data from multiple files
	'''
	@staticmethod
	def merge_files(file_list):
		file_count=len(file_list)
		
		#read data from files
		data_list=[]
		for i in range(file_count):
			#print(file_list[i])
			fname=open(file_list[i], 'r')
			data=fname.readlines()
			fname.close()
			data_list.append(data)
			
		#get row size based on branchmark dataset
		data_size=len(data_list[0])
		#print(str(file_count)+" "+ str(data_size))
		
		#merge data to single dataset
		merged_data=[]
		for row in range(data_size):
			row_data=[]
			for col in range(file_count): 
				data_list[col][row]=data_list[col][row].replace('\n','')
				row_data.append(data_list[col][row])
			merged_data.append(row_data)

		return merged_data
   
'''
Data visualization class to display data as bar or lines
''' 
class VisualizeData(object):
	'''
	plot groupbar chart given ls_data
	'''
	@staticmethod
	def plot_groupbar_Platform(xtick_label, y_label, legend_label, ls_data):
	    
	    N = len(xtick_label)
	    
	    ind = np.arange(N)  # the x locations for the groups
	    width = 0.4           # the width of the bars
	    
	    #generate bar axis object
	    fig, ax = plt.subplots()
	    
	    edge_exec_time = ls_data[0]
	    rects_edge = ax.bar(ind, edge_exec_time, width, color='g')
	    
	    fog_exec_time = ls_data[1]    
	    rects_fog = ax.bar(ind + width, fog_exec_time, width, color='b')
	    
	   
	    # add some text for labels, title and axes ticks
	    ax.set_ylabel(y_label, fontsize=18)
	    #ax.set_title('Execution time by group', fontsize=18)
	    ax.set_xticks(ind + width/2)
	    ax.set_xticklabels(xtick_label, fontsize=18)
	    #plt.ylim(0, 45)
	    
	    ax.legend((rects_edge[0], rects_fog[0]), legend_label, loc='upper right', fontsize=18)
	    
	    VisualizeData.autolabel(rects_edge, ax)
	    VisualizeData.autolabel(rects_fog, ax)
	    
	    plt.show()
	    pass    

	@staticmethod
	def autolabel(rects, ax):
		"""
		Attach a text label above each bar displaying its height
		"""
		for rect in rects:
			height = rect.get_height()
			ax.text(rect.get_x() + rect.get_width()/2, (height+0.2),
			        '%.1f' % height,
			        ha='center', va='bottom', fontsize=16)

	'''
	plot multiple lines in single chart given ls_data
	'''
	@staticmethod
	def plot_txs_MultiLines(title_name, legend_label, y_label, ls_data):
		x=[]
		tx_ethereum=[]  
		tx_tendermint=[] 
		
		i=1
		for record in ls_data:
			x.append(i)
			tx_ethereum.append(float(record[0]))
			tx_tendermint.append(float(record[1]))		
			i+=1

		line_list=[]
		line_list.append(plt.plot(x, tx_ethereum, lw=1.0, marker='o', color='darkorange'))
		line_list.append(plt.plot(x, tx_tendermint, lw=1.0, marker='*', color='seagreen'))

		plt.xlabel('Number of runs', fontsize=18)
		plt.ylabel(y_label, fontsize=18)
		plt.ylim(0, 20)
		plt.title(title_name)
		plt.legend(legend_label, loc='upper left', fontsize=18)

		#show plot
		plt.show()
            
    
	'''
	plot multiple lines in single chart given ls_data
	'''
	@staticmethod
	def plot_services_MultiLines(title_name, legend_label, y_label, ls_data):
		x=[]
		AuthID_tx=[]  
		BlendCAC_tx=[]  
		IndexAuth_tx=[]         
		
		for record in ls_data:
			# print(record)
			x.append(record[0])

			AuthID_tx.append(float(record[1]))
			BlendCAC_tx.append(float(record[2]))
			IndexAuth_tx.append(float(record[3]))		

		line_list=[]
		line_list.append(plt.plot(x, AuthID_tx, lw=1.0, marker='o', color='brown'))
		line_list.append(plt.plot(x, BlendCAC_tx, lw=1.0, marker='s', color='m'))
		line_list.append(plt.plot(x, IndexAuth_tx, lw=1.0, marker='^', color='seagreen'))

		plt.xlabel("Send transactions per second (TPS)", fontsize=18)
		plt.ylabel(y_label, fontsize=18)
		plt.title(title_name)
		plt.xlim(0, 110)

		for x, a, b, c in zip(x, AuthID_tx, BlendCAC_tx, IndexAuth_tx): 
			# plt.plot(x, y, "b^")
			if(x=='100'):
				# str_a='('+ str(x)+', '+format(a, '.3f') + ')'
				str_a = format(a, '.1f')
				plt.text(int(x)-1, a+0.25, str_a)
				# str_b='('+ str(x)+', '+format(b, '.3f') + ')'
				str_b = format(b, '.1f')
				plt.text(int(x)-1, b+0.25, str_b)
				# str_c='('+ str(x)+', '+format(c, '.3f') + ')'
				str_c = format(c, '.1f')
				plt.text(int(x)-1, c+0.25, str_c)

		plt.ylim(0, 12)
		plt.legend(legend_label, loc='upper left', fontsize=18)

		#show plot
		plt.show()

	'''
	plot multiple lines in single chart given ls_data
	'''
	@staticmethod
	def plot_srvdropout_MultiLines(title_name, legend_label, y_label, ls_data):
		x=[]
		Dropout_0=[]  
		Dropout_1=[]  
		Dropout_2=[]
		Dropout_3=[]   
		Mono_srv=[]      
		
		for record in ls_data:
			# print(record)
			x.append(record[0])

			Dropout_0.append(float(record[1]))
			Dropout_1.append(float(record[2]))
			Dropout_2.append(float(record[3]))
			Dropout_3.append(float(record[4]))
			Mono_srv.append(float(record[5]))			

		line_list=[]
		line_list.append(plt.plot(x, Dropout_0, lw=1.0, marker='o', color='seagreen'))
		line_list.append(plt.plot(x, Dropout_1, lw=1.0, marker='s', color='m'))
		line_list.append(plt.plot(x, Dropout_2, lw=1.0, marker='^', color='brown'))
		line_list.append(plt.plot(x, Dropout_3, lw=1.0, marker='*', color='r'))
		line_list.append(plt.plot(x, Mono_srv, lw=1.0, marker='>', color='b'))

		plt.xlabel("Send transactions per second (TPS)", fontsize=18)
		plt.ylabel(y_label, fontsize=18)
		plt.title(title_name)
		plt.xlim(0, 110)

		for x, a, b, c, d, e in zip(x, Dropout_0, Dropout_1, Dropout_2, Dropout_3, Mono_srv): 
			# plt.plot(x, y, "b^")
			if(x=='100'):
				str_a = format(a, '.1f')
				plt.text(int(x)-0.5, a-0.5, str_a)
				str_b = format(b, '.1f')
				plt.text(int(x)-0.5, b+0.2, str_b)
				str_c = format(c, '.1f')
				plt.text(int(x)-0.5, c+0.25, str_c)
				str_d = format(d, '.1f')
				plt.text(int(x)-0.5, d+0.25, str_d)
				str_e = format(e, '.1f')
				plt.text(int(x)-0.5, e+0.25, str_e)

		plt.ylim(0, 12)
		plt.legend(legend_label, loc='upper left', fontsize=18)

		#show plot
		plt.show()

	'''
	plot multiple lines in single chart given ls_data
	'''
	@staticmethod
	def plot_srvdropout_Throughput(title_name, legend_label, y_label, ls_data):
		x=[]
		Dropout_0=[]  
		Dropout_1=[]  
		Dropout_2=[]
		Dropout_3=[]   
		Mono_srv=[]      
		
		for record in ls_data:
			# print(record)
			x.append(record[0])

			Dropout_0.append(float(record[1]))
			Dropout_1.append(float(record[2]))
			Dropout_2.append(float(record[3]))
			Dropout_3.append(float(record[4]))
			Mono_srv.append(float(record[5]))			

		line_list=[]
		line_list.append(plt.plot(x, Dropout_0, lw=1.0, marker='o', color='seagreen'))
		line_list.append(plt.plot(x, Dropout_1, lw=1.0, marker='s', color='m'))
		line_list.append(plt.plot(x, Dropout_2, lw=1.0, marker='^', color='brown'))
		line_list.append(plt.plot(x, Dropout_3, lw=1.0, marker='*', color='r'))
		line_list.append(plt.plot(x, Mono_srv, lw=1.0, marker='>', color='b'))

		plt.xlabel("Send transactions per second (TPS)", fontsize=18)
		plt.ylabel(y_label, fontsize=18)
		plt.title(title_name)
		plt.xlim(0, 110)

		for x, a, b, c, d, e in zip(x, Dropout_0, Dropout_1, Dropout_2, Dropout_3, Mono_srv): 
			# plt.plot(x, y, "b^")
			# if(x=='100'):
			str_a=format(a, '.1f')
			plt.text(int(x)-3.5, a+1, str_a)
			str_b=format(b, '.1f')
			plt.text(int(x)-3.5, b+1, str_b)
			str_c=format(c, '.1f')
			plt.text(int(x)-3.5, c+1, str_c)
			str_d=format(d, '.1f')
			plt.text(int(x)-3.5, d+1, str_d)
			str_e=format(e, '.1f')
			plt.text(int(x)-3.5, e+1, str_e)

		plt.ylim(0, 70)
		plt.legend(legend_label, loc='upper left', fontsize=18)

		#show plot
		plt.show()

 
def plot_cost_services():
	#prepare data
	ls_exec_time=[]

	edge_ave_exec_time = []

	exec_time= ExecTime.read_exec_time('Demo_App/AuthID/edge_auth_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	edge_ave_exec_time.append(ave_exec_time[0])


	exec_time= ExecTime.read_exec_time('Demo_App/CapAC/edge_capac_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	ave_exec_time_sum = float(ave_exec_time[0])+float(ave_exec_time[1])+float(ave_exec_time[2])
	edge_ave_exec_time.append(format(ave_exec_time_sum, '.3f'))

	exec_time= ExecTime.read_exec_time('Demo_App/IndexAuth/edge_exec_time_authIndex.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	ave_exec_time_sum = float(ave_exec_time[0])+float(ave_exec_time[1])+float(ave_exec_time[2])
	edge_ave_exec_time.append(format(ave_exec_time_sum, '.3f'))

	exec_time= ExecTime.read_exec_time('Demo_App/ENFAuth/edge_exec_verify_ENF.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	edge_ave_exec_time.append(format(float(ave_exec_time[0]), '.3f'))


	fog_ave_exec_time = []
	exec_time= ExecTime.read_exec_time('Demo_App/AuthID/fog_auth_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	fog_ave_exec_time.append(ave_exec_time[0])

	exec_time= ExecTime.read_exec_time('Demo_App/CapAC/fog_capac_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	ave_exec_time_sum = float(ave_exec_time[0])+float(ave_exec_time[1])+float(ave_exec_time[2])
	fog_ave_exec_time.append(format(ave_exec_time_sum, '.3f'))

	exec_time= ExecTime.read_exec_time('Demo_App/IndexAuth/fog_exec_time_authIndex.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	ave_exec_time_sum = float(ave_exec_time[0])+float(ave_exec_time[1])+float(ave_exec_time[2])
	fog_ave_exec_time.append(format(ave_exec_time_sum, '.3f'))

	exec_time= ExecTime.read_exec_time('Demo_App/ENFAuth/fog_exec_verify_ENF.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	fog_ave_exec_time.append(format(float(ave_exec_time[0]), '.3f'))

	#append data to list
	ls_exec_time.append(edge_ave_exec_time)
	ls_exec_time.append(fog_ave_exec_time)

	# print(ls_exec_time)
	xtick_label=['Identity Verification', 'Access Control', 'Data Integrity', 'VideoStream Fingerprint']
	legend_label=['Raspberry Pi', 'Desktop']

	VisualizeData.plot_groupbar_Platform(xtick_label,'Processing time (ms)', legend_label, ls_exec_time)

def plot_tx_commit():
	exec_time_eth=ExecTime.read_exec_time("tx_commit/exec_tx_commit_ethereum.log")
	exec_time_ten=ExecTime.read_exec_time("tx_commit/exec_tx_commit_ENF.log")

	exec_time_data = []
	for i in range(0, len(exec_time_eth)):
		exec_time_data.append([ exec_time_eth[i][0], exec_time_ten[i][0] ])

	legend_label=['Ethereum', 'Tendermint']
	VisualizeData.plot_txs_MultiLines("", legend_label, 'Transaction committed time (s)', exec_time_data)

def plot_txs_services():
	data_dir = "single_srv_tx"
	ls_services = ["AuthID", "BlendCAC", "IndexAuth"]
	file_list = []
	file_list.append("exec_services_client_1.log")
	file_list.append("exec_services_client_2.log")
	file_list.append("exec_services_client_5.log")
	file_list.append("exec_services_client_10.log")
	file_list.append("exec_services_client_20.log")
	file_list.append("exec_services_client_50.log")
	file_list.append("exec_services_client_100.log")

	exec_time_data = []
	for file_name in file_list:
		x_label = file_name.split('_')[3].split('.')[0]
		file_AuthID = data_dir + "/" + ls_services[0] + "/" + file_name
		file_BlendCAC = data_dir + "/" + ls_services[1] + "/" + file_name
		file_IndexAuth = data_dir + "/" + ls_services[2] + "/" + file_name
		exec_time_data.append( (x_label, ave_Totaldelay(file_AuthID)[0],
								ave_Totaldelay(file_BlendCAC)[0], ave_Totaldelay(file_IndexAuth)[0]))
	# print(exec_time_data)

	legend_label=['Identity Verification', 'Access Control', 'Data Integrity']
	VisualizeData.plot_services_MultiLines("", legend_label, 'Network delay (s)', exec_time_data)


def plot_txs_multiservices():
	data_dir = "multi_srv_tx"
	ls_services = ["mono", "2", "3", "4", "5"]
	file_list = []
	file_list.append("exec_services_client_10.log")
	file_list.append("exec_services_client_20.log")
	file_list.append("exec_services_client_50.log")
	file_list.append("exec_services_client_100.log")

	exec_time_data = []
	for file_name in file_list:
		x_label = file_name.split('_')[3].split('.')[0]
		file_mono = data_dir + "/" + ls_services[0] + "/" + file_name
		file_2 = data_dir + "/" + ls_services[1] + "/" + file_name
		file_3 = data_dir + "/" + ls_services[2] + "/" + file_name
		file_4 = data_dir + "/" + ls_services[3] + "/" + file_name
		file_5 = data_dir + "/" + ls_services[4] + "/" + file_name
		exec_time_data.append( (x_label, 
								ave_Totaldelay(file_5)[0], ave_Totaldelay(file_4)[0],
								ave_Totaldelay(file_3)[0], ave_Totaldelay(file_2)[0],
								ave_Totaldelay(file_mono)[0]))
	# print(exec_time_data)

	legend_label=["Micro_App:   0% dropout", "Micro_App: 20% dropout", "Micro_App: 40% dropout", 
					"Micro_App: 60% dropout", "Mono_App"]

	VisualizeData.plot_srvdropout_MultiLines("", legend_label, 'Network delay (s)', exec_time_data)

def plot_multiservices_throughput():
	data_dir = "multi_srv_tx"
	ls_services = ["mono", "2", "3", "4", "5"]
	file_list = []
	file_list.append("exec_services_client_10.log")
	file_list.append("exec_services_client_20.log")
	file_list.append("exec_services_client_50.log")
	file_list.append("exec_services_client_100.log")

	exec_time_data = []
	for file_name in file_list:
		x_label = file_name.split('_')[3].split('.')[0]
		file_mono = data_dir + "/" + ls_services[0] + "/" + file_name
		file_2 = data_dir + "/" + ls_services[1] + "/" + file_name
		file_3 = data_dir + "/" + ls_services[2] + "/" + file_name
		file_4 = data_dir + "/" + ls_services[3] + "/" + file_name
		file_5 = data_dir + "/" + ls_services[4] + "/" + file_name
		exec_time_data.append( (x_label, 
								ave_Totaldelay(file_5)[0], ave_Totaldelay(file_4)[0],
								ave_Totaldelay(file_3)[0], ave_Totaldelay(file_2)[0],
								ave_Totaldelay(file_mono)[0]))

	# calculate tx throughput: txs per second
	tx_throughput = []
	for exec_time in exec_time_data:
		# print(float(exec_time[0])/float(exec_time[1]))
		tx_throughput.append( (exec_time[0],
			format( float(exec_time[0])/float(exec_time[1]), '.3f' ),
			format( float(exec_time[0])/float(exec_time[2]), '.3f' ),
			format( float(exec_time[0])/float(exec_time[3]), '.3f' ),
			format( float(exec_time[0])/float(exec_time[4]), '.3f' ),
			format( float(exec_time[0])/float(exec_time[5]), '.3f' )   
			) )
	# for tx_data in tx_throughput:
	# 	print(tx_data)

	legend_label=["Micro_App:   0% dropout", "Micro_App: 20% dropout", "Micro_App: 40% dropout", 
					"Micro_App: 60% dropout", "Mono_App"]

	VisualizeData.plot_srvdropout_Throughput("", legend_label, 'Transaction throughput (tx/s)', tx_throughput)
	
def ave_Totaldelay(file_name):
	exec_time_data=ExecTime.read_exec_time(file_name)

	ave_exec_time=ExecTime.calc_exec_time_ave(exec_time_data)

	return ave_exec_time

def define_and_get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Run test evaulation app."
    )
    parser.add_argument("--test_op", type=int, default=0, 
                        help="Execute test operation: \
                        0-function test, \
                        1-plot_cost_services, \
                        2-plot_tx_commit, \
                        3-plot_txs_services, \
                        4-plot_txs_multiservices, \
                        5-plot_multiservices_throughput")

    args = parser.parse_args(args=args)
    return args
    
if __name__ == "__main__":
	matplotlib.rcParams.update({'font.size': 14})

	args = define_and_get_arguments()

	if(args.test_op==1):
		plot_cost_services()
	elif(args.test_op==2):
		plot_tx_commit()
	elif(args.test_op==3):
		plot_txs_services()
	elif(args.test_op==4):
		plot_txs_multiservices()
	elif(args.test_op==5):
		plot_multiservices_throughput()
	else:
		# ave_Totaldelay()
		print( "tx_commit_ethereum:   {}".format( ave_Totaldelay("tx_commit/exec_tx_commit_ethereum.log")) )
		print( "tx_commit_tendermint: {}".format( ave_Totaldelay("tx_commit/exec_tx_commit_ENF.log")) )
