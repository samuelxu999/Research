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

'''
Data preparation class, such as merge data, calculate execute time
'''
class ExecTime(object):
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
        plt.ylim(0, 300)
        plt.title(title_name)
        
        #handles, labels = ax.get_legend_handles_labels()
        ax.legend(Bar_list[::], x_label[::], loc='upper right')
        
        plt.show()

    '''
    plot groupbar chart given ls_data
    '''
    @staticmethod
    def plot_groupbar_Platform(xtick_label, y_label, legend_label, ls_data):
        
        N = len(xtick_label)
        
        ind = np.arange(N)  # the x locations for the groups
        width = 0.30           # the width of the bars
        
        #generate bar axis object
        fig, ax = plt.subplots()
        
        edge_exec_time = ls_data[0]
        rects_edge = ax.bar(ind, edge_exec_time, width, color='g')
        
        fog_exec_time = ls_data[1]    
        rects_fog = ax.bar(ind + width, fog_exec_time, width, color='b')
        
       
        # add some text for labels, title and axes ticks
        ax.set_ylabel(y_label)
        #ax.set_title('Execution time by group', fontsize=18)
        ax.set_xticks(ind + width/2)
        ax.set_xticklabels(xtick_label, fontsize=16)
        #plt.ylim(0, 70)
        
        ax.legend((rects_edge[0], rects_fog[0]), legend_label, loc='upper left', fontsize=18)
        
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
                    ha='center', va='bottom', fontsize=12)
            
    
    '''
    plot multiple lines in single chart given ls_data
    '''
    @staticmethod
    def plot_ACVsNoAC(title_name, x_label, y_label, ls_data):
        x=[]
        AC_edge_delay=[]
        NoAC_edge_delay=[]
        AC_fog_delay=[]  
        NoAC_fog_delay=[]      
        #prepare data for plot
        i=1
        for record in ls_data:
            x.append(i)
            AC_edge_delay.append(record[0])
            NoAC_edge_delay.append(record[1])
            AC_fog_delay.append(record[2])
            NoAC_fog_delay.append(record[3])
            i+=1
            
        line_list=[]
        line_list.append(plt.plot(x, AC_edge_delay, lw=1.0, color='orange'))
        line_list.append(plt.plot(x, NoAC_edge_delay, lw=1.0, color='g'))
        line_list.append(plt.plot(x, AC_fog_delay, lw=1.0, color='r'))
        line_list.append(plt.plot(x, NoAC_fog_delay, lw=1.0, color='b'))
        plt.xlabel('Run cycles', fontsize=14)
        plt.ylabel(y_label, fontsize=14)
        plt.title(title_name)
        #plt.ylim(0, 300)
        plt.legend(x_label, loc='upper right', fontsize=14)
        
        #show plot
        plt.show()

def plot_bar():
    #exec_time_data=ExecTime.read_exec_time('test_results/exec_time_edge.log')
    merged_data = ExecTime.merge_exec_time('results/nocache/edge/exec_time_client_ac.log', 
                                           'results/nocache/edge/auth_exec_time_server.log', 
                                           'results/nocache/edge/capac_exec_time_server.log')
    #print(merged_data)
    ave_tmp=[0.0, 0.0, 0.0]
    ave_exec_time=ExecTime.calc_exec_time(merged_data)
    
    obj_label=['Identity Authentication', 'Capability-based Access Control', 'Total Delay']
    
    VisualizeData.plot_bar("", obj_label, 'Time (ms)', ave_exec_time)
    
def plot_groupbar_Platform():
    xtick_label=['Identity Authentication', 'Capability-based Access Control', 'Total Delay']
    legend_label=['Edge', 'Fog']
    
    #prepare data
    ls_exec_time=[]

    edge_exec_time = ExecTime.merge_exec_time('results/nocache/edge/exec_time_client_ac.log', 
                                              'results/nocache/edge/auth_exec_time_server.log', 
                                              'results/nocache/edge/capac_exec_time_server.log')
    
    edge_ave_exec_time = ExecTime.calc_exec_time(edge_exec_time)

    fog_exec_time = ExecTime.merge_exec_time('results/nocache/fog/exec_time_client_ac.log', 
                                             'results/nocache/fog/auth_exec_time_server.log', 
                                             'results/nocache/fog/capac_exec_time_server.log')
    
    fog_ave_exec_time = ExecTime.calc_exec_time(fog_exec_time)
    
    #append data to list
    ls_exec_time.append(edge_ave_exec_time)
    ls_exec_time.append(fog_ave_exec_time)

    VisualizeData.plot_groupbar_Platform(xtick_label,'Time (ms)', legend_label, ls_exec_time)
    
def plot_lines():
    #exec_time_data=ExecTime.merge_data('BlendCapAC_optimized/exec_time_client.log', 'CapVsNoCap/exec_time_client_NoCap.log')
    file_list=['results/cache/edge/exec_time_client_ac.log']
    file_list.append('results/cache/edge/exec_time_client_noac.log')
    file_list.append('results/cache/fog/exec_time_client_ac.log')
    file_list.append('results/cache/fog/exec_time_client_noac.log')
    exec_time_data=ExecTime.merge_files(file_list)
    
    #print(exec_time_data)
    obj_label=['BlendCAC on edge', 'No Access Control on edge', 'BlendCAC on fog', 'No Access Control on fog']
    VisualizeData.plot_ACVsNoAC("", obj_label, 'Time (ms)', exec_time_data)

def ave_Totaldelay():
    #exec_time_data=ExecTime.merge_data('BlendCapAC_optimized/exec_time_client.log', 'CapVsNoCap/exec_time_client_NoCap.log')
    file_list=['results/cache/edge/exec_time_client_ac.log']
    file_list.append('results/cache/edge/exec_time_client_noac.log')
    file_list.append('results/cache/fog/exec_time_client_ac.log')
    file_list.append('results/cache/fog/exec_time_client_noac.log')
    exec_time_data=ExecTime.merge_files(file_list)
    
    ave_exec_time=ExecTime.calc_exec_time(exec_time_data)
    
    print(ave_exec_time)
    
if __name__ == "__main__":
    #matplotlib.rcParams.update({'font.size': 16})
    #plot_bar()
    #plot_groupbar_Platform()
    #plot_lines()
    ave_Totaldelay()
    pass