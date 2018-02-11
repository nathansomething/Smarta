import requests
import simplejson
import json
import time
import datetime
import calendar
#BASE_URL = 'http://' + HARD_CODED_HOST_NAME

def get_token():
    json_dict = load_environment('Hackathon')
    api_adapter = ApiAdapter(json_dict)
    api_adapter.init_token()

    print("got token={}".format(api_adapter.token))

def get_results():
    vehicle_counts = get_vehicle_counts_for_asset_id(2)
    print(vehicle_counts) 
    return vehicle_counts

def get_results_filtered_assets():
    json_dict = load_environment('Schenectady')
    api_adapter = ApiAdapter(json_dict)
    api_adapter.init_token()    
    all_pages_dict_list = api_adapter.get_all_assets_all_pages()
    filtered_assets = api_adapter.filter_assets_data(all_pages_dict_list)    
    single_datapoint = api_adapter.get_data_for_filtered_assets(filtered_assets)
    print(single_datapoint)

def time_now_as_epoch():
    today = datetime.datetime.now()
    epoch_now = (today - datetime.datetime(1970,1,1)).total_seconds()
    print(epoch_now)
    

def get_tfevt_assets() :
    ''' this is exposed as an endpoint in flask
    '''
    #json_dict = load_environment('Hackathon')
    json_dict = load_environment('Schenectady')
    api_adapter = ApiAdapter(json_dict)
    api_adapter.init_token()    
    all_pages_dict_list = api_adapter.get_all_assets_all_pages()
    filtered_assets = api_adapter.filter_assets_data(all_pages_dict_list)    
    #api_adapter.get_data_for_filtered_assets(filtered_assets)
    return filtered_assets
    
def get_vehicle_counts_for_asset_id(userfriendly_id=2):
    json_dict = load_environment('Schenectady')
    api_adapter = ApiAdapter(json_dict)
    api_adapter.init_token()    
    all_pages_dict_list = api_adapter.get_all_assets_all_pages()
    filtered_assets = api_adapter.filter_assets_data(all_pages_dict_list)    
    #asset_id = '385656d5-7a48-4755-a0f7-ef6ce92efe46'
    #userfriendly_id = api_adapter.tfevt_id_dict[asset_id]
    asset_id = api_adapter.tfevt_id_reverse_dict[userfriendly_id]
    #print("userfriendly_id={}, asset_id={}".format(userfriendly_id, asset_id))
    return api_adapter.get_vehicle_count_from_now(asset_id)

    
def load_environment(type):
    if type == 'Hackathon' :
        #filename = '/Users/ilya/work/GenomeCenterWorkArea/development/hacktechvalley_2018/HackTechValley/Hackathon - DEMO Data.postman_environment.json'
        filename = 'sample_data_environment/Hackathon - DEMO Data.postman_environment.json'
    elif type == 'Schenectady' :
        #filename = '/Users/ilya/work/GenomeCenterWorkArea/development/hacktechvalley_2018/HackTechValley/Schenectady - Live.postman_environment.json'
        filename = 'sample_data_environment/Schenectady - Live.postman_environment.json'
    else :
        raise ValueError("type={}".format(type))
    
    with open(filename, 'r') as f :
        string_val = f.read()
        json_dict = json.loads(string_val)
        return json_dict

def lookup_value_dict(json_dict, value_name):
    values = json_dict['values']
    for val_dict in values :
        val_key = val_dict['key']
        if value_name == val_key :
            return val_dict

def lookup_value(json_dict, value_name):
    value_dict = lookup_value_dict(json_dict, value_name)
    if value_dict is not None :
        return value_dict['value']

class ApiAdapter():
    def __init__(self, json_dict):
        self.json_dict = json_dict
        self.current_token = None
        self.tfevt_id_dict = {}
        self.tfevt_id_reverse_dict = {}
        self.tfevt_id_list = []
    
    def init_token(self):
        #url = "https://890407d7-e617-4d70-985f-01792d693387.predix-uaa.run.aws-usw02-pr.ice.predix.io/oauth/token"
        url = lookup_value(self.json_dict, 'UAAURL')
        querystring = {"grant_type":"client_credentials"}
        
        payload = "username=ic.admin&password=admin"
        
        headers = {
            'Authorization': "Basic aWMuc3RhZ2Uuc2ltLmRldmVsb3A6ZGV2",
            'Cache-Control': "no-cache",
            'Postman-Token': "98b01f17-cfa2-2f99-97b8-fb727966a421"
            }
        
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        
        #print(response.text)
        self.token = response.text
        
    def get_tfevt_by_asset_id_default(self):
        url = "https://ic-event-service-sch.run.aws-usw02-pr.ice.predix.io/v2/assets/385656d5-7a48-4755-a0f7-ef6ce92efe46/events"

        querystring = {"eventType":"TFEVT","startTime":"1517673396000","endTime":"1518191796000"}
        
        headers = {
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiIyMDk1NTAzOGRkODQ0ZTc4OGUwZTUwM2ZjNTcxZTAzMSIsInN1YiI6InNjaC5oYWNrYXRob24iLCJzY29wZSI6WyJ1YWEucmVzb3VyY2UiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBFREVTVFJJQU4uSUUtUEVERVNUUklBTi5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBBUktJTkcuSUUtUEFSS0lORy5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBVQkxJQy1TQUZFVFkuSUUtUFVCTElDLVNBRkVUWS5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVRSQUZGSUMuSUUtVFJBRkZJQy5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLUVOVklST05NRU5UQUwuSUUtRU5WSVJPTk1FTlRBTC5GUkVFLkRFVkVMT1AiXSwiY2xpZW50X2lkIjoic2NoLmhhY2thdGhvbiIsImNpZCI6InNjaC5oYWNrYXRob24iLCJhenAiOiJzY2guaGFja2F0aG9uIiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiI4YTZkMzIwNyIsImlhdCI6MTUxODMxNTQ5MSwiZXhwIjoxNTE4OTIwMjkxLCJpc3MiOiJodHRwczovLzg5MDQwN2Q3LWU2MTctNGQ3MC05ODVmLTAxNzkyZDY5MzM4Ny5wcmVkaXgtdWFhLnJ1bi5hd3MtdXN3MDItcHIuaWNlLnByZWRpeC5pby9vYXV0aC90b2tlbiIsInppZCI6Ijg5MDQwN2Q3LWU2MTctNGQ3MC05ODVmLTAxNzkyZDY5MzM4NyIsImF1ZCI6WyJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBVQkxJQy1TQUZFVFkuSUUtUFVCTElDLVNBRkVUWS5GUkVFIiwidWFhIiwic2NoLmhhY2thdGhvbiIsImllLWN1cnJlbnQuU2NoZW5lY3RhZHktSUUtUEVERVNUUklBTi5JRS1QRURFU1RSSUFOLkZSRUUiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLUVOVklST05NRU5UQUwuSUUtRU5WSVJPTk1FTlRBTC5GUkVFIiwiaWUtY3VycmVudC5TY2hlbmVjdGFkeS1JRS1QQVJLSU5HLklFLVBBUktJTkcuRlJFRSIsImllLWN1cnJlbnQuU2NoZW5lY3RhZHktSUUtVFJBRkZJQy5JRS1UUkFGRklDLkZSRUUiXX0.eAWv2tHgurYasQrrSu3cRhCEtqzlwgLsmmUak6OS1fKpsj2vJNZ7hFAt7-1_AteCNwZAkSMiKJ7v8p0AQvIIotFgQ_UZd9o5xRT5pfYxvs9prMxO7GbC3xeSA_FetaIdeckYQ7PZaiFqQAtzp69z-94jrkVSD_y4BVqyaYvUOR9tLC4iQBrCfShtYltzA1nI-_ouT62KlD5r0Cq9L8e1pB3Er4EhAlX42m8An1usWCOG7coXq0FAUb7ZtEqQVny-OPpaIcd_3N0ZDObLqn7q5kjoET-dhK52EhQkZwY7u2-jtgCnWbsoew1hjp0CTfFjB3Bs-j-3v_r33sIAwQymfQ",
            'Predix-Zone-Id': "Schenectady-IE-TRAFFIC",
            'Cache-Control': "no-cache",
            'Postman-Token': "30108cab-4557-4311-2c6c-271f48fa71bb"
            }
        
        response = requests.request("GET", url, headers=headers, params=querystring)
        
        print(response.text)

    def get_tfevt_by_asset_id_from_now(self, asset_id):
        print("asset_id={}".format(asset_id))
        today = datetime.datetime.now()
        one_period = datetime.timedelta(minutes=1)
        x_periods = 60
        x_periods_ago = today - (x_periods * one_period)
        
        epoch_x_periods = (x_periods_ago - datetime.datetime(1970,1,1)).total_seconds() * 1000
        epoch_now = (today - datetime.datetime(1970,1,1)).total_seconds() * 1000
        epoch_x_periods = long(round(epoch_x_periods))
        epoch_now = long(round(epoch_now))
        #detailed_data_str = self.get_tfevt_by_asset_id(asset_id, epoch_one_days, epoch_now)
        start_time = epoch_x_periods
        end_time = epoch_now
        #start_time="1517673396000"
        #end_time="1518191796000"
        return self.get_tfevt_by_asset_id(asset_id, start_time, end_time)
        
    #def get_tfevt_by_asset_id(self, asset_id, start_time="1517673396000", end_time="1518191796000"):
    def get_tfevt_by_asset_id(self, asset_id, start_time, end_time):
        print("start_time={}, end_time={}".format(start_time, end_time))
        event_url = lookup_value(self.json_dict, 'eventurl')
        #https://ic-event-service.run.aws-usw02-pr.ice.predix.io/v2
        #url = "https://ic-event-service.run.aws-usw02-pr.ice.predix.io/v2/assets/CAM-HYP1071-F/events"
        url = "{}/assets/{}/events".format(event_url, asset_id)
        querystring = {"eventType":"TFEVT","startTime":start_time,"endTime":end_time}
        #TODO: replace Authorization with token from init_token
        headers = {
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiIyMDk1NTAzOGRkODQ0ZTc4OGUwZTUwM2ZjNTcxZTAzMSIsInN1YiI6InNjaC5oYWNrYXRob24iLCJzY29wZSI6WyJ1YWEucmVzb3VyY2UiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBFREVTVFJJQU4uSUUtUEVERVNUUklBTi5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBBUktJTkcuSUUtUEFSS0lORy5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBVQkxJQy1TQUZFVFkuSUUtUFVCTElDLVNBRkVUWS5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVRSQUZGSUMuSUUtVFJBRkZJQy5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLUVOVklST05NRU5UQUwuSUUtRU5WSVJPTk1FTlRBTC5GUkVFLkRFVkVMT1AiXSwiY2xpZW50X2lkIjoic2NoLmhhY2thdGhvbiIsImNpZCI6InNjaC5oYWNrYXRob24iLCJhenAiOiJzY2guaGFja2F0aG9uIiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiI4YTZkMzIwNyIsImlhdCI6MTUxODMxNTQ5MSwiZXhwIjoxNTE4OTIwMjkxLCJpc3MiOiJodHRwczovLzg5MDQwN2Q3LWU2MTctNGQ3MC05ODVmLTAxNzkyZDY5MzM4Ny5wcmVkaXgtdWFhLnJ1bi5hd3MtdXN3MDItcHIuaWNlLnByZWRpeC5pby9vYXV0aC90b2tlbiIsInppZCI6Ijg5MDQwN2Q3LWU2MTctNGQ3MC05ODVmLTAxNzkyZDY5MzM4NyIsImF1ZCI6WyJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBVQkxJQy1TQUZFVFkuSUUtUFVCTElDLVNBRkVUWS5GUkVFIiwidWFhIiwic2NoLmhhY2thdGhvbiIsImllLWN1cnJlbnQuU2NoZW5lY3RhZHktSUUtUEVERVNUUklBTi5JRS1QRURFU1RSSUFOLkZSRUUiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLUVOVklST05NRU5UQUwuSUUtRU5WSVJPTk1FTlRBTC5GUkVFIiwiaWUtY3VycmVudC5TY2hlbmVjdGFkeS1JRS1QQVJLSU5HLklFLVBBUktJTkcuRlJFRSIsImllLWN1cnJlbnQuU2NoZW5lY3RhZHktSUUtVFJBRkZJQy5JRS1UUkFGRklDLkZSRUUiXX0.eAWv2tHgurYasQrrSu3cRhCEtqzlwgLsmmUak6OS1fKpsj2vJNZ7hFAt7-1_AteCNwZAkSMiKJ7v8p0AQvIIotFgQ_UZd9o5xRT5pfYxvs9prMxO7GbC3xeSA_FetaIdeckYQ7PZaiFqQAtzp69z-94jrkVSD_y4BVqyaYvUOR9tLC4iQBrCfShtYltzA1nI-_ouT62KlD5r0Cq9L8e1pB3Er4EhAlX42m8An1usWCOG7coXq0FAUb7ZtEqQVny-OPpaIcd_3N0ZDObLqn7q5kjoET-dhK52EhQkZwY7u2-jtgCnWbsoew1hjp0CTfFjB3Bs-j-3v_r33sIAwQymfQ",
            'Predix-Zone-Id': "Schenectady-IE-TRAFFIC",
            'Cache-Control': "no-cache",
            'Postman-Token': "daa5222a-387a-6118-650f-a46f01ac41da"
        }
        
        response = requests.request("GET", url, headers=headers, params=querystring)
        print(response.text)
        return response.text

    

    def get_all_assets_default(self):
        metadata_url = lookup_value(self.json_dict, 'metadataurl')
        #https://ic-metadata-service.run.aws-usw02-pr.ice.predix.io/v2/metadata
        url = "https://ic-metadata-service.run.aws-usw02-pr.ice.predix.io/v2/metadata/assets/search"

        querystring = {"bbox":"32.715675:-117.161230,32.708498:-117.151681","page":"0","size":"200","q":"assetType:CAMERA"}
        
        headers = {
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiJkZjgxYzEzZDBkODU0ZDhlYWJkMzEyZDQ1MjhhYTlhMCIsInN1YiI6ImhhY2thdGhvbiIsInNjb3BlIjpbInVhYS5yZXNvdXJjZSIsImllLWN1cnJlbnQuU0RTSU0tSUUtUFVCTElDLVNBRkVUWS5JRS1QVUJMSUMtU0FGRVRZLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtRU5WSVJPTk1FTlRBTC5JRS1FTlZJUk9OTUVOVEFMLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtVFJBRkZJQy5JRS1UUkFGRklDLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtUEFSS0lORy5JRS1QQVJLSU5HLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtUEVERVNUUklBTi5JRS1QRURFU1RSSUFOLkxJTUlURUQuREVWRUxPUCJdLCJjbGllbnRfaWQiOiJoYWNrYXRob24iLCJjaWQiOiJoYWNrYXRob24iLCJhenAiOiJoYWNrYXRob24iLCJncmFudF90eXBlIjoiY2xpZW50X2NyZWRlbnRpYWxzIiwicmV2X3NpZyI6IjlmMWYyYzRkIiwiaWF0IjoxNTE4Mjk3NDQxLCJleHAiOjE1MTg5MDIyNDEsImlzcyI6Imh0dHBzOi8vODkwNDA3ZDctZTYxNy00ZDcwLTk4NWYtMDE3OTJkNjkzMzg3LnByZWRpeC11YWEucnVuLmF3cy11c3cwMi1wci5pY2UucHJlZGl4LmlvL29hdXRoL3Rva2VuIiwiemlkIjoiODkwNDA3ZDctZTYxNy00ZDcwLTk4NWYtMDE3OTJkNjkzMzg3IiwiYXVkIjpbImllLWN1cnJlbnQuU0RTSU0tSUUtVFJBRkZJQy5JRS1UUkFGRklDLkxJTUlURUQiLCJpZS1jdXJyZW50LlNEU0lNLUlFLVBBUktJTkcuSUUtUEFSS0lORy5MSU1JVEVEIiwiaWUtY3VycmVudC5TRFNJTS1JRS1QVUJMSUMtU0FGRVRZLklFLVBVQkxJQy1TQUZFVFkuTElNSVRFRCIsInVhYSIsImhhY2thdGhvbiIsImllLWN1cnJlbnQuU0RTSU0tSUUtRU5WSVJPTk1FTlRBTC5JRS1FTlZJUk9OTUVOVEFMLkxJTUlURUQiLCJpZS1jdXJyZW50LlNEU0lNLUlFLVBFREVTVFJJQU4uSUUtUEVERVNUUklBTi5MSU1JVEVEIl19.uzcmD7_iVGHKbmgivWJJ1c4HBAEQZmxT_HvGp02yqiBrHuJNgpTrxYhuRG96tuYEgfb31_jbaGwcDY2xqseyLw-1k-P6D_VTNgdh8ZX0Y2GxzE_TCnzpAvpW-Hx7yoVEofj2glP23Rc_OTBNgT68MSATKCAxQaww-KImM4BQmEh-2ErfBuPzG7tpnRiv5fTJ-D4VslwWCYm4YGSzu9HAaNftQtaX9XKRQtyWpxevg-Fww1PKo0HFG-xytulrcT8ldII4xp05TFVN5n6AalkI1BVyZBK590Xuz4r7GOTiFkfNL2zVzY-YmWCuWbTQDoxQXtbBurSU8PArNL1_VYUPig",
            'Predix-Zone-Id': "SDSIM-IE-TRAFFIC",
            'Cache-Control': "no-cache",
            'Postman-Token': "507f4dde-1864-343f-f125-bf7ef603576d"
            }
        
        response = requests.request("GET", url, headers=headers, params=querystring)
        
        print(response.text)

    def get_all_assets_all_pages(self):
        all_pages_dict_list = []
        current_page = 0
        page_str = self.get_all_assets(current_page)
        page_dict = json.loads(page_str)
        all_pages_dict_list.append(page_dict)
        while not page_dict['last'] :
            current_page += 1
            page_str = self.get_all_assets(current_page)
            page_dict = json.loads(page_str)
            all_pages_dict_list.append(page_dict)
        #print(all_pages_dict_list)
        return all_pages_dict_list
        
        
    def get_all_assets(self, page_num):
        url = "https://ic-metadata-service-sch.run.aws-usw02-pr.ice.predix.io/v2/metadata/assets/search"

        #querystring = {"bbox":"42.829939:-73.979727,42.791626:-73.892380","page":"0","size":"200","q":"assetType:CAMERA"}
        querystring = {"bbox":"42.829939:-73.979727,42.791626:-73.892380","page":str(page_num),"size":"200","q":"assetType:CAMERA"}
        headers = {
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiIyMDk1NTAzOGRkODQ0ZTc4OGUwZTUwM2ZjNTcxZTAzMSIsInN1YiI6InNjaC5oYWNrYXRob24iLCJzY29wZSI6WyJ1YWEucmVzb3VyY2UiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBFREVTVFJJQU4uSUUtUEVERVNUUklBTi5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBBUktJTkcuSUUtUEFSS0lORy5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBVQkxJQy1TQUZFVFkuSUUtUFVCTElDLVNBRkVUWS5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVRSQUZGSUMuSUUtVFJBRkZJQy5GUkVFLkRFVkVMT1AiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLUVOVklST05NRU5UQUwuSUUtRU5WSVJPTk1FTlRBTC5GUkVFLkRFVkVMT1AiXSwiY2xpZW50X2lkIjoic2NoLmhhY2thdGhvbiIsImNpZCI6InNjaC5oYWNrYXRob24iLCJhenAiOiJzY2guaGFja2F0aG9uIiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiI4YTZkMzIwNyIsImlhdCI6MTUxODMxNTQ5MSwiZXhwIjoxNTE4OTIwMjkxLCJpc3MiOiJodHRwczovLzg5MDQwN2Q3LWU2MTctNGQ3MC05ODVmLTAxNzkyZDY5MzM4Ny5wcmVkaXgtdWFhLnJ1bi5hd3MtdXN3MDItcHIuaWNlLnByZWRpeC5pby9vYXV0aC90b2tlbiIsInppZCI6Ijg5MDQwN2Q3LWU2MTctNGQ3MC05ODVmLTAxNzkyZDY5MzM4NyIsImF1ZCI6WyJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLVBVQkxJQy1TQUZFVFkuSUUtUFVCTElDLVNBRkVUWS5GUkVFIiwidWFhIiwic2NoLmhhY2thdGhvbiIsImllLWN1cnJlbnQuU2NoZW5lY3RhZHktSUUtUEVERVNUUklBTi5JRS1QRURFU1RSSUFOLkZSRUUiLCJpZS1jdXJyZW50LlNjaGVuZWN0YWR5LUlFLUVOVklST05NRU5UQUwuSUUtRU5WSVJPTk1FTlRBTC5GUkVFIiwiaWUtY3VycmVudC5TY2hlbmVjdGFkeS1JRS1QQVJLSU5HLklFLVBBUktJTkcuRlJFRSIsImllLWN1cnJlbnQuU2NoZW5lY3RhZHktSUUtVFJBRkZJQy5JRS1UUkFGRklDLkZSRUUiXX0.eAWv2tHgurYasQrrSu3cRhCEtqzlwgLsmmUak6OS1fKpsj2vJNZ7hFAt7-1_AteCNwZAkSMiKJ7v8p0AQvIIotFgQ_UZd9o5xRT5pfYxvs9prMxO7GbC3xeSA_FetaIdeckYQ7PZaiFqQAtzp69z-94jrkVSD_y4BVqyaYvUOR9tLC4iQBrCfShtYltzA1nI-_ouT62KlD5r0Cq9L8e1pB3Er4EhAlX42m8An1usWCOG7coXq0FAUb7ZtEqQVny-OPpaIcd_3N0ZDObLqn7q5kjoET-dhK52EhQkZwY7u2-jtgCnWbsoew1hjp0CTfFjB3Bs-j-3v_r33sIAwQymfQ",
            'Predix-Zone-Id': "Schenectady-IE-TRAFFIC",
            'Cache-Control': "no-cache",
            'Postman-Token': "3afa28b3-a1e1-c93f-a2c8-4364c1c65deb"
            }
        
        response = requests.request("GET", url, headers=headers, params=querystring)

        return response.text
    
    def get_all_assets_hackathon(self, page_num):
        metadata_url = lookup_value(self.json_dict, 'metadataurl')
        #https://ic-metadata-service.run.aws-usw02-pr.ice.predix.io/v2/metadata
        url = "https://ic-metadata-service.run.aws-usw02-pr.ice.predix.io/v2/metadata/assets/search"

        #querystring = {"bbox":"32.715675:-117.161230,32.708498:-117.151681","page":"0","size":"200","q":"assetType:CAMERA"}
        querystring = {"bbox":"32.715675:-117.161230,32.708498:-117.151681","page":str(page_num),"size":"200","q":"assetType:CAMERA"}
        #{"content":[{"assetUid":"CAM-HYP1017-L","parentAssetUid":"NODE-HYP1017","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714759:-117.157563"},{"assetUid":"CAM-HYP1030-L","parentAssetUid":"NODE-HYP1030","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712695:-117.157313"},{"assetUid":"CAM-HYP1039-L","parentAssetUid":"NODE-HYP1039","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712668:-117.157546"},{"assetUid":"CAM-HYP1040-L","parentAssetUid":"NODE-HYP1040","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711653:-117.157314"},{"assetUid":"CAM-HYP1041-L","parentAssetUid":"NODE-HYP1041","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712513:-117.157283"},{"assetUid":"CAM-HYP1047-L","parentAssetUid":"NODE-HYP1047","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711664:-117.156404"},{"assetUid":"CAM-HYP1050-L","parentAssetUid":"NODE-HYP1050","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711618:-117.157534"},{"assetUid":"CAM-HYP1052-L","parentAssetUid":"NODE-HYP1052","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712468:-117.157511"},{"assetUid":"CAM-HYP1061-L","parentAssetUid":"NODE-HYP1061","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713521:-117.159346"},{"assetUid":"CAM-HYP1063-L","parentAssetUid":"NODE-HYP1063","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714806:-117.156426"},{"assetUid":"CAM-HYP1066-L","parentAssetUid":"NODE-HYP1066","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714774:-117.158245"},{"assetUid":"CAM-HYP1068-L","parentAssetUid":"NODE-HYP1068","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713521:-117.158423"},{"assetUid":"CAM-HYP1070-L","parentAssetUid":"NODE-HYP1070","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713534:-117.157517"},{"assetUid":"CAM-HYP1071-L","parentAssetUid":"NODE-HYP1071","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.156634"},{"assetUid":"CAM-HYP1072-L","parentAssetUid":"NODE-HYP1072","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71459:-117.158204"},{"assetUid":"CAM-HYP1073-L","parentAssetUid":"NODE-HYP1073","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.157547"},{"assetUid":"CAM-HYP1083-R","parentAssetUid":"NODE-HYP1083","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713557:-117.157961"},{"assetUid":"CAM-HYP1065-R","parentAssetUid":"NODE-HYP1065","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713549:-117.159114"},{"assetUid":"CAM-HYP1062-R","parentAssetUid":"NODE-HYP1062","eventTypes":[],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713552:-117.15846"},{"assetUid":"CAM-HYP1042-L","parentAssetUid":"NODE-HYP1042","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711628:-117.156618"},{"assetUid":"CAM-HYP1037-L","parentAssetUid":"NODE-HYP1037","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711421:-117.157264"},{"assetUid":"CAM-HYP1081-L","parentAssetUid":"NODE-HYP1081","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711617:-117.158441"},{"assetUid":"CAM-HYP1077-L","parentAssetUid":"NODE-HYP1077","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.715611:-117.157534"},{"assetUid":"CAM-HYP1074-L","parentAssetUid":"NODE-HYP1074","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714797:-117.157343"},{"assetUid":"CAM-HYP1064-L","parentAssetUid":"NODE-HYP1064","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713763:-117.156411"},{"assetUid":"CAM-HYP1018-L","parentAssetUid":"NODE-HYP1018","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713735:-117.158238"},{"assetUid":"CAM-HYP1065-L","parentAssetUid":"NODE-HYP1065","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713549:-117.159114"},{"assetUid":"CAM-HYP1046-L","parentAssetUid":"NODE-HYP1046","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712471:-117.158423"},{"assetUid":"CAM-HYP1082-L","parentAssetUid":"NODE-HYP1082","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712672:-117.156635"},{"assetUid":"CAM-HYP1047-R","parentAssetUid":"NODE-HYP1047","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711664:-117.156404"},{"assetUid":"CAM-HYP1071-F","parentAssetUid":"NODE-HYP1071","eventTypes":["TFEVT","PKOUT","PEDEVT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.156634"},{"assetUid":"CAM-HYP1077-R","parentAssetUid":"NODE-HYP1077","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.715611:-117.157534"},{"assetUid":"CAM-HYP1043-F","parentAssetUid":"NODE-HYP1043","eventTypes":["PKIN","TFEVT","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712513:-117.158008"},{"assetUid":"CAM-HYP1065-F","parentAssetUid":"NODE-HYP1065","eventTypes":["PKOUT","PEDEVT","PKIN","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713549:-117.159114"},{"assetUid":"CAM-HYP1068-F","parentAssetUid":"NODE-HYP1068","eventTypes":["TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713521:-117.158423"},{"assetUid":"CAM-HYP1073-F","parentAssetUid":"NODE-HYP1073","eventTypes":["PEDEVT","TFEVT","PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.157547"},{"assetUid":"CAM-HYP1078-L","parentAssetUid":"NODE-HYP1078","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712507:-117.157666"},{"assetUid":"CAM-HYP1062-F","parentAssetUid":"NODE-HYP1062","eventTypes":["PKIN","PKOUT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713552:-117.15846"},{"assetUid":"CAM-HYP1037-R","parentAssetUid":"NODE-HYP1037","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711421:-117.157264"},{"assetUid":"CAM-HYP1024-F","parentAssetUid":"NODE-HYP1024","eventTypes":["PKOUT","PKIN","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713715:-117.157158"},{"assetUid":"CAM-HYP1081-F","parentAssetUid":"NODE-HYP1081","eventTypes":["PKIN","PEDEVT","TFEVT","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711617:-117.158441"},{"assetUid":"CAM-HYP1061-F","parentAssetUid":"NODE-HYP1061","eventTypes":["PKIN","PKOUT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713521:-117.159346"},{"assetUid":"CAM-HYP1070-R","parentAssetUid":"NODE-HYP1070","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713534:-117.157517"},{"assetUid":"CAM-HYP1052-R","parentAssetUid":"NODE-HYP1052","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712468:-117.157511"},{"assetUid":"CAM-HYP1029-L","parentAssetUid":"NODE-HYP1029","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71355:-117.158815"},{"assetUid":"CAM-HYP1042-F","parentAssetUid":"NODE-HYP1042","eventTypes":["PKIN","PKOUT","PEDEVT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711628:-117.156618"},{"assetUid":"CAM-HYP1032-F","parentAssetUid":"NODE-HYP1032","eventTypes":["PKOUT","PKIN","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71162:-117.156866"},{"assetUid":"CAM-HYP1030-R","parentAssetUid":"NODE-HYP1030","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712695:-117.157313"},{"assetUid":"CAM-HYP1077-F","parentAssetUid":"NODE-HYP1077","eventTypes":["PKIN","TFEVT","PEDEVT","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.715611:-117.157534"},{"assetUid":"CAM-HYP1039-F","parentAssetUid":"NODE-HYP1039","eventTypes":["PEDEVT","TFEVT","PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712668:-117.157546"},{"assetUid":"CAM-HYP1018-R","parentAssetUid":"NODE-HYP1018","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713735:-117.158238"},{"assetUid":"CAM-HYP1082-R","parentAssetUid":"NODE-HYP1082","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712672:-117.156635"},{"assetUid":"CAM-HYP1033-F","parentAssetUid":"NODE-HYP1033","eventTypes":["TFEVT","PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71162:-117.157972"},{"assetUid":"CAM-HYP1029-R","parentAssetUid":"NODE-HYP1029","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71355:-117.158815"},{"assetUid":"CAM-HYP1042-R","parentAssetUid":"NODE-HYP1042","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711628:-117.156618"},{"assetUid":"CAM-HYP1074-R","parentAssetUid":"NODE-HYP1074","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714797:-117.157343"},{"assetUid":"CAM-HYP1073-R","parentAssetUid":"NODE-HYP1073","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.157547"},{"assetUid":"CAM-HYP1040-F","parentAssetUid":"NODE-HYP1040","eventTypes":["PKOUT","TFEVT","PKIN","PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711653:-117.157314"},{"assetUid":"CAM-HYP1066-F","parentAssetUid":"NODE-HYP1066","eventTypes":["TFEVT","PKIN","PEDEVT","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714774:-117.158245"},{"assetUid":"CAM-HYP1032-L","parentAssetUid":"NODE-HYP1032","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71162:-117.156866"},{"assetUid":"CAM-HYP1037-F","parentAssetUid":"NODE-HYP1037","eventTypes":["PKIN","PKOUT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711421:-117.157264"},{"assetUid":"CAM-HYP1029-F","parentAssetUid":"NODE-HYP1029","eventTypes":["TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71355:-117.158815"},{"assetUid":"CAM-HYP1078-R","parentAssetUid":"NODE-HYP1078","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712507:-117.157666"},{"assetUid":"CAM-HYP1072-F","parentAssetUid":"NODE-HYP1072","eventTypes":["TFEVT","PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71459:-117.158204"},{"assetUid":"CAM-HYP1018-F","parentAssetUid":"NODE-HYP1018","eventTypes":["PEDEVT","PKOUT","PKIN","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713735:-117.158238"},{"assetUid":"CAM-HYP1063-F","parentAssetUid":"NODE-HYP1063","eventTypes":["PEDEVT","TFEVT","PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714806:-117.156426"},{"assetUid":"CAM-HYP1072-R","parentAssetUid":"NODE-HYP1072","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71459:-117.158204"},{"assetUid":"CAM-HYP1064-R","parentAssetUid":"NODE-HYP1064","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713763:-117.156411"},{"assetUid":"CAM-HYP1028-F","parentAssetUid":"NODE-HYP1028","eventTypes":["TFEVT","PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713559:-117.15765"},{"assetUid":"CAM-HYP1078-F","parentAssetUid":"NODE-HYP1078","eventTypes":["TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712507:-117.157666"},{"assetUid":"CAM-HYP1061-R","parentAssetUid":"NODE-HYP1061","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713521:-117.159346"},{"assetUid":"CAM-HYP1023-R","parentAssetUid":"NODE-HYP1023","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711615:-117.157765"},{"assetUid":"CAM-HYP1033-R","parentAssetUid":"NODE-HYP1033","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71162:-117.157972"},{"assetUid":"CAM-HYP1041-F","parentAssetUid":"NODE-HYP1041","eventTypes":["PKOUT","PEDEVT","TFEVT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712513:-117.157283"},{"assetUid":"CAM-HYP1050-R","parentAssetUid":"NODE-HYP1050","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711618:-117.157534"},{"assetUid":"CAM-HYP1008-R","parentAssetUid":"NODE-HYP1008","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.156876"},{"assetUid":"CAM-HYP1022-L","parentAssetUid":"NODE-HYP1022","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712502:-117.158897"},{"assetUid":"CAM-HYP1081-R","parentAssetUid":"NODE-HYP1081","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711617:-117.158441"},{"assetUid":"CAM-HYP1008-L","parentAssetUid":"NODE-HYP1008","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.156876"},{"assetUid":"CAM-HYP1026-L","parentAssetUid":"NODE-HYP1026","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711426:-117.156802"},{"assetUid":"CAM-HYP1028-L","parentAssetUid":"NODE-HYP1028","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713559:-117.15765"},{"assetUid":"CAM-HYP1068-R","parentAssetUid":"NODE-HYP1068","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713521:-117.158423"},{"assetUid":"CAM-HYP1039-R","parentAssetUid":"NODE-HYP1039","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712668:-117.157546"},{"assetUid":"CAM-HYP1021-R","parentAssetUid":"NODE-HYP1021","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713562:-117.156732"},{"assetUid":"CAM-HYP1040-R","parentAssetUid":"NODE-HYP1040","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711653:-117.157314"},{"assetUid":"CAM-HYP1034-L","parentAssetUid":"NODE-HYP1034","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711424:-117.157012"},{"assetUid":"CAM-HYP1046-R","parentAssetUid":"NODE-HYP1046","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712471:-117.158423"},{"assetUid":"CAM-HYP1050-F","parentAssetUid":"NODE-HYP1050","eventTypes":["PKIN","PKOUT","PEDEVT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711618:-117.157534"},{"assetUid":"CAM-HYP1026-R","parentAssetUid":"NODE-HYP1026","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711426:-117.156802"},{"assetUid":"CAM-HYP1023-L","parentAssetUid":"NODE-HYP1023","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711615:-117.157765"},{"assetUid":"CAM-HYP1064-F","parentAssetUid":"NODE-HYP1064","eventTypes":["PKIN","TFEVT","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713763:-117.156411"},{"assetUid":"CAM-HYP1024-R","parentAssetUid":"NODE-HYP1024","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713715:-117.157158"},{"assetUid":"CAM-HYP1079-F","parentAssetUid":"NODE-HYP1079","eventTypes":["TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713561:-117.156982"},{"assetUid":"CAM-HYP1034-F","parentAssetUid":"NODE-HYP1034","eventTypes":["PKOUT","PKIN","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711424:-117.157012"},{"assetUid":"CAM-HYP1043-R","parentAssetUid":"NODE-HYP1043","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712513:-117.158008"},{"assetUid":"CAM-HYP1062-L","parentAssetUid":"NODE-HYP1062","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713552:-117.15846"},{"assetUid":"CAM-HYP1022-F","parentAssetUid":"NODE-HYP1022","eventTypes":["PKIN","PKOUT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712502:-117.158897"},{"assetUid":"CAM-HYP1017-F","parentAssetUid":"NODE-HYP1017","eventTypes":["PKOUT","PKIN","PEDEVT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714759:-117.157563"},{"assetUid":"CAM-HYP1074-F","parentAssetUid":"NODE-HYP1074","eventTypes":["PKIN","PKOUT","PEDEVT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714797:-117.157343"},{"assetUid":"CAM-HYP1083-F","parentAssetUid":"NODE-HYP1083","eventTypes":["TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713557:-117.157961"},{"assetUid":"CAM-HYP1023-F","parentAssetUid":"NODE-HYP1023","eventTypes":["TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711615:-117.157765"},{"assetUid":"CAM-HYP1047-F","parentAssetUid":"NODE-HYP1047","eventTypes":["PEDEVT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711664:-117.156404"},{"assetUid":"CAM-HYP1034-R","parentAssetUid":"NODE-HYP1034","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711424:-117.157012"},{"assetUid":"CAM-HYP1024-L","parentAssetUid":"NODE-HYP1024","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713715:-117.157158"},{"assetUid":"CAM-HYP1022-R","parentAssetUid":"NODE-HYP1022","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712502:-117.158897"},{"assetUid":"CAM-HYP1063-R","parentAssetUid":"NODE-HYP1063","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714806:-117.156426"},{"assetUid":"CAM-HYP1043-L","parentAssetUid":"NODE-HYP1043","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712513:-117.158008"},{"assetUid":"CAM-HYP1021-L","parentAssetUid":"NODE-HYP1021","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713562:-117.156732"},{"assetUid":"CAM-HYP1054-F","parentAssetUid":"NODE-HYP1054","eventTypes":["PKIN","TFEVT","PKOUT","PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712514:-117.158185"},{"assetUid":"CAM-HYP1033-L","parentAssetUid":"NODE-HYP1033","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71162:-117.157972"},{"assetUid":"CAM-HYP1066-R","parentAssetUid":"NODE-HYP1066","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714774:-117.158245"},{"assetUid":"CAM-HYP1070-F","parentAssetUid":"NODE-HYP1070","eventTypes":["PKIN","PKOUT","TFEVT","PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713534:-117.157517"},{"assetUid":"CAM-HYP1046-F","parentAssetUid":"NODE-HYP1046","eventTypes":["PKIN","PKOUT","PEDEVT","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712471:-117.158423"},{"assetUid":"CAM-HYP1041-R","parentAssetUid":"NODE-HYP1041","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712513:-117.157283"},{"assetUid":"CAM-HYP1017-R","parentAssetUid":"NODE-HYP1017","eventTypes":["PKOUT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.714759:-117.157563"},{"assetUid":"CAM-HYP1082-F","parentAssetUid":"NODE-HYP1082","eventTypes":["PKOUT","PEDEVT","TFEVT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712672:-117.156635"},{"assetUid":"CAM-HYP1030-F","parentAssetUid":"NODE-HYP1030","eventTypes":["PKOUT","PEDEVT","TFEVT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712695:-117.157313"},{"assetUid":"CAM-HYP1026-F","parentAssetUid":"NODE-HYP1026","eventTypes":["PKIN","TFEVT","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.711426:-117.156802"},{"assetUid":"CAM-HYP1052-F","parentAssetUid":"NODE-HYP1052","eventTypes":["PKIN","PKOUT","TFEVT","PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.712468:-117.157511"},{"assetUid":"CAM-HYP1008-F","parentAssetUid":"NODE-HYP1008","eventTypes":["PKOUT","PKIN","TFEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.156876"},{"assetUid":"CAM-HYP1032-R","parentAssetUid":"NODE-HYP1032","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71162:-117.156866"},{"assetUid":"CAM-HYP1071-R","parentAssetUid":"NODE-HYP1071","eventTypes":["PKIN","PKOUT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.71372:-117.156634"},{"assetUid":"CAM-HYP1021-F","parentAssetUid":"NODE-HYP1021","eventTypes":["PKOUT","TFEVT","PKIN"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.713562:-117.156732"}],"last":true,"totalPages":1,"totalElements":123,"sort":null,"first":true,"numberOfElements":123,"size":2000,"number":0}

        headers = {
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiJkZjgxYzEzZDBkODU0ZDhlYWJkMzEyZDQ1MjhhYTlhMCIsInN1YiI6ImhhY2thdGhvbiIsInNjb3BlIjpbInVhYS5yZXNvdXJjZSIsImllLWN1cnJlbnQuU0RTSU0tSUUtUFVCTElDLVNBRkVUWS5JRS1QVUJMSUMtU0FGRVRZLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtRU5WSVJPTk1FTlRBTC5JRS1FTlZJUk9OTUVOVEFMLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtVFJBRkZJQy5JRS1UUkFGRklDLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtUEFSS0lORy5JRS1QQVJLSU5HLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtUEVERVNUUklBTi5JRS1QRURFU1RSSUFOLkxJTUlURUQuREVWRUxPUCJdLCJjbGllbnRfaWQiOiJoYWNrYXRob24iLCJjaWQiOiJoYWNrYXRob24iLCJhenAiOiJoYWNrYXRob24iLCJncmFudF90eXBlIjoiY2xpZW50X2NyZWRlbnRpYWxzIiwicmV2X3NpZyI6IjlmMWYyYzRkIiwiaWF0IjoxNTE4Mjk3NDQxLCJleHAiOjE1MTg5MDIyNDEsImlzcyI6Imh0dHBzOi8vODkwNDA3ZDctZTYxNy00ZDcwLTk4NWYtMDE3OTJkNjkzMzg3LnByZWRpeC11YWEucnVuLmF3cy11c3cwMi1wci5pY2UucHJlZGl4LmlvL29hdXRoL3Rva2VuIiwiemlkIjoiODkwNDA3ZDctZTYxNy00ZDcwLTk4NWYtMDE3OTJkNjkzMzg3IiwiYXVkIjpbImllLWN1cnJlbnQuU0RTSU0tSUUtVFJBRkZJQy5JRS1UUkFGRklDLkxJTUlURUQiLCJpZS1jdXJyZW50LlNEU0lNLUlFLVBBUktJTkcuSUUtUEFSS0lORy5MSU1JVEVEIiwiaWUtY3VycmVudC5TRFNJTS1JRS1QVUJMSUMtU0FGRVRZLklFLVBVQkxJQy1TQUZFVFkuTElNSVRFRCIsInVhYSIsImhhY2thdGhvbiIsImllLWN1cnJlbnQuU0RTSU0tSUUtRU5WSVJPTk1FTlRBTC5JRS1FTlZJUk9OTUVOVEFMLkxJTUlURUQiLCJpZS1jdXJyZW50LlNEU0lNLUlFLVBFREVTVFJJQU4uSUUtUEVERVNUUklBTi5MSU1JVEVEIl19.uzcmD7_iVGHKbmgivWJJ1c4HBAEQZmxT_HvGp02yqiBrHuJNgpTrxYhuRG96tuYEgfb31_jbaGwcDY2xqseyLw-1k-P6D_VTNgdh8ZX0Y2GxzE_TCnzpAvpW-Hx7yoVEofj2glP23Rc_OTBNgT68MSATKCAxQaww-KImM4BQmEh-2ErfBuPzG7tpnRiv5fTJ-D4VslwWCYm4YGSzu9HAaNftQtaX9XKRQtyWpxevg-Fww1PKo0HFG-xytulrcT8ldII4xp05TFVN5n6AalkI1BVyZBK590Xuz4r7GOTiFkfNL2zVzY-YmWCuWbTQDoxQXtbBurSU8PArNL1_VYUPig",
            'Predix-Zone-Id': "SDSIM-IE-TRAFFIC",
            'Cache-Control': "no-cache",
            'Postman-Token': "507f4dde-1864-343f-f125-bf7ef603576d"
            }
        
        response = requests.request("GET", url, headers=headers, params=querystring)
        
        return response.text

    def filter_assets_data(self, all_pages_dict_list, filter_by='TFEVT'):
        #[{u'sort': None, u'last': True, u'size': 200, u'number': 0, u'content': [{u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714759:-117.157563', u'parentAssetUid': u'NODE-HYP1017', u'eventTypes': [], u'assetUid': u'CAM-HYP1017-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712695:-117.157313', u'parentAssetUid': u'NODE-HYP1030', u'eventTypes': [], u'assetUid': u'CAM-HYP1030-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712668:-117.157546', u'parentAssetUid': u'NODE-HYP1039', u'eventTypes': [], u'assetUid': u'CAM-HYP1039-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711653:-117.157314', u'parentAssetUid': u'NODE-HYP1040', u'eventTypes': [], u'assetUid': u'CAM-HYP1040-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712513:-117.157283', u'parentAssetUid': u'NODE-HYP1041', u'eventTypes': [], u'assetUid': u'CAM-HYP1041-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711664:-117.156404', u'parentAssetUid': u'NODE-HYP1047', u'eventTypes': [], u'assetUid': u'CAM-HYP1047-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711618:-117.157534', u'parentAssetUid': u'NODE-HYP1050', u'eventTypes': [], u'assetUid': u'CAM-HYP1050-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712468:-117.157511', u'parentAssetUid': u'NODE-HYP1052', u'eventTypes': [], u'assetUid': u'CAM-HYP1052-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713521:-117.159346', u'parentAssetUid': u'NODE-HYP1061', u'eventTypes': [], u'assetUid': u'CAM-HYP1061-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714806:-117.156426', u'parentAssetUid': u'NODE-HYP1063', u'eventTypes': [], u'assetUid': u'CAM-HYP1063-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714774:-117.158245', u'parentAssetUid': u'NODE-HYP1066', u'eventTypes': [], u'assetUid': u'CAM-HYP1066-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713521:-117.158423', u'parentAssetUid': u'NODE-HYP1068', u'eventTypes': [], u'assetUid': u'CAM-HYP1068-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713534:-117.157517', u'parentAssetUid': u'NODE-HYP1070', u'eventTypes': [], u'assetUid': u'CAM-HYP1070-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.156634', u'parentAssetUid': u'NODE-HYP1071', u'eventTypes': [], u'assetUid': u'CAM-HYP1071-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71459:-117.158204', u'parentAssetUid': u'NODE-HYP1072', u'eventTypes': [], u'assetUid': u'CAM-HYP1072-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.157547', u'parentAssetUid': u'NODE-HYP1073', u'eventTypes': [], u'assetUid': u'CAM-HYP1073-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713557:-117.157961', u'parentAssetUid': u'NODE-HYP1083', u'eventTypes': [], u'assetUid': u'CAM-HYP1083-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713549:-117.159114', u'parentAssetUid': u'NODE-HYP1065', u'eventTypes': [], u'assetUid': u'CAM-HYP1065-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713552:-117.15846', u'parentAssetUid': u'NODE-HYP1062', u'eventTypes': [], u'assetUid': u'CAM-HYP1062-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711628:-117.156618', u'parentAssetUid': u'NODE-HYP1042', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1042-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711421:-117.157264', u'parentAssetUid': u'NODE-HYP1037', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1037-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711617:-117.158441', u'parentAssetUid': u'NODE-HYP1081', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1081-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.715611:-117.157534', u'parentAssetUid': u'NODE-HYP1077', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1077-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714797:-117.157343', u'parentAssetUid': u'NODE-HYP1074', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1074-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713763:-117.156411', u'parentAssetUid': u'NODE-HYP1064', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1064-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713735:-117.158238', u'parentAssetUid': u'NODE-HYP1018', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1018-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713549:-117.159114', u'parentAssetUid': u'NODE-HYP1065', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1065-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712471:-117.158423', u'parentAssetUid': u'NODE-HYP1046', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1046-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712672:-117.156635', u'parentAssetUid': u'NODE-HYP1082', u'eventTypes': [u'PEDEVT'], u'assetUid': u'CAM-HYP1082-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711664:-117.156404', u'parentAssetUid': u'NODE-HYP1047', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1047-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.156634', u'parentAssetUid': u'NODE-HYP1071', u'eventTypes': [u'PEDEVT', u'TFEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1071-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.715611:-117.157534', u'parentAssetUid': u'NODE-HYP1077', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1077-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712513:-117.158008', u'parentAssetUid': u'NODE-HYP1043', u'eventTypes': [u'TFEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1043-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713549:-117.159114', u'parentAssetUid': u'NODE-HYP1065', u'eventTypes': [u'PKIN', u'TFEVT', u'PEDEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1065-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713521:-117.158423', u'parentAssetUid': u'NODE-HYP1068', u'eventTypes': [u'TFEVT'], u'assetUid': u'CAM-HYP1068-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.157547', u'parentAssetUid': u'NODE-HYP1073', u'eventTypes': [u'TFEVT', u'PKIN', u'PEDEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1073-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712507:-117.157666', u'parentAssetUid': u'NODE-HYP1078', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1078-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713552:-117.15846', u'parentAssetUid': u'NODE-HYP1062', u'eventTypes': [u'TFEVT', u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1062-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711421:-117.157264', u'parentAssetUid': u'NODE-HYP1037', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1037-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713715:-117.157158', u'parentAssetUid': u'NODE-HYP1024', u'eventTypes': [u'PKOUT', u'PKIN', u'TFEVT'], u'assetUid': u'CAM-HYP1024-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711617:-117.158441', u'parentAssetUid': u'NODE-HYP1081', u'eventTypes': [u'TFEVT', u'PKIN', u'PKOUT', u'PEDEVT'], u'assetUid': u'CAM-HYP1081-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713521:-117.159346', u'parentAssetUid': u'NODE-HYP1061', u'eventTypes': [u'TFEVT', u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1061-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713534:-117.157517', u'parentAssetUid': u'NODE-HYP1070', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1070-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712468:-117.157511', u'parentAssetUid': u'NODE-HYP1052', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1052-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71355:-117.158815', u'parentAssetUid': u'NODE-HYP1029', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1029-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711628:-117.156618', u'parentAssetUid': u'NODE-HYP1042', u'eventTypes': [u'PEDEVT', u'TFEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1042-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71162:-117.156866', u'parentAssetUid': u'NODE-HYP1032', u'eventTypes': [u'PKOUT', u'TFEVT', u'PKIN'], u'assetUid': u'CAM-HYP1032-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712695:-117.157313', u'parentAssetUid': u'NODE-HYP1030', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1030-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.715611:-117.157534', u'parentAssetUid': u'NODE-HYP1077', u'eventTypes': [u'PKIN', u'PEDEVT', u'TFEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1077-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712668:-117.157546', u'parentAssetUid': u'NODE-HYP1039', u'eventTypes': [u'PEDEVT', u'TFEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1039-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713735:-117.158238', u'parentAssetUid': u'NODE-HYP1018', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1018-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712672:-117.156635', u'parentAssetUid': u'NODE-HYP1082', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1082-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71162:-117.157972', u'parentAssetUid': u'NODE-HYP1033', u'eventTypes': [u'PKIN', u'TFEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1033-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71355:-117.158815', u'parentAssetUid': u'NODE-HYP1029', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1029-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711628:-117.156618', u'parentAssetUid': u'NODE-HYP1042', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1042-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714797:-117.157343', u'parentAssetUid': u'NODE-HYP1074', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1074-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.157547', u'parentAssetUid': u'NODE-HYP1073', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1073-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711653:-117.157314', u'parentAssetUid': u'NODE-HYP1040', u'eventTypes': [u'PKOUT', u'PKIN', u'PEDEVT', u'TFEVT'], u'assetUid': u'CAM-HYP1040-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714774:-117.158245', u'parentAssetUid': u'NODE-HYP1066', u'eventTypes': [u'PKOUT', u'PKIN', u'PEDEVT', u'TFEVT'], u'assetUid': u'CAM-HYP1066-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71162:-117.156866', u'parentAssetUid': u'NODE-HYP1032', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1032-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711421:-117.157264', u'parentAssetUid': u'NODE-HYP1037', u'eventTypes': [u'PKIN', u'PKOUT', u'TFEVT'], u'assetUid': u'CAM-HYP1037-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71355:-117.158815', u'parentAssetUid': u'NODE-HYP1029', u'eventTypes': [u'TFEVT'], u'assetUid': u'CAM-HYP1029-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712507:-117.157666', u'parentAssetUid': u'NODE-HYP1078', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1078-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71459:-117.158204', u'parentAssetUid': u'NODE-HYP1072', u'eventTypes': [u'TFEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1072-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713735:-117.158238', u'parentAssetUid': u'NODE-HYP1018', u'eventTypes': [u'PKIN', u'TFEVT', u'PEDEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1018-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714806:-117.156426', u'parentAssetUid': u'NODE-HYP1063', u'eventTypes': [u'PEDEVT', u'PKOUT', u'TFEVT', u'PKIN'], u'assetUid': u'CAM-HYP1063-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71459:-117.158204', u'parentAssetUid': u'NODE-HYP1072', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1072-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713763:-117.156411', u'parentAssetUid': u'NODE-HYP1064', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1064-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713559:-117.15765', u'parentAssetUid': u'NODE-HYP1028', u'eventTypes': [u'TFEVT', u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1028-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712507:-117.157666', u'parentAssetUid': u'NODE-HYP1078', u'eventTypes': [u'TFEVT'], u'assetUid': u'CAM-HYP1078-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713521:-117.159346', u'parentAssetUid': u'NODE-HYP1061', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1061-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711615:-117.157765', u'parentAssetUid': u'NODE-HYP1023', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1023-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71162:-117.157972', u'parentAssetUid': u'NODE-HYP1033', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1033-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712513:-117.157283', u'parentAssetUid': u'NODE-HYP1041', u'eventTypes': [u'PKOUT', u'TFEVT', u'PEDEVT', u'PKIN'], u'assetUid': u'CAM-HYP1041-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711618:-117.157534', u'parentAssetUid': u'NODE-HYP1050', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1050-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.156876', u'parentAssetUid': u'NODE-HYP1008', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1008-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712502:-117.158897', u'parentAssetUid': u'NODE-HYP1022', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1022-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711617:-117.158441', u'parentAssetUid': u'NODE-HYP1081', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1081-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.156876', u'parentAssetUid': u'NODE-HYP1008', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1008-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711426:-117.156802', u'parentAssetUid': u'NODE-HYP1026', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1026-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713559:-117.15765', u'parentAssetUid': u'NODE-HYP1028', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1028-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713521:-117.158423', u'parentAssetUid': u'NODE-HYP1068', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1068-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712668:-117.157546', u'parentAssetUid': u'NODE-HYP1039', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1039-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713562:-117.156732', u'parentAssetUid': u'NODE-HYP1021', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1021-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711653:-117.157314', u'parentAssetUid': u'NODE-HYP1040', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1040-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711424:-117.157012', u'parentAssetUid': u'NODE-HYP1034', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1034-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712471:-117.158423', u'parentAssetUid': u'NODE-HYP1046', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1046-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711618:-117.157534', u'parentAssetUid': u'NODE-HYP1050', u'eventTypes': [u'TFEVT', u'PKIN', u'PKOUT', u'PEDEVT'], u'assetUid': u'CAM-HYP1050-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711426:-117.156802', u'parentAssetUid': u'NODE-HYP1026', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1026-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711615:-117.157765', u'parentAssetUid': u'NODE-HYP1023', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1023-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713763:-117.156411', u'parentAssetUid': u'NODE-HYP1064', u'eventTypes': [u'PKIN', u'TFEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1064-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713715:-117.157158', u'parentAssetUid': u'NODE-HYP1024', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1024-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713561:-117.156982', u'parentAssetUid': u'NODE-HYP1079', u'eventTypes': [u'TFEVT'], u'assetUid': u'CAM-HYP1079-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711424:-117.157012', u'parentAssetUid': u'NODE-HYP1034', u'eventTypes': [u'PKOUT', u'PKIN', u'TFEVT'], u'assetUid': u'CAM-HYP1034-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712513:-117.158008', u'parentAssetUid': u'NODE-HYP1043', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1043-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713552:-117.15846', u'parentAssetUid': u'NODE-HYP1062', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1062-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712502:-117.158897', u'parentAssetUid': u'NODE-HYP1022', u'eventTypes': [u'PKIN', u'TFEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1022-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714759:-117.157563', u'parentAssetUid': u'NODE-HYP1017', u'eventTypes': [u'PEDEVT', u'PKOUT', u'PKIN', u'TFEVT'], u'assetUid': u'CAM-HYP1017-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714797:-117.157343', u'parentAssetUid': u'NODE-HYP1074', u'eventTypes': [u'PEDEVT', u'PKOUT', u'TFEVT', u'PKIN'], u'assetUid': u'CAM-HYP1074-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713557:-117.157961', u'parentAssetUid': u'NODE-HYP1083', u'eventTypes': [u'TFEVT'], u'assetUid': u'CAM-HYP1083-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711615:-117.157765', u'parentAssetUid': u'NODE-HYP1023', u'eventTypes': [u'TFEVT'], u'assetUid': u'CAM-HYP1023-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711664:-117.156404', u'parentAssetUid': u'NODE-HYP1047', u'eventTypes': [u'PEDEVT', u'TFEVT'], u'assetUid': u'CAM-HYP1047-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711424:-117.157012', u'parentAssetUid': u'NODE-HYP1034', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1034-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713715:-117.157158', u'parentAssetUid': u'NODE-HYP1024', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1024-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712502:-117.158897', u'parentAssetUid': u'NODE-HYP1022', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1022-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714806:-117.156426', u'parentAssetUid': u'NODE-HYP1063', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1063-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712513:-117.158008', u'parentAssetUid': u'NODE-HYP1043', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1043-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713562:-117.156732', u'parentAssetUid': u'NODE-HYP1021', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1021-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712514:-117.158185', u'parentAssetUid': u'NODE-HYP1054', u'eventTypes': [u'PEDEVT', u'TFEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1054-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71162:-117.157972', u'parentAssetUid': u'NODE-HYP1033', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1033-L'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714774:-117.158245', u'parentAssetUid': u'NODE-HYP1066', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1066-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713534:-117.157517', u'parentAssetUid': u'NODE-HYP1070', u'eventTypes': [u'PKOUT', u'PEDEVT', u'TFEVT', u'PKIN'], u'assetUid': u'CAM-HYP1070-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712471:-117.158423', u'parentAssetUid': u'NODE-HYP1046', u'eventTypes': [u'PKIN', u'PEDEVT', u'TFEVT', u'PKOUT'], u'assetUid': u'CAM-HYP1046-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712513:-117.157283', u'parentAssetUid': u'NODE-HYP1041', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1041-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.714759:-117.157563', u'parentAssetUid': u'NODE-HYP1017', u'eventTypes': [u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1017-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712672:-117.156635', u'parentAssetUid': u'NODE-HYP1082', u'eventTypes': [u'TFEVT', u'PEDEVT', u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1082-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712695:-117.157313', u'parentAssetUid': u'NODE-HYP1030', u'eventTypes': [u'TFEVT', u'PKIN', u'PKOUT', u'PEDEVT'], u'assetUid': u'CAM-HYP1030-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.711426:-117.156802', u'parentAssetUid': u'NODE-HYP1026', u'eventTypes': [u'TFEVT', u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1026-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.712468:-117.157511', u'parentAssetUid': u'NODE-HYP1052', u'eventTypes': [u'TFEVT', u'PEDEVT', u'PKOUT', u'PKIN'], u'assetUid': u'CAM-HYP1052-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.156876', u'parentAssetUid': u'NODE-HYP1008', u'eventTypes': [u'PKOUT', u'PKIN', u'TFEVT'], u'assetUid': u'CAM-HYP1008-F'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71162:-117.156866', u'parentAssetUid': u'NODE-HYP1032', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1032-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.71372:-117.156634', u'parentAssetUid': u'NODE-HYP1071', u'eventTypes': [u'PKIN', u'PKOUT'], u'assetUid': u'CAM-HYP1071-R'}, {u'assetType': u'CAMERA', u'mediaType': u'IMAGE,VIDEO', u'coordinates': u'32.713562:-117.156732', u'parentAssetUid': u'NODE-HYP1021', u'eventTypes': [u'PKIN', u'PKOUT', u'TFEVT'], u'assetUid': u'CAM-HYP1021-F'}], u'totalPages': 1, u'numberOfElements': 123, u'totalElements': 123, u'first': True}]
        #{"assetUid":"CAM-HYP1077-L","parentAssetUid":"NODE-HYP1077","eventTypes":["PEDEVT"],"mediaType":"IMAGE,VIDEO","assetType":"CAMERA","coordinates":"32.715611:-117.157534"},
        filtered_assets = []
        for page_dict in all_pages_dict_list :
            content_list = page_dict['content']
            for asset_dict in content_list :
                if filter_by in asset_dict['eventTypes'] :
                    #print("id: {}, eventTypes: {}, coordinates: {}".format(asset_dict['assetUid'], asset_dict['eventTypes'], asset_dict['coordinates'])) 
                    #{
                    #  id: 1,
                    #  lat: 12321,
                    #  lng: 123123
                    #}
                    mod_asset_dict = {}
                    asset_uid = asset_dict['assetUid']
                    if self.tfevt_id_dict.get(asset_uid) is None :
                        self.tfevt_id_list.append(asset_uid)
                        self.tfevt_id_dict[asset_uid] = len(self.tfevt_id_list)
                        self.tfevt_id_reverse_dict[len(self.tfevt_id_list)] = asset_uid 
                    mod_asset_dict['id'] = self.tfevt_id_dict[asset_uid]
                    coordinates_str = asset_dict['coordinates']
                    coord_tokens = coordinates_str.split(':')                     
                    mod_asset_dict['lat'] = long(coord_tokens[0])
                    mod_asset_dict['lng'] = long(coord_tokens[1]) 
                    filtered_assets.append(mod_asset_dict)
        return filtered_assets
    
    
    def parse_single_tfevt_data(self, detailed_data_dict):
        print(detailed_data_dict.keys())
        content_list = detailed_data_dict['content']
        print("len(content_list)={}".format(len(content_list)))
        for content_item in content_list :
            #print(content_item['eventType']) #always TFEVT
            #print(content_item)
            measures_data = content_item['measures']
            print("timestamp={}, vehicle_count={}, counter_count={}".format(content_item['timestamp'], measures_data['vehicleCount'], measures_data['counter_direction_vehicleCount']))
            #print(content_item['properties'])
        
    '''
    #doesn't work because 1 day or 7 days is too much
    def test_get_detailed_data1(self):
        asset_id = '385656d5-7a48-4755-a0f7-ef6ce92efe46'
        #time_now = time.time()
        #(datetime.datetime(2012,04,01,0,0) - datetime.datetime(1970,1,1)).total_seconds()
        ###data_now = datetime.datetime.now()
        ###datetime.datetime(2018, 2, 10, 23, 45, 43, 108666)
        ###time.mktime(data_now.timetuple())
        ###1518324463.0
        #calendar.timegm(time.gmtime())
        #1518324858
        
        #today = datetime.date.today()
        #today = datetime.datetime.now()
        #one_day = datetime.timedelta(days=1)
        #one_days_ago = today - (1 * one_day)
        #epoch_one_days = (one_days_ago - datetime.datetime(1970,1,1)).total_seconds()
        #epoch_now = (today - datetime.datetime(1970,1,1)).total_seconds()
        #epoch_one_days = long(round(epoch_one_days))
        #epoch_now = long(round(epoch_now))
        #detailed_data_str = self.get_tfevt_by_asset_id(asset_id, epoch_one_days, epoch_now)
        
        #start_time="1517673396000"
        #end_time="1518191796000"
        interval1 = 1518191796000 - 1517673396000
        start_time =  1517673396000 - interval1
        end_time =  1517673396000
        detailed_data_str = self.get_tfevt_by_asset_id(asset_id, start_time, end_time)
        print(detailed_data_str)
        detailed_data_dict = json.loads(detailed_data_str)
        #print("found first valid data, asset_id={}, data={}".format(asset_id, detailed_data_dict))
        content_data = detailed_data_dict['content']
        print(len(content_data))

    #works with intervals
    def test_get_detailed_data2(self):
        asset_id = '385656d5-7a48-4755-a0f7-ef6ce92efe46'
        start_time=1517673396000
        end_time=1518191796000
        interval1 = 1518191796000 - 1517673396000
        #start_time =  1517673396000 - interval1
        #end_time =  1517673396000
        detailed_data_str = self.get_tfevt_by_asset_id(asset_id, start_time, end_time)
        print(detailed_data_str)
        detailed_data_dict = json.loads(detailed_data_str)
        #print("found first valid data, asset_id={}, data={}".format(asset_id, detailed_data_dict))
        content_data = detailed_data_dict['content']
        #print(len(content_data))
        self.get_vehicle_count_per_slice(content_data)
    '''     
    
    
    def test_get_detailed_data(self):
        asset_id = '385656d5-7a48-4755-a0f7-ef6ce92efe46'
        '''
        today = datetime.datetime.now()
        #one_second = datetime.timedelta(seconds=1)
        #one_day = datetime.timedelta(days=1)
        one_period = datetime.timedelta(minutes=1)
        x_periods = 60
        x_periods_ago = today - (x_periods * one_period)        
        epoch_x_periods = (x_periods_ago - datetime.datetime(1970,1,1)).total_seconds() * 1000
        epoch_now = (today - datetime.datetime(1970,1,1)).total_seconds() * 1000
        epoch_seven_days = long(round(epoch_x_periods))
        epoch_now = long(round(epoch_now))
        #detailed_data_str = self.get_tfevt_by_asset_id(asset_id, epoch_one_days, epoch_now)
        start_time = epoch_seven_days
        end_time = epoch_now 
        detailed_data_str = self.get_tfevt_by_asset_id(asset_id, start_time, end_time)
        print(detailed_data_str)
        detailed_data_dict = json.loads(detailed_data_str)
        #print("found first valid data, asset_id={}, data={}".format(asset_id, detailed_data_dict))
        content_data = detailed_data_dict['content']
        print(len(content_data))
        self.get_vehicle_count_per_slice(content_data)
        '''
        vehicle_counts = self.get_vehicle_count_from_now(asset_id)
        print(vehicle_counts)

    def get_vehicle_count_from_now(self, asset_id, n_hours=24):        
        vehicle_counts = []
        today = datetime.datetime.now()
        #start_time is same as today
        (vehicle_count, start_time, end_time) = self.get_vehicle_count(asset_id, today)
        #print("vehicle_count={}, start_time={}, end_time={}".format(vehicle_count, start_time, end_time))
        
        vehicle_counts.append(vehicle_count)
        for i in range(0, n_hours) :
            (vehicle_count, start_time, end_time) = self.get_vehicle_count(asset_id, end_time)
            #print("vehicle_count={}, start_time={}, end_time={}".format(vehicle_count, start_time, end_time))
            vehicle_counts.append(vehicle_count)
        return vehicle_counts
    def get_vehicle_count(self, asset_id, today):
        one_period = datetime.timedelta(minutes=1)
        x_periods = 60
        x_periods_ago = today - (x_periods * one_period)
        
        epoch_x_periods = (x_periods_ago - datetime.datetime(1970,1,1)).total_seconds() * 1000
        epoch_now = (today - datetime.datetime(1970,1,1)).total_seconds() * 1000
        epoch_x_periods = long(round(epoch_x_periods))
        epoch_now = long(round(epoch_now))
        #detailed_data_str = self.get_tfevt_by_asset_id(asset_id, epoch_one_days, epoch_now)
        start_time = epoch_x_periods
        end_time = epoch_now 
        detailed_data_str = self.get_tfevt_by_asset_id(asset_id, start_time, end_time)
        print(detailed_data_str)
        detailed_data_dict = json.loads(detailed_data_str)
        content_data = detailed_data_dict['content']
        print(len(content_data))
        vehicle_count = self.get_vehicle_count_per_slice(content_data)
        return (vehicle_count, today, x_periods_ago)

    def get_vehicle_count_per_slice(self, content_data):
        #measures_data['vehicleCount'], measures_data['counter_direction_vehicleCount']
        vehicle_counts = [content_item['measures']['vehicleCount'] for content_item in content_data]
        vehicle_sum = sum(vehicle_counts)
        print(vehicle_counts)
        print(vehicle_sum)
        return (vehicle_sum)
        
    
    def get_data_for_filtered_assets(self, filtered_assets):
        for i, asset_dict in enumerate(filtered_assets) :
            userfriendly_id = asset_dict['id']
            asset_id = self.tfevt_id_reverse_dict[userfriendly_id]            
            #latitude = asset_dict['lat']
            #longtitude = asset_dict['lng']
            detailed_data_str = self.get_tfevt_by_asset_id_from_now(asset_id)
            if(detailed_data_str is None or len(detailed_data_str) == 0) :
                print("empty data")
            else :
                print(detailed_data_str)
                detailed_data_dict = json.loads(detailed_data_str)
                if len(detailed_data_dict['content']) > 0 :
                    print("found first valid data, asset_id={}, data={}".format(asset_id, detailed_data_dict))
                    print("userfriendly_id={}".format(self.tfevt_id_dict[asset_id]))
                    return detailed_data_dict
    
    def get_all_locations(self):
        url = "https://ic-metadata-service.run.aws-usw02-pr.ice.predix.io/v2/metadata/locations/search"

        querystring = {"q":"locationType:TRAFFIC_LANE","bbox":"32.715675:-117.161230,32.708498:-117.151681","page":"0","size":"50"}
        
        headers = {
            'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiJkZjgxYzEzZDBkODU0ZDhlYWJkMzEyZDQ1MjhhYTlhMCIsInN1YiI6ImhhY2thdGhvbiIsInNjb3BlIjpbInVhYS5yZXNvdXJjZSIsImllLWN1cnJlbnQuU0RTSU0tSUUtUFVCTElDLVNBRkVUWS5JRS1QVUJMSUMtU0FGRVRZLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtRU5WSVJPTk1FTlRBTC5JRS1FTlZJUk9OTUVOVEFMLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtVFJBRkZJQy5JRS1UUkFGRklDLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtUEFSS0lORy5JRS1QQVJLSU5HLkxJTUlURUQuREVWRUxPUCIsImllLWN1cnJlbnQuU0RTSU0tSUUtUEVERVNUUklBTi5JRS1QRURFU1RSSUFOLkxJTUlURUQuREVWRUxPUCJdLCJjbGllbnRfaWQiOiJoYWNrYXRob24iLCJjaWQiOiJoYWNrYXRob24iLCJhenAiOiJoYWNrYXRob24iLCJncmFudF90eXBlIjoiY2xpZW50X2NyZWRlbnRpYWxzIiwicmV2X3NpZyI6IjlmMWYyYzRkIiwiaWF0IjoxNTE4Mjk3NDQxLCJleHAiOjE1MTg5MDIyNDEsImlzcyI6Imh0dHBzOi8vODkwNDA3ZDctZTYxNy00ZDcwLTk4NWYtMDE3OTJkNjkzMzg3LnByZWRpeC11YWEucnVuLmF3cy11c3cwMi1wci5pY2UucHJlZGl4LmlvL29hdXRoL3Rva2VuIiwiemlkIjoiODkwNDA3ZDctZTYxNy00ZDcwLTk4NWYtMDE3OTJkNjkzMzg3IiwiYXVkIjpbImllLWN1cnJlbnQuU0RTSU0tSUUtVFJBRkZJQy5JRS1UUkFGRklDLkxJTUlURUQiLCJpZS1jdXJyZW50LlNEU0lNLUlFLVBBUktJTkcuSUUtUEFSS0lORy5MSU1JVEVEIiwiaWUtY3VycmVudC5TRFNJTS1JRS1QVUJMSUMtU0FGRVRZLklFLVBVQkxJQy1TQUZFVFkuTElNSVRFRCIsInVhYSIsImhhY2thdGhvbiIsImllLWN1cnJlbnQuU0RTSU0tSUUtRU5WSVJPTk1FTlRBTC5JRS1FTlZJUk9OTUVOVEFMLkxJTUlURUQiLCJpZS1jdXJyZW50LlNEU0lNLUlFLVBFREVTVFJJQU4uSUUtUEVERVNUUklBTi5MSU1JVEVEIl19.uzcmD7_iVGHKbmgivWJJ1c4HBAEQZmxT_HvGp02yqiBrHuJNgpTrxYhuRG96tuYEgfb31_jbaGwcDY2xqseyLw-1k-P6D_VTNgdh8ZX0Y2GxzE_TCnzpAvpW-Hx7yoVEofj2glP23Rc_OTBNgT68MSATKCAxQaww-KImM4BQmEh-2ErfBuPzG7tpnRiv5fTJ-D4VslwWCYm4YGSzu9HAaNftQtaX9XKRQtyWpxevg-Fww1PKo0HFG-xytulrcT8ldII4xp05TFVN5n6AalkI1BVyZBK590Xuz4r7GOTiFkfNL2zVzY-YmWCuWbTQDoxQXtbBurSU8PArNL1_VYUPig",
            'Predix-Zone-Id': "SDSIM-IE-TRAFFIC",
            'Cache-Control': "no-cache",
            'Postman-Token': "a608b396-8245-2309-36f6-d5b2bea74d95"
            }
        
        response = requests.request("GET", url, headers=headers, params=querystring)
        
        print(response.text)

if __name__ == "__main__":
    get_results()