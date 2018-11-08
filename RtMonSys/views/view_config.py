# * coding:utf-8 *
# Author    : Administrator
# Createtime: 8/5/2018

from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from RtMonSys.models import model_config
from RtMonSys.models.models_logger import Logger
import json

def go_config(request):
    Logger.write_log("进入config界面")
    return render(request, 'Config.html')

def init_config(request):
    Logger.write_log("初始化config数据")
    result = model_config.get_config()
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)