# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
from RtMonSys.models import models_common, model_setting
import json


def getSerialDetail(model_name,name,limit, process_cd, datatype_id, line_cd,start_time, end_time):
    result = []
    try:
        # allJson = json.loads(str_allJson)
        allJson = models_common.getDetailList_update3(model_name,name,line_cd, process_cd, datatype_id, limit, start_time, end_time)
        serial_cd_list = []
        process = ''

        for item in allJson:
            if line_cd == item['line_cd'] and item['judge_text'] == '1':
                if not item['serial_cd'] in serial_cd_list:
                    serial_cd_list.append(item['serial_cd'])
        for serial_cd in serial_cd_list:
            count = 0
            for item in allJson:
                if item['serial_cd'] == serial_cd and item['judge_text'] == '1':
                    process = item['process_at']
                    count = count + 1
            result.append({"serial_cd": serial_cd, "ng_count": count, "process_at": process})
        # row = model_setting.getProcess(model_name, process_cd)
        # process_name = row[0]['PROCESS_NAME']
        # limit = row[0]['LIMIT']
        # inspect = (row[0]['INSPECT']).split(',')
        # cur = connections[model_name].cursor()
        # sql = "SELECT \
        #             serial_cd,\
        #             inspect_cd, \
        #             process_at \
        #         FROM\
        #             (\
        #         SELECT DISTINCT \
        #             T1.serial_cd,\
        #             inspect_cd ,\
        #             d.process_at \
        #         FROM\
        #             (\
        #         SELECT \
        #             serial_cd,\
        #             judge_text,\
        #             insp_seq \
        #         FROM\
        #             (\
        #         SELECT DISTINCT \
        #             i.serial_cd,\
        #             i.process_at,\
        #             i.judge_text, \
        #             i.insp_seq, \
        #             ROW_NUMBER ( ) OVER ( PARTITION BY serial_cd ORDER BY process_at DESC ) RANK \
        #         FROM \
        #             t_insp_" + model_name + " i,\
        #             m_process p \
        #         WHERE \
        #             i.proc_uuid = p.proc_uuid \
        #             AND p.line_cd = '(line_cd)' \
        #             AND p.process_cd = '(process_cd)' \
        #             AND i.process_at >= '(start_time)' \
        #             AND i.process_at <= '(end_time)' \
        #         ORDER BY \
        #             i.process_at DESC \
        #             LIMIT (LIMIT) \
        # 	        ) BASE \
        #         WHERE \
        #             RANK = 1 \
        #             AND judge_text = '1' \
        #             ) T1 \
        #             INNER JOIN (\
        #         SELECT DISTINCT \
        #             f.partsserial_cd AS station_slot,\
        #             f.serial_cd,\
        #             f.process_at \
        #         FROM \
        #             m_process p,\
        #             t_faci_" + model_name + " f \
        #         WHERE \
        #             f.proc_uuid = p.proc_uuid \
        #             AND p.Process_cd = '(process_cd)' \
        #             AND f.datatype_id = '(datatype_id)' \
        #             ) T2 ON T1.serial_cd = T2.serial_cd \
        #         LEFT JOIN t_data_" + model_name + " d ON T1.insp_seq = d.insp_seq \
        #         AND d.judge_text = '1' \
        #         WHERE \
        #             T2.station_slot = '(station_slot)' \
        #             AND T1.judge_text = '1' \
        #             ) MAIN \
        #         GROUP BY \
        #             serial_cd,inspect_cd,process_at \
        #         ORDER BY serial_cd"
        # sql = sql.replace("(process_cd)", process_name).replace("(start_time)", start_time).replace("(end_time)", end_time) \
        #     .replace("(datatype_id)", datatype_id).replace("(LIMIT)", str(limit)).replace("(line_cd)", line_cd) \
        #     .replace("(station_slot)", station_slot)
        # cur.execute(sql)
        # rows = cur.fetchall()
        # # rows = [('GH9830188W3JL4K7K', 'OVEN_ED_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)'),
        # #         ('GH9830188W3JL4K7K', 'OVEN_ST_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)'),
        # #         ('GH9830188W3JL4K8K', 'OVEN_ST_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)'),
        # #         ('GH9830188W3JL4K8K', 'OVEN_ST_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)'),
        # #         ('GH9830188W3JL4K9K', 'OVEN_ST_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)'),
        # #         ('GH9830188W3JL4K9K', 'OVEN_ST_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)'),
        # #         ('GH9830188W3JL4K9K', 'OVEN_ST_TIME', 'datetime.datetime(2018, 8, 5, 12, 34, 3)')]
        # serial_cd_list = []
        # process = ''
        # for row in rows:
        #     if not row[0] in serial_cd_list:
        #         serial_cd_list.append(row[0])
        # for i in serial_cd_list:
        #     count = 0
        #     for row in rows:
        #         if row[0] == i:
        #             process = str(row[2])
        #             if row[1] in inspect:
        #                 count = count + 1
        #     result.append({"serial_cd": i, "ng_count": count,"process_at":process})
    except BaseException as exp:
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result