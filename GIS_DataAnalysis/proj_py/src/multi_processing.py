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

import time, math, sys, os
import logging
import multiprocessing
import numpy as np
from RF_Nepal import RF_Nepal
from Data_Preprocessing import Pre_Data
from utilities import FileUtil

logger = logging.getLogger(__name__)


def multiprocessing_func(data_config):
	## Call process func
	RF_Nepal.RF_predict(data_config)


def getSRvalues(data_config):
	## parameters configuration setup
	data_dir = data_config['dataset']
	row_start= data_config['process_region'][0]
	row_end = data_config['process_region'][1]
	col_start = data_config['process_region'][2]
	col_end = data_config['process_region'][3]

	data_type = data_config['data_type']

	ls_datainfo=Pre_Data.get_datainfo(data_dir)

	SR_BandValues = Pre_Data.get_SR_Values(ls_datainfo, row_start, row_end, col_start, col_end)
	logger.info("Calculate SR_BandValues, region: {}, shape:{}".format(data_config['process_region'], SR_BandValues.shape))

	if(data_type==1):
		## setup directory to save all SR_BandValues as csv file
		csv_dir = "../csv_data/"

		## a) set csv path to save SR_BandValues
		csv_path = os.path.join(csv_dir, "Range_{}_{}_{}_{}.csv".format(row_start, row_end, col_start, col_end))
		
		## b) save SR_BandValues to csv file
		start_time=time.time()
		if(not os.path.exists(csv_dir)):
					os.makedirs(csv_dir)	

		FileUtil.data2csv(csv_path, SR_BandValues)
		exec_time=time.time()-start_time
		logger.info("Save SR_BandValues to {}, Running time: {:.3f} s".format(csv_path, exec_time))

		## c) reload data from csv file
		start_time=time.time()
		np_SR_BandValues = FileUtil.csv2data(csv_path)
		exec_time=time.time()-start_time
		logger.info("Reload {}, shape:{}, Running time: {:.3f} s".format(csv_path, np_SR_BandValues.shape, exec_time))
	else:
		## setup directory to save all SR_BandValues as npy file
		npy_dir = "../npy_data/"

		## a) set npy path to save SR_BandValues
		npy_path = os.path.join(npy_dir, "Range_{}_{}_{}_{}.npy".format(row_start, row_end, col_start, col_end))
		
		## b) save SR_BandValues to csv file
		start_time=time.time()
		if(not os.path.exists(npy_dir)):
			os.makedirs(npy_dir)	

		np.save(npy_path, SR_BandValues)
		exec_time=time.time()-start_time
		logger.info("Save SR_BandValues to {}, Running time: {:.3f} s".format(npy_path, exec_time))

		## c) reload data from csv file
		start_time=time.time()
		np_SR_BandValues = np.load(npy_path)
		exec_time=time.time()-start_time
		logger.info("Reload {}, shape:{}, Running time: {:.3f} s".format(npy_path, np_SR_BandValues.shape, exec_time))


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
		logger.info('Total pixel number:', pixel_num)
		
		# pixel_num = 14

		# set process_range and final_range that are used to split predicate into multiple process
		process_range = math.floor(pixel_num/pix_range_step)

		final_range = pixel_num%pix_range_step

		# logger.info(process_range, final_range)
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

		logger.info('That took {} seconds'.format(time.time() - starttime))

'''
Multiprocess task class
'''
class Multi_PreData(object):
	@staticmethod
	def multi_getSRvalues(data_config={}):

		## ----------------- Set run_range, process step is 1 row  -----------------------
		run_range = data_config['row_range'][1]-data_config['row_range'][0]

		## new process_region to record region data for each process.
		data_config['process_region'] = [0,0,0,0]

		## ----------------- evalualte time cost -----------------------
		starttime = time.time()

		## new processes pool
		processes = []		

		# ----------------- Start multiprocessing tasks -----------------------
		for run_index in range(0, run_range):
			## set process_region that are used to feed each process 
			data_config['process_region'][0] = data_config['row_range'][0]+run_index
			data_config['process_region'][1] = data_config['process_region'][0]+1
			data_config['process_region'][2] = data_config['col_range'][0]
			data_config['process_region'][3] = data_config['col_range'][1]
			
			# logger.info(data_config)
			p = multiprocessing.Process(target=getSRvalues, args=(data_config,))
			processes.append(p)
			p.start()

		for process in processes:
			process.join()

		logger.info('That took {} seconds'.format(time.time() - starttime))
