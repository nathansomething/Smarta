from flask import Flask, request
from flask_restful import Resource, Api, abort
import get_sample_data

app = Flask(__name__)
api = Api(app)

TODOS = {}

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist.".format(todo_id))

class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return {todo_id:TODOS[todo_id]}

    def put(self, todo_id):
        data = request.form['data']
        TODOS[todo_id] = data
        return {todo_id:data}, 201

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

class TodoList(Resource):

    def get(self):
        return TODOS

    def post(self):
        todo_id = len(TODOS)
        data = request.form['data']
        TODOS[todo_id] = data
        return {todo_id:data}, 201

class SmartaSampleData(Resource):
    
    def get(self):
        return get_sample_data.get_tfevt_assets()
        
api.add_resource(Todo, '/todolist/<int:todo_id>')
api.add_resource(TodoList, '/todolist/')
api.add_resource(SmartaSampleData, '/')

if __name__ == '__main__':
    app.run(debug=True)
