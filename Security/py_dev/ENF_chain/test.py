#This is used to unit function test.

import sys
import time
import random
import logging
import argparse
from utils.utilities import FileUtil, TypesUtil, PlotUtil
from consensus.ENF_consensus import ENFUtil
from utils.Swarm_RPC import Swarm_RPC

logger = logging.getLogger(__name__)

# tx commit timeout.
TX_TIMEOUT = 10
TX_INTERVAL = 0.1

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
	ls_ENF1 = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length), 1])
	ENF_dataset.append(ls_ENF1)

	head_pos = args.sample_head + sample_length
	ls_ENF2 = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length), 1])
	ENF_dataset.append(ls_ENF2)

	sqr_dist = ENFUtil.sqr_distance(ENF_dataset, scale=100)
	print("Squire distance is: {}".format(sqr_dist))

	## ************** choose ENF samples from dataset ****************
	sample_node = args.sample_node
	ENF_samples = []
	head_pos = args.sample_head
	for ENF_id in range(sample_node):
		if(args.random_sample):
			##-----------  random choose sample for node ------------------
			head_pos = random.randint(0,7200) 
		else:
			##----------- choose continuous sample for node ------------------
			head_pos = head_pos + sample_length
		ls_ENF = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length), 1])
		ENF_samples.append( [ENF_id, ls_ENF] )

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

def swarm_test(args):
	ENF_file = "./data/one_day_enf.csv"
	head_pos = args.sample_head
	sample_length = args.sample_length
	ENF_data = FileUtil.csv_read(ENF_file)
	ls_ENF = TypesUtil.np2list(ENF_data[head_pos:(head_pos+sample_length), 1])

	## ******************** upload ENF samples **********************
	## build json ENF data for transaction
	tx_json = {}

	json_ENF={}
	json_ENF['id']='1ad48ca78653f3f4b16b0622432db7d995613c42'
	json_ENF['enf']=ls_ENF
	tx_data = TypesUtil.json_to_string(json_ENF)  

	## save ENF data in transaction
	tx_json['data']=tx_data
	# print(tx_json)

	start_time=time.time()
	## random choose a swarm server
	record_address = Swarm_RPC.get_service_address()
	post_ret = Swarm_RPC.upload_data(record_address, tx_json)
	exec_time=time.time()-start_time
	print("Record ENF samples on swarm server: {}, time: {:.3f}     at: {}".format(record_address, exec_time, post_ret['data']))

	## ******************** download ENF samples **********************
	start_time=time.time()
	tx_time = 0.0
	while(True):
		## random choose a swarm server
		query_address = Swarm_RPC.get_service_address()
		## use different swarm server address to evaluate data synchronous time.
		if(query_address==record_address):
			continue
		swarm_hash = post_ret['data']
		query_ret = Swarm_RPC.download_data(query_address,swarm_hash)
		if(query_ret!=""):
			break
		time.sleep(TX_INTERVAL)
		tx_time +=TX_INTERVAL
		if(tx_time>=TX_TIMEOUT):
			break
	exec_time=time.time()-start_time
	if(query_ret==""):
		print("Timeout, download ENF samples fail.") 
	else:
		print("Fetch ENF samples from swarm server: {}, time: {:.3f}    at: {}\n{}".format(query_address, exec_time, swarm_hash, query_ret['data']))
	

def define_and_get_arguments(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Run test.")

	parser.add_argument("--test_func", type=int, default=0, 
						help="Execute test function: 0-function test, \
													1-ENF_Process(), \
													2-swarm_test()")

	parser.add_argument("--sample_node", type=int, default=10, help="Sample node size n for test.")

	parser.add_argument("--sample_head", type=int, default=0, help="Start point of ENF sample data for node.")

	parser.add_argument("--sample_length", type=int, default=60, help="Length of ENF sample data for node.")

	parser.add_argument("--random_sample", action="store_true", help="Random choose samples for ENF dataset.")

	parser.add_argument("--show_fig", action="store_true", help="Show plot figure model.")

	parser.add_argument("--save_fig", action="store_true", help="Save plot figure on local disk.")

	args = parser.parse_args(args=args)
	return args

if __name__ == '__main__':

	args = define_and_get_arguments()

	if(args.test_func==1):
		ENF_Process(args)
	elif(args.test_func==2):
		swarm_test(args)
	else:
		load_ENF(args)