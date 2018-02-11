from flask import Flask
from flask_restful import Api, Resource, abort
from flask import request
import get_sample_data
import json

app = Flask(__name__)
api = Api(app)

class SmartaSampleData(Resource):
    
    def get(self):
        return get_sample_data.get_tfevt_assets(), {'Access-Control-Allow-Origin': '*'}
        

class SmartaDataForAssetId(Resource):
    #http://127.0.0.1:5000/aggr?id=${this.id}&start_days_ago=${this.startDaysAgo}&end_days_ago=${endDaysAgo}&aggregate_num_hours=${this.getAggregateHours()}
    def get(self):
        args = request.args
        print("args={}".format(args))
        userfriendly_id = args['id']
        start_days_ago = args.get('start_days_ago', None)
        if start_days_ago is not None and (len(start_days_ago.strip()) == 0 or (start_days_ago ==  "''"))  :
            start_days_ago = None
        else :
            start_days_ago = int(start_days_ago)
        end_days_ago = args.get('end_days_ago', None)
        if end_days_ago is not None and (len(end_days_ago.strip()) == 0 or (end_days_ago ==  "''"))  :
            end_days_ago = None        
        else :
            end_days_ago = int(end_days_ago)
        aggregate_num_hours = args.get('aggregate_num_hours', None)
        if aggregate_num_hours is not None and (len(aggregate_num_hours.strip()) == 0 or (aggregate_num_hours ==  "''")):
            aggregate_num_hours = None
        else :
            aggregate_num_hours = int(aggregate_num_hours)
            
        if aggregate_num_hours >= 24 :
            aggregate_num_days = 1
            aggregate_num_hours = None
        else :
            aggregate_num_days = None
        result_list = get_sample_data.get_vehicle_counts_for_asset_id(userfriendly_id, start_days_ago, end_days_ago, aggregate_num_hours, aggregate_num_days) 
        return result_list, {'Access-Control-Allow-Origin': '*'}
                
    
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
