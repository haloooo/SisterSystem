# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import connections
import os
import re

import RtMonSys.models


def get_config(key):
    # 加载配置文件
    file_path = os.getcwd() + '/config/config.json'
    fp = open(file_path)
    json_data = json.load(fp)
    return json_data[key]

def databaseException(exp):
    if 'could not connect to server' in str(exp):
        return 101
    else:
        return 102

# 获取ng数据
def getDetailList(model_name, process_cd, datatype_id, start_time, end_time, firstFlg):
    result = []
    sql_orderby = "ORDER BY line_cd, station_slot"

    # 获取产线按钮数据的场合
    if firstFlg:
        sql_orderby = " ORDER BY line_cd ASC, count_serial_cd DESC "

    try:
        # 从config文件中取得line数组
        database_list = get_config("database")
        lineArr = []

        # 根据model_name和process_cd获取limit
        for item in database_list:
            if item["MODEL"] == model_name:
                for dataItem in item["DATA"]:
                    if dataItem["PROCESS"] == process_cd:
                        limit = dataItem["LIMIT"]
                        break

        for row in database_list:
            if row['MODEL'] == model_name:
                # 从配置文件里取得LINE
                lineArr = row['LINE']
                break
        cur = connections[model_name].cursor()
        sql = "SELECT \
                    line_cd,\
                    station_slot,\
                    COUNT( serial_cd ) AS count_serial_cd \
                FROM\
                    (\
                SELECT DISTINCT \
                    line_cd,\
                    T2.station_slot,\
                    T1.serial_cd,\
                    judge_text \
                FROM\
                    (\
                SELECT \
                    serial_cd,\
                    line_cd,\
                    judge_text \
                FROM\
                    (\
                SELECT \
				    serial_cd,\
				    process_at,\
				    line_cd,\
				    judge_text, \
                    ROW_NUMBER ( ) OVER ( PARTITION BY line_cd, serial_cd ORDER BY process_at DESC ) RANK1 \
			    FROM\
				    (\
				SELECT DISTINCT \
					i.serial_cd,\
					i.process_at,\
					p.line_cd,\
					i.judge_text,\
					ROW_NUMBER ( ) OVER ( PARTITION BY line_cd ORDER BY i.process_at DESC ) RANK \
				FROM \
					t_insp_" + model_name + " i,\
					m_process p \
				WHERE \
					i.proc_uuid = p.proc_uuid \
					AND p.line_cd IN ( %s ) \
					AND p.process_cd = '(process_cd)' \
                    AND i.process_at >= '(start_time)' \
					AND i.process_at <= '(end_time)' \
				ORDER BY i.process_at DESC \
				) BASE1 \
			    WHERE RANK <= (LIMIT) \
                ) BASE2 \
                WHERE \
                    judge_text = '1' \
                    AND RANK1 = 1 \
                ) T1 \
                    INNER JOIN (\
                SELECT DISTINCT \
                    f.partsserial_cd AS station_slot,\
                    f.serial_cd,\
                    f.process_at \
                FROM \
                    m_process p,\
                    t_faci_" + model_name + " f \
                WHERE \
                    f.proc_uuid = p.proc_uuid \
                    AND p.process_cd = '(process_cd)' \
                    AND f.datatype_id = '(datatype_id)' \
                    ) T2 ON T1.serial_cd = T2.serial_cd AND T1.judge_text = '1' \
                    ) T3 \
                GROUP BY \
                    line_cd,station_slot " + sql_orderby
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace("(process_cd)", process_cd).replace("(start_time)", start_time).replace("(end_time)", end_time) \
            .replace("(datatype_id)", datatype_id).replace("(LIMIT)", str(limit))
        cur.execute(sql, lineArr)
        rows = cur.fetchall()

        # 计算对应的IN/Yield
        sql_1 = "SELECT \
                            line_cd,\
                            station_slot,\
                            COUNT( serial_cd ) AS count_serial_cd \
                        FROM\
                            (\
                        SELECT DISTINCT \
                            line_cd,\
                            T2.station_slot,\
                            T1.serial_cd,\
                            judge_text \
                        FROM\
                            (\
                        SELECT \
                            serial_cd,\
                            line_cd,\
                            judge_text \
                        FROM\
                            (\
                        SELECT \
        				    serial_cd,\
        				    process_at,\
        				    line_cd,\
        				    judge_text, \
                            ROW_NUMBER ( ) OVER ( PARTITION BY line_cd, serial_cd ORDER BY process_at DESC ) RANK1 \
        			    FROM\
        				    (\
        				SELECT DISTINCT \
        					i.serial_cd,\
        					i.process_at,\
        					p.line_cd,\
        					i.judge_text,\
        					ROW_NUMBER ( ) OVER ( PARTITION BY line_cd ORDER BY i.process_at DESC ) RANK \
        				FROM \
        					t_insp_" + model_name + " i,\
        					m_process p \
        				WHERE \
        					i.proc_uuid = p.proc_uuid \
        					AND p.line_cd IN ( %s ) \
        					AND p.process_cd = '(process_cd)' \
                            AND i.process_at >= '(start_time)' \
        					AND i.process_at <= '(end_time)' \
        				ORDER BY i.process_at DESC \
        				) BASE1 \
        			    WHERE RANK <= (LIMIT) \
                        ) BASE2 \
                        WHERE \
                             RANK1 = 1 \
                        ) T1 \
                            INNER JOIN (\
                        SELECT DISTINCT \
                            f.partsserial_cd AS station_slot,\
                            f.serial_cd,\
                            f.process_at \
                        FROM \
                            m_process p,\
                            t_faci_" + model_name + " f \
                        WHERE \
                            f.proc_uuid = p.proc_uuid \
                            AND p.process_cd = '(process_cd)' \
                            AND f.datatype_id = '(datatype_id)' \
                            ) T2 ON T1.serial_cd = T2.serial_cd \
                            ) T3 \
                        GROUP BY \
                            line_cd,station_slot " + sql_orderby
        sql_1 = sql_1 % ','.join(['%s'] * len(lineArr))
        sql_1 = sql_1.replace("(process_cd)", process_cd).replace("(start_time)", start_time).replace("(end_time)",
                                                                                                      end_time) \
            .replace("(datatype_id)", datatype_id).replace("(LIMIT)", str(limit))
        cur.execute(sql_1, lineArr)
        rows_1 = cur.fetchall()
        # 产线按钮的场合
        if firstFlg:
            last_line = ""
            for row in rows:
                # 每条产线只取第一条数据（ng最大的station）
                if row[0] != last_line:
                    result.append({"line_cd": row[0], "ng_count": int(row[2]), })
                    last_line = row[0]
        else:# 下方ng列表的场合
            # 获取NG_RGB
            for item in database_list:
                if item["MODEL"] == model_name:
                    for dataItem in item["DATA"]:
                        if dataItem["PROCESS"] == process_cd:
                            ngRgb = dataItem["JIG"]
                            break
            count = 0
            for row in rows:
                in_ = int(rows_1[count][2])
                yield_ = (100 * ((in_- int(row[2]))/in_))
                result.append({"line_cd":row[0], "station_slot":row[1], "ng_count":int(row[2]),"in":int(rows_1[count][2]),"yield":yield_ })
                count = count + 1
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result

