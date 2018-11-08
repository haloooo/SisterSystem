# * coding:utf-8 *
# Author    : Administrator
# Createtime: 10/26/2018
from urllib import request
import json

# put请求
import RtMonSys.models


def requests_post(serial_cd, status, ip):
        textmod = {"serial_cd": serial_cd, "status": status}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {"Content-Type": "application/json"}
        url = ip
        req = request.Request(url=url, data=textmod, headers=header_dict, method="POST")
        res = request.urlopen(req)
        res = res.read()
        data = json.loads(res)
        RtMonSys.models.model_config.complete_config(data)

def requests_put(serial_cd, datatype_id, line_cd, status, ip):
        textmod = {"serial_cd": serial_cd, "status": status, "datatype_id": datatype_id, "line_cd": line_cd}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {"Content-Type": "application/json"}
        url = ip
        req = request.Request(url=url, data=textmod, headers=header_dict, method="PUT")
        res = request.urlopen(req)
        res.read()
        # data = json.loads(res)
        # RtMonSys.models.model_config.complete_config(data)

if __name__ == '__main__':
    result = []
    result.append({"state": "fail", "msg": "ss"})
    jsonstr = json.dumps(result)
    print(jsonstr)