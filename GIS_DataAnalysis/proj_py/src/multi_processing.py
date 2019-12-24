'''
========================
test.py
========================
Created on Dec.16, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for multiprocessing task.
@Reference: https://medium.com/@urban_institute/using-multiprocessing-to-make-python-code-faster-23ea5ef996ba
'''

import time, math
import multiprocessing 
from RF_Nepal import RF_Nepal
from utilities import FileUtil


def multiprocessing_func(data_config):
	# print(data_config)
	RF_Nepal.RF_predict(data_config)


'''
Multiprocess task class
'''
class Multi_ProcessRF(object):
	@staticmethod
	def multi_processRF(data_config={}):

		# ----------------- Set process ranges and pix step -----------------------
		pix_range_step = data_config['pix_range_step']

		# Get coefset data file list
		ls_files = FileUtil.list_files(data_config['dataset'] + data_config['coefset'], '*.csv')

		# calculate pixel number
		pixel_num = len(ls_files)
		print('Total pixel number:', pixel_num)
		
		# pixel_num = 14

		# set process_range and final_range that are used to split predicate into multiple process
		process_range = math.floor(pixel_num/pix_range_step)

		final_range = pixel_num%pix_range_step

		# print(process_range, final_range)
		# ----------------- evalualte time cost -----------------------
		starttime = time.time()

		processes = []

		# ----------------- Start multiprocessing tasks -----------------------
		for run_index in range(0, process_range):
			data_config['pixel_range'] = [run_index*pix_range_step,(run_index+1)*pix_range_step]
			p = multiprocessing.Process(target=multiprocessing_func, args=(data_config,))
			processes.append(p)
			p.start()
		
		if( final_range!=0 ):
			data_config['pixel_range'] = [process_range*pix_range_step,process_range*pix_range_step+final_range]
			p = multiprocessing.Process(target=multiprocessing_func, args=(data_config,))
			processes.append(p)
			p.start()

		for process in processes:
			process.join()

		print('That took {} seconds'.format(time.time() - starttime))
