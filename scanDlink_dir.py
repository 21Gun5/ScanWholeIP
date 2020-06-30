#coding=utf-8
import requests
import re
import warnings
import ssl
import datetime
import threading
import socket
import time
import fcntl
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
# from concurrent.futures import ThreadPoolExecutor

# 全局变量
mutex = threading.Lock()
thread_number = 300  # 控制线程数
total_item = 0
success_item = 0
FINGER_PRINT = "/HNAP1/"
OUTPUT_FILE = "output-dlink-dir.txt"

# 不显示因verigy=false的产生的警告
warnings.filterwarnings('ignore')


def get_string(data, start, end):
	if data.upper().find(start.upper())== -1:
		return ""
	temp = data[data.upper().find(start.upper())+len(start):]
	if temp.upper().find(end.upper())== -1:
		return ""
	value = temp[:temp.upper().find(end.upper())]
	return value
def host_is_alive(url):
    if url.find("https://") > -1:
        ip = url.replace("https://",'')
        port = 443
        s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    else:
        ip = url.replace("http://",'')
        port = 80
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((ip, port))
    except Exception as e:
        # print("%s %d"%(url,0))
        return False
    else:
        # print("%s %d" % (url, 1))
        return True

def send_request(url, index,timeout):
    # # 主机不存活直接return
    if not host_is_alive(url):
        return
    try:
        # 无论https与否，都不验证
        response = requests.get(url + FINGER_PRINT, timeout=timeout, verify=False)
    except Exception as e:
        return
        # return save_failure_reason(url, str(e), index)
    else:
        # 找不到就找不到，为空，若用正则的research，找不到会异常
        ModelName = get_string(str(response.content).replace("\r", "\n"), '<ModelName>', '</ModelName>')
        FirmwareVersion = get_string(str(response.content).replace("\r", "\n"), '<FirmwareVersion>', '</FirmwareVersion>')
        # 两者皆为空则ret
        if ModelName == "" and FirmwareVersion == "":
            return
        return save_success_info(index,url,ModelName,FirmwareVersion)
def save_success_info(index,url, Firmware,RegionTag):
    mutex.acquire()
    with open(OUTPUT_FILE, 'a+') as f:
        f.write("%-5s %-30s %-20s %s\n" % (index,url, Firmware,RegionTag))
        f.close()
    mutex.release()
def save_failure_reason(url, errorInfo,index):
    mutex.acquire()
    with open(OUTPUT_FILE, 'a+') as f:
        f.write("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
        f.close()
    mutex.release()

def main(url_list):
    executor = ThreadPoolExecutor(max_workers=thread_number)
    task_list = []
    for i in url_list:
        task = executor.submit(send_request, i, str(url_list.index(i)+1),3)
        task_list.append(task)
    wait(task_list, return_when=ALL_COMPLETED)

if __name__ == '__main__':
    # pass
    # send_request("http://66.183.0.10",0,3)
    send_request("http://66.183.152.90:8080", 0, 3) # 可成功，注意端口8080
    # res = requests.get("http://66.183.152.90:8080/HNAP1/",verify=False)
    # print(res.content)

