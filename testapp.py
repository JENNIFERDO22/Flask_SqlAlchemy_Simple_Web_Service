# Back-end style

from flask import Flask, jsonify, abort, make_response, request, url_for
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

testapp = Flask(__name__)

# set database uri to save
Base = declarative_base()

class Task(Base):
    __tablename__ = "task"

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(100), nullable=False)
    description = Column('description', String(500), nullable=True)
    done = Column('done', Boolean, nullable=False, default=False)

    def __init__(self, task):
        self.id = task['id']
        self.title = task['title']
        self.description = task['description']
        self.done = task['done']

    def asdict(self):
        return {"id": self.id, "title": self.title,"description": self.description,"done": self.done}

engine = create_engine('sqlite:///task.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# def add_task(task):
#     session = Session()
#     t = Task(task)
#     session.add(t)
#     session.commit()
#     session.close()

def get_num_rows():
    session = Session()
    num = session.query(Task).count()
    session.commit()
    session.close()
    return num

# change id into uri
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            # use get_task function
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

# retrieve all tasks
@testapp.route('/test/api/v1.0/tasks/', methods=['GET'])
def get_all_tasks():
    session = Session()
    tasks = session.query(Task).all()
    session.close()
    return jsonify({'tasks': [make_public_task(t.asdict()) for t in tasks]})

    
# retrieve by id
@testapp.route('/test/api/v1.0/tasks/<int:task_id>', methods=['GET'])  
def get_task(task_id):
    session = Session()
    task = session.query(Task).filter(Task.id==task_id).first()
    session.close()
    if task is None:
        # 404 - not found
        abort(404)  
    return jsonify({'task': task.asdict()})

# create
@testapp.route('/test/api/v1.0/tasks/', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        # 400 - bad request 
        return make_response(jsonify({'error': 'No title'}), 400)
    
    task = {
        'id': get_num_rows() + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ''),
        'done': False
    }

    session = Session()
    t = Task(task)
    session.add(t)
    session.commit()
    session.close()

    return jsonify({'task': make_public_task(task)}), 201


# error handler
@testapp.errorhandler(404)
def not_found(error):
    # return a json object and raise error 404
    return make_response(jsonify({'error': 'Not found'}), 404)

# update task
@testapp.route('/test/api/v1.0/tasks/<int:task_id>', methods=['PUT']) 
def update_task(task_id):
    if (not request.json):
        abort(400)

    if 'title' in request.json and not isinstance(request.json['title'], str):
        abort(400)

    if 'description' in request.json and not isinstance(request.json['title'], str):
        abort(400)

    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)

    session = Session()
    task = session.query(Task).filter(Task.id==task_id).first()
    session.close()
    if task is None:
        # 404 - not found
        abort(404) 

    task = task.asdict()
    task['title'] = request.json.get('title', task['title'])    
    task['description'] = request.json.get('description', task['description'])
    task['done'] = request.json.get('done', task['done'])
    return jsonify({'task': task})

# delete
@testapp.route("/test/api/v1.0/tasks/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
    session = Session()
    t = session.query(Task).filter(Task.id==task_id).first()
    session.delete(t)
    session.commit()
    session.close()

    if t is None:
        abort(404)
    return jsonify({'status': 'successfully deleted'})

if __name__ == '__main__':
    testapp.run(debug=True)