def getDetailList_update3(model_name,name,line_cd, process_name, datatype_id, limit, start_time, end_time):
    try:
        row = RtMonSys.models.model_setting.getProcess(model_name, name)
        INSPECT = (row[0]['INSPECT']).split(',')
        str_inspect = ""
        for item in INSPECT:
            str_inspect += "'%s'," % (item)
        str_inspect = str_inspect[:-1]
        cur = connections[model_name].cursor()
        sql = '''select m.line_cd,m.partsserial_cd,m.serial_cd,m.judge_text,m.process_at,d.inspect_cd,d.inspect_text from t_data_(model_name) as d,
               (select i.insp_seq,f.serial_cd,i.line_cd,i.process_at,f.partsserial_cd,i.judge_text,row_number() over (partition by f.serial_cd,f.datatype_id order by f.process_at) from t_faci_(model_name) f , 
               (select insp_seq,serial_cd,process_at,judge_text,line_cd,process_cd from 
               (select a.insp_seq,a.serial_cd,a.process_at,a.judge_text,b.line_cd,b.process_cd,row_number() over (partition by a.serial_cd order by a.process_at desc) from t_insp_(model_name) a,m_process b 
               where a.proc_uuid = b.proc_uuid
               and b.line_cd = '(line_cd)'  
               and b.process_cd = '(process_cd)' 
               and a.process_at >= '(start_time)' 
               and a.process_at <= '(end_time)' 
                ) as n 
               where n.row_number = '1' 
               order by n.process_at desc 
               limit '(limit)' 
               ) as I 
               where f.serial_cd = i.serial_cd 
               and f.datatype_id = '(datatype_id)'
               ) as m 
                where d.insp_seq = m.insp_seq 
                and m.row_number = '1' 
                and d.inspect_cd in ('''+ str_inspect +''')'''
        sql = sql.replace('(model_name)', model_name) \
            .replace("(line_cd)", line_cd) \
            .replace("(process_cd)", process_name) \
            .replace("(start_time)", start_time) \
            .replace("(end_time)",end_time) \
            .replace("(datatype_id)", datatype_id) \
            .replace("(limit)", str(limit))
        cur.execute(sql)
        rows = cur.fetchall()
        count = 0
        for row in rows:
            count = count + 1
        if count > 0:
            return True
        else:
            return False
    except BaseException as exp:
        return False
    connections[model_name].close()
    return False

