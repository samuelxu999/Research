'''
========================
RF_Nepal.py
========================
Created on Nov.14, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for create geo training data table and apply RF training and predicate
@Reference: For RF: https://towardsdatascience.com/random-forest-in-python-24d0893d51c0
'''

from utilities import *
import georasters as gr
import numpy as np
from datetime import datetime,timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

def read_data_xls(file_xls):
	'''
	read sample data from excel
	'''
	G = FileUtil.xlsread(file_xls)
	
	col_0=[]
	col_1=[]
	col_2=[]
	for row in G:
		col_0.append(row[0])
		col_1.append(row[1])
		col_2.append(row[2])

	return [col_0, col_1, col_2]

def map2pix(file_tiff, X, Y):
	'''
	Conver map cooridinate to pixel cooridinate
	'''

	# Load data from tiff image
	raster = file_tiff 

	# get geo information
	NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(raster)


	# load geo data
	data = gr.from_file(raster)

	# Find location of point (x,y) on raster, e.g. to extract info at that location
	#(xmin, xsize, x, ymax, y, ysize) = data.geot
	#Convert UTM coordinates to pixel coordinate (row&col)
	row, col = gr.map_pixel(X,Y,GeoT[1],GeoT[-1], GeoT[0],GeoT[3])
	
	return [row, col]

def rm_negative_value(G_data, pix_data):
	G_x = []
	G_y = []
	G_z = []
	pix_row = []
	pix_col = []
	i = 0
	for i in range(len(G_data[0])):
		if( pix_data[0][i]>0 and pix_data[1][i]>0 ):
			G_x.append(G_data[0][i])
			G_y.append(G_data[1][i])
			G_z.append(G_data[2][i])
			pix_row.append(pix_data[0][i])
			pix_col.append(pix_data[1][i])

	return np.array([np.array(G_x), np.array(G_y), np.array(G_z)]), np.array([np.array(pix_row), np.array(pix_col)])

def datevect(np_array):
	ls_year = []
	ls_month = []
	ls_day = []

	for time_stamp in np_array:
		matlab_datenum = int(time_stamp)
		python_datetime = datetime.fromordinal(matlab_datenum) + timedelta(days=matlab_datenum%1) - timedelta(days = 366)
		ls_year.append(python_datetime.year)
		ls_month.append(python_datetime.month)
		ls_day.append(python_datetime.day)

	return np.array(ls_year), np.array(ls_month), np.array(ls_day)

