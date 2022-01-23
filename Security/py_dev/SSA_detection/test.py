'''
========================
test.py
========================
Created on Dec.17, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This is used to unit function test and demo.
@Reference: 
'''

import sys
import time
import random
import logging
import argparse
from utils.utilities import FileUtil, TypesUtil, PlotUtil
from ssa import SingularSpectrumAnalysis

## use tkagg to remotely display plot
# import matplotlib
# matplotlib.use('tkagg')

logger = logging.getLogger(__name__)


def show_data(args):
	data_file = "./data/rho.pkl"

	rho = FileUtil.pkl_read(data_file)

	dataset = []
	ls_data = TypesUtil.np2list(rho)
	dataset.append(ls_data)

	fig_file = "Data_figure"
	PlotUtil.Plotline(dataset, is_show=args.show_fig, is_savefig=args.save_fig, datafile=fig_file)

def load_data():
	data_file = "./data/rho.pkl"

	ts_data = FileUtil.pkl_read(data_file)

	return ts_data
	 

def ssa_test(args):
	## load time series data
	ts_vector = load_data()
	print(ts_vector.shape)

	## initialize SSA object
	my_ssa = SingularSpectrumAnalysis(40, n_eofs=5)

	## inject noisy data
	ts_vector[50:51]=0.1
	ts_vector[150:155]=0.3
	ts_vector[450:451]=0.15	

	## inject fakedata
	ts_vector[300:315]=0.1
	
	## apply SSA to get score (D)
	score = my_ssa.score_ssa(ts_vector)

	## get normalized sum of squired distances.
	S = my_ssa.Sn_ssa(score)

	## calculate CUSUM statistics W
	W,h = my_ssa.Wn_CUSUM(S)

	## plot ts data and scores
	PlotUtil.plot_data_and_score(ts_vector,W,h)

def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Run test.")

	parser.add_argument("--test_func", type=int, default=0, 
						help="Execute test function: 0-show_data(), \
													1-ssa_test()")

	parser.add_argument("--show_fig", action="store_true", help="Show plot figure model.")

	parser.add_argument("--show_info", action="store_true", help="Print test information on screen.")

	parser.add_argument("--save_fig", action="store_true", help="Save plot figure on local disk.")

	parser.add_argument("--save_log", action="store_true", help="Save test logs on local disk.")

	args = parser.parse_args(args=args)
	return args

if __name__ == '__main__':
	FORMAT = "%(asctime)s %(levelname)s | %(message)s"
	LOG_LEVEL = logging.INFO
	logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

	# ssa_logger = logging.getLogger("ssa")
	# ssa_logger.setLevel(logging.DEBUG)

	args = define_and_get_arguments()

	if(args.test_func==1):
		ssa_test(args)
	elif(args.test_func==2):
		pass
	else:
		show_data(args)
