#!/usr/bin/env python

'''
========================
meas_perform module
========================
Created on Nov.13, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide performance measure utilities.
'''

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np

class ExecTime(object):
	'''
	merge execution time from client and server
	'''
	@staticmethod
	def merge_exec_time(client_log, server_log):
		f_client = open(client_log, 'r')
		ls_client=f_client.readlines()
		#close file
		f_client.close()
		
		f_server = open(server_log, 'r')
		ls_server=f_server.readlines()
		#close file
		f_server.close()
		
		line_len=len(ls_client)
		
		exec_time_data=[]
		
		for i in range(line_len):
			ls_client[i]=ls_client[i].replace('\n','')
			ls_server[i]=ls_server[i].replace('\n','')
			if(ls_client[i]=='' or ls_server[i]==''):
				continue
			tmp_str=ls_server[i] +" " + ls_client[i]
			exec_time_data.append(tmp_str.split())
		
		return exec_time_data
	
	'''
	calculate execution time by using average
	'''
	@staticmethod
	def calc_exec_time(ls_exec_time):	
		ave_exec_time=[0.0, 0.0, 0.0, 0.0]
		
		for exec_time in ls_exec_time:
			for i in range(len(exec_time)):
				ave_exec_time[i]+=float(exec_time[i])
		
		for i in range(len(ls_exec_time[0])):
			ave_exec_time[i]=format(ave_exec_time[i]/len(ls_exec_time), '.3f')
		
		#print(ave_exec_time)
		return ave_exec_time

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
		Bar_list[3].set_color('gray')
		
		#add value on bar
		ax=plt.axes()
		#ax.grid()
		for p in ax.patches:
			ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/4, p.get_height()+0.2))

		#plt.xticks(x_pos, x_label)
		plt.xticks(x_pos, [])
		plt.ylabel(y_label)
		plt.title(title_name)
		
		#handles, labels = ax.get_legend_handles_labels()
		ax.legend(Bar_list[::], x_label[::], loc='upper left')
		
		plt.show()
		
	'''
	plot lines chart given ls_data
	'''
	@staticmethod
	def plot_lines(x_label, y_label, ls_data):
		x=[]
		token_verify=[]
		access_verify=[]
		sign_verify=[]
		total_delay=[]
		
		#prepare data for plot
		plot_data=[]
		i=1
		for record in ls_data:
			x.append(i)
			token_verify.append(record[0])
			access_verify.append(record[1])
			sign_verify.append(record[2])
			total_delay.append(record[3])
			i+=1
		
		plot_data.append(token_verify)
		plot_data.append(access_verify)
		plot_data.append(sign_verify)
		plot_data.append(total_delay)
		
		
		plot_gird='22'
		#define figure
		plt.figure(plot_gird) 
		
		for i in range(len(plot_data)):
			plotnum=plot_gird+str(i+1)
			
			#-----------subplot-Speed-----------
			plt.subplot(plotnum)
			#labels
			plt.xlabel(x_label[i])
			plt.ylabel(y_label)
			
			#plot data
			#plt.plot(x, plot_data[i])
			plt.plot(x, plot_data[i], lw=1.0)
			#plt.suptitle(x_label[i])
		
		#plt.title(title_name)
		
		#plt.savefig("test.pdf")
		
		#show plot
		plt.show()
		
		
	'''
	plot multiple lines in single chart given ls_data
	'''
	@staticmethod
	def plot_Multilines(title_name, x_label, y_label, ls_data):
		x=[]
		token_verify=[]
		access_verify=[]
		sign_verify=[]
		total_delay=[]
		
		#prepare data for plot
		i=1
		for record in ls_data:
			x.append(i)
			token_verify.append(record[0])
			access_verify.append(record[1])
			sign_verify.append(record[2])
			total_delay.append(record[3])
			i+=1
		line_list=[]
		line_list.append(plt.plot(x, token_verify, lw=1.0, color='r'))
		line_list.append(plt.plot(x, access_verify, lw=1.0, color='g'))
		line_list.append(plt.plot(x, sign_verify, lw=1.0, color='b'))
		line_list.append(plt.plot(x, total_delay, lw=1.0, color='gray'))
		plt.xlabel('Run cycles')
		plt.ylabel(y_label)
		
		plt.title(title_name)
		
		plt.legend(x_label, loc='upper left')
		
		#show plot
		plt.show()

def plot_bar():
	exec_time_data=ExecTime.merge_exec_time('Lan/exec_time_client.log', 'Lan/exec_time_server.log')
	#print(exec_time_data)
	ave_exec_time=ExecTime.calc_exec_time(exec_time_data)
	
	obj_label=['Token verification', 'Access right verification', 'Issuer signature verification', 'Total Delay']
	
	VisualizeData.plot_bar("Execution Time", obj_label, 'Time: ms', ave_exec_time)	
	
def plot_line():
	exec_time_data=ExecTime.merge_exec_time('Lan/exec_time_client.log', 'Lan/exec_time_server.log')
	obj_label=['Token verification', 'Access right verification', 'Issuer signature verification', 'Total Delay']
	VisualizeData.plot_lines(obj_label, 'Time: ms', exec_time_data)
	
def plot_multilines():
	exec_time_data=ExecTime.merge_exec_time('Wlan/exec_time_client.log', 'Wlan/exec_time_server.log')
	obj_label=['Token verification', 'Access right verification', 'Issuer signature verification', 'Total Delay']
	VisualizeData.plot_Multilines("Multi-Cycles Time", obj_label, 'Time: ms', exec_time_data)
			
if __name__ == "__main__":
	#plot_bar()
	#plot_line()
	plot_multilines()
	pass