def getDetailList_update2(model_name, process_name, datatype_id, limit, start_time, end_time):
    try:
        database_list = get_config("database")
        lineArr = []
        for row in database_list:
            if row['MODEL'] == model_name:
                # 从配置文件里取得LINE
                lineArr = row['LINE']
                break
        cur = connections[model_name].cursor()
        sql = '''select m.line_cd,m.partsserial_cd,m.serial_cd,m.judge_text,m.process_at,d.inspect_cd,d.inspect_text from t_data_(model_name) as d,
               (select i.insp_seq,f.serial_cd,i.line_cd,i.process_at,f.partsserial_cd,i.judge_text,row_number() over (partition by f.serial_cd,f.datatype_id order by f.process_at) from t_faci_(model_name) f , 
               (select insp_seq,serial_cd,process_at,judge_text,line_cd,process_cd from 
               (select a.insp_seq,a.serial_cd,a.process_at,a.judge_text,b.line_cd,b.process_cd,row_number() over (partition by a.serial_cd order by a.process_at desc) from t_insp_(model_name) a,m_process b 
               where a.proc_uuid = b.proc_uuid
             and b.line_cd in (%s)   
               and b.process_cd = '(process_cd)' 
               and a.process_at >= '(start_time)' 
               and a.process_at <= '(end_time)' 
                ) as n 
               where n.row_number = '1' 
               order by n.process_at desc 
               limit '(limit)' 
               ) as I 
               where f.serial_cd = i.serial_cd 
               and f.datatype_id = '(datatype_id)'
               ) as m 
                where d.insp_seq = m.insp_seq 
                and m.row_number = '1' ORDER BY line_cd,partsserial_cd '''
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace('(model_name)', model_name) \
            .replace("(process_cd)", process_name) \
            .replace("(start_time)", start_time) \
            .replace("(end_time)",end_time) \
            .replace("(datatype_id)", datatype_id) \
            .replace("(limit)", str(limit))
        cur.execute(sql, lineArr)
        rows = cur.fetchall()
        data_list = []
        for row in rows:
            re = {}
            re['line_cd'] = row[0]
            re['station_slot'] = row[1]
            re['serial_cd'] = row[2]
            re['judge_text'] = row[3]
            re['process_at'] = row[4].strftime("%Y-%m-%d %H:%M:%S")
            re['inspect_cd'] = row[5]
            re['inspect_text'] = row[6]
            data_list.append(re)
    except BaseException as exp:
        data_list = databaseException(exp)
    connections[model_name].close()
    return data_list

def getDetailList_update(model_name, process_name, datatype_id, limit, start_time, end_time,JIG_type, lineArr):
    result = []
    try:
        cur = connections[model_name].cursor()
        # After
        sql = "SELECT line_cd,partsserial_cd AS station_slot,serial_cd,judge_text FROM ( \
		       SELECT f.serial_cd, i.line_cd,f.process_at,f.partsserial_cd,i.judge_text,ROW_NUMBER () OVER ( \
				PARTITION BY f.serial_cd ORDER BY f.process_at) FROM t_faci_"+ model_name +" f,(SELECT serial_cd,process_at, \
				judge_text,line_cd,process_cd FROM(SELECT A .serial_cd,A .process_at,A .judge_text,b.line_cd,b.process_cd,\
				ROW_NUMBER () OVER (PARTITION BY A .serial_cd ORDER BY A .process_at DESC) FROM t_insp_"+ model_name +" A,m_process b \
				WHERE A .proc_uuid = b.proc_uuid AND b.line_cd IN (%s) AND b.process_cd = '(process_name)' AND A.process_at >= '(start_time)' \
				AND A.process_at <= '(end_time)') AS n WHERE ROW_NUMBER = '1') AS I WHERE f.serial_cd = i.serial_cd \
		        AND f.datatype_id = '(datatype_id)') AS M WHERE M . ROW_NUMBER = '1' LIMIT '(limit)';"
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace("(process_name)", process_name).replace("(start_time)", start_time).replace("(end_time)",end_time) \
            .replace("(datatype_id)", datatype_id).replace("(limit)", str(limit))
        cur.execute(sql,lineArr)
        rows = cur.fetchall()
        line_cd_list = []
        JIG_list = []

        for row in rows:
            if not row[0] in line_cd_list:
                line_cd_list.append(row[0])
        for item in line_cd_list:
            for row_1 in rows:
                if item == row_1[0]:
                    if not row_1[1] in JIG_list:
                        JIG_list.append(row_1[1])
            for JIG_item in JIG_list:
                IN_ = 0
                NG_ = 0
                for row_ in rows:
                    if row_[0] == item and row_[1] == JIG_item and int(row_[3]) == 1:
                        NG_ = NG_ + 1
                    if row_[0] == item and row_[1] == JIG_item:
                        IN_ = IN_ + 1
                Yield = '%.2f' % (100 * ((IN_- NG_)/IN_))
                result.append({"line_cd":item,"station_slot":JIG_item,"ng_count":NG_,"in":IN_,"yield":Yield})
            JIG_list = []
        # 排序
        # if JIG_type == 'NG COUNT':
        #     result.sort(key=lambda x:x['ng_count'])
        # else:
        #     result.sort(key=lambda x:x['ng_count'],reverse=True)
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result

