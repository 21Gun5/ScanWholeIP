#coding=utf-8
import requests
import re
import warnings
import ssl
import datetime
import threading
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
empty_item = 0
# 不显示因verigy=false的产生的警告
warnings.filterwarnings('ignore')

def send_request(url, index,timeout):
    global empty_item
    try:
        if url.find("https") != -1:
            response = requests.get(url + '/currentsetting.htm', timeout=timeout, verify=False)
        else:
            response = requests.get(url + '/currentsetting.htm', timeout=timeout)
    except Exception as e:
        # return
        return save_failure_reason(url, str(e), index)
    else:
        try:
            Firmware = re.search(r'(?<=Firmware=)[._0-9a-zA-Z]*', str(response.content)).group()
            RegionTag = re.search(r'(?<=RegionTag=)[._0-9a-zA-Z]*', str(response.content)).group()
        except Exception as e:
            Firmware = None
            RegionTag = None
            empty_item +=1
        return save_success_info(index,url,Firmware,RegionTag)
def save_success_info(index,url, Firmware,RegionTag):
    global success_item
    success_item += 1



    mutex.acquire()
    with open('success_output.txt', 'a+') as f:
        # fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write("%-5s %-30s %-20s %s\n" % (index,url, Firmware,RegionTag))
        # print("%-5s %-30s %-20s %s\n" % (index,url, Firmware,RegionTag))
        f.close()
        # fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    mutex.release()
def save_failure_reason(url, errorInfo,index):
    mutex.acquire()
    with open('success_output.txt', 'a+') as f:
        f.write("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
        f.close()
    mutex.release()

    # global failure_item
    # failure_item += 1

    # errorFile = what_error(errorInfo)
    # # mutex.acquire()
    # f2 = open(errorFile, 'a+')
    # f2.write("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
    # # print("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
    # f2.close()
    # # mutex.release()

def main(ip):
    executor = ThreadPoolExecutor(max_workers=thread_number)
    executor.submit(send_request, ip, 0, 3)