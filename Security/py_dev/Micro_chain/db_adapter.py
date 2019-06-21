'''
========================
db_adapter.py
========================
Created on June.21, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide database implementation.
@Reference: https://www.sqlite.org/
'''


CHAIN_DATA_DIR = 'chaindata'
#CHAIN_DATABASE = 'chain_db'

import os
import sqlite3

def new_db(db_path):
	conn = sqlite3.connect(db_path)
	print("New database successfully at: ", db_path)
	conn.close()

class DataManager():

	def __init__(self, db_file):
		if(not os.path.exists(CHAIN_DATA_DIR)):
			os.makedirs(CHAIN_DATA_DIR)
		self.db_path = CHAIN_DATA_DIR+'/'+db_file

		if(not os.path.exists(self.db_path)):
			new_db(self.db_path)

	def create_table(self, table_name):
		'''
		#create table given table_name
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("CREATE TABLE IF NOT EXISTS %s \
				 (Block_hash	REAL		PRIMARY KEY, \
				 Block_data	TEXT    	NOT NULL);" %(table_name))

		conn.close()

	def remove_table(self, table_name):
		'''
		#remove table given table_name
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("DROP TABLE IF EXISTS %s;" %(table_name))

		conn.close()

	def select_block(self, table_name, block_hash=0):
		'''
		# return matched block data in table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		if( block_hash==0 ):
			#select all data
			cursor = conn.execute("SELECT * FROM %s;" %(table_name))
		else:
			#select data given block.hash
			cursor = conn.execute("SELECT * FROM %s where Block_hash=%d;" %(table_name, block_hash))

		ls_result=[]

		for row in cursor:
			ls_result.append(row)

		conn.close()

		return ls_result

	def add_block(self, table_name, block_hash, block_data):
		'''
		# insert block data into table_name
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("INSERT INTO %s (Block_hash, Block_data) VALUES ('%d', '%s');" \
			%(table_name, block_hash, block_data));

		conn.commit()

		conn.close()

	def update_block(self, table_name, block_hash, block_data):
		'''
		# update block data in table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("UPDATE %s set Block_data=%s where Block_hash=%d;" \
			%(table_name, block_data, block_hash));

		conn.commit()

		conn.close()

	def delete_block(self, table_name, block_hash):
		'''
		# remove block data from  table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("DELETE from %s where Block_hash=%d;" \
			%(table_name, block_hash));

		conn.commit()

		conn.close()