'''
========================
utilities.py
========================
Created on Oct.10, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide curve fit function to support project.
@Reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
'''

from scipy.optimize import curve_fit
from scipy import asarray as exp
import numpy as np
import numpy.polynomial.polynomial as poly

CURVE_STEP = 100

#The sigmoid function
def sigmoid(x, x0, k):
	y = 1 / (1 + np.exp(-k*(x-x0)))
	return y

#The scaled sigmoid function
def sigmoidscaled(x, x0, k, lapse, guess):
    F = (1 + np.exp(-k*(x-x0))) 
    z = guess + (1-guess-lapse)/F
    return z

#The gaussan function
def gaussian(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))

'''
FileUtil class for handling curve fit operation
'''
class CurveFit(object):
	@staticmethod
	def sigm_fit(x_vect, y_vect):
		'''
		Function: sigmond fit
		@arguments: 
		(in) [x_vect, y_vect]:   data for curve_fit
		(out) popt:   Optimal values for the parameters so that the sum of the squared error of f(xdata, *popt)
			  pcov:   The estimated covariance of popt. perr = np.sqrt(np.diag(pcov)).
			  [x, y, fit_y]: x, y used for plot curve, and fit_y used for calculate RMSE_Fit
		'''
		#generate x and y data
		xdata = np.array(x_vect)

		# normalized xdata
		xdata = xdata - x_vect[0]
		ydata = np.array(y_vect)
		popt, pcov = curve_fit(sigmoidscaled, xdata, ydata)
		
		x = np.linspace(-0.5, len(xdata), CURVE_STEP)
		y = sigmoidscaled(x, *popt)
		fit_y = sigmoidscaled(xdata, *popt)

		# return unnormalized x vector (x+x_vect[0])
		return popt, pcov, x+x_vect[0], y, fit_y

	@staticmethod
	def gauss_fit(x_vect, y_vect):
		'''
		Function: gaussian fit
		@arguments: 
		(in) [x_vect, y_vect]:   data for curve_fit
		(out) popt:   Optimal values for the parameters so that the sum of the squared error of f(xdata, *popt)
			  pcov:   The estimated covariance of popt. perr = np.sqrt(np.diag(pcov)).
			  [x, y, fit_y]: x, y used for plot curve, and fit_y used for calculate RMSE_Fit
		'''
		#generate x and y data
		xdata = np.array(x_vect)
		# normalized xdata
		xdata = xdata - x_vect[0]
		ydata = np.array(y_vect)

		n = len(x_vect)
		mean = sum(xdata*ydata)/n 
		sigma = sum(ydata*(xdata-mean)**2)/n 

		#print(mean) 
		#print(sigma) 

		popt,pcov = curve_fit(gaussian,xdata,ydata, p0=[1,mean,sigma])
		
		x = np.linspace(-0.5, len(xdata), CURVE_STEP)
		y = gaussian(x, *popt)
		fit_y = gaussian(xdata, *popt)

		# return unnormalized x vector (x+x_vect[0])
		return popt, pcov, x+x_vect[0], y, fit_y

	@staticmethod
	def poly_fit(x_vect, y_vect, poly_n=2):
		'''
		Function: ploynom fit
		@arguments: 
		(in) [x_vect, y_vect]:   data for curve_fit
		(out) poly_coefs: Polynomial coefficients, highest power first. .
			  [x, y, fit_y]: x, y used for plot curve, and fit_y used for calculate RMSE_Fit
		'''

		#generate x and y data
		xdata = np.array(x_vect)
		# normalized xdata
		xdata = xdata - x_vect[0]
		ydata = np.array(y_vect)

		poly_coefs = poly.polyfit(xdata, ydata, poly_n)

		x = np.linspace(-0.5, len(xdata), CURVE_STEP)
		y = poly.polyval(x, poly_coefs)
		fit_y = poly.polyval(xdata, poly_coefs)

		# return unnormalized x vector (x+x_vect[0])
		return poly_coefs, x+x_vect[0], y, fit_y
	