def getDetailList_StationSlot2(model_name,line_cd, name, process_name, datatype_id, limit, start_time, end_time):
    try:
        row = RtMonSys.models.model_setting.getProcess(model_name, name)
        INSPECT = (row[0]['INSPECT']).split(',')
        str_inspect = ""
        for item in INSPECT:
            str_inspect += "'%s'," % (item)
        str_inspect = str_inspect[:-1]
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT line_cd,station_slot,serial_cd,judge_text,process_at,inspect_cd,inspect_text FROM\
                      (SELECT T2.line_cd,station_slot,T2.serial_cd,T2.judge_text,T2.process_at,d.inspect_cd,d.inspect_text FROM(  \
                      SELECT line_cd,serial_cd,judge_text,insp_seq,process_at FROM ( SELECT DISTINCT P .line_cd,i.serial_cd, \
                      i.process_at,i.judge_text,i.insp_seq,ROW_NUMBER () OVER ( PARTITION BY serial_cd ORDER BY process_at DESC \
                      ) RANK FROM t_insp_" + model_name + " i,m_process P WHERE i.proc_uuid = P .proc_uuid AND P .line_cd = '(line_cd)' \
                      AND P .process_cd = '(process_cd)' AND i.process_at >= '(start_time)' AND i.process_at <= '(end_time)' \
                      ORDER BY i.process_at DESC LIMIT '(limit)') BASE WHERE RANK = 1 ) T2 LEFT JOIN t_data_" + model_name + " d ON T2.insp_seq = d.insp_seq \
                      INNER JOIN ( SELECT DISTINCT f.partsserial_cd AS station_slot,f.serial_cd,f.process_at FROM m_process P,t_faci_" + model_name + " f \
                      WHERE f.proc_uuid = P .proc_uuid AND P .Process_cd = '(process_cd)' AND f.datatype_id = '(datatype_id)' ) T3 ON T2.serial_cd = T3.serial_cd) T4 \
                      WHERE inspect_cd in (" + str_inspect + ") "
        sql = sql.replace("(process_cd)", process_name).replace("(start_time)", start_time).replace("(end_time)",end_time).replace("(datatype_id)", datatype_id).replace("(limit)", str(limit)).replace("(line_cd)", line_cd)
        cur.execute(sql)
        rows = cur.fetchall()
        count = 0
        for row in rows:
            count = count + 1
        if count > 0:
            return True
        else:
            return False
    except BaseException as exp:
        connections[model_name].close()
        return False
    connections[model_name].close()
    return False

def getDetailList_StationSlot(model_name, process_name, datatype_id, limit, start_time, end_time, lineArr, station_slot):
    result = []
    try:
        cur = connections[model_name].cursor()
        # After
        sql = "SELECT line_cd,partsserial_cd AS station_slot,serial_cd,judge_text FROM ( \
    		       SELECT f.serial_cd, i.line_cd,f.process_at,f.partsserial_cd,i.judge_text,ROW_NUMBER () OVER ( \
    				PARTITION BY f.serial_cd ORDER BY f.process_at) FROM t_faci_" + model_name + " f,(SELECT serial_cd,process_at, \
    				judge_text,line_cd,process_cd FROM(SELECT A .serial_cd,A .process_at,A .judge_text,b.line_cd,b.process_cd,\
    				ROW_NUMBER () OVER (PARTITION BY A .serial_cd ORDER BY A .process_at DESC) FROM t_insp_" + model_name + " A,m_process b \
    				WHERE A .proc_uuid = b.proc_uuid AND b.line_cd IN (%s) AND b.process_cd = '(process_name)' AND A.process_at >= '(start_time)' \
    				AND A.process_at <= '(end_time)' AND A.judge_text = '1') AS n WHERE ROW_NUMBER = '1') AS I WHERE f.serial_cd = i.serial_cd \
    		        AND f.datatype_id = '(datatype_id)') AS M WHERE M . ROW_NUMBER = '1' AND partsserial_cd = '(station_slot)' LIMIT '(limit)';"
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace("(process_name)", process_name).replace("(start_time)", start_time).replace("(end_time)",end_time) \
            .replace("(datatype_id)", datatype_id).replace("(station_slot)", station_slot).replace("(limit)", str(limit))
        cur.execute(sql, lineArr)
        rows = cur.fetchall()
        count = 0
        for row in rows:
            count = count + 1
        if count > 0:
            return True
        else:
            return False
    except BaseException as exp:
        count = 0
    connections[model_name].close()
    return False

