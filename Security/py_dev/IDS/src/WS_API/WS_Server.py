#!/usr/bin/env python

'''
========================
WS_Server module
========================
Created on Nov.2, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of server API that handle and response client's request.
'''

from flask import Flask, jsonify
from flask import abort,make_response,request
import datetime
from CapAC_Policy import CapToken, CapPolicy

app = Flask(__name__)

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

#Defining dictionary dataset model
projects = [
    {
        'id': 1,
		'title':u'test',
		'description':u'Hello World',
		'date':u'04-28-2017',
        'time': u'Morning'
    },
    {
        'id': 2,
        'title':u'GET',
        'description':u'test GET APIs',
		'date':u'4-29-2017',
		'time': u'12:00 am'
    }
]

#========================================== Error handler ===============================================
#Error handler for abort(400) 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#Error handler for abort(404) 
@app.errorhandler(400)
def type_error(error):
    return make_response(jsonify({'error': 'type error'}), 400)

	
#========================================== Request handler ===============================================
#GET req
@app.route('/test/api/v1.0/dt', methods=['GET'])
def get_projects():
	'''print(request.url)
	print(request.method)'''
	token_data=request.args
	if(not CapPolicy.is_valid_access_request(token_data)):
		abort(404)
	return jsonify({'projects': projects})
	
#GET req for specific ID
@app.route('/test/api/v1.0/dt/project', methods=['GET'])
def get_project():
	#filter = request.args.get('filter', default = '*', type = str)
	project_id = request.args.get('project_id', default = 1, type = int)
	project = [project for project in projects if project['id'] == project_id]
	if len(project) == 0:
		abort(404)
	return jsonify({'project': project[0]})
	
#POST req. add title,description , date-time will be taken current fron system. id will be +1
@app.route('/test/api/v1.0/dt/create', methods=['POST'])
def create_project():
	if not request.json:
		abort(400)
	req_json=request.json['project_data']
	project = {
        'id': projects[-1]['id'] + 1,
        'title': req_json['title'],
        'description': req_json['description'],
        'date': req_json['date'],
		'time': req_json['time']
    }
	projects.append(project)
	return jsonify({'project_data': project}), 201

#PUT req. Update any paraments by id number.
@app.route('/test/api/v1.0/dt/update', methods=['PUT'])
def update_project():
	#get json data
	req_json=request.json['project_data']
	
	#get updating record id
	project_id=req_json['id']
	
	#get record based on id
	project = [project for project in projects if project['id'] == project_id]
	
	#data verification
	if len(project) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	if 'date' in request.json and type(request.json['date']) is not unicode:
		abort(400)
	if 'time' in request.json and type(request.json['time']) is not unicode:
		abort(400)
		
	#update data field
	project[0]['title'] = req_json['title']
	project[0]['description'] = req_json['description']
	project[0]['date'] = req_json['date']
	project[0]['time'] = req_json['time']
	
	#return jsonify({'project_data': project}), 201
	return jsonify({'result': True})
	
#DELETE req. Delete by id number.
@app.route('/test/api/v1.0/dt/delete', methods=['DELETE'])
def delete_project():
	#get json data
	req_json=request.json

	#get updating record id
	project_id=req_json['id']

	#get record based on id
	project = [project for project in projects if project['id'] == project_id]

	if len(project) == 0:
		abort(404)
	projects.remove(project[0])
	return jsonify({'result': True})
	
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
