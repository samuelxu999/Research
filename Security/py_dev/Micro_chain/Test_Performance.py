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
	merge execution time from client and server
	'''
	@staticmethod
	def merge_exec_time(client_log, server_ac_log):
	    #------------ read data from log file -------------
	    f_client = open(client_log, 'r')
	    ls_client=f_client.readlines()
	    #close file
	    f_client.close()        
	   
	    f_ac_server = open(server_ac_log, 'r')
	    ls_ac_server=f_ac_server.readlines()
	    #close file
	    f_ac_server.close()
	    
	    line_len=len(ls_client)
	    
	    exec_time_data=[]
	    
	    for i in range(line_len):
	        ls_client[i]=ls_client[i].replace('\n','')
	        ls_ac_server[i]=ls_ac_server[i].replace('\n','')
	        if(ls_client[i]=='' or ls_ac_server[i]==''):
	            continue
	        tmp_str = ls_ac_server[i] + " " + ls_client[i]
	        exec_time_data.append(tmp_str.split())
	    
	    return exec_time_data

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
	plot bar chart given ls_data
	'''
	@staticmethod
	def plot_bar(title_name, x_label, y_label, ls_data):
	    x_pos = np.arange(len(x_label))
	    
	    #create bar list given ls_data
	    Bar_list=plt.bar(x_pos, ls_data, align='center', alpha=0.5)
	    
	    #set color for each bar
	    Bar_list[0].set_color('r')
	    Bar_list[1].set_color('g')
	    Bar_list[2].set_color('b')
	    
	    #add value on bar
	    ax=plt.axes()
	    #ax.grid()
	    for p in ax.patches:
	        ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/3, p.get_height()+0.2))

	    #plt.xticks(x_pos, x_label)
	    plt.xticks(x_pos, [])
	    plt.ylabel(y_label)
	    plt.ylim(0, 90)
	    plt.title(title_name)
	    
	    #handles, labels = ax.get_legend_handles_labels()
	    ax.legend(Bar_list[::], x_label[::], loc='upper right')
	    
	    plt.show()

	'''
	plot groupbar chart given ls_data
	'''
	@staticmethod
	def plot_groupbar(xtick_label, y_label, legend_label, ls_data):
		Y_RATIO = 1000
		N = len(xtick_label)

		ind = np.arange(N)  # the x locations for the groups
		width = 0.30           # the width of the bars

		#generate bar axis object
		fig, ax = plt.subplots()

		exec_time_512K = []
		for i in range(len(ls_data)):
			exec_time_512K.append(float(ls_data[i][0])/1000)

		rects_512K = ax.bar(ind, exec_time_512K, width, color='b')

		exec_time_1M = []
		for i in range(len(ls_data)):
			exec_time_1M.append(float(ls_data[i][1])/1000)
   
		rects_1M = ax.bar(ind + width, exec_time_1M, width, color='orange')

		exec_time_2M = []
		for i in range(len(ls_data)):
			exec_time_2M.append(float(ls_data[i][3])/1000)
   
		rects_2M = ax.bar(ind + 2*width, exec_time_2M, width, color='g')


		# add some text for labels, title and axes ticks
		ax.set_ylabel(y_label, fontsize=16)
		#ax.set_title('Execution time by group', fontsize=18)
		ax.set_xticks(ind + width)
		ax.set_xticklabels(xtick_label, fontsize=16)
		#plt.ylim(0, 22)

		ax.legend((rects_512K[0], rects_1M[0], rects_2M[0]), legend_label, loc='upper left', fontsize=18)

		VisualizeData.autolabel(rects_512K, ax)
		VisualizeData.autolabel(rects_1M, ax)
		VisualizeData.autolabel(rects_2M, ax)
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

def plot_bars():
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
	#for tmp in exec_time_data:
	#	print(tmp)

	x_label=['512 KB', '1 MB', '2 MB', '4 MB']
	legend_label=['Commit Transaction', 'Block Proposal', 'Chain Finality']

	VisualizeData.plot_groupbar(x_label, 'Time (s)', legend_label, exec_time_data)
    
   
def plot_lines():
	
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
	#print(exec_time_data)

	obj_label=['Commit Transaction', 'Block Proposal', 'Chain Finality']
	VisualizeData.plot_MultiLines("", obj_label, 'Time (s)', exec_time_data)

def ave_Totaldelay(file_name):
	exec_time_data=ExecTime.load_data(file_name)

	ave_exec_time=ExecTime.calc_exec_time(exec_time_data)

	return ave_exec_time
    
if __name__ == "__main__":
	#matplotlib.rcParams.update({'font.size': 16})
	#plot_bar()
	file_name='block_size/exec_time_512K.log'
	#file_name='network_latency/exec_time_12.log'
	#print(ave_Totaldelay(file_name))

	#--------------- show nodes latency curves--------------------
	#plot_lines()

	#--------------- show block size latency curves--------------------
	#plot_bars()

	pass