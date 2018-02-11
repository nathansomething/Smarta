from flask import Flask, request
from flask_restful import Resource, Api, abort
import get_sample_data

app = Flask(__name__)
api = Api(app)

class SmartaSampleData(Resource):

    def get(self):
        return get_sample_data.get_tfevt_assets(), {'Access-Control-Allow-Origin': '*'}

class SmartaDataForAssetId(Resource):

    def get(self, userfriendly_id):
        print("got id={}".format(userfriendly_id))
        return get_sample_data.get_vehicle_counts_for_asset_id(userfriendly_id), {'Access-Control-Allow-Origin': '*'}

api.add_resource(SmartaSampleData, '/')
api.add_resource(SmartaDataForAssetId, '/<int:userfriendly_id>')

if __name__ == '__main__':
    app.run(debug=True)
