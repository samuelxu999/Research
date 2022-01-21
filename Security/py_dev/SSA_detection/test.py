#This is used to unit function test.

import sys
import time
import random
import logging
import argparse
from utils.utilities import FileUtil, TypesUtil, PlotUtil
from ssa import SingularSpectrumAnalysis


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
	ts_vector = load_data()

	print(ts_vector.shape)

	my_ssa = SingularSpectrumAnalysis(30, n_eofs=5)
	# X = SingularSpectrumAnalysis.create_hankel(ts_vector, 60, 30, 0)
	# print(X.shape)

	# sigma = SingularSpectrumAnalysis.sigma_svd(X, 5)
	# print(sigma)

	# x_reconstruct = SingularSpectrumAnalysis.reconstruct(X, 5)
	# print(x_reconstruct.shape)

	## inject noise
	ts_vector[50:51]=0.1
	ts_vector[150:151]=0.3
	ts_vector[250:251]=0.2

	## inject fakedata
	ts_vector[400:435]=0.25

	score = my_ssa.score_ssa(ts_vector)
	# print(score)

	PlotUtil.plot_data_and_score(ts_vector,score)

def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Run test.")

	parser.add_argument("--test_func", type=int, default=0, 
						help="Execute test function: 0-function test, \
													1-analyze_data()")

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
