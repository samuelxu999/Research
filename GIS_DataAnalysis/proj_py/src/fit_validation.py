'''
========================
utilities.py
========================
Created on Oct.11, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module used for fit valudation operation.
@Reference: 
'''

import logging
from utilities import *
from curve_fit import *
import numpy as np
import math

logger = logging.getLogger(__name__)

'''
FileUtil class for handling curve fit operation
'''

MAX_OUTLIER = 4

def valid_perr(pcov):
	'''
	Function: validate if pcov is valid by checking nan in perr
	@arguments: 
	(in) pcov:   		covariance or coefficients matrix
	(out) is_valid:     True or False
	'''
	if(pcov.ndim>1):
		perr = np.sqrt(np.diag(pcov))
		#print(perr)
		perr_isNan = np.isnan(perr)
	else:
		perr_isNan = np.isnan(pcov)
	return not (True in perr_isNan)

def fit_data(fit_type, x_vect, y_vect):
	if(fit_type =='sigmoid'):
		popt, pcov, x, y, fit_ydata = CurveFit.sigm_fit(x_vect, y_vect)
	elif(fit_type =='gussain'):
		popt, pcov, x, y, fit_ydata = CurveFit.gauss_fit(x_vect, y_vect)
	elif(fit_type =='polynom'):
		pcov, x, y, fit_ydata = CurveFit.poly_fit(x_vect, y_vect, poly_n=2)
	else:
		pcov = [nan]
	return pcov, x, y, fit_ydata 


