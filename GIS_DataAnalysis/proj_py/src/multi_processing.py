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

import time
import multiprocessing 
from RF_Nepal import RF_Nepal


def multiprocessing_func(data_config):
	# print(data_config)
	RF_Nepal.RF_predict(data_config)
    

if __name__ == '__main__':

	# ----------------- Prepare data config -----------------------
	data_config= {}
	data_config['dataset'] = "../training_set/"
	data_config['file_traindata'] = "trainset.dat"
	data_config['file_tif'] = "141041_Kathmandu_Charikot_subset.tif"
	data_config['coefset'] = "TS_Coefficients/"
	# data_config['pixel_range'] = [4,6]
	data_config['year_range'] = [2018,1986]
	data_config['predictset'] = "RF_Predicate/"
	data_config['predict_matrix'] = "predict_matrix"

	# ----------------- Set process ranges and pix step -----------------------
	pix_range_step = 3

	process_range = 3

	# ----------------- evalualte time cost -----------------------
	starttime = time.time()

	processes = []

	# ----------------- Start multiprocessing tasks -----------------------
	for run_index in range(0, process_range):
		data_config['pixel_range'] = [run_index*pix_range_step,(run_index+1)*range_step]
		p = multiprocessing.Process(target=multiprocessing_func, args=(data_config,))
		processes.append(p)
		p.start()

	for process in processes:
		process.join()

	print('That took {} seconds'.format(time.time() - starttime))
	pass