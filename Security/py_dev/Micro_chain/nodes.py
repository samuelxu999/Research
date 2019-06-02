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


CHAIN_DATA_DIR = 'chaindata'
PEER_NODES = 'static_nodes'

class PeerNodes:

    def __init__(self):
        
        self.nodes = set()

    def register_node(self, address, public_key, node_url):
        """
        Add a new node to the list of nodes
        """
        #Checking node_url has valid format
        node_data={'address': address,
                'public_key': public_key,
                'node_url': ''}
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            #self.nodes.add(parsed_url.netloc)
            node_data['node_url'] = parsed_url.netloc
            self.nodes.add(TypesUtil.json_to_string(node_data))
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            #self.nodes.add(parsed_url.path)
            node_data['node_url'] = parsed_url.path
            self.nodes.add(TypesUtil.json_to_string(node_data))
        else:
            raise ValueError('Invalid URL')

    def save_node(self, node_file=PEER_NODES):
        """
        Save the list of nodes to static node file
        """
        if(not os.path.exists(CHAIN_DATA_DIR)):
            os.makedirs(CHAIN_DATA_DIR)
        FileUtil.List_save(CHAIN_DATA_DIR+'/'+node_file, list(self.nodes))

    def load_node(self, node_file=PEER_NODES):
        """
        load nodes from static node file
        """
        #self.nodes = fname.read()
        if(os.path.isfile(CHAIN_DATA_DIR+'/'+node_file)):
            self.nodes = set(FileUtil.List_load(CHAIN_DATA_DIR+'/'+node_file))

    def get_node(self, node_address):
        """
        get node information given node address
        """
        json_node = {}
        for node in self.nodes:
            node_data = TypesUtil.string_to_json(node)
            if(node_data['address']==node_address):
                json_node = node_data
        return json_node

def node_test():
    # Instantiate the PeerNodes
    peer_nodes = PeerNodes()

    # ----------------------- register node -------------------------------
    peer_nodes.register_node('ceeebaa052718c0a00adb87de857ba63608260e9',
        '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414b396a6a6e486e332f70492f596c6e4175454c492b35574b34394c397776510a5950346471516e514a7a66312f634d34416a726835484e706f5974622b326a6c33336a6b684850662f2b784f694f52346b4a685658526b434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
        'http://128.226.77.51:5011')
    peer_nodes.register_node('1699600976ec6fc0fe35d54174eb6094e671d2fd',
        '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414d58736e354f706b57706e3359695a386257753749397168363873784439370a2b2f4f5374616270305a464e365745475a415452316f397051684273727041416f656f4d4876717871784d2f645a636e7a43377a4f394d434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
        'http://128.226.77.51:8081')
    peer_nodes.register_node('f55af09f40768ca05505767cd013b6b9a78579c4',
        '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4677774451594a4b6f5a496876634e41514542425141445377417753414a42414e393072576d52506b6e46446b6d51536368414f74594434686f675a4d57330a6f4b4d77626559306a322f4966705a642b614447414863754c317534463443314d712b426354765239336b4b34573657346b6e59383145434177454141513d3d0a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a',
        'http://128.226.77.51:5300')
    
    nodes = peer_nodes.nodes
    #print(nodes)

    print('List registered nodes:')
    for node in list(nodes):
        json_node = TypesUtil.string_to_json(node)
        print('    ' + json_node['address'] + '    ' + json_node['node_url'])

    # ------------------ save and load node -------------------
    #peer_nodes.save_node(PEER_NODES)
    peer_nodes.load_node(PEER_NODES)
    reload_nodes = peer_nodes.nodes
    #print(reload_nodes)

    print('List loaded nodes:')
    for node in list(reload_nodes):
        json_node = TypesUtil.string_to_json(node)
        print('    ' + json_node['address'] + '    ' + json_node['node_url'])

    # ---------------------- search node ----------------------
    node_address = '1699600976ec6fc0fe35d54174eb6094e671d2fd'
    print('Search nodes:' + node_address)
    print(peer_nodes.get_node(node_address))
 
if __name__ == '__main__':
    node_test()
    pass