class FitValidation(object):
	@staticmethod
	def valid_curvefit(pre_dataset, fit_type, fig_file='fit_result', 
						is_optimized=True, showfig=False, savefig=False):
		'''
		Function: sigmond fit
		@arguments: 
		(in) pre_dataset:   procossed data for curve_fit
			 fit_type:   	supported fit functions [sigmoid, gussain, polynom]
			 fig_file:		fileaname for saving fit curver figure
			 is_optimized:	optimized curve by removing outlier 
			 showfig:		show fig during test (single test)
			 savefig:		save fig during test (group test)
		(out) RMSE_Fit:     RMSE based on fit data, lower value means better fitting
		'''
		x_vect = []
		y_vect= []
		for row_data in pre_dataset:
			x_vect.append(row_data[0])
			y_vect.append(row_data[1])
		#print(x_vect)
		#print(y_vect)

		#xdata = np.array(x_vect)
		#ydata = np.array(y_vect)
		RMSE_Fit = 1.0
		try:
			pcov, x, y, fit_ydata = fit_data(fit_type, x_vect, y_vect)
			#print(popt)
			#print(pcov)
			if(valid_perr(pcov)):
				#Calculate RMSE 
				RMSE_Fit=np.sqrt(np.mean((y_vect-fit_ydata)**2))

				# plot fit curve if applicable
				fig_title = fit_type +'_fit'
				if(is_optimized):
					# optimize rmse by removing outlier who is great than 2*RMSE
					xdata_opt = []
					ydata_opt = []
					for i in range(0,len(y_vect)):
					    # remove outlier
					    if(np.sqrt((y_vect[i]-fit_ydata[i])**2) < (RMSE_Fit*1.5)):
					        ydata_opt.append(y_vect[i]);
					        xdata_opt.append(x_vect[i]);

					# Check of removed outlier points excel MAX_OUTLIER
					if((len(x_vect)-len(xdata_opt))<MAX_OUTLIER):
						#Refit to calculate new estimated_params
						pcov_new, x_new, y_new, fit_ydata_new = fit_data(fit_type, xdata_opt, ydata_opt)
						
						#recalculate rmse
						RMSE_Fit=np.sqrt(np.mean((ydata_opt-fit_ydata_new)**2))
					else:
						RMSE_Fit = 1.0
					
					# Bad fitting condition, do not plot curve
					if(RMSE_Fit<1.0):
						PlotUtil.Plotfit_Opt(x_vect, y_vect, xdata_opt, ydata_opt, x, y, 'Year', 'Percentage (%)', 
										plt_title=fig_title, is_show=showfig, is_savefig=savefig, datafile=fig_file)
					else:
						logger.info('{}-Bad fitting condition, do not plot curve.'.format(fit_type))
						PlotUtil.PlotData(pre_dataset, 'Year', 'Percentage (%)', 
									is_show=showfig, is_savefig=savefig, datafile=fig_file)
				else:
					PlotUtil.Plotfit(x_vect, y_vect, x, y, 'Year', 'Percentage (%)', 
										plt_title=fig_title, is_show=showfig, is_savefig=savefig, datafile=fig_file)

			else:
				## valid_perr failed, show information
				logger.info('{}-valid_perr failed, only show data'.format(fit_type))
				PlotUtil.PlotData(pre_dataset, 'Year', 'Percentage (%)', 
									is_show=showfig, is_savefig=savefig, datafile=fig_file)
		except Exception as e:
			## fit failed with error, show information
			logger.info('{}-fit failed with error, only show data'.format(fit_type))
			PlotUtil.PlotData(pre_dataset, 'Year', 'Percentage (%)', 
								is_show=showfig, is_savefig=savefig, datafile=fig_file)
		finally:
			return RMSE_Fit

	@staticmethod
	def ts_curvefit(pre_dataset, fit_type, fig_file='fit_result', 
						is_optimized=True, showfig=False, savefig=False):
		'''
		Function: ts model fit
		@arguments: 
		(in) pre_dataset:   procossed data for curve_fit
			 fit_type:   	supported fit functions [sigmoid, gussain, polynom]
			 fig_file:		fileaname for saving fit curver figure
			 is_optimized:	optimized curve by removing outlier 
			 showfig:		show fig during test (single test)
			 savefig:		save fig during test (group test)
		(out) RMSE_Fit:     RMSE based on fit data, lower value means better fitting
		'''
		x_vect = []
		y_vect= []
		plot_dataset = []
		for row_data in pre_dataset:
			x_vect.append(row_data[0])
			y_vect.append(row_data[1])
			plot_dataset.append([row_data[2],row_data[1]])
		
		RMSE_Fit = 1.0
		try:
			pcov, x, y, fit_ydata = fit_data(fit_type, x_vect, y_vect)
			#print(popt)
			#print(pcov)
			if(valid_perr(pcov)):
				#Calculate RMSE 
				RMSE_Fit=np.sqrt(np.mean((y_vect-fit_ydata)**2))

				# plot fit curve if applicable
				fig_title = fit_type +'_fit'
				if(is_optimized):
					# optimize rmse by removing outlier who is great than 2*RMSE
					xdata_opt = []
					ydata_opt = []
					for i in range(0,len(y_vect)):
					    # remove outlier
					    if(np.sqrt((y_vect[i]-fit_ydata[i])**2) < (RMSE_Fit*1.5)):
					        ydata_opt.append(y_vect[i]);
					        xdata_opt.append(x_vect[i]);

					# Check of removed outlier points excel MAX_OUTLIER
					if((len(x_vect)-len(xdata_opt))<MAX_OUTLIER):
						#Refit to calculate new estimated_params
						pcov_new, x_new, y_new, fit_ydata_new = fit_data(fit_type, xdata_opt, ydata_opt)
						
						#recalculate rmse
						RMSE_Fit=np.sqrt(np.mean((ydata_opt-fit_ydata_new)**2))
					else:
						RMSE_Fit = 1.0
					
					# Bad fitting condition, do not plot curve
					if(RMSE_Fit<1.0):
						PlotUtil.Plotfit_Opt(x_vect, y_vect, xdata_opt, ydata_opt, x, y, 'Year', 'Percentage (%)', 
										plt_title=fig_title, is_show=showfig, is_savefig=savefig, datafile=fig_file)
					else:
						logger.info('{}-Bad fitting condition, do not plot curve.'.format(fit_type))
						PlotUtil.PlotData(pre_dataset, 'Year', 'Percentage (%)', 
									is_show=showfig, is_savefig=savefig, datafile=fig_file)
				else:
					PlotUtil.Plotfit(x_vect, y_vect, x, y, 'Year', 'Percentage (%)', 
										plt_title=fig_title, is_show=showfig, is_savefig=savefig, datafile=fig_file)

			else:
				## valid_perr failed, show information
				logger.info('{}-valid_perr failed, only show data'.format(fit_type))
				PlotUtil.PlotData(pre_dataset, 'Year', 'Percentage (%)', 
									is_show=showfig, is_savefig=savefig, datafile=fig_file)
		except Exception as e:
			## fit failed with error, show information
			logger.info('{}-fit failed with error, only show data'.format(fit_type))
			PlotUtil.PlotData(pre_dataset, 'Year', 'Percentage (%)', 
								is_show=showfig, is_savefig=savefig, datafile=fig_file)
		finally:
			return RMSE_Fit


