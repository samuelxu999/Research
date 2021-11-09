'''
========================
Data_Preprocessing.py
========================
Created on Jan.20, 2020
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for data preparasion task.
@Reference:
'''

import time, math, os
from datetime import datetime
import numpy as np
import gdal
# import ccd

from utilities import FileUtil


def walkFiles(srcPath, ext=".tif"):
	'''
	Function: walk in all files within a directory.
	@srcPath: 		directory path that saves files
	@fileList: 		sorted list of files
	'''
	if not os.path.exists(srcPath):
		print("not find path:{0}".format(srcPath))
		return None
	if os.path.isfile(srcPath):
		return None

	if os.path.isdir(srcPath):
		fileList = []
		for root, dirs, files in os.walk(srcPath):
			for name in files:
				filePath = os.path.join(root, name)
				if ext:
					if ext == os.path.splitext(name)[1]:
						fileList.append(filePath)
				else:
					fileList.append(filePath)
		fileList.sort()
		return fileList
	else:
	    return None

def walkDirs(srcPath):
	'''
	Function: walk in all children folders within a directory.
	@srcPath: 			directory path that saves files
	@datapath_list: 	list of children folders
	'''
	datapath_list=[]
	for home, dirs, files in os.walk(srcPath):
		dirs_list = []
		if( files != []):	
			dirs_list.append(home)		
			dirs_list.append(walkFiles(home))
			datapath_list.append(dirs_list)
	return datapath_list

def QA_Conversion(raw_value):
	'''
	Function: convert data to QA value.
	@raw_value: 	original data
	@QA_value: 		converted QA data
	'''
	if(raw_value == 1):
		QA_value = 255    
	    
	elif(raw_value == 0):
		QA_value = 4
	    
	else:
		QA_value = int(math.log2(raw_value % 64) - 1)
	    
	if(QA_value > 4):
		QA_value = 4 

	return QA_value

def date_Conversion(Day_Original):
	'''
	Function: convert date to Julian_Day.
	@Day_Original: 		original day
	@Julian_Day: 		Julian day
	'''
	Date_value = datetime.strptime(Day_Original, '%Y%m%d').date()
	Julian_Day = Date_value.toordinal()
	return Julian_Day

def raster2array(rasterfn, isAlldata=True):
	'''
	Function: demo and test reading file functions of gdal.
	@rasterfn: 		original raster file path
	@array: 		return array of whole data
	'''
	raster = gdal.Open(rasterfn)
	band = raster.GetRasterBand(1)
	if(isAlldata):
		array = band.ReadAsArray()
	else:
		array = band.ReadAsArray(0, 0, 1, 1)
	return array

def fetch_bandInfo(band):
	'''
	Function: printout band information given a raster_band.
	@band: 		raster_band = ds.GetRasterBand(1)
	'''
	print("Band Type={}".format(gdal.GetDataTypeName(band.DataType)))

	min_value = band.GetMinimum()
	max_value = band.GetMaximum()
	if( not min_value or not max_value ):
	    (min_value,max_value) = band.ComputeRasterMinMax(True)
	print("Min={:.3f}, Max={:.3f}".format(min_value,max_value))
	print("Xsize={:d}, Ysize={:d}".format(band.XSize,band.YSize))

	if( band.GetOverviewCount() > 0 ):
	    print("Band has {} overviews".format(band.GetOverviewCount()))

	if( band.GetRasterColorTable() ):
	    print("Band has a color table with {} entries".format(band.GetRasterColorTable().GetCount()))

