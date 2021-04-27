#!/usr/bin/env python

'''
========================
Perform measurement module
========================
Created on March.20, 2021
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
	def read_exec_time(client_log, skip_section=1):
		#------------ read data from log file -------------
		f_client = open(client_log, 'r')
		ls_client=f_client.readlines()
		#close file
		f_client.close()

		line_len=len(ls_client)

		exec_time_data=[]

		for i in range(line_len):
			if( ((i+1) % skip_section) !=0):
				continue
			ls_client[i]=ls_client[i].replace('\n','')
			tmp_list=ls_client[i].split()
			exec_time_data.append(tmp_list)

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
	    width = 0.3           # the width of the bars
	    
	    #generate bar axis object
	    fig, ax = plt.subplots()
	    
	    edge_exec_time = ls_data[0]
	    rects_edge = ax.bar(ind, edge_exec_time, width, color='seagreen')
	    
	    fog_exec_time = ls_data[1]    
	    rects_fog = ax.bar(ind + width, fog_exec_time, width, color='brown')
	    
	   
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
			        '%.0f' % height,
			        ha='center', va='bottom', fontsize=16)

	'''
	plot errror bars shown mdedian and std given ls_dataset[mean, std, median, max, min]
	'''
	@staticmethod
	def plot_errorBar(title_name, legend_label, ax_label, ls_dataset):

		N = len(legend_label)

		# the x locations for the groups
		ind = np.arange(N)

		np_dataset=np.array(ls_dataset, dtype=np.float32)
		trans_np_dataset=np_dataset.transpose()
		ls_mean = trans_np_dataset[0]
		ls_std = trans_np_dataset[1]
		ls_median = trans_np_dataset[2]
		ls_max = trans_np_dataset[3]
		ls_min = trans_np_dataset[4]

		fig, ax = plt.subplots()

		# create stacked errorbars:
		plt.errorbar(ind, ls_mean, ls_std, fmt='or', ecolor='seagreen', lw=50)
		plt.errorbar(ind, ls_median, [ls_mean - ls_min, ls_max - ls_mean], 
					fmt='*k', ecolor='gray', lw=5)

		ax.set_xticks(ind)
		ax.set_xticklabels(legend_label, fontsize=18)
		ax.set_ylabel(ax_label[1], fontsize=18)
		ax.yaxis.grid(True)
		plt.xlim(-0.5, 1.5)

		plt.show()
            
def plot_cost_services():
	#prepare data
	ls_exec_time=[]

	edge_ave_exec_time = []

	exec_time= ExecTime.read_exec_time('01_AuthID/edge_auth_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	edge_ave_exec_time.append(ave_exec_time[0])


	exec_time= ExecTime.read_exec_time('02_CapAC/edge_capac_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	ave_exec_time_sum = float(ave_exec_time[0])+float(ave_exec_time[1])+float(ave_exec_time[2])
	edge_ave_exec_time.append(format(ave_exec_time_sum, '.3f'))

	exec_time= ExecTime.read_exec_time('03_broker_verify/exec_getBroker_edge.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	edge_ave_exec_time.append(format(float(ave_exec_time[0]), '.3f'))

	exec_time= ExecTime.read_exec_time('04_tx_verify/exec_tx_verify_edge.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	edge_ave_exec_time.append(format(float(ave_exec_time[0]), '.3f'))


	fog_ave_exec_time = []
	exec_time= ExecTime.read_exec_time('01_AuthID/fog_auth_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	fog_ave_exec_time.append(ave_exec_time[0])

	exec_time= ExecTime.read_exec_time('02_CapAC/fog_capac_exec_time_server.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	ave_exec_time_sum = float(ave_exec_time[0])+float(ave_exec_time[1])+float(ave_exec_time[2])
	fog_ave_exec_time.append(format(ave_exec_time_sum, '.3f'))


	exec_time= ExecTime.read_exec_time('03_broker_verify/exec_getBroker_fog.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	fog_ave_exec_time.append(format(float(ave_exec_time[0]), '.3f'))

	exec_time= ExecTime.read_exec_time('04_tx_verify/exec_tx_verify_fog.log')
	ave_exec_time = ExecTime.calc_exec_time_ave(exec_time)
	fog_ave_exec_time.append(format(float(ave_exec_time[0]), '.3f'))

	#append data to list
	ls_exec_time.append(edge_ave_exec_time)
	ls_exec_time.append(fog_ave_exec_time)

	# print(ls_exec_time)
	xtick_label=['Identity Verification', 'Access Control', 'Verify Broker', 'Verify Transaction']
	legend_label=['Raspberry Pi', 'Desktop']

	VisualizeData.plot_groupbar_Platform(xtick_label,'Processing time (ms)', legend_label, ls_exec_time)

def exec_commit_tx(file_name):
	exec_time_data=ExecTime.read_exec_time(file_name, 1)
	ls_data = []
	for time_data in exec_time_data:
		ls_data.append(time_data[0])

	np_data=np.array(ls_data, dtype=np.float32)

	ave_exec_time=format(np.average(np_data), '.3f' )
	median_exec_time=format(np.median(np_data), '.3f' )
	std_exec_time=format(np.std(np_data), '.3f' )
	max_exec_time=format(np.max(np_data), '.3f' )
	min_exec_time=format(np.min(np_data), '.3f' )

	return [ave_exec_time, std_exec_time, median_exec_time, max_exec_time, min_exec_time]

def plot_tx_commit():
	data_files = ["exec_broker_commit.log", "exec_tx_commit.log"]

	exec_time_devices = []
	for data_file in data_files:
		## for each files to build ls_data
		file_name = "05_tx_commit/"+data_file
		tx_time = exec_commit_tx(file_name)
		exec_time_devices.append(tx_time)
		print( "{}:\t average-{}\t std-{}\t median-{}\t max-{}\t min-{}".format( 
			data_file, tx_time[0], tx_time[1], tx_time[2], tx_time[3], tx_time[4]) )

	# print(exec_time_devices)

	ax_label = ['', 'Time (s)']
	legend_label=['Inter-ledger', 'Intra-ledger']

	# VisualizeData.plot_Bar_mean_std('', legend_label, ax_label, exec_time_devices)
	VisualizeData.plot_errorBar('', legend_label, ax_label, exec_time_devices)


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
                        2-plot_tx_commit")

    args = parser.parse_args(args=args)
    return args
    
if __name__ == "__main__":
	matplotlib.rcParams.update({'font.size': 14})

	args = define_and_get_arguments()

	if(args.test_op==1):
		plot_cost_services()
	elif(args.test_op==2):
		plot_tx_commit()
	else:
		# ave_Totaldelay()
		print( "tx_commit_ethereum:   {}".format( ave_Totaldelay("05_tx_commit/exec_broker_commit.log")) )
		print( "tx_commit_tendermint: {}".format( ave_Totaldelay("05_tx_commit/exec_tx_commit.log")) )
