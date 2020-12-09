'''
========================
utilities.py
========================
Created on Dec.8, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility function to support project.
@Reference: 
'''

import glob, os
import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt

'''
FileUtil class for handling file read and write
'''
class FileUtil(object):
	@staticmethod
	def csv_read(csv_file):
		'''
		Function: Read data from csv file
		@arguments: 
		(out) np_dataset:   	return np.array object
		(in) csv_file:   		csv file path
		'''
		ls_dataset = []
		with open(csv_file, 'r') as csvFile:
			csv_reader = csv.reader(csvFile, delimiter=',')
			for row in csv_reader:
				ls_dataset.append(row)
		# transfer to np array and return
		np_dataset = np.array(ls_dataset)
		return np_dataset

	@staticmethod
	def csv_write(csv_file, dataset):
		'''
		Function: Write data to csv file
		@arguments: 
		(in) dataset:   	np.array data
		(in) csv_file:   	csv file path
		'''
		ls_dataset = []
		with open(csv_file, 'a') as csvFile:
			csv_writer = csv.writer(csvFile, delimiter=',')
			for row in dataset:
				csv_writer.writerow(row)

'''
TypesUtil class used to convert between differnt data type and format
'''
class TypesUtil(object):
	# list dataset to numpy matrix
	@staticmethod
	def list2np(ls_data):
		# transfer to np array and return
		np_data = np.array(ls_data, dtype=np.float32)
		return np_data

	# numpy matrix to list dataset
	@staticmethod
	def np2list(np_data):
		# transfer to list dataset and return
		ls_data = np_data.tolist()
		return ls_data

'''
PlotUtil class for data visualization
'''
class PlotUtil(object):
	@staticmethod
	def Plotline(ENF_dataset, font_size=14, is_show=True, is_savefig=False, datafile=''):
		'''
		Function: plot ENF data as line on fig
		@arguments: 
		(in) ENF_dataset: 	ENF list dataset that can input two ENF signals
			   font_size:	font size for label and legend
			     is_show:	Display plot on screen
			  is_savefig:	Save plot on local as *.png
			  	datafile:	file name to save plot
		'''
		ls_color=['darkorange', 'seagreen']
		legend_label = []
		for ENF_id in range(len(ENF_dataset)):
			#generate x and y data
			xdata = [];
			ydata = [];
			ls_dataset = ENF_dataset[ENF_id]
			for i in range(0, len(ls_dataset)):
				xdata.append(i)
				ydata.append( float(ls_dataset[i][1]) )

			line_list=[]
			line_list.append(plt.plot(xdata, ydata, lw=1.0, color=ls_color[ENF_id]))
			legend_label.append("ENF-{}".format(ENF_id))

		plt.xlabel('Time slot', fontsize=font_size)
		plt.ylabel('ENF (HZ)', fontsize=font_size) 
		# plt.ylim(59.995, 60.005)
		plt.legend(legend_label, loc='upper right', fontsize=font_size)
		
		if( is_show ):
			plt.show()
		if( is_savefig ):
			figname = os.path.splitext(datafile)[0] +'.png'
			plt.savefig(figname)
		plt.close()