'''
Train data class
'''
class RF_Nepal(object):
	@staticmethod
	def create_training_table(data_config={}):

		if(data_config=={}):
			print("data_config is empty!")
			return

		# --------------------- read Geo sample data from excel --------------------------------------
		file_xls = data_config['dataset'] + data_config['file_xls'] 
		Geo_values = read_data_xls(file_xls)
		#print(len(Geo_values))
		#print(len(Geo_values[0]))
		#print(Geo_values[0])

		# get pixel coordinate as [row, col]
		file_tiff = data_config['dataset'] + data_config['file_tif'] 
		pixel_values = map2pix(file_tiff, Geo_values[0], Geo_values[1])

		# print(pixel_values[0])
		# print(pixel_values[1])

		# refine by removing negative from list
		Geo_new, pixel_new = rm_negative_value(Geo_values, pixel_values)

		# print(Geo_new.shape)
		#print(Geo_new[0])

		#print(pixel_new.shape)
		#print(pixel_new[0])
		#print(pixel_new[1])	

		# --------------- for each vlaue in Geo_new to get coefficents data from TS_Coefficients -----------
		N_geo = Geo_new.shape[1]
		# N_geo = 9
		#print(N_geo)
		A = np.zeros( (N_geo, 68), dtype=np.float)
		#print(A.shape)

		i=0
		for i in range(0, N_geo):

			PixelRow = pixel_new[0][i];
			PixelCol = pixel_new[1][i];

			if(PixelRow==0):
				print(i, PixelRow , PixelCol)
				break
			#print(PixelRow , PixelCol)

			# read sample data from excel
			tmp_file = "row_"+ str(PixelRow) + ".csv"
			file_csv = data_config['dataset'] + data_config['coefset'] + tmp_file 
			csv_data = FileUtil.csv_read(file_csv)
			#print(csv_data.shape)

			#k = find(R(:,67)==PixelRow & R(:,68)==PixelCol);
			k = np.where( (csv_data[:,66] == str(PixelRow)) & (csv_data[:,67] == str(PixelCol)) )
			#print(k[0])
			# print(csv_data[k[0]])

			#[Yr, M, D, H, MN, z] = datevec(R(k,2));
			Year, Month, Day = datevect(csv_data[k[0],1])
			#print(Year, Month, Day)

			a = np.where( Year > 2016 ) 
			#print(a[0].size)
			# if cannot find (isempty is true), all are earlier than 2018, then use the last one directly
			if(a[0].size==0):
				A[i,:] = csv_data[ k[-1],0:68]
			# use last one of a
			else:
				#print(a[0][-1])
				#print(k[0][a[0][-1]])
				A[i,:] = csv_data[ k[0][a[0][-1]], 0:68 ]

		# print(A[0,:])

		# ------------- Prepare data: remove rows with all zeros: r[~np.all(r == 0, axis=1)] -----------
		y = ~np.all(A == 0, axis=1)
		A = A[y,:]
		# print(A.shape)

		#--------------------- construct train table matrix  ----------------------------
		# print(np.transpose(A)[66:68,:])
		# print(np.reshape(Geo_new[2,:], (1,N_geo)))
		# print(np.transpose(A)[0:66,:])
		# Row, Col, Imp%, Coefficients from B,G,R,NIR, SWIR1,2, BT,RMSE 
		List_array =[ np.transpose(A)[66:68,:], np.reshape(Geo_new[2,0:N_geo], (1,N_geo)), np.transpose(A)[0:66,:] ]; 
		train_data = np.concatenate( List_array, axis=0 )
		print(train_data.shape)

		#--------------------- write train table matrix to csv file ----------------------------	
		# ls_traindata = train_data.tolist()
		train_file = data_config['dataset'] + data_config['file_traindata'] 
		np.savetxt(train_file, np.transpose(train_data), fmt='%s', delimiter=",")
		# FileUtil.csv_write(train_file,ls_traindata)

	@staticmethod
	def RF_predict(data_config={}):

		if(data_config=={}):
			print("data_config is empty!")
			return

		# ------------------ read training table data ----------------------------
		file_traindata = data_config['dataset'] + data_config['file_traindata']
		traindata = FileUtil.csv_read(file_traindata)
		# print(traindata.shape)
		# print(traindata[0,:])

		nTrees = 100;
		features = traindata[:, 14:54]
		# print(features.shape)
		# print(features[:,0])
		classLabels = traindata[:, 2]
		# print(classLabels.shape)

		#------------------------ Train random forest model------------------------
		# read ref1 data from tif image
		file_tiff = data_config['dataset'] + data_config['file_tif'] 
		ref1_data = gr.from_file(file_tiff)
		# get dimension of ref1_data
		D_ref1 = ref1_data.shape
		# print(D_ref1)

		# --------------------------- Train model ------------------------------------------------
		# Instantiate model with 1000 decision trees
		rf = RandomForestRegressor(n_estimators = nTrees, random_state = 42)

		# Train the model on training data
		rf.fit(features, classLabels);

		# ------------------------ Apply RF model to all pixels in all years -----------------------
		year_range = data_config['year_range'][0] - data_config['year_range'][1] + 1
		pixel_range = data_config['pixel_range'][1] - data_config['pixel_range'][0] 

		predict_results = np.zeros( (pixel_range, D_ref1[1], year_range), dtype=np.float)
		print(predict_results.shape)

		for pixel_id in range(data_config['pixel_range'][0], data_config['pixel_range'][1]):
			print("------------- pixel_id:", pixel_id+1, "-----------------------")

			# read sample data from excel
			tmp_file = "row_"+ str(pixel_id+1) + ".csv"
			file_csv = data_config['dataset'] + data_config['coefset'] + tmp_file 
			csv_data = FileUtil.csv_read(file_csv)
			# print(csv_data.shape)
			# print(csv_data[:,67])
			j_range = D_ref1[1]
			# j_range = 10
			for j in range(0, j_range):
				T = np.where( csv_data[:,67] == str(j) )[0]
				# chech if T is empty
				if(len(T)!=0):
					# --------------------- Make Predictions on the Test Set --------------
					if( csv_data[T[0],0]== '0' and csv_data[T[0],1]== '737334' ):
						# print("condition 1")
						test_features = csv_data[T[0],11:51].reshape((1,40))
						predictions = rf.predict(test_features)
						predict_results[pixel_id-data_config['pixel_range'][0],j,:]= predictions
					else:
						# print("condition 2")
						# start year in the csv
						A = datevect(csv_data[T,0])[0]
						# end year in the csv
						B = datevect(csv_data[T,1])[0]
						# print(A)
						# print(B)
						for k in range(0, len(T)):
							test_features = csv_data[T[k],11:51].reshape((1,40))
							predictions = rf.predict(test_features)
							# print( predictions )
							low_year = A[k]- data_config['year_range'][1]
							up_year = B[k] - data_config['year_range'][1] + 1
							# print(low_year)
							# print(up_year)
							predict_results[pixel_id-data_config['pixel_range'][0],j,low_year:up_year] = predictions 
					# print(predict_results[pixel_id,j,:])

		# save predict_results matrix to local file
		predict_file = data_config['dataset'] + data_config['predictset'] + \
						data_config['predict_matrix'] + '_' + \
						str(data_config['pixel_range'][0]) + '_' + \
						str(data_config['pixel_range'][1]) + '.npy' 
		np.save(predict_file, predict_results)

	@staticmethod
	def Merge_predict(data_config={}):
		if(data_config=={}):
			print("data_config is empty!")
			return

		# Get data file list
		ls_files = FileUtil.list_files(data_config['dataset'] + data_config['predictset'], '*.npy')


		# for each npy files to calculate all ranges
		list_range = []
		for test_file in ls_files:

			# get range from predict_file name
			tmp_range = test_file.split('.')[0].split('_')[2:4]

			list_range.append( (tmp_range[0], tmp_range[1]) )

		list_range.sort()

		list_np_predict=[]
		# For each npy files to merge matrix
		for pixel_range in list_range:
			# print(pixel_range)
		
			# Load predict_results matrix to local file
			predict_file = data_config['dataset'] + data_config['predictset'] + \
							data_config['predict_matrix'] + '_' + \
							pixel_range[0] + '_' + \
							pixel_range[1] + '.npy' 
			predict_file = data_config['dataset'] + data_config['predictset'] + test_file
			predict_results = np.load(predict_file)
			# print(predict_results.shape)

			list_np_predict.append(predict_results)
		merged_results = np.concatenate( list_np_predict, axis=0 )
		print(merged_results.shape)

		# save predict_results matrix to local file
		merged_file = data_config['dataset'] + 'merged_predict.npy'
		np.save(merged_file, merged_results)

	@staticmethod
	def Load_predict(data_config={}):
		if(data_config=={}):
			print("data_config is empty!")
			return
		# load predict_results matrix from local file
		merged_file = data_config['dataset'] + data_config['predict_merge']
		merged_results=np.load(merged_file)

		return merged_results


	

# if __name__ == "__main__":
# 	# --------------------- configuration for work path and folder ---------------------------
# 	data_config= {}
# 	data_config['dataset'] = "../training_set/"
# 	data_config['file_tif'] = "141041_Kathmandu_Charikot_subset.tif"
# 	data_config['file_xls'] = "Samples_Charikot_1012.xlsx"
# 	data_config['file_traindata'] = "trainset.dat"
# 	data_config['coefset'] = "TS_Coefficients/"
# 	TrainNepal.create_training_table(data_config)
# 	pass