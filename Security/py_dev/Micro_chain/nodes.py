'''
========================
nodes.py
========================
Created on June.2, 2019
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide nodes implementation.
@Reference: 
'''

from collections import OrderedDict
import os
import json
from uuid import uuid4
from urllib.parse import urlparse

from utilities import FileUtil, TypesUtil
from db_adapter import DataManager
from configuration import *

class PeerNodes:

	def __init__(self):

		#self.nodes = set()
		self.nodes = []
		self.node_db = DataManager(NODE_DATA_DIR, NODE_DATABASE)
		self.node_db.create_table(NODE_TABLE)

	def register_node(self, address, public_key, node_url):
		"""
		Add a new node to the node database
		"""
		# avoid adding duplicate data
		if( self.node_db.select_block(NODE_TABLE, address) !=[]):
			return

		#Checking node_url has valid format
		node_data={'address': address,
					'public_key': public_key,
					'node_url': ''}
		parsed_url = urlparse(node_url)
		if parsed_url.netloc:
			#self.nodes.add(parsed_url.netloc)
			node_data['node_url'] = parsed_url.netloc
			#self.nodes.add(TypesUtil.json_to_string(node_data))
			self.node_db.insert_block(NODE_TABLE, node_data['address'], TypesUtil.json_to_string(node_data))
		elif parsed_url.path:
			# Accepts an URL without scheme like '192.168.0.5:5000'.
			#self.nodes.add(parsed_url.path)
			node_data['node_url'] = parsed_url.path
			#self.nodes.add(TypesUtil.json_to_string(node_data))
			self.node_db.insert_block(NODE_TABLE, node_data['address'], TypesUtil.json_to_string(node_data))
		else:
		    raise ValueError('Invalid URL')

	def load_ByAddress(self, node_address = ""):
		self.nodes = self.node_db.select_block(NODE_TABLE, node_address)

	def load_ByStatus(self, node_status = 0):
		self.nodes = self.node_db.select_status(NODE_TABLE, node_status)

	def update_node(self, node_address, node_data):
		self.node_db.update_block(NODE_TABLE, node_address, node_data)

	def update_status(self, node_address, node_status):
		self.node_db.update_status(NODE_TABLE, node_address, node_status)

	def remove_node(self, node_address):
		self.node_db.delete_block(NODE_TABLE, node_address)

	def get_nodelist(self):
		list_nodes = set()
		for node in self.nodes:
			list_nodes.add(node[2])
		return list_nodes

'''	def get_node(self, node_address):
		"""
		get node information given node address
		"""
		json_node = {}
		for node in self.nodes:
			node_data = TypesUtil.string_to_json(node)
			if(node_data['address']==node_address):
				json_node = node_data
		return json_node

	def save_node(self, node_file=PEER_NODES):
			"""
			Save the list of nodes to static node file
			"""
			if(not os.path.exists(NODE_DATA_DIR)):
			    os.makedirs(NODE_DATA_DIR)
			FileUtil.List_save(NODE_DATA_DIR+'/'+node_file, list(self.nodes))

	def load_node(self, node_file=PEER_NODES):
			"""
			load nodes from static node file
			"""
			#self.nodes = fname.read()
			if(os.path.isfile(NODE_DATA_DIR+'/'+node_file)):
			    self.nodes = set(FileUtil.List_load(NODE_DATA_DIR+'/'+node_file))'''

