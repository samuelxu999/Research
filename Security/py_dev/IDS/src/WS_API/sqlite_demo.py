#!/usr/bin/env python

import sqlite3

def open_db(path_db):
	conn = sqlite3.connect(path_db)
	print "Opened database successfully";
	conn.close()
	
def create_table(path_db):
	conn = sqlite3.connect(path_db)
	print "Opened database successfully";

	conn.execute('''CREATE TABLE COMPANY
			 (ID INTEGER PRIMARY KEY     AUTOINCREMENT,
			 NAME           TEXT    NOT NULL,
			 AGE            INT     NOT NULL,
			 ADDRESS        CHAR(50),
			 SALARY         REAL);''')
	print "Table created successfully";

	conn.close()

def insert_entry(path_db):	
	conn = sqlite3.connect(path_db)
	print "Opened database successfully";

	conn.execute("INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY) \
		  VALUES ('Paul', 32, 'California', 20000.00 )");

	conn.execute("INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY) \
		  VALUES ('Allen', 25, 'Texas', 15000.00 )");

	conn.execute("INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY) \
		  VALUES ('Teddy', 23, 'Norway', 20000.00 )");

	conn.execute("INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY) \
		  VALUES ('Mark', 25, 'Rich-Mond ', 65000.00 )");

	conn.commit()
	print "Records created successfully";
	conn.close()
	
def select_entry(path_db):
	conn = sqlite3.connect(path_db)
	print "Opened database successfully";

	cursor = conn.execute("SELECT id, name, address, salary from COMPANY")
	for row in cursor:
	   print "ID = ", row[0]
	   print "NAME = ", row[1]
	   print "ADDRESS = ", row[2]
	   print "SALARY = ", row[3], "\n"

	print "Operation done successfully";
	conn.close()
	
def update_entry(path_db):
	conn = sqlite3.connect(path_db)
	print "Opened database successfully";

	conn.execute("UPDATE COMPANY set SALARY = 25000.00 where ID = 1")
	conn.commit
	print "Total number of rows updated :", conn.total_changes

	cursor = conn.execute("SELECT id, name, address, salary from COMPANY")
	for row in cursor:
	   print "ID = ", row[0]
	   print "NAME = ", row[1]
	   print "ADDRESS = ", row[2]
	   print "SALARY = ", row[3], "\n"

	print "Operation done successfully";
	conn.close()
	
def delete_entry(path_db):
	conn = sqlite3.connect(path_db)
	print "Opened database successfully";

	conn.execute("DELETE from COMPANY where name = 'Paul';")
	conn.commit()
	print "Total number of rows deleted :", conn.total_changes

	cursor = conn.execute("SELECT id, name, address, salary from COMPANY")
	for row in cursor:
	   print "ID = ", row[0]
	   print "NAME = ", row[1]
	   print "ADDRESS = ", row[2]
	   print "SALARY = ", row[3], "\n"

	print "Operation done successfully";
	conn.close()

if __name__ == '__main__':
	path_db='sqlite_db/test.db'
	#open_db(path_db)
	#create_table(path_db)
	#insert_entry(path_db)
	select_entry(path_db)
	#update_entry(path_db)
	#delete_entry(path_db)
	pass