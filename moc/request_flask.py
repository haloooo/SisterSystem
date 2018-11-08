# * coding:utf-8 *
# Author    : Administrator
# Createtime: 8/5/2018
from flask import Flask,request
import json
app = Flask(__name__)

@app.route('/index')
def hello_world():
    serial_cd = request.args.get('serial_cd')
    status = request.args.get('status')
    # serial_cd = '1'
    # status = '1'
    str_json = '{"serial_cd": ' + '"' + serial_cd + '"' + ',"datatype_id":"M_MG_PLATE_STATION","line_cd":"xx","created_at":"2018-08-05 11:20:00","updated_at":"2018-08-05 11:20:00","status":' + str(
        status) + '}'
    data = json.loads(str_json)
    return str_json

if __name__ == '__main__':
    app.run()