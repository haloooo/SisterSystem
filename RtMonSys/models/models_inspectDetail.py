# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
from RtMonSys.models import models_common, model_setting
import json


def getInspectList(model_name, serial_cd, process_cd):
    inspectList = []
    # INSPECT = getInspectFromConf(model_name, process_cd)

    row = model_setting.getProcess(model_name, process_cd)
    INSPECT = (row[0]['INSPECT']).split(';')
    INSPECT_LIST = []
    for item in INSPECT:
        INSPECT_LIST.append({'name':item.split(':')[0],'value':item.split(':')[1]})
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT \
                    inspect_cd,d.inspect_text\
                FROM \
                    t_insp_" + model_name + " i \
                    INNER JOIN t_data_" + model_name + " d ON i.insp_seq = d.insp_seq \
                    AND i.serial_cd = %s \
                    AND d.judge_text = '1' \
                ORDER BY inspect_cd"
        cur.execute(sql, (serial_cd,))
        rows = cur.fetchall()
        for item in INSPECT_LIST:
            print(item['name'])
        for row in rows:
            flag, list = check_exist(row[0], INSPECT_LIST)
            if flag:
                inspectList.append({'inspect_code':row[0],'inspect':row[1]})
    except BaseException as exp:
        print(exp)
        inspectList = models_common.databaseException(exp)
    connections[model_name].close()
    return inspectList

def check_exist(val, INSPECT_LIST):
    for item in INSPECT_LIST:
        if item['name'] == val:
            list = item['value'].split(',')
            return True,list
    return False


def getInspectFromConf(model_name, process_cd):
    INSPECT = []
    database_list = models_common.get_config("database")
    for item in database_list:
        if item["MODEL"] == model_name:
            for dataItem in item["DATA"]:
                if dataItem["PROCESS"] == process_cd:
                    INSPECT = dataItem["INSPECT"]
                    break
    return INSPECT

if __name__ == '__main__':
    inp_strr = '{"k1":123, "k2": "456", "k3":"ares"}'
    inp_dict = json.loads(inp_strr)  # 根据字符串书写格式，将字符串自动转换成 字典类型
    print(inp_dict)
