# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import RtMonSys.models
import threading


def getStart_End_time():
    now = datetime.datetime.now()
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    hour_interval = RtMonSys.models.models_common.get_config("hour_interval")
    start_time = (now + datetime.timedelta(hours=-hour_interval)).strftime("%Y-%m-%d %H:%M:%S")
    return start_time,end_time

def getDataList(model_name, process_cd, datatype_id, limit):
    start_time, end_time = getStart_End_time()
    dataList = RtMonSys.models.models_common.getDetailList_update2(model_name, process_cd, datatype_id, limit, start_time, end_time)
    return dataList

def get_models():
    model = RtMonSys.models.model_setting.get_models()
    return model

def get_process(model):
    process = RtMonSys.models.model_setting.get_process(model)
    return process

def get_datatype(model,process):
    datatype = RtMonSys.models.model_setting.get_datatype(model,process)
    return datatype

def initConfig():
    try:
        database = RtMonSys.models.models_common.get_config("database")
        result = []
        model = database[0]["MODEL"]
        process = RtMonSys.models.model_setting.get_process(model)[0]
        dataType = RtMonSys.models.model_setting.get_datatype(model, process)
        result.append({"model": model})
        result.append({"process": process})
        result.append({"dataType": dataType})
        return result
    except BaseException as exp:
        result = [{'status': 'fail','msg':'Please make sure the config is currect'}]
        return result

def get_all_line_count(model_name, process_cd, datatype_id):
    database = RtMonSys.models.models_common.get_config("database")
    counts = []
    for item in database:
        if item["MODEL"] == model_name:
            for dataItem in item["DATA"]:
                if dataItem["PROCESS"] == process_cd:
                    type = dataItem["TYPE"]
                    break
    for item in database:
        if item["MODEL"] == model_name:
            line_counts = getDataList(model_name, process_cd, datatype_id, True)
            for lineItem in item["LINE"]:
                num = 0
                for line_id in line_counts:
                    if line_id['line_cd'] == lineItem:
                        if type == "NG COUNT":
                            num = line_id['ng_count']
                counts.append(num)
    return counts

def getLine(model,name, process, datatype_Id, JIG_type, PROCESS_type, str_line, limit, ip):
    try:
        start_time, end_time = getStart_End_time()
        result = []
        line = str_line.split(',')
        row = RtMonSys.models.model_setting.getProcess(model, name)
        mix_data = int(row[0]['MIX_DATA'])
        jig_s = float(row[0]['JIG_S'])
        str_inspect = row[0]['INSPECT']
        dataList = getDataList(model, process, datatype_Id, limit)
        fin_dataList = RtMonSys.models.models_common.get_real_data(dataList, mix_data, str_inspect,jig_s)
        start_thread(fin_dataList,name, model, process, datatype_Id, limit, start_time, end_time, ip)
        result.append({"line": line, "INTERVAL": RtMonSys.models.models_common.get_config("hour_interval"), "DATALIST": fin_dataList, "start_time": start_time,
             "end_time": end_time, 'JIG_type': JIG_type, 'PROCESS_type': PROCESS_type})
    except BaseException as exp:
        result.append({'status': 'fail', 'msg': str(exp)})
    return result

def auto_updating():
    auto_update = RtMonSys.models.models_common.get_config("auto_updating")
    return auto_update

def start_thread(fin_dataList,name, model, process, datatype_Id, limit, start_time, end_time, ip):
    try:
        thread = threading.Thread(target=RtMonSys.models.model_config.update_config,args=(fin_dataList,name, model, process, datatype_Id, limit, start_time, end_time, ip,))
        thread.start() # 启动多线程
    except:
        print("Error:unable to start thread")
