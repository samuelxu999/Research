#!/usr/bin/env python

'''
========================
filter_list.py
========================
Created on Nov.3, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide filter list management by using SQLite.
@Reference: https://www.sqlite.org/
'''

import sqlite3


'''
FilterList class for manage filter list files
'''
class FilterManager(object):
	
	#new db file based on db_path
	@staticmethod
	def new_db(db_path):
		conn = sqlite3.connect(db_path)
		print "New database successfully at: " + db_path;
		conn.close()
	
	#Create table in db file
	@staticmethod	
	def create_table(db_path):
		conn = sqlite3.connect(path_db)
		
		#create whitelist table
		conn.execute('''CREATE TABLE Whitelist
				 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
				 Type           		TEXT    	NOT NULL,
				 Address        		TEXT    	NOT NULL,
				 StartTime        		TEXT    	NOT NULL,
				 ExpireTime         	TEXT    	NOT NULL);''')
		
		#create blacklist table
		conn.execute('''CREATE TABLE Blacklist
				 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
				 Type           		TEXT    	NOT NULL,
				 Address        		TEXT    	NOT NULL,
				 StartTime        		TEXT    	NOT NULL,
				 ExpireTime         	TEXT    	NOT NULL);''')

		conn.close()
	
	#Insert record into table
	@staticmethod	
	def insert_entry(path_db, tb_name, arg_list):	
		conn = sqlite3.connect(path_db)
			  
		conn.execute("INSERT INTO %s (Type, Address, StartTime, ExpireTime) VALUES ('%s', '%s', '%s','%s');" \
			%(tb_name, arg_list[0], arg_list[1], arg_list[2], arg_list[3]));

		conn.commit()
		conn.close()
	
	#Update record of table based on condition
	@staticmethod	
	def update_entry(path_db, tb_name, value_list):
		conn = sqlite3.connect(path_db)
		
		conn.execute("UPDATE %s set StartTime='%s',ExpireTime='%s' where Address='%s';" \
					%(tb_name, value_list[2], value_list[3], value_list[1]))
		
		conn.commit()
		conn.close()
	
	#Delete record from table
	@staticmethod		
	def delete_entry(path_db, tb_name, value_list):
		conn = sqlite3.connect(path_db)

		conn.execute("DELETE from %s where Address = '%s';" %(tb_name, value_list[1]))
		conn.commit()
		print "Total number of rows deleted :", conn.total_changes
		
		conn.close()
	
	#Select all record from table in db file
	@staticmethod		
	def select_entry(path_db, tb_name):
		conn = sqlite3.connect(path_db)	
	
		cursor = conn.execute("SELECT Type, Address, StartTime, ExpireTime from %s;" %(tb_name))
		
		for row in cursor:
		   print "Type = ", row[0]
		   print "ADDRESS = ", row[1]
		   print "StartTime = ", row[2]
		   print "ExpireTime = ", row[3], "\n"

		conn.close()
		
	
if __name__ == '__main__': 
	path_db='ipset_config/ipset_filter.db'
	tb_name1='Whitelist'
	tb_name2='Blacklist'
	ls_arg1=['Net', '172.16.201.0/24', '2016-10-15 10:29:42', '2016-11-28 11:29:42']
	ls_arg2=['IP', '128.226.79.117', '2017-10-19 12:29:42', '2017-11-9 16:29:42']

	#FilterManager.new_db(path_db)
	#FilterManager.create_table(path_db)
	#FilterManager.insert_entry(path_db, tb_name, ls_arg2)
	#FilterManager.update_entry(path_db, tb_name, ls_arg1)
	#FilterManager.delete_entry(path_db, tb_name, ls_arg2)
	FilterManager.select_entry(path_db, tb_name2)
	pass