# 获取指定产线和datatype_id下的station和slot
def getStationSlot(model_name, datatype_id, line_cd):
    result = {}
    partsserial_cd = line_cd + "MS%"
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT\
                    max(\
                    substr(\
                    partsserial_cd,\
                    position( 'MS' IN partsserial_cd ) + 2,\
                    ( position( '-' IN partsserial_cd ) - ( position( 'MS' IN partsserial_cd ) + 2 ) ) \
                    ) \
                    ) AS station,\
                    max( substr( partsserial_cd, position( '-' IN partsserial_cd ) + 1 ) ) AS slot \
                FROM\
                    t_faci_" + model_name + " faci \
                WHERE\
                    datatype_id = %s \
                    AND partsserial_cd LIKE %s"
        cur.execute(sql, (datatype_id, partsserial_cd))
        rows = cur.fetchall()
        for row in rows:
            result = {"station": row[0], "slot": row[1]}
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result

def getJIGByLine_(model_name, process_cd, start_time, end_time):
    result = []
    try:
        # 从config文件中取得line数组
        database_list = get_config("database")
        lineArr = []

        # 根据model_name和process_cd获取limit
        for item in database_list:
            if item["MODEL"] == model_name:
                for dataItem in item["DATA"]:
                    if dataItem["PROCESS"] == process_cd:
                        limit = dataItem["LIMIT"]
                        break

        for row in database_list:
            if row['MODEL'] == model_name:
                # 从配置文件里取得LINE
                lineArr = row['LINE']
                break
        cur = connections[model_name].cursor()
        sql = "SELECT line_cd, COUNT (B.line_cd) FROM (  \
                SELECT DISTINCT A .serial_cd,A .judge_text,A .line_cd \
                FROM ( SELECT DISTINCT (i.serial_cd),i.process_at,i.judge_text,P .line_cd \
                FROM t_insp_"+model_name+" i,m_process P WHERE i.proc_uuid = P .proc_uuid \
                AND P .line_cd IN ( %s ) AND P .Process_cd = '(process_cd)' \
                AND i.process_at >= '(start_time)' \
                AND i.process_at <= '(end_time)' \
                ORDER BY i.process_at DESC LIMIT '(LIMIT)') AS A WHERE a.judge_text = '1' \
                ORDER BY A .judge_text) AS B GROUP BY B.line_cd; "
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace("(process_cd)", process_cd).replace("(start_time)", start_time).replace("(end_time)", end_time) \
            .replace("(LIMIT)", str(limit))
        cur.execute(sql, lineArr)
        rows = cur.fetchall()
        count = 0
        for line in lineArr:
            if checkExist(line, rows):
                for row in rows:
                    if line == row[0]:
                        count = int(row[1])
                        break
            else:
                count = 0
            result.append(count)
    except BaseException as exp:
        print(exp)
        # result = databaseException(exp)
    connections[model_name].close()
    return result

def getNGByLine_(model_name, process_cd, start_time, end_time):
    result = []
    try:
        # 从config文件中取得line数组
        database_list = get_config("database")
        lineArr = []

        # 根据model_name和process_cd获取limit
        for item in database_list:
            if item["MODEL"] == model_name:
                for dataItem in item["DATA"]:
                    if dataItem["PROCESS"] == process_cd:
                        limit = dataItem["LIMIT"]
                        break

        for row in database_list:
            if row['MODEL'] == model_name:
                # 从配置文件里取得LINE
                lineArr = row['LINE']
                break
        cur = connections[model_name].cursor()
        sql = "SELECT line_cd, COUNT (B.line_cd) FROM (  \
                    SELECT DISTINCT A .serial_cd,A .judge_text,A .line_cd \
                    FROM ( SELECT DISTINCT (i.serial_cd),i.process_at,i.judge_text,P .line_cd \
                    FROM t_insp_" + model_name + " i,m_process P WHERE i.proc_uuid = P .proc_uuid \
                    AND P .line_cd IN ( %s ) AND P .Process_cd = '(process_cd)' \
                    AND i.process_at >= '(start_time)' \
                    AND i.process_at <= '(end_time)' \
                    ORDER BY i.process_at DESC LIMIT '(LIMIT)') AS A \
                    ORDER BY A .judge_text) AS B GROUP BY B.line_cd; "
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace("(process_cd)", process_cd).replace("(start_time)", start_time).replace("(end_time)", end_time) \
            .replace("(LIMIT)", str(limit))
        cur.execute(sql, lineArr)
        rows = cur.fetchall()
        count = 0
        for line in lineArr:
            if checkExist(line, rows):
                for row in rows:
                    if line == row[0]:
                        count = int(row[1])
                        break
            else:
                count = 0
            result.append(count)
    except BaseException as exp:
        print(exp)
        # result = databaseException(exp)
    connections[model_name].close()
    return result

