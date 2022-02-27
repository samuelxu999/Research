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


#CHAIN_DATA_DIR = 'chaindata'
#CHAIN_DATABASE = 'chain_db'

import os
import sqlite3

def new_db(db_path):
	'''
	# New database file given db_path
	'''
	conn = sqlite3.connect(db_path)
	print("New database successfully at: ", db_path)
	conn.close()

class DataManager():
	'''
	# block data manager class based on sqlite database
	'''
	def __init__(self, db_dir, db_file):
		if(not os.path.exists(db_dir)):
			os.makedirs(db_dir)
		self.db_path = db_dir+'/'+db_file

		if(not os.path.exists(self.db_path)):
			new_db(self.db_path)

	def create_table(self, table_name):
		'''
		#create table given table_name
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("CREATE TABLE IF NOT EXISTS %s \
				 (ID 			INTEGER 	PRIMARY KEY AUTOINCREMENT, \
				 Block_hash		TEXT		NOT NULL, \
				 Block_data		TEXT    	NOT NULL, \
				 Block_status	INTEGER    	NOT NULL);" %(table_name))

		conn.close()		

	def remove_table(self, table_name):
		'''
		#remove table given table_name
		'''
		conn = sqlite3.connect(self.db_path)
		
		conn.execute("DROP TABLE IF EXISTS %s;" %(table_name))

		conn.close()		

	def select_block(self, table_name, block_hash=''):
		'''
		# return matched block data in table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		if( block_hash=='' ):
			#select all data
			cursor = conn.execute("SELECT * FROM %s;" %(table_name))
		else:
			#select data given block.hash
			sql = ("SELECT * FROM %s where Block_hash=?;" %(table_name) )			
			cursor = conn.execute(sql, (block_hash,))


		ls_result=[]

		for row in cursor:
			ls_result.append(row)

		conn.close()

		return ls_result

	def select_status(self, table_name, block_status):
		'''
		# return matched block data in table_name given block_status
		'''
		conn = sqlite3.connect(self.db_path)		

		#select data given block.status
		cursor = conn.execute("SELECT * FROM %s where Block_status=%d;" %(table_name, block_status))

		ls_result=[]

		for row in cursor:
			ls_result.append(row)

		conn.close()

		return ls_result

	def insert_block(self, table_name, block_hash, block_data, block_status=0):
		'''
		# insert block data into table_name
		'''
		conn = sqlite3.connect(self.db_path)
		
		sql = ("INSERT INTO %s (Block_hash, Block_data, Block_status) VALUES (?, ?, ?);" %(table_name))
		'''conn.execute("INSERT INTO %s (Block_hash, Block_data, Block_status) \
					VALUES (?, ?, ?);" \
					%(table_name, sqlite3.Binary(block_hash), block_data, block_status));'''
		conn.execute(sql, (block_hash, block_data, block_status) )

		conn.commit()

		conn.close()

	def update_block(self, table_name, block_hash, block_data):
		'''
		# update block data in table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		sql = ( "UPDATE %s set Block_data=? where Block_hash=?;" %(table_name) )

		conn.execute(sql, (block_data, block_hash));

		conn.commit()

		conn.close()

	def update_status(self, table_name, block_hash, block_status):
		'''
		# update block data in table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		sql = ( "UPDATE %s set Block_status=? where Block_hash=?;" %(table_name) )

		conn.execute(sql, (block_status, block_hash));

		conn.commit()

		conn.close()

	def delete_block(self, table_name, block_hash):
		'''
		# remove block data from  table_name given block_hash
		'''
		conn = sqlite3.connect(self.db_path)
		
		sql = ( "DELETE from %s where Block_hash=?;" %(table_name) )

		conn.execute(sql, (block_hash,));

		conn.commit()

		conn.close()
