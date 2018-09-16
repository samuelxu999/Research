#!/usr/bin/env python

'''
========================
meas_perform module
========================
Created on July.10, 2018
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide performance measure utilities.
'''
import matplotlib
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np


class ExecTime(object):
    '''
    read execution time from log
    '''
    @staticmethod
    def read_exec_time(server_log):
        # read data from log file
        f_server = open(server_log, 'r')
        ls_server=f_server.readlines()
        #close file
        f_server.close()
        
        line_len=len(ls_server)
        
        exec_time_data=[]
        
        for i in range(line_len):
            ls_server[i]=ls_server[i].replace('\n','')
            if(ls_server[i]==''):
                continue
            exec_time_data.append(ls_server[i].split())
        
        return exec_time_data
    
    '''
    calculate execution time by using average
    '''
    @staticmethod
    def calc_exec_time(ls_exec_time):    
        ave_exec_time=[0.0, 0.0, 0.0]
        
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
        
        #add value on bar
        ax=plt.axes()
        #ax.grid()
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/3, p.get_height()+0.2))

        #plt.xticks(x_pos, x_label)
        plt.xticks(x_pos, [])
        plt.ylabel(y_label)
        plt.ylim(0, 70)
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
        rects_fog = ax.bar(ind + width, fog_exec_time, width, color='r')
        
       
        # add some text for labels, title and axes ticks
        ax.set_ylabel(y_label)
        #ax.set_title('Execution time by group', fontsize=18)
        ax.set_xticks(ind + width)
        ax.set_xticklabels(xtick_label)
        #plt.ylim(0, 70)
        
        ax.legend((rects_edge[0], rects_fog[0]), legend_label, loc='upper right', fontsize=14)
        
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

def plot_bar():
    exec_time_data=ExecTime.read_exec_time('test_results/exec_time_edge.log')
    #print(exec_time_data)
    ave_exec_time=ExecTime.calc_exec_time(exec_time_data)
    
    obj_label=['Query Indexed Token', 'Extract Information', 'Verify Index']
    
    VisualizeData.plot_bar("", obj_label, 'Time (ms)', ave_exec_time)
    
def plot_groupbar_Platform():
    xtick_label=['Query Indexed Token', 'Extract Information', 'Verify Index']
    legend_label=['Edge', 'Fog']
    
    #prepare data
    ls_exec_time=[]
    edge_exec_time=ExecTime.read_exec_time('test_results/exec_time_edge.log')
    edge_ave_exec_time=ExecTime.calc_exec_time(edge_exec_time)

    fog_exec_time=ExecTime.read_exec_time('test_results/exec_time_fog.log')
    fog_ave_exec_time=ExecTime.calc_exec_time(fog_exec_time)
    
    #append data to list
    ls_exec_time.append(edge_ave_exec_time)
    ls_exec_time.append(fog_ave_exec_time)

    VisualizeData.plot_groupbar_Platform(xtick_label,'Time (ms)', legend_label, ls_exec_time)
    
if __name__ == "__main__":
    matplotlib.rcParams.update({'font.size': 16})
    #plot_bar()
    plot_groupbar_Platform()
    pass