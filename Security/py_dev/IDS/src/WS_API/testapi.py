from flask import Flask, jsonify
from flask import abort,make_response,request
import datetime


app = Flask(__name__)

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

#Defining dict
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


#GET req
@app.route('/test/api/v1.0/dt', methods=['GET'])
def get_projects():
    return jsonify({'projects': projects})

#GET req for specific ID
@app.route('/test/api/v1.0/dt/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = [project for project in projects if project['id'] == project_id]
    if len(project) == 0:
        abort(404)
    return jsonify({'project': project[0]})

#Error handler for abort(404) 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


#POST req. add title,description , date-time will be taken current fron system. id will be +1
@app.route('/test/api/v1.0/dt', methods=['POST'])
def create_project():
    if not request.json or not 'title' in request.json:
        abort(400)
    project = {
        'id': projects[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'date': datestr,
	'time': timestr
    }
    projects.append(project)
    return jsonify({'project': project}), 201

#PUT req. Update any paraments by id number.
@app.route('/test/api/v1.0/dt/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = [project for project in projects if project['id'] == project_id]
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
    project[0]['title'] = request.json.get('title', project[0]['title'])
    project[0]['description'] = request.json.get('description', project[0]['description'])
    project[0]['date'] = request.json.get('date', project[0]['date'])
    project[0]['time'] = request.json.get('time', project[0]['time'])
    return jsonify({'project': project[0]})

#DELETE req. Delete by id number.
@app.route('/test/api/v1.0/dt/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = [project for project in projects if project['id'] == project_id]
    if len(project) == 0:
        abort(404)
    projects.remove(project[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
