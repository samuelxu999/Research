#!/bin/bash

# new folder based on test node size
for i in 1 2 3 4
do
	# new folders for local test
	if [ ! -d "local_test$i" ]
	then
		mkdir local_test$i
	fi

	# copy server and client code to localtest folder
	cp ./WS_Server.py local_test$i/
	cp ./WS_Client.py local_test$i/

	# copy libs to localtest folder
	cp -r ./cryptolib local_test$i/
	cp -r ./network local_test$i/
	cp -r ./consensus local_test$i/
	cp -r ./randomness local_test$i/
	cp -r ./utils local_test$i/
	cp -r ./kademlia local_test$i/
	cp -r ./rpcudp local_test$i/

	# clear test data and results
	rm -rf local_test$i/chaindata/*
	rm -rf local_test$i/randomdata/*
	rm -rf local_test$i/test_results/*
	rm -f local_test$i/nodedata/*

done

## clear test data and results
rm -rf ./chaindata/*
rm -rf ./randomdata/*
rm -rf ./test_results/*
rm -f ./nodedata/*
touch ./WS_Server.py
