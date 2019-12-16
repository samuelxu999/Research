'''
========================
test.py
========================
Created on Oct.9, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for functions test.
@Reference: 
'''

from curve_validation import Curve_Validation
from RF_Nepal import RF_Nepal
import numpy as np

def test_validation():
	data_config= {}
	data_config['dataset'] = "../dataset/"
	data_config['datatype'] = "*.xlsx"
	data_config['test_dir'] = "../test_results/"
	
	Curve_Validation.test_validation(data_config)

def test_create_train_table():
	data_config= {}
	data_config['dataset'] = "../training_set/"
	data_config['file_tif'] = "141041_Kathmandu_Charikot_subset.tif"
	data_config['file_xls'] = "Samples_Charikot_1012.xlsx"
	data_config['file_traindata'] = "trainset.dat"
	data_config['coefset'] = "TS_Coefficients/"
	RF_Nepal.create_training_table(data_config)

def test_RF_predict():
	data_config= {}
	data_config['dataset'] = "../training_set/"
	data_config['file_traindata'] = "trainset.dat"
	data_config['file_tif'] = "141041_Kathmandu_Charikot_subset.tif"
	data_config['coefset'] = "TS_Coefficients/"
	data_config['pixel_range'] = [4,6]
	data_config['year_range'] = [2018,1986]
	data_config['predictset'] = "RF_Predicate/"
	data_config['predict_matrix'] = "predict_matrix"

	# RF_Nepal.RF_predict(data_config)
	RF_Nepal.Merge_predict(data_config)



if __name__ == "__main__":
	# test_validation()
	# test_create_train_table()
	# test_RF_predict()
	pass