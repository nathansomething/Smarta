from flask import Flask, request
from flask_restful import Resource, Api, abort
import get_sample_data

app = Flask(__name__)
api = Api(app)

class SmartaSampleData(Resource):

    def get(self):
        return get_sample_data.get_tfevt_assets()

api.add_resource(SmartaSampleData, '/')

if __name__ == '__main__':
    app.run(debug=True)
