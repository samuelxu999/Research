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
import copy
from RF_Nepal import RF_Nepal
from Data_Preprocessing import Pre_Data
from TS_fit import TS_Fit
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

def ts_fit(param_config):
	## parse parameters
	data_dir = param_config['data_dir']
	result_dir = param_config['result_dir']

	## set data range that is used to process a region of the map figure. 
	region_param = param_config['region'].split('_')
	row_start= int(region_param[0])
	row_end = int(region_param[1])
	col_start = int(region_param[2])
	col_end = int(region_param[3])

	## set fit parameter.
	fit_function = param_config['fit_func']
	json_param = {}
	json_param['output_dir'] = '{}/{}/'.format(result_dir, fit_function)
	json_param['region_param'] = [row_start, col_start]
	json_param['fit_type'] = fit_function
	json_param['is_optimized'] = param_config['optimized']
	json_param['showfig'] = param_config['showfig']
	json_param['savefig'] = param_config['savefig']

	## 1) for each file to get data information ['raster_file', [band, Band_Number, band_list], Julian_Day]
	ls_datainfo=Pre_Data.get_datainfo(data_dir)

	## 2) Get SR_BandValues by for each ls_datainfo
	SR_BandValues = Pre_Data.get_SR_Values(ls_datainfo, row_start, row_end, col_start, col_end)
	logger.info("Get SR_BandValues, row:{}-{}, column:{}-{}, shape:{}".format(row_start, row_end, col_start, col_end, 
																				SR_BandValues.shape))
	## 3) Use TS_fit.norm_data() to normalize SR_BandValues
	logger.info("Apply TS_fit: {}\t region: {}".format(fit_function, param_config['region']))
	norm_values, ls_datetime = TS_Fit.norm_data(SR_BandValues, norm_type=param_config['norm_type'], 
															isDebug=param_config['isdebug'])

	## 4) Apply TS_fit_model to analyze data, Get RMSE results from TS_fit_model.
	ret_RMSE = TS_Fit.fit_model(norm_values, ls_datetime, fit_param=json_param, 
															isDebug=param_config['isdebug'])

	## 5) save log as csv file
	csv_log = '{}/{}_{}.csv'.format(result_dir, fit_function, param_config['region'])
	FileUtil.csv_write(csv_log,ret_RMSE)


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

		logger.info('Task took {} seconds'.format(time.time() - starttime))

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

		logger.info('Task took {} seconds'.format(time.time() - starttime))

'''
Multiprocess task class to handle fit model
'''
class Multi_fit(object):
	@staticmethod
	def TS_fit(param_config):
		## ----------------- Set run_range, process step is 1 row  -----------------------
		region_param = param_config['region'].split('_')
		run_range = int(region_param[1])-int(region_param[0])

		## ----------------- evalualte time cost -----------------------
		starttime = time.time()

		## new processes pool
		processes = []		

		# ----------------- Start multiprocessing tasks -----------------------
		for run_index in range(0, run_range):
			## make a copy of param_config
			_param_config = copy.deepcopy(param_config)
			row_id = int(region_param[0])+run_index
			## set process_region that are used to feed each process 
			_param_config['region'] = "{}_{}_{}_{}".format(row_id,
				row_id+1, int(region_param[2]), int(region_param[3]))
			
			# logger.info(data_config)
			p = multiprocessing.Process(target=ts_fit, args=(_param_config,))
			processes.append(p)
			p.start()

		for process in processes:
			process.join()

		logger.info('Task took {} seconds'.format(time.time() - starttime))