def get_SR_BandValues(ls_datainfo, row_start=0, row_end=0, col_start=0, col_end=0):
	'''
	Function: Construct SR_BandValues by for each data file in ls_datainfo.
	@ls_datainfo: 		list data information by walking all files
	@row_start: 		row start index of a data range
	@row_end:			row end index of a data range
	@col_start:			column start index of a data range
	@col_end:			column end index of a data range
	@SR_BandValues:		Save all extracted values and return
	'''

	## initial SR_BandValues to save results.
	SR_BandValues = np.zeros((row_end-row_start,col_end-col_start, len(ls_datainfo), 9))

	## initial date_index used to process data of a raster_file
	date_index = 0
	## for each data_info to get SR_BandValues
	for data_info in ls_datainfo:
		## extract key information
		raster_file = data_info[0]
		band_info = data_info[1]
		Julian_Day = data_info[2]

		## check if raster_file is existed and can open correctly
		if os.path.exists(raster_file):
			## open raster_file
			ds = gdal.Open(raster_file)
		
		if ds is None:
			print('Could not open {0}'.format(raster_file))
		else:
			## a) ---------- read band data ---------------
			raster_band = ds.GetRasterBand(1)
			## used for debug
			# fetch_bandInfo(raster_band)

			Band_Number = band_info[1]
			## get point values given region[row_start:row_end,col_start:col_end]
			for i in range(row_start, row_end):
				for j in range(col_start,col_end):
					## add Julian_Day to the last dimension of SR_BandValues
					SR_BandValues[i - row_start, j-col_start, date_index, 0] = Julian_Day

					## b) ----------- read a point value -------------		 
					raster_point = raster_band.ReadAsArray(j, i, 1, 1)

					## post-process data before saving into SR_BandValues
					if(raster_point):
						data_value = raster_point[0][0]
					else:
						## ????????how to handle empty or invid raster_point?
						data_value = 0

					## perform QA_Conversion
					if( (Band_Number == len(band_info[2])) and (data_value > 0) ):
						data_value = QA_Conversion(data_value)

					## skip operation if Band_Number is not valid.
					if(Band_Number>0):
						SR_BandValues[i - row_start, j-col_start, date_index, Band_Number] = data_value

		## increase date_index for next raster_file
		date_index+=1
	return SR_BandValues


def get_bandinfo(raster_file):
	'''
	Function: get band information given a raster file.
	@raster_file: 		raster file path
	@return:			[band_name, Band_Number, Band_list]
	'''
	file_name = raster_file.split('/')[-1]
	band_type = file_name.split('_')[0]
	band = file_name.split('_')[-1][:-4]

	if band_type == "LC08":
		bandList = ["band2","band3","band4","band5","band6","band7","band10","el_qa"]

	else:
		bandList = ["band1","band2","band3","band4","band5","band7","band6","el_qa"]

	## Band_Number is used to index item in bandList, 0 mean not supported band
	Band_Number = 0
	if( band in bandList):
		Band_Number = bandList.index(band) + 1

	return [band, Band_Number, bandList]

def get_datainfo(dataset_dir):
	'''
	Function: get data information by for each file within data directory.
	@dataset_dir: 		directory path that saves all files
	@datainfo:			return extracted data information as list [raster_file, band_info, Julian_Day]
	'''

	## get all data src path
	ls_datapath = walkDirs(data_dir)

	datainfo = []
	## for each dataset folder
	for datapath in ls_datapath:
		## get list files within datapath
		list_files = datapath[1]

		Julian_Day_Original = datapath[0].split('/')[-1]
		Julian_Day = date_Conversion('20130415')
		
		## process each raster_file to get data infomation
		for raster_file in list_files:
			band_info = get_bandinfo(raster_file)
			data_item = []
			## set data_item
			data_item.append(raster_file)
			data_item.append(band_info)
			data_item.append(Julian_Day)

			## append to datainfo
			datainfo.append(data_item)

	return datainfo

def test_readArray(loadAlldata = False):
	## ----------------- test readArray performance -------------------- 
	start_time=time.time()
	raster_file = "../VIIRS_ntl/201401/SVDNB_npp_20140101-20140131_00N060E_vcmslcfg_v10_c2015006171539.avg_rade9h.tif" 
	raster_array=raster2array(raster_file, loadAlldata)
	exec_time=time.time()-start_time
	print("raster_array shape: {}".format(raster_array.shape))
	print("Running time: {:.3f} s".format(exec_time))	

def test_getSRvalues(data_dir):
	## 1) for each file to get data information ['raster_file', [band, Band_Number, band_list], Julian_Day]
	ls_datainfo=get_datainfo(data_dir)
	# print(ls_datainfo[0])

	## set data range
	row_start=870
	row_end=872
	col_start=0
	col_end=5

	## 2) Get SR_BandValues by for each ls_datainfo
	start_time=time.time()
	SR_BandValues = get_SR_BandValues(ls_datainfo, row_start, row_end, col_start, col_end)
	print("SR_BandValues shape:{}".format(SR_BandValues.shape))
	# print(SR_BandValues.T[0][0].T)
	# print(SR_BandValues.T[0])
	exec_time=time.time()-start_time
	print("Running time: {:.3f} s".format(exec_time))


if __name__ == "__main__":

	# test_readArray(False)

	## data_dir = "/media/external/Deng/142041/LC081420412013041501T1-SC20191127190639"
	data_dir = "/media/external/viirs_all"
	## data_dir = "/media/external/Deng/142041"
	# data_dir = "../VIIRS_ntl"

	test_getSRvalues(data_dir)


	## 3) Calculate CCD points


	pass