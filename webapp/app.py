#!flask/bin/python
# -*- coding: utf-8 -*-

from flask_restful import reqparse, fields, marshal, Api, Resource
from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, abort, make_response

app = Flask(__name__, static_url_path="")
api = Api(app)

help_message = """
    - /Tarefa/ - GET: lista todas as tarefas do dicionário.
    - /Tarefa/ - POST: Adiciona uma tarefa.
    - /Tarefa/<id> - GET: lista a tarefa com o determinado id.
    - /Tarefa/<id> - PUT: atualiza uma tarefa com o determinado id.
    - /Tarefa/<id> - DELETE: apaga a tarefa com o determinado id.
    - /healthcheck/ - Retorna o código 200 sem texto.
    """

Tarefas = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('Tarefa')
}

class TaskListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True,
            help = 'Título é obrigatório para criar tarefa.', location = 'json')
        self.reqparse.add_argument('description', type = str, default = "", location = 'json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return {'Tarefas': [marshal(Tarefa, task_fields) for Tarefa in Tarefas]}

    def post(self):
        args = self.reqparse.parse_args()
        Tarefa = {
            'id': Tarefas[-1]['id'] + 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        Tarefas.append(Tarefa)
        return {'Tarefa': marshal(Tarefa, task_fields)}, 201

class TaskAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        self.reqparse.add_argument('done', type = bool, location = 'json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        Tarefa = [Tarefa for Tarefa in Tarefas if Tarefa['id'] == id]
        if len(Tarefa) == 0:
            abort(404)
        return {'Tarefa': marshal(Tarefa[0], task_fields)}

    def put(self, id):
        Tarefa = [Tarefa for Tarefa in Tarefas if Tarefa['id'] == id]
        if len(Tarefa) == 0:
            abort(404)
        Tarefa = Tarefa[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                Tarefa[k] = v
        return {'Tarefa': marshal(Tarefa, task_fields)}

    def delete(self, id):
        Tarefa = [Tarefa for Tarefa in Tarefas if Tarefa['id'] == id]
        if len(Tarefa) == 0:
            abort(404)
        Tarefas.remove(Tarefa[0])
        return {'result': True}


class Help(Resource):    
    def get(self):
        return help_message

class Healthcheck(Resource):
    def get(self):
        return 200

api.add_resource(TaskListAPI, '/Tarefa/', endpoint = 'Tarefas')
api.add_resource(TaskAPI, '/Tarefa/<int:id>', endpoint = 'Tarefa')
api.add_resource(Help, '/help/', endpoint = 'Help')
api.add_resource(Healthcheck, '/healthcheck/', endpoint = 'Healthcheck')

if __name__ == '__main__':
    app.run(debug=True)