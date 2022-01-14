'''
========================
TS_fit.py
========================
Created on Jan.13, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for TS model fit task.
@Reference:
'''

import math, os
import logging
import numpy as np
from Data_Preprocessing import Pre_Data
from fit_validation import FitValidation

logger = logging.getLogger(__name__)

'''
TF model fit class
'''
class TS_Fit(object):
	@staticmethod
	def norm_data(SR_BandValues, norm_type=0, isDebug=False):
		'''
		Function: prepare and normize data for model fit.
		@SR_BandValues:		Input raw SR band values from figures.
		@norm_type:			Normalization algorithm, 0:none; 1:year max.
		@isDebug:			Enable debug option to print log.
		@norm_SR_Values:	return normalized value vector
		'''
		## decompose SR_BandValues into SR_Datetime and SR_Values
		SR_Datetime = SR_BandValues.T[0]
		SR_Values = SR_BandValues.T[1].T

		if(isDebug):
			## show dimension of SR_BandValues
			logger.info("SR_BandValues shape:{}".format(SR_BandValues.shape))
			## show date vector
			logger.info("Date vector:{}".format(SR_Datetime))
			## show value vector
			logger.info("Values vector:{}".format(SR_Values))

		## initial norm_SR_Values (row, column, datetime) to save results.
		norm_SR_Values = np.zeros(SR_Values.shape)

		## save time serial
		ls_datatime=[]

		if(norm_type==1):
			## Annually normalization
			year_label = []
			year_id=0
			start_year_id = 0
			end_year_id = 0

			## for each datetime to calcuate year range
			for year_values in SR_Datetime:
				## append current datetime to ls_datatime
				ls_datatime.append(str(year_values[0][0])[:8])
				current_year = str(year_values[0][0])[:4]
				## Not found in year_label, current_year falls into another year range.
				if(current_year not in year_label):
					## 1) add current year label
					year_label.append(current_year)
					## 2) set the end id of previous year range
					if( year_id>0 ):
						## set end id of previous year range
						end_year_id = year_id-1
						## a) normalize values based on current year range
						if(isDebug):
							logger.info("{}-{}-{}".format(SR_Datetime[start_year_id][0][0], 
														SR_Datetime[end_year_id][0][0],
														end_year_id-start_year_id))
							logger.info(norm_SR_Values[:,:,start_year_id:end_year_id+1].shape)
						
						## for each cell to normize data given max year array.
						for i in range(norm_SR_Values.shape[0]):
							for j in range(norm_SR_Values.shape[1]):
								max_cell = SR_Values[i,j,start_year_id:end_year_id+1].max(0)
								norm_SR_Values[i,j,start_year_id:end_year_id+1]=SR_Values[i,j,start_year_id:end_year_id+1]/max_cell

					## set sthe tart id of a new year range
					start_year_id = year_id

				## increase year_id
				year_id+=1

			## set the end id of the last year range
			end_year_id = year_id-1

			## b) normalize values based on the last year range
			if(isDebug):
				logger.info("{}-{}-{}".format(SR_Datetime[start_year_id][0][0], 
											SR_Datetime[end_year_id][0][0],
											end_year_id-start_year_id))
				logger.info(norm_SR_Values[:,:,start_year_id:end_year_id+1].shape)
				
			## for each cell to normize data given max year array.
			for i in range(norm_SR_Values.shape[0]):
				for j in range(norm_SR_Values.shape[1]):
					max_cell = SR_Values[i,j,start_year_id:end_year_id+1].max(0)
					norm_SR_Values[i,j,start_year_id:end_year_id+1]=SR_Values[i,j,start_year_id:end_year_id+1]/max_cell

			if(isDebug):
				logger.info(year_label)
		else:
			## for each datetime to calcuate year range
			for year_values in SR_Datetime:
				## append current datetime to ls_datatime
				ls_datatime.append(str(year_values[0][0])[:8])

			## No normalization
			norm_SR_Values = SR_Values

		return norm_SR_Values, ls_datatime

	@staticmethod
	def fit_model(norm_SR_Values, ls_datetime, fit_param, isDebug=False):
		'''
		Function: Use normized SR values to fit a model.
		@norm_SR_Values:	Input normalized SR_value matrix.
		@ls_datetime:		Datetime list to rebuild time point of x axis.
		@fit_param:			parameter for fit model (json).
		@isDebug:			Enable debug option to print log.
		@fit_data:			return fix results
		'''
		## create time serial
		time_serial = np.array(ls_datetime)

		## for each cell to fit model based on TS
		row_start = fit_param['region_param'][0]
		col_start = fit_param['region_param'][1]

		for i in range(norm_SR_Values.shape[0]):
			for j in range(norm_SR_Values.shape[1]):
				## 1) prepare dataset for fit model
				pre_dataset = []
				for k in range(norm_SR_Values.shape[2]):
					# pre_dataset.append([time_serial[k], norm_SR_Values[i][j][k]])
					pre_dataset.append([k, norm_SR_Values[i][j][k], time_serial[k]])

				## 2) set fit_figure path
				fig_path = fit_param['output_dir'] + "plot_fit_{}_{}".format(row_start+i, col_start+j)

				## 3) call fit model function
				logger.info(FitValidation.ts_curvefit(pre_dataset, fit_param['fit_type'], 
														is_optimized=fit_param['is_optimized'],
														showfig=fit_param['showfig'],
														savefig=fit_param['savefig'], 
														fig_file=fig_path))



		