def getJIG_NGByLine(model_name, process_cd, limit, start_time, end_time):
    result = []
    try:
        # 从config文件中取得line数组
        database_list = get_config("database")
        lineArr = []
        for row in database_list:
            if row['MODEL'] == model_name:
                # 从配置文件里取得LINE
                lineArr = row['LINE']
                break
        cur = connections[model_name].cursor()
        # sql = "SELECT DISTINCT (i.serial_cd),i.judge_text,P .line_cd \
        #     FROM t_insp_"+ model_name +" i,m_process P WHERE i.proc_uuid = P .proc_uuid AND P .line_cd IN ( %s ) \
        #     AND P .Process_cd = '(process_cd)' AND i.process_at >= '(start_time)' \
        #     AND i.process_at <= '(end_time)'ORDER BY i.judge_text DESC LIMIT '(LIMIT)';"

        sql = "SELECT DISTINCT (i.serial_cd),i.process_at,i.judge_text,P .line_cd \
                    FROM t_insp_" + model_name + " i,m_process P WHERE i.proc_uuid = P .proc_uuid AND P .line_cd IN ( %s ) \
                    AND P .Process_cd = '(process_cd)' AND i.process_at >= '(start_time)' \
                    AND i.process_at <= '(end_time)'ORDER BY i.process_at DESC LIMIT '(LIMIT)';"
        sql = sql % ','.join(['%s'] * len(lineArr))
        sql = sql.replace("(process_cd)", process_cd).replace("(start_time)", start_time).replace("(end_time)",end_time) \
            .replace("(LIMIT)", str(limit))
        cur.execute(sql, lineArr)
        rows = cur.fetchall()

        rows_list = []
        serial_cd_list = []
        for row in rows:
            if not row[0] in serial_cd_list:
                serial_cd_list.append(row[0])
                rows_list.append(row)

        ng_list = []
        in_list = []
        ng_count = 0
        in_count = 0
        for item in lineArr:
            for row in rows_list:
                if row[3] == item and int(row[2]) == 1:
                    ng_count = ng_count + 1
                if row[3] == item:
                    in_count = in_count + 1
            ng_list.append(ng_count)
            in_list.append(in_count)
            ng_count = 0
            in_count = 0
    except BaseException as exp:
        print(exp)
        # result = databaseException(exp)
    connections[model_name].close()
    return ng_list, in_list

def checkExist(line, lines):
    flag = False
    for item in lines:
        if item[0] == line:
            flag = True
    return flag



def get_real_data(dataList, mix_data, str_inspect,JIG_S):
    # 1. 去除小于最低データ数的数据
    fin_dataList = []
    fin_dataListResult = get_dataListResult(dataList)
    for fin_data in fin_dataListResult:
        if fin_data['in'] > mix_data:
            count = 0
            for item in dataList:
                count = count + 1
                if item['line_cd'] == fin_data['line_cd'] and item['station_slot'] == fin_data['station_slot']:
                    fin_dataList.append(item)

    # 2. 去除不感兴趣的数据
    inspect_list = get_inspect_list(str_inspect)
    sec_dataList = []
    for item in fin_dataList:
        if item["inspect_cd"] in inspect_list:
            sec_dataList.append(item)

    # 3. 去除yeild大于JIG_S的数据
    thr_dataList = []
    thr_dataListResult = get_dataListResult(sec_dataList)
    for thr_data in thr_dataListResult:
        if float(thr_data['yield']) < JIG_S:
            for item in sec_dataList:
                if item['line_cd'] == thr_data['line_cd'] and item['station_slot'] == thr_data['station_slot']:
                    thr_dataList.append(item)

    # 4. 去除不属于inspect text范围的数据
    for_dataList = []
    for item in thr_dataList:
        try:
            upper, lower = get_inspect_border_list(item['inspect_cd'], str_inspect)
            if float(item['inspect_text']) > float(upper) or float(item['inspect_text']) < float(lower):
                for_dataList.append(item)
        except ValueError:
            pass
        # if ':' not in item['inspect_text']:
        #     upper, lower = get_inspect_border_list(item['inspect_cd'], str_inspect)
        #     if float(item['inspect_text']) > float(upper) or float(item['inspect_text']) < float(lower):
        #         for_dataList.append(item)

    # 5. 去除剩余数据中judge_text为0的数据
    fiv_dataList = []
    for item in for_dataList:
        if item['judge_text'] == '1':
            fiv_dataList.append(item)

    return fiv_dataList







