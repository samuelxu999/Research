#This is used to unit function test.

import sys
import random
import logging
import argparse
from utilities import FileUtil, TypesUtil, PlotUtil
from ENF_consensus import ENFUtil

logger = logging.getLogger(__name__)

def load_ENF(args):
	ENF_file = "./data/one_day_enf.csv"
	ENF_data = FileUtil.csv_read(ENF_file)
	print("ENF dataset shape:  {}".format(ENF_data.shape))
	print("ENF data[:10]:      {}".format(ENF_data[:10,1]))

	ls_data = [['60.003862785368945', '60.00222228853508', '60.00211681010308',
				 '60.00367708457075', '60.00223181828196', '59.999928650064575',
				'60.000678388958924', '60.002585777224475', '60.004295511612064',
				'60.004408258363405']]
	print("ls_data type: {}".format(type(ls_data)))

	## test TypesUtil functions
	np_data=TypesUtil.list2np(ls_data)
	print("ls_data --> np_data, shape: {}     type: {}".format( np_data.shape, type(np_data) ))
	print( "np_data --> list, type: {}".format( type(TypesUtil.np2list(np_data)) ))

	## ------------------ display 10 minutes ENF signals -----------------------------------
	head_pos = args.sample_head
	sample_length = args.sample_length
	ENF_dataset = []
	## get sample data for node 0
	ls_ENF1 = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length)])
	ENF_dataset.append(ls_ENF1)

	head_pos = args.sample_head + sample_length
	## get sample data for node 1
	ls_ENF2 = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length)])
	ENF_dataset.append(ls_ENF2)

	fig_file = "ENF_figure"
	PlotUtil.Plotline(ENF_dataset, is_show=args.show_fig, is_savefig=args.save_fig, datafile=fig_file)

def ENF_Process(args):
	ENF_file = "./data/one_day_enf.csv"
	sample_length = args.sample_length
	ENF_data = FileUtil.csv_read(ENF_file)
	ENF_dataset = []

	## ******************** function module test ***********************
	head_pos = args.sample_head
	ls_ENF1 = TypesUtil.np2list(ENF_data[head_pos:sample_length, 1])
	ENF_dataset.append(ls_ENF1)

	head_pos = args.sample_head + sample_length
	ls_ENF2 = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length), 1])
	ENF_dataset.append(ls_ENF2)

	sqr_dist = ENFUtil.sqr_distance(ENF_dataset, scale=100)
	print("Squire distance is: {}".format(sqr_dist))

	## ************** choose ENF samples from dataset ****************
	sample_node = args.sample_node
	ENF_samples = []
	head_pos = 0
	for ENF_id in range(sample_node):
		##-----------  random choose sample for node ------------------
		# head_pos = random.randint(0,7200) 
		ls_ENF = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length), 1])
		ENF_samples.append( [ENF_id, ls_ENF] )
		##----------- choose continuous sample for node ------------------
		head_pos = head_pos + sample_length

	# ## calculate sqr_dist that is between node0 and other ones
	# ## define benchmark node
	# benchmark_node = 1
	# sorted_ENF_sqr_dist=ENFUtil.sort_ENF_sqr_dist(ENF_samples, benchmark_node)
	# print(sorted_ENF_sqr_dist)

	# ENF_score = ENFUtil.ENF_score(sorted_ENF_sqr_dist)
	# print(ENF_score)

	## ******************* calculate ENF score for each node *****************
	ls_ENF_score = []
	for ENF_id in range(sample_node):
		sorted_ENF_sqr_dist=ENFUtil.sort_ENF_sqr_dist(ENF_samples, ENF_id)
		ENF_score = ENFUtil.ENF_score(sorted_ENF_sqr_dist)
		ls_ENF_score.append([ENF_id, ENF_score])

	# print("ENF score is: {}".format(ls_ENF_score))
	print("Sorted ENF score is: {}".format(sorted(ls_ENF_score, key=lambda x:x[1])))
	

def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Run test.")

	parser.add_argument("--test_func", type=int, default=0, 
						help="Execute test function: 0-function test, \
													1-ENF_Process()")

	parser.add_argument("--sample_node", type=int, default=10, help="Sample node size n for test.")

	parser.add_argument("--sample_head", type=int, default=0, help="Start point of ENF sample data for node.")

	parser.add_argument("--sample_length", type=int, default=600, help="Length of ENF sample data for node.")

	parser.add_argument("--random_sample", action="store_true", help="Random choose samples for ENF dataset.")

	parser.add_argument("--show_fig", action="store_true", help="Show plot figure model.")

	parser.add_argument("--save_fig", action="store_true", help="Save plot figure on local disk.")

	args = parser.parse_args(args=args)
	return args

if __name__ == '__main__':

	args = define_and_get_arguments()

	if(args.test_func==1):
		ENF_Process(args)
	else:
		load_ENF(args)