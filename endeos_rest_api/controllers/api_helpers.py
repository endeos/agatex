from typing import Union
import logging

_logger = logging.getLogger(__name__)

def prepare_response(data=[], errors=[]):
        res = {
            "data": data,
            "errors": errors
        }

        return res

def search_records(model:object, domain:list, limit:Union[int,None]=None) -> Union[object,bool]:
     recordset = model.search(domain, limit=limit)
     if recordset:
          return recordset
     return False

def browse_records(model:object, rec_ids:Union[int,list]) -> Union[object,bool]:
    recordset = model.browse(rec_ids).exists()
    if recordset:
        return recordset
    return False

def create_record(model:object, data:dict) -> object:
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