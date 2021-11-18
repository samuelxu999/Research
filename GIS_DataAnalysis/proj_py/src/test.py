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
import time, sys, os
import argparse
import logging
from curve_validation import Curve_Validation
from RF_Nepal import RF_Nepal
from multi_processing import Multi_ProcessRF
from Data_Preprocessing import Pre_Data
from utilities import FileUtil
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
	data_config['pixel_range'] = [27,30]
	data_config['year_range'] = [2018,1986]
	data_config['predictset'] = "RF_Predicate/"
	data_config['predict_matrix'] = "predict_matrix"

	RF_Nepal.RF_predict(data_config)

def test_Merge_predict():
	data_config= {}
	data_config['dataset'] = "../training_set/"
	data_config['file_traindata'] = "trainset.dat"
	data_config['file_tif'] = "141041_Kathmandu_Charikot_subset.tif"
	data_config['coefset'] = "TS_Coefficients/"
	data_config['predictset'] = "RF_Predicate/"
	data_config['predict_matrix'] = "predict_matrix"
	RF_Nepal.Merge_predict(data_config)

def test_Load_predict():
	data_config= {}
	data_config['dataset'] = "../training_set/"
	data_config['predict_merge'] = "merged_predict.npy"
	np_merged_results, mat_merged_results = RF_Nepal.Load_predict(data_config)
	print("Loaded Merged results npy shape:", np_merged_results.shape)
	print("Loaded Merged results mat shape:", mat_merged_results['merged_results'].shape)
	print(np_merged_results[-1])

def test_Multi_Process_RF():
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
	data_config['pix_range_step'] = 10

	Multi_ProcessRF.multi_processRF(data_config)


def test_readArray(args):
	## ----------------- test readArray performance -------------------- 
	start_time=time.time()
	raster_file = "../VIIRS_ntl/201401/SVDNB_npp_20140101-20140131_00N060E_vcmslcfg_v10_c2015006171539.avg_rade9h.tif" 
	if(args.op_status==1):
		raster_array=Pre_Data.raster2array(raster_file, True)
	else:
		raster_array=Pre_Data.raster2array(raster_file, False)
	exec_time=time.time()-start_time
	print("raster_array shape: {}".format(raster_array.shape))
	print("Running time: {:.3f} s".format(exec_time))	

def test_getSRvalues():
	## ------------------------------ test configuration --------------------------------
	## raw data sources
	data_dir = "/media/external/Deng/142041/LC081420412013041501T1-SC20191127190639"
	# data_dir = "/media/external/viirs_all"
	# data_dir = "/media/external/Deng/142041"

	## csv data directory to save all SR_BandValues
	csv_dir = "../csv_data/"

	## set data range that is used to process a region of the map figure. 
	row_start=870
	row_end=871
	col_start=0
	col_end=1

	## --------------------------- SR_BandValues process test ----------------------------
	## 1) for each file to get data information ['raster_file', [band, Band_Number, band_list], Julian_Day]
	ls_datainfo=Pre_Data.get_datainfo(data_dir)
	# print(ls_datainfo[0])

	## 2) Get SR_BandValues by for each ls_datainfo
	start_time=time.time()
	SR_BandValues = Pre_Data.get_SR_BandValues(ls_datainfo, row_start, row_end, col_start, col_end)
	print("Calculate SR_BandValues, shape:{}".format(SR_BandValues.shape))
	# print(SR_BandValues.T[0][0].T)
	# print(SR_BandValues.T[0])
	exec_time=time.time()-start_time
	print("Running time: {:.3f} s".format(exec_time))


	## --------------------------- data save and read test ----------------------------
	## a) set csv path to save SR_BandValues
	csv_path = os.path.join(csv_dir, "Range_{}_{}_{}_{}.csv".format(row_start, row_end, col_start, col_end))
	
	## b) save SR_BandValues to csv file
	start_time=time.time()
	if(not os.path.exists(csv_dir)):
				os.makedirs(csv_dir)	

	FileUtil.data2csv(csv_path, SR_BandValues)
	print("Save SR_BandValues to {}".format(csv_path))
	exec_time=time.time()-start_time
	print("Running time: {:.3f} s".format(exec_time))

	## c) reload data from csv file
	start_time=time.time()
	np_SR_BandValues = FileUtil.csv2data(csv_path)
	print("Reload {}    shape:{}".format(csv_path, np_SR_BandValues.shape))
	exec_time=time.time()-start_time
	print("Running time: {:.3f} s".format(exec_time))


def define_and_get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Run test evaulation app."
    )
    parser.add_argument("--test_func", type=int, default=0, 
                        help="Execute test operation: \
                        0-function test, \
                        1-test_validation, \
                        2-test_create_train_table, \
                        3-test_RF_predict, \
                        4-test_Multi_Process_RF, \
                        5-test_Merge_predict, \
                        6-test_Load_predict, \
                        7-test_readArray, \
                        8-test_getSRvalues")
    parser.add_argument("--op_status", type=int, default=0, 
                        help="Execute test based on condition.")

    args = parser.parse_args(args=args)
    return args

if __name__ == "__main__":
	FORMAT = "%(asctime)s %(levelname)s | %(message)s"
	LOG_LEVEL = logging.INFO
	logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

	PreData_logger = logging.getLogger("Pre_Data")
	PreData_logger.setLevel(logging.INFO)

	## define arguments for test app
	args = define_and_get_arguments()

	if(args.test_func==1):
		test_validation()
	elif(args.test_func==2):
		test_create_train_table()
	elif(args.test_func==3):
		test_RF_predict()
	elif(args.test_func==4):
		test_Multi_Process_RF()
	elif(args.test_func==5):
		test_Merge_predict()
	elif(args.test_func==6):
		test_Load_predict()
	elif(args.test_func==7):
		test_readArray(args)
	elif(args.test_func==8):
		test_getSRvalues()
	else:
		pass