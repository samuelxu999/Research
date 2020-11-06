import string
import hashlib

from merklelib import MerkleTree, verify_tree_consistency, beautify, export, jsonify

# a sample hash function
# you can also omit it and the default hash function will be used
def hashfunc(value):
	return hashlib.sha256(value).hexdigest()


def build_tree():


	# a list of all ASCII letters
	data = list(string.ascii_letters)

	# build a Merkle tree for that list
	tree = MerkleTree(data, hashfunc)

	# generate an audit proof the letter A
	test_data = 'A'
	proof = tree.get_proof(test_data)

	# now verify that A is in the tree
	# you can also pass in the hash value of 'A'
	# it will hash automatically if the user forgot to hash it
	if tree.verify_leaf_inclusion(test_data, proof):
		print('{} is in the tree'.format(test_data))
	else:
		print('{} is not in the tree'.format(test_data))

def updated_tree():

	print("Update 'D' in the tree to 'F'")
	# a list of all ASCII letters
	data = ['A', 'B', 'C', 'D']

	mytree = MerkleTree(data, hashfunc)

	# print the tree in the terminal
	print('---------------------- Before ----------------')
	beautify(mytree) 

	# now update that 'D' is in the tree to 'E'
	mytree.update('D', 'E')

	# print the tree in the terminal
	print('---------------------- After ----------------')
	beautify(mytree) 
	
def compare_tree():

	print("Compare old_tree and new_tree")
	# a list of all ASCII letters
	data = ['A', 'B', 'C', 'D']

	old_tree = MerkleTree(data, hashfunc)

	# print the tree in the terminal
	print('---------------------- old_tree ----------------')
	beautify(old_tree) 


	# a list of all ASCII letters
	new_data = ['A', 'B', 'C', 'd']

	new_tree = MerkleTree(new_data, hashfunc)

	# print the tree in the terminal
	print('---------------------- new_tree ----------------')
	beautify(new_tree) 


	# information that we need to provide
	old_hash_root = old_tree.merkle_root
	old_tree_size = len(old_tree)
	# print(old_tree_size)

	# check if the new tree contains the same items
	# and in the same order as the old version
	if verify_tree_consistency(new_tree, old_hash_root, old_tree_size):
		print('Versions are consistent')
	else:
		print('Versions are different')

def export_tree():
	print("Export tree mapping")
	# a list of all ASCII letters
	mydata = ['A', 'B', 'C', 'D', 1, 2, 3, 4]

	mytree = MerkleTree(mydata, hashfunc)

	# export(mytree, filename='transactions')
	# export(mytree, filename='transactions', ext='jpg')

	json_tree=jsonify(mytree)
	print(json_tree)


if __name__ == '__main__':
	build_tree()
	updated_tree()
	compare_tree()
	export_tree()
	pass