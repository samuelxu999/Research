'''
========================
utilities.py
========================
Created on Oct.9, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for functions test.
@Reference: 
'''

from utilities import *
from curve_fit import *
import numpy as np
from operator import itemgetter
from fit_validation import FitValidation

def test_validation(dataset_config):
	# Get data file list
	ls_files = FileUtil.list_files(dataset_config['dataset'], dataset_config['datatype'])

	batch_test = False
	if(not batch_test):
		#==================== single test ==========================
		test_file = ls_files[3]
		print(test_file)
		data_file = dataset_config['dataset'] + test_file
		dataset = FileUtil.xlsread(data_file, ['A2','C500'], True)
		#dataset = FileUtil.xlsread(data_file, is_dropNaN=True)
		#print(len(dataset))
		#print(dataset[0])

		#process raw data to get year average dataset	
		pre_dataset = DataUtil.PrepareData(dataset)
		#print(pre_dataset)
		print(FitValidation.valid_curvefit(pre_dataset, 'sigmoid', showfig=True))
		print(FitValidation.valid_curvefit(pre_dataset, 'gussain', showfig=True))
		print(FitValidation.valid_curvefit(pre_dataset, 'polynom', showfig=True))
	else:
		RMSE_list = []
		#==================== Group test ==========================
		for test_file in ls_files[0:-1]:
			RMSE_row = []
			RMSE_row.append(test_file)

			# get data file
			data_file = dataset_config['dataset'] + test_file

			# get dataset from file
			dataset = FileUtil.xlsread(data_file, ['A2','C500'], True)
			pre_dataset = DataUtil.PrepareData(dataset)


			# -------------- fit and validate test ----------------
			RMSE_tuples = []

			RMSE_tuples.append( ('sigmoid', FitValidation.valid_curvefit(pre_dataset, 'sigmoid')) )
			RMSE_tuples.append( ('gussain', FitValidation.valid_curvefit(pre_dataset, 'gussain')) )
			RMSE_tuples.append( ('polynom', FitValidation.valid_curvefit(pre_dataset, 'polynom')) )

			RMSE_sorted = sorted(RMSE_tuples, key=itemgetter(1))
	
			#print(RMSE_sorted)
			RMSE_row.append(RMSE_sorted[0][0])
			RMSE_row.append(RMSE_sorted[0][1])
			RMSE_list.append(RMSE_row)	
		
		
			# ------------- plot and save optimized fitting curve ---------
			figfile = dataset_config['test_dir'] + test_file
			FitValidation.valid_curvefit(pre_dataset, RMSE_row[1], 
										showfig=False, savefig=True, fig_file=figfile)
	
		#print(RMSE_list)
		# write test result into log_file
		log_file = dataset_config['test_dir'] + 'RMSE.txt'
		FileUtil.AddDataByLine(log_file, RMSE_list)


if __name__ == "__main__":
	data_config= {}
	data_config['dataset'] = "../dataset/"
	data_config['datatype'] = "*.xlsx"
	data_config['test_dir'] = "../test_results/"
	
	test_validation(data_config)

	pass