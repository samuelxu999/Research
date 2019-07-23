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
import matplotlib
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import math

'''
Data preparation class, such as merge data, calculate execute time
'''
class ExecTime(object):
	'''
	calculate execution time by using average
	'''
	@staticmethod
	def calc_exec_time(ls_exec_time):  
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
	load data from file
	'''
	@staticmethod
	def load_data(file_name):

		#read data from file
		data_list=[]

		#print(file_list[i])
		fname=open(file_name, 'r')
		data=fname.readlines()
		fname.close()
		for i in range(len(data)):
			#only add epoch record
			if(i%2==0):
				continue
			tmp_data = data[i].replace('\n','')
			data_list.append(tmp_data.split())

		return data_list

'''
Data visualization class to display data as bar or lines
''' 
class VisualizeData(object):
	'''
	plot groupbar chart given ls_data
	'''
	@staticmethod
	def plot_groupbars_block(xtick_label, y_label, legend_label, ls_data):
		Y_RATIO = 1000
		N = len(xtick_label)

		ind = np.arange(N)  # the x locations for the groups
		width = 0.25           # the width of the bars

		#generate bar axis object
		fig, ax = plt.subplots()

		exec_time_tx = []
		for i in range(len(ls_data)):
			exec_time_tx.append(float(ls_data[i][0])/Y_RATIO)

		rects_tx = ax.bar(ind, exec_time_tx, width, color='b')

		exec_time_block = []
		for i in range(len(ls_data)):
			exec_time_block.append(float(ls_data[i][1])/Y_RATIO)
   
		rects_block = ax.bar(ind + width, exec_time_block, width, color='orange')

		exec_time_vote = []
		for i in range(len(ls_data)):
			exec_time_vote.append(float(ls_data[i][3])/Y_RATIO)
   
		rects_vote = ax.bar(ind + 2*width, exec_time_vote, width, color='g')


		# add some text for labels, title and axes ticks
		ax.set_ylabel(y_label, fontsize=16)
		#ax.set_title('Execution time by group', fontsize=18)
		ax.set_xticks(ind + width)
		ax.set_xticklabels(xtick_label, fontsize=16)
		#plt.ylim(0, 22)

		ax.legend((rects_tx[0], rects_block[0], rects_vote[0]), legend_label, loc='upper left', fontsize=18)

		VisualizeData.autolabel(rects_tx, ax)
		VisualizeData.autolabel(rects_block, ax)
		VisualizeData.autolabel(rects_vote, ax)
		plt.show()
		pass   

	@staticmethod
	def plot_groupbars_cost(xtick_label, y_label, legend_label, ls_data):
		Y_RATIO = 1
		N = len(xtick_label)

		ind = np.arange(N)  # the x locations for the groups
		width = 0.20           # the width of the bars

		#generate bar axis object
		fig, ax = plt.subplots()

		exec_time_tx = []
		for i in range(len(ls_data)):
			exec_time_tx.append(float(ls_data[i][0])/Y_RATIO)

		rects_tx = ax.bar(ind, exec_time_tx, width, color='b')

		exec_time_mine = []
		for i in range(len(ls_data)):
			exec_time_mine.append(float(ls_data[i][1])/Y_RATIO)
   
		rects_mine = ax.bar(ind + width, exec_time_mine, width, color='r')

		exec_time_block = []
		for i in range(len(ls_data)):
			exec_time_block.append(float(ls_data[i][2])/Y_RATIO)
   
		rects_block = ax.bar(ind + 2*width, exec_time_block, width, color='orange')

		exec_time_vote = []
		for i in range(len(ls_data)):
			exec_time_vote.append(float(ls_data[i][3])/Y_RATIO)
   
		rects_vote = ax.bar(ind + 3*width, exec_time_vote, width, color='g')


		# add some text for labels, title and axes ticks
		ax.set_ylabel(y_label, fontsize=16)
		#ax.set_title('Execution time by group', fontsize=18)
		ax.set_xticks(ind + 3*width/2)
		ax.set_xticklabels(xtick_label, fontsize=16)
		#plt.ylim(0, 22)

		#ax.legend((rects_tx[0], rects_block[0], rects_vote[0]), legend_label, loc='upper left', fontsize=18)
		ax.legend((rects_tx[0], rects_mine[0], rects_block[0], rects_vote[0]), legend_label, loc='upper left', fontsize=18)

		VisualizeData.autolabel(rects_tx, ax)
		VisualizeData.autolabel(rects_mine, ax)
		VisualizeData.autolabel(rects_block, ax)
		VisualizeData.autolabel(rects_vote, ax)
		plt.show()
		pass  

	@staticmethod
	def plot_groupbars_platform(xtick_label, y_label, legend_label, ls_data):
		Y_RATIO = 1
		N = len(xtick_label)

		ind = np.arange(N)  # the x locations for the groups
		width = 0.3           # the width of the bars

		#generate bar axis object
		fig, ax = plt.subplots()

		exec_time_fog = []
		for j in range(len(ls_data[0])):
			exec_time_fog.append(float(ls_data[0][j])/Y_RATIO)

		rects_fog = ax.bar(ind, exec_time_fog, width, color='b')

		exec_time_edge = []
		for j in range(len(ls_data[0])):
			exec_time_edge.append(float(ls_data[1][j])/Y_RATIO)
   
		rects_edge = ax.bar(ind + width, exec_time_edge, width, color='g')

		# add some text for labels, title and axes ticks
		ax.set_ylabel(y_label, fontsize=16)
		#ax.set_title('Execution time by group', fontsize=18)
		ax.set_xticks(ind + width/2)
		ax.set_xticklabels(xtick_label, fontsize=16)
		#plt.ylim(0, 22)

		#ax.legend((rects_tx[0], rects_block[0], rects_vote[0]), legend_label, loc='upper left', fontsize=18)
		ax.legend((rects_fog[0], rects_edge[0]), legend_label, loc='upper left', fontsize=18)

		VisualizeData.autolabel(rects_fog, ax)
		VisualizeData.autolabel(rects_edge, ax)
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
	                ha='center', va='bottom', fontsize=12)
	        

	'''
	plot multiple lines in single chart given ls_data
	'''
	@staticmethod
	def plot_MultiLines(title_name, x_label, y_label, ls_data, isLog=0):
		Y_RATIO = 1000
		x=[]
		commit_tx=[]  
		block_proposal=[]  
		fix_head=[]  
		chain_finality=[]        
		
		# Start from 4 nodes	
		i=4
		for record in ls_data:
			x.append(i)
			if(isLog==10):
				commit_tx.append(math.log10(float(record[0])))
				block_proposal.append(math.log10( float(record[1])))
				#fix_head.append(math.log10(float(record[2])))
				chain_finality.append(math.log10(float(record[3])))
			else:
				commit_tx.append(float(record[0])/Y_RATIO)
				block_proposal.append(float(record[1])/Y_RATIO)
				#fix_head.append(float(record[2]))
				chain_finality.append(float(record[3])/Y_RATIO)			
			i+=1

		line_list=[]
		line_list.append(plt.plot(x, commit_tx, lw=1.0, marker='*', color='b'))
		line_list.append(plt.plot(x, block_proposal, lw=1.0, marker='s', color='orange'))
		#line_list.append(plt.plot(x, fix_head, lw=1.0, color='orange'))
		line_list.append(plt.plot(x, chain_finality, lw=1.0, marker='o', color='g'))

		plt.xlabel('Number of nodes', fontsize=16)
		plt.ylabel(y_label, fontsize=16)
		plt.title(title_name)
		#plt.ylim(0, 34)
		plt.legend(x_label, loc='upper left', fontsize=18)

		#show plot
		plt.show()

def ave_Totaldelay(file_name):
	exec_time_data=ExecTime.load_data(file_name)

	ave_exec_time=ExecTime.calc_exec_time(exec_time_data)

	return ave_exec_time

def cal_throughput(exec_time):
	Y_RATIO = 1000
	ls_throughput=[]
	ls_blocksize = [0.5, 1, 2, 4]
	i = 0
	for ls_time in exec_time:
		#print(ls_time)
		tmp_data = (float(ls_time[0])+float(ls_time[1])+float(ls_time[3]))/Y_RATIO 
		ls_throughput.append(format(ls_blocksize[i]*3600/tmp_data, '.0f'))
		i+=1

	print(ls_throughput)

def plot_blocksize():
	file_list = []
	file_list.append('block_size/exec_time_512K.log')
	file_list.append('block_size/exec_time_1M.log')
	file_list.append('block_size/exec_time_2M.log')
	file_list.append('block_size/exec_time_4M.log')

	'''merged_data = ExecTime.merge_exec_time('results/exec_time_client_ac.log', 
	                                       'results/capac_exec_time_server.log')
	#print(merged_data)
	ave_tmp=[0.0, 0.0, 0.0]
	ave_exec_time=ExecTime.calc_exec_time(merged_data)'''
	exec_time_data = []
	for file_name in file_list:
		exec_time_data.append(ave_Totaldelay(file_name))

	#calculate throughput
	cal_throughput(exec_time_data)

	x_label=['512 KB', '1 MB', '2 MB', '4 MB']
	legend_label=['Commit Transaction', 'Block Proposal', 'Chain Finality']

	VisualizeData.plot_groupbars_block(x_label, 'Time (s)', legend_label, exec_time_data)
    
   
def plot_nodes_latency():
	
	file_list = []
	file_list.append('network_latency/exec_time_4.log')
	file_list.append('network_latency/exec_time_5.log')
	file_list.append('network_latency/exec_time_6.log')
	file_list.append('network_latency/exec_time_7.log')
	file_list.append('network_latency/exec_time_8.log')
	file_list.append('network_latency/exec_time_9.log')
	file_list.append('network_latency/exec_time_10.log')
	file_list.append('network_latency/exec_time_11.log')
	file_list.append('network_latency/exec_time_12.log')
	file_list.append('network_latency/exec_time_13.log')
	file_list.append('network_latency/exec_time_14.log')
	file_list.append('network_latency/exec_time_15.log')
	file_list.append('network_latency/exec_time_16.log')
	file_list.append('network_latency/exec_time_17.log')

	exec_time_data = []
	for file_name in file_list:
		exec_time_data.append(ave_Totaldelay(file_name))
	print(exec_time_data)

	obj_label=['Commit Transaction', 'Block Proposal', 'Chain Finality']
	VisualizeData.plot_MultiLines("", obj_label, 'Time (s)', exec_time_data)

def plot_cost_exec():
	exec_time_data = []

	test_dir_list = []
	test_dir_list.append('cost_exec_fog/cost_exec_1K')
	test_dir_list.append('cost_exec_fog/cost_exec_512K')
	test_dir_list.append('cost_exec_fog/cost_exec_1M')

	for test_dir in test_dir_list:
		file_list = []
		file_list.append(test_dir + '/exec_verify_tx.log')
		file_list.append(test_dir + '/exec_mining.log')
		file_list.append(test_dir + '/exec_verify_block.log')
		file_list.append(test_dir + '/exec_verify_vote.log')
		ls_data = []
		for file_name in file_list:
			ls_data.append(ave_Totaldelay(file_name)[0])
		exec_time_data.append(ls_data)
	#print(exec_time_data)

	x_label=['1 KB', '512 KB', '1 MB']
	legend_label=['Verify Transaction', 'Mining Block', 'Verify Block', 'Verify Vote']

	VisualizeData.plot_groupbars_cost(x_label, 'Time (ms)', legend_label, exec_time_data)

def plot_cost_platform():
	exec_time_data = []

	test_dir_list = []
	test_dir_list.append('cost_exec_fog/cost_exec_1M')
	test_dir_list.append('cost_exec_edge/cost_exec_1M')

	for test_dir in test_dir_list:
		file_list = []
		file_list.append(test_dir + '/exec_verify_tx.log')
		file_list.append(test_dir + '/exec_mining.log')
		file_list.append(test_dir + '/exec_verify_block.log')
		file_list.append(test_dir + '/exec_verify_vote.log')
		ls_data = []
		for file_name in file_list:
			ls_data.append(ave_Totaldelay(file_name)[0])
		exec_time_data.append(ls_data)
	#print(exec_time_data)

	x_label=['Verify Transaction', 'Mining Block', 'Verify Block', 'Verify Vote']
	legend_label=['Desktop', 'Raspberry Pi B+']

	VisualizeData.plot_groupbars_platform(x_label, 'Time (ms)', legend_label, exec_time_data)

if __name__ == "__main__":
	#--------------- show nodes latency curves--------------------
	#plot_nodes_latency()

	#--------------- show block size latency curves--------------------
	#plot_blocksize()

	#--------------- show performance cost on host--------------------
	#plot_cost_exec()
	#plot_cost_platform()

	pass