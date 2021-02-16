'''
========================
p2p.py
========================
Created on Feb.12, 2021
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide p2p implementation based on kademlia.
@Reference: https://kademlia.readthedocs.io/en/latest/intro.html
'''

import logging
import asyncio
import os.path

from kademlia.network import Server
from kademlia.utils import digest
from kademlia.crawling import NodeSpiderCrawl
from utils.utilities import FileUtil, TypesUtil
from utils.configuration import *

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

node_file = NODE_DATA_DIR + "/peer_nodes"

class Kademlia_Server:

	def __init__(self, rpc_port, freq_loop, node_id=None, ksize=20, alpha=3):
		"""
		Create a server instance.  This will assign paramsters.

		Args:
			node_id: The uuid for this node on the network.
			ksize (int): The k parameter from the paper
			alpha (int): The alpha parameter from the paper
			freq_loop [int]: The frequency for: [0]-save_state; [1]-refresh_neighbors  
		"""
		self.node_id = digest(node_id)
		self.rpc_port = rpc_port
		self.freq_save_state = freq_loop[0]
		self.freq_refresh_neighbors = freq_loop[1]
		self.kademlia_srv = Server(node_id=self.node_id, ksize=ksize, alpha=alpha)
		self.run_loop = None
		self.refresh_loop = None


	def run(self, firstnode, bootstrapnode):
		"""
		Run a server instance.  This will start listening on the given port.

		"""
		# self.run_loop = asyncio.get_event_loop()
		self.run_loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.run_loop)
		self.run_loop.set_debug(True)

		## bind listen port
		self.run_loop.run_until_complete(self.kademlia_srv.listen(self.rpc_port))

		if(not firstnode):
			node_address = bootstrapnode.split(':')
			bootstrap_node = (node_address[0], int(node_address[1])) 
			log.info("bootstrap node address: {}:{}".format(bootstrap_node[0], bootstrap_node[1]))
			self.run_loop.run_until_complete(self.kademlia_srv.bootstrap([bootstrap_node]))

			## set refresh neighbors task
			self.refresh_neighbors_regularly()
		else:
			## if there are cached peer nodes, connect bootstrap node
			if(os.path.exists(node_file)):
				## load cached peer nodes. 
				self.kademlia_srv = self.run_loop.run_until_complete(Server.load_state(node_file, self.rpc_port))

			## set save state task
			self.kademlia_srv.save_state_regularly(node_file, self.freq_save_state)

		try:
			self.run_loop.run_forever()
		except (KeyboardInterrupt, SystemExit):
			log.info('\n! Received keyboard interrupt, quitting service.\n')
		finally:
			self.kademlia_srv.save_state(node_file)
			self.kademlia_srv.stop()
			self.run_loop.close()
			self.refresh_loop.close()

	async def _refresh_neighbors(self):
		neighbors = self.kademlia_srv.bootstrappable_neighbors()

		cos = list(map(self.kademlia_srv.bootstrap_node, neighbors))
		gathered = await asyncio.gather(*cos)
		nodes = [node for node in gathered if node is not None]
		spider = NodeSpiderCrawl(self.kademlia_srv.protocol, self.kademlia_srv.node, nodes,
								self.kademlia_srv.ksize, self.kademlia_srv.alpha)
		return await spider.find()

	def refresh_neighbors_regularly(self):
		log.info("Refreshing neighbors.")
		
		asyncio.ensure_future(self._refresh_neighbors())
		loop = asyncio.get_event_loop()
		self.refresh_loop = loop.call_later(self.freq_refresh_neighbors, self.refresh_neighbors_regularly)
