from flask import Flask
from flask_restful import Api, Resource, abort
from flask import request
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
    
    def get(self):
        args = request.args
        print("args={}".format(args))
        userfriendly_id = args['id']
        to_date = args['to_date']
        if to_date is not None and (len(to_date.strip()) == 0 or (to_date ==  "''"))  :
            to_date = None
        aggregate_num_hours = args['aggregate_num_hours']
        if aggregate_num_hours is not None and (len(aggregate_num_hours.strip()) == 0 or (aggregate_num_hours ==  "''")):
            aggregate_num_hours = None
        else :
            aggregate_num_hours = int(aggregate_num_hours)
        aggregate_num_days = args['aggregate_num_days']
        if aggregate_num_days is not None and (len(aggregate_num_days.strip()) == 0 or (aggregate_num_days ==  "''")) :
            aggregate_num_days = None
        else :
            aggregate_num_days = int(aggregate_num_days)

        return get_sample_data.get_vehicle_counts_for_asset_id(userfriendly_id, to_date, aggregate_num_hours, aggregate_num_days), {'Access-Control-Allow-Origin': '*'}

    '''
    def get(self, userfriendly_id):
        print("got id={}".format(userfriendly_id))
        #return get_sample_data.get_vehicle_counts_for_asset_id(userfriendly_id)
        return get_sample_data.get_vehicle_counts_for_asset_id(userfriendly_id=2, to_date=None, aggregate_num_hours=None, aggregate_num_days=1)
    '''

api.add_resource(SmartaSampleData, '/')
#api.add_resource(SmartaDataForAssetId, '/<int:userfriendly_id>')
api.add_resource(SmartaDataForAssetId, '/aggr', endpoint='aggr')


if __name__ == '__main__':
    app.run(debug=True)
