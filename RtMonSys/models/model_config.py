# * coding:utf-8 *
# Author    : Administrator
# Createtime: 8/5/2018
import sqlite3, os, datetime, time

from RtMonSys.models import model_homePage, models_common
from moc import requestHelper


def get_config():
    start_time, end_time = model_homePage.getStart_End_time()
    result = []
    create_table()
    file_path = os.getcwd() + '/data.db'
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    rows = c.execute("SELECT ID, SERIAL_CD, DATATYPE_ID, LINE_CD, CREATE_AT, UPDATED_AT, STATE from CONFIG WHERE CREATE_AT > ? AND CREATE_AT < ?",(start_time, end_time,))
    for row in rows:
        result.append(
            {'id': row[0], 'serial_cd': row[1], 'datatype_id': row[2], 'line_cd': row[3], 'create_at': row[4],
             'updated_at': row[5], 'state': row[6]})
    conn.close()
    return result

def create_table():
    file_path = os.getcwd() + '/data.db'
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS CONFIG
               (
               ID INTEGER PRIMARY KEY AUTOINCREMENT,
               SERIAL_CD varchar(40),
               DATATYPE_ID varchar(40), 
               LINE_CD varchar(40),
               CREATE_AT text(40),
               UPDATED_AT text(40),
               STATE varchar(40));''')
    conn.commit()
    conn.close()

def update_config(datalist,name, model, process, datatype_id, limit, start_time, end_time, ip):
    create_table()
    file_path = os.getcwd() + '/data.db'
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    for item in datalist:
        serial_cd = item['station_slot']
        line_cd = item['line_cd']
        rows = c.execute("SELECT CREATE_AT FROM CONFIG WHERE SERIAL_CD = ?",(serial_cd,))
        count = 0
        CREATE_AT_list = []
        for row in rows:
            count = count + 1
            CREATE_AT_list.append(row[0])
        if count == 0:
            # 新規登録 Http PUT
            requestHelper.requests_put(serial_cd, datatype_id, line_cd, '1', ip)
            c.execute("INSERT INTO CONFIG(SERIAL_CD, CREATE_AT, STATE) VALUES(?,?,?);",(item['station_slot'], end_time, '1'))
            conn.commit()
        else:
            for row in CREATE_AT_list:
                create_at = row
                if create_at != '':
                    create_at_time = datetime.datetime.strptime(create_at, "%Y-%m-%d %H:%M:%S")
                    start_time_ = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    end_time_ = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                    if create_at_time > start_time_ and create_at_time < end_time_:
                        if models_common.getDetailList_StationSlot2(model,line_cd, name, process, datatype_id, limit, start_time, end_time):
                            # 登録情報の変更 Http Post
                            requestHelper.requests_post(serial_cd, '1', ip)
    conn.close()


def complete_config(data):
    file_path = os.getcwd() + '/data.db'
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("UPDATE CONFIG SET datatype_id=?,line_cd=?,create_at=?,updated_at=?,state=? WHERE serial_cd=?;",(data['datatype_id'],data['line_cd'],data['created_at'],data['updated_at'],data['status'], data['serial_cd'],))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print(get_config())