def getDataListResult(dataList_, JIG_S_=0):
    line_cd_list_ = []
    serial_cd_list_1_ = []
    serial_cd_list_2_ = []
    JIG_list_ = []
    dataListResult_ = []
    for row in dataList_:
        if not row["line_cd"] in line_cd_list_:
            line_cd_list_.append(row["line_cd"])
    for item in line_cd_list_:
        for row_1 in dataList_:
            if item == row_1["line_cd"]:
                if not row_1["station_slot"] in JIG_list_:
                    JIG_list_.append(row_1["station_slot"])
        for JIG_item in JIG_list_:
            IN_ = 0
            NG_ = 0
            for row_ in dataList_:
                if row_["line_cd"] == item and row_["station_slot"] == JIG_item and int(row_["judge_text"]) == 1:
                    if not row_["serial_cd"] in serial_cd_list_1_:
                        serial_cd_list_1_.append(row_["serial_cd"])
                        NG_ = NG_ + 1
                if row_["line_cd"] == item and row_["station_slot"] == JIG_item:
                    if not row_["serial_cd"] in serial_cd_list_2_:
                        serial_cd_list_2_.append(row_["serial_cd"])
                        IN_ = IN_ + 1
            if IN_ == 0:
                Yield_ = 0
            else:
                Yield_ = float('%.2f' % (100 * ((IN_ - NG_) / IN_)))
            if JIG_S_ != 0:
                if Yield_ < JIG_S_:
                    dataListResult_.append(
                        {"line_cd": item, "station_slot": JIG_item, "ng_count": NG_, "in": IN_, "yield": Yield_})
            else:
                dataListResult_.append(
                    {"line_cd": item, "station_slot": JIG_item, "ng_count": NG_, "in": IN_, "yield": Yield_})
        JIG_list = []
    return dataListResult_

def txt_wrap_by(start_str, end, html):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()

def get_inspect_border_list(inspect_cd, str_inspect):
    # a = 'OVEN_ED_TIME[10:20],OVEN_ST_TIME[20:30]'
    a_ = str_inspect.split(',')
    upper = ''
    lower = ''
    b = []
    for item in a_:
        if inspect_cd == str(re.findall(r'(.*)\[', item)[0]):
            newsDate = txt_wrap_by("[", "]", item).split(':')
            upper = newsDate[0]
            lower = newsDate[1]
            # b.append({'inspect_cd': re.findall(r'(.*)\[', item)[0], "inspect_s": newsDate[0], "inspect_e": newsDate[1]})
    return upper, lower

def get_inspect_list(str_inspect):
    a_ = str_inspect.split(',')
    upper = ''
    lower = ''
    b = []
    for item in a_:
        b.append(re.findall(r'(.*)\[', item)[0])
    return b

def get_obj(dataList):
    ng_obj = {}
    in_obj = {}
    for item in dataList:
        line_cd = item["line_cd"]
        station_slot = item["station_slot"]
        judge_text = item["judge_text"]
        if judge_text == '1':
            if line_cd not in ng_obj.keys():
                ng_obj[line_cd] = [station_slot]
            else:
                ng_obj[line_cd].append(station_slot)
        else:
            if line_cd not in in_obj.keys():
                in_obj[line_cd] = [station_slot]
            else:
                in_obj[line_cd].append(station_slot)
    return ng_obj, in_obj

