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
# 不显示因verigy=false的产生的警告
warnings.filterwarnings('ignore')

def send_request(url, index,timeout):
    try:
        if url.find("https") != -1:
            response = requests.get(url + '/currentsetting.htm', timeout=timeout, verify=False)
        else:
            response = requests.get(url + '/currentsetting.htm', timeout=timeout)
    except Exception as e:
        # print("%d %s\n"%(index,e))
        return save_failure_reason(url, str(e), index)
    else:
        # print(response)
        try:
            Firmware = re.search(r'(?<=Firmware=)[._0-9a-zA-Z]*', str(response.content)).group()
            RegionTag = re.search(r'(?<=RegionTag=)[._0-9a-zA-Z]*', str(response.content)).group()
        except Exception as e:
            Firmware = None
            RegionTag = None
        return save_success_info(index,url,Firmware,RegionTag)
def save_success_info(index,url, Firmware,RegionTag):
    mutex.acquire()
    with open('output.txt', 'a+') as f:
        f.write("%-5s %-30s %-20s %s\n" % (index,url, Firmware,RegionTag))
        f.close()
    mutex.release()
def save_failure_reason(url, errorInfo,index):
    mutex.acquire()
    with open('output.txt', 'a+') as f:
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
    pass