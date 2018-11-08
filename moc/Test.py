

#PUT
from urllib import request
import json
textmod={"serial_cd":"Test1234","status":"1","datatype_id":"JIG_TAB","line_cd":"L12"}
textmod = json.dumps(textmod).encode(encoding='utf-8')
header_dict = {"Content-Type": "application/json"}
url='http://10.10.100.120/kk07/rms-ng/api/resource'
req = request.Request(url=url,data=textmod,headers=header_dict,method="PUT")
res = request.urlopen(req)
res = res.read()
print(res)
 

#POST
from urllib import request
import json
textmod={"serial_cd":"Test1234","status":"1"}
textmod = json.dumps(textmod).encode(encoding='utf-8')
header_dict = {"Content-Type": "application/json"}
url='http://10.10.100.120/kk07/rms-ng/api/resource'
req = request.Request(url=url,data=textmod,headers=header_dict,method="POST")
res = request.urlopen(req)
res = res.read()
print(res)