def get_dataListResult(dataList):
    line_cd = ""
    station_slot = ""
    judge_text = ""
    num = 0
    newlist = []
    for item in dataList:
        judge_text = item["judge_text"]
        if item["line_cd"] != line_cd:
            newitem = {
                'line_cd': item["line_cd"],
                'station_slot': item["station_slot"],
                'ng': 1,
                'in': 1
            }
            newlist.append(newitem)
            line_cd = item["line_cd"]
            station_slot = item["station_slot"]
            num += 1
        else:
            if item["station_slot"] == station_slot:
                if judge_text == '1':
                    newlist[num - 1]["ng"] += 1
                newlist[num - 1]["in"] += 1
            else:
                newitem = {
                    'line_cd': item["line_cd"],
                    'station_slot': item["station_slot"],
                    'ng': 1,
                    'in': 1
                }
                newlist.append(newitem)
                line_cd = item["line_cd"]
                station_slot = item["station_slot"]
                num += 1
    fin_result = []
    for item in newlist:
        ng_count = int(item['ng'])
        in_count = int(item['in'])
        if in_count == 0:
            yield_percent = 0.0
        else:
            yield_percent = float('%.2f' % (100 * ((in_count - ng_count) / in_count)))
        fin_result.append({'line_cd':item['line_cd'],'station_slot':item['station_slot'],'ng':ng_count,'in':in_count,'yield':yield_percent})
    return fin_result
    # fin_result = []
    # # result = []
    # # line_List = []
    # # for item in dataList:
    # #     if not item['line_cd'] in line_List:
    # #         line_List.append(item['line_cd'])
    # # for line in line_List:
    # #     station_cdList = []
    # #     for item in dataList:
    # #         if item['line_cd'] == line:
    # #             if not item['station_slot'] in station_cdList:
    # #                 station_cdList.append(item['station_slot'])
    # #     result.append({'line_cd':line,'station_slot_list':station_cdList})
    #
    # obj = {}
    # result = []
    # for item in dataList:
    #     line_cd = item["line_cd"]
    #     station_slot = item["station_slot"]
    #     if line_cd not in obj.keys():
    #         obj[line_cd] = [station_slot]
    #     else:
    #         obj[line_cd].append(station_slot)
    # for key, value in obj.items():
    #     result.append({'line_cd': key, 'station_slot_list': value})
    #     # print(key)
    # for data in result:
    #     for station_slot in data['station_slot_list']:
    #         # print(data['line_cd'])
    #         # print(station_slot)
    #         in_count = 0
    #         ng_count = 0
    #         yield_percent = 0
    #         for item in dataList:
    #             if item['line_cd'] == data['line_cd'] and item['station_slot'] == station_slot:
    #                 if item['judge_text'] == '1':
    #                     ng_count = ng_count + 1
    #                 in_count = in_count + 1
    #             if in_count == 0:
    #                 yield_percent = 0.0
    #             else:
    #                 yield_percent = float('%.2f' % (100 * ((in_count - ng_count) / in_count)))
    #         fin_result.append({'line_cd':data['line_cd'],'station_slot':station_slot,'ng':ng_count,'in':in_count,'yield':yield_percent})
    # return fin_result


if __name__ == '__main__':
    dataList = [{'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K711', 'judge_text': '0', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K712', 'judge_text': '1', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K713', 'judge_text': '0', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K714', 'judge_text': '1', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K715', 'judge_text': '0', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K716', 'judge_text': '1', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K717', 'judge_text': '0', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K718', 'judge_text': '1', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'},
                {'line_cd': 'L01', 'station_slot': '22', 'serial_cd': 'GH983018AGSJL4K719', 'judge_text': '0', 'process_at': '2018-08-05 12:21:28', 'inspect_cd': 'OVEN_ST_TIME', 'inspect_text': '12.00'}
                ]


    # for item in dataList:
    #     print(item)


    # {'name':'L01','sec':'L01-1','num':2}
    line_cd=""
    station_slot=""
    judge_text=""
    in_num=0
    ng_num=0
    num=0
    newlist=[]
    for item in dataList:
        judge_text = item["judge_text"]
        if item["line_cd"]!=line_cd:
            newitem={
                'line_cd':item["line_cd"],
                'station_slot': item["station_slot"] ,
                'ng':1,
                'in':1
            }
            newlist.append(newitem)
            line_cd=item["line_cd"]
            station_slot=item["station_slot"]

            num+=1
        else:
            if item["station_slot"] == station_slot:
                if judge_text == '1':
                    newlist[num - 1]["ng"] += 1
                newlist[num-1]["in"]+=1
            else:
                newitem = {
                    'line_cd': item["line_cd"],
                    'station_slot': item["station_slot"],
                    'ng': 1,
                    'in': 1
                }
                newlist.append(newitem)
                line_cd = item["line_cd"]
                station_slot = item["station_slot"]
                num += 1
    for item in newlist:
        print(item)





























    # import sqlite3
    # conn = sqlite3.connect('D:\项目汇总\SisterSystem\data.db')
    # print("Opened database successfully")
    # cur = conn.cursor()
    # cur.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'data'")
    # if not cur.fetchone():
    #     conn.execute('''CREATE TABLE data
    #     (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     line_cd varchar(40),
    #     partsserial_cd varchar(40),
    #     serial_cd varchar(40),
    #     judge_text varchar(40),
    #     process_at varchar(40),
    #     inspect_cd varchar(40),
    #     inspect_text varchar(40)
    #     );''')
    #     print("Table created successfully")
    # sql = 'INSERT INTO data (line_cd, partsserial_cd, serial_cd, judge_text, process_at, inspect_cd, inspect_text) VALUES (?,?,?,?,?,?,?);'
    # cur.executemany(sql, dataList)
    # conn.commit()
    # conn.close()

    # result = []
    # for item in dataList:
    #     line_cd = item["line_cd"]
    #     station_slot = item["station_slot"]
    #     if line_cd not in obj.keys():
    #         obj[line_cd] = [station_slot]
    #     else:
    #         obj[line_cd].append(station_slot)
    #
    # for key, value in obj.items():
    #     for val in value:
    #         print(key,val)
    #
    #         for item in dataList:
    #             str = item['line_cd'] + "_" + item['station_slot']
    #             if str == (key + "_" + val) and item['judge_text'] == '1':









