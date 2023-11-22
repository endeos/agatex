from typing import Union
import logging
import traceback
import json
import ast

_logger = logging.getLogger(__name__)

def prepare_response(data=[], errors=[]):
        res = {
            "data": data,
            "errors": errors
        }

        return res

def search_records(model:object, domain:list, limit:Union[int,None]=None, context:dict={}, company:Union[int,None]=None) -> Union[object,bool]:
    if context:
        model = model.with_context(**context)

    if company:
        model = model.with_company(company)

    recordset = model.search(domain, limit=limit)
    return recordset

def browse_records(model:object, rec_ids:Union[int,list], context:dict={}) -> Union[object,bool]:
    if context:
        model = model.with_context(**context)

    recordset = model.browse(rec_ids).exists()
    return recordset

def create_record(model:object, data:dict, context:dict={}, company:Union[int,None]=None) -> object:
    if context:
        model = model.with_context(**context)

    if company:
        model = model.with_company(company)
        
    new_record = model.create(data)
    return new_record

def update_record(model:object, rec_id:int, new_data:dict) -> bool:
    record = model.browse(rec_id).exists()
    if record:
        record.write(new_data)
        return True
    return False

def delete_record(model: object, rec_id:int) -> bool:
     record = model.browse(rec_id).exists()
     if record:
          record.unlink()
          return True
     return False

def dict_keys_lower(d:dict) -> dict:
    res = dict()
    for key in d.keys():
        if isinstance(d[key], dict):
            res[key.lower()] = dict_keys_lower(d[key])
        else:
            res[key.lower()] = d[key]
    return res

def deserialize_request_params_json(request:object) -> list:
    raw_data = request.httprequest.data
    errors = []

    data = request.params
    if not data:
        # if there aren't request.params, try with json default deserialize first
        try:
            data = json.loads(raw_data.decode("utf-8"))
            _logger.warning(f"Params: {data}")
        except Exception as e:
            errors.append(f"{e}")

            _logger.error(f"{e}")
            _logger.warning(f"deserialize_request_params_json | json.loads failed converting raw data. Trying again without decoding to utf8...")
            pass
    
    # if default deserialize failed, try again withoud decoding raw data
    if not data:
        try:
            data = json.loads(raw_data)
            _logger.warning(f"Params: {data}")
        except Exception as e:
            errors.append(f"{e}")

            _logger.error(f"{e}")
            _logger.warning(f"deserialize_request_params_json | json.loads failed. Trying with literal eval...")
            pass
    
    # if the above also failed, then try literal evaluation of the raw data
    if not data:
        try:
            data = ast.literal_eval(raw_data.decode("utf-8"))
            _logger.warning(f"Params: {data}")
        except Exception as e:
            errors.append(f"{e}")
            
            _logger.error(f"Raw data type: {type(raw_data)} Val: {raw_data}")
            _logger.error(f"deserialize_request_params_json | Error decoding raw data to json | {e}")
            _logger.error(traceback.format_exc())
    
    """ # lowercase all dictionary keys
    if data and type(data) is dict:
        data = dict_keys_lower(data) """

    return data.get("params") or data, errors


def validate_request_token(request):
    env = request.env
    post_data = request.params
    if not post_data:
        post_data, deserialize_errors = deserialize_request_params_json(request)

    api_key = post_data.get("api_key", "")
    ResUsersApiKeys = env["res.users.apikeys"]
            
    user_id = ResUsersApiKeys._check_credentials(scope="rpc", key=api_key)

    _logger.warning(f"Validating user token: {api_key} | user_id: {user_id}")

    if not user_id:
        return False
    
    request.update_env(user=user_id)
    return True