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
failure_ConnectionResetError = 0
failure_ConnectTimeoutError = 0
failure_NewConnectionError = 0
failure_OSError = 0
failure_ReadTimeoutError = 0
failure_RemoteDisconnected = 0
failure_SSLError = 0
failure_FailedToDecode = 0
failure_OtherError = 0

# 不显示因verigy=false的产生的警告
warnings.filterwarnings('ignore')


# 发起请求、多线程的target
def send_request(url, index,timeout):
    global empty_item
    try:
        if url.find("https") != -1:
            response = requests.get(url + '/currentsetting.htm', timeout=timeout, verify=False)
        else:
            response = requests.get(url + '/currentsetting.htm', timeout=timeout)
    except Exception as e:
        # reason = re.search(r'(?<=Caused by )\w*', str(e)).group()
        # return save_failure_reason(url, reason, index)
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

# 保存信息
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
    # mutex.acquire()
    # with open('success_output.txt', 'a+') as f:
    #     # fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    #     f.write("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
    #     f.close()
    #     # fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    # mutex.release()

    # global failure_item
    # failure_item += 1

    errorFile = what_error(errorInfo)
    # mutex.acquire()
    f2 = open(errorFile, 'a+')
    f2.write("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
    # print("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
    f2.close()
    # mutex.release()

# 其他辅助函数
def clear_file_content(filename):
    with open(filename, 'r+', encoding='utf-8') as f:
        res = f.readlines()
        # print(res)
        f.seek(0)
        f.truncate()
    return
def what_error(errorInfo):
    global failure_ConnectionResetError,failure_ConnectTimeoutError,failure_NewConnectionError,failure_OSError,failure_ReadTimeoutError,\
        failure_RemoteDisconnected,failure_SSLError,failure_FailedToDecode,failure_OtherError

    if errorInfo.find("ConnectTimeoutError") != -1:
        error_file = "failure_ConnectTimeoutError.txt"
        failure_ConnectTimeoutError+=1
    elif errorInfo.find("Read timed out") != -1:
        error_file = "failure_Readtimedout.txt"
        failure_ReadTimeoutError+=1
    elif errorInfo.find("OSError") != -1:
        error_file = "failure_OSError.txt"
        failure_OSError+=1
    elif errorInfo.find("NewConnectionError") != -1:
        error_file = "failure_NewConnectionError.txt"
        failure_NewConnectionError+=1
    elif errorInfo.find("failed to decode") != -1:
        error_file = "failure_failedtodecode.txt"
        failure_FailedToDecode+=1
    elif errorInfo.find("RemoteDisconnected") != -1:
        error_file = "failure_RemoteDisconnected.txt"
        failure_RemoteDisconnected+=1
    elif errorInfo.find("ConnectionResetError") != -1:
        error_file = "failure_ConnectionResetError.txt"
        failure_ConnectionResetError += 1
    elif errorInfo.find("SSLError") != -1:
        error_file = "failure_SSLError.txt"
        failure_SSLError+=1
    else:
        error_file = "failure_otherError.txt"
        failure_OtherError += 1
    return error_file


def main(ip):
    executor = ThreadPoolExecutor(max_workers=thread_number)
    executor.submit(send_request, ip, 0, 3)

    # begin = datetime.datetime.now()
    # fp = open("NetGear.txt", "r")
    # lines = fp.readlines()
    # fp.close()
    #
    # executor = ThreadPoolExecutor(max_workers=thread_number)
    # url_list = []
    # for line in lines:
    #     total_item += 1
    #     (ip, port, isHttps) = line.split()
    #     if isHttps == 'TRUE':
    #         url = "https://%s:%s" % (ip, port)
    #     else:
    #         url = "http://%s:%s" % (ip, port)
    #     url_list.append(url)
    #
    # task_list = []
    # for i in url_list:
    #     task = executor.submit(send_request, i, str(url_list.index(i)+1),3)
    #     task_list.append(task)
    #
    #
    # # 第一波结束
    # wait(task_list, return_when=ALL_COMPLETED)
    #
    #
    # print("time: %f\n" %((datetime.datetime.now() - begin).total_seconds()))
    #
    # f = open('success_output.txt', 'a+')
    # f.write("time: %f\n" % ((datetime.datetime.now() - begin).total_seconds()))
    # f.write("--------------------------------- retry Error --------------------------------\n\n")
    # f.close()
    #
    # # 重试各种error
    # handle_OS_error()
    # handle_RemoteDisconnected_error()
    # # handle_ConnectionResetError_error()#here
    # # handle_SSL_error()#here
    # for i in [5, 8, 12]:
    #     handle_timeout_error(i)
    #
    # print("\ntotal time: %f\n" % ((datetime.datetime.now() - begin).total_seconds()))
    # print(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
    # print("current thread numbers: %d\n" % thread_number)
    # print("total: %d, success: %d(empty:%d), failure: %d\n" % (
    # total_item, success_item, empty_item, total_item - success_item))
    # print(
    #     "ConnectionResetError: %d, ConnectTimeoutError: %d, NewConnectionError: %d, OSError: %d, ReadTimeoutError: %d, RemoteDisconnected: %d, SSLError: %d, FailedToDecode: %d" \
    #     % (failure_ConnectionResetError, failure_ConnectTimeoutError, failure_NewConnectionError, failure_OSError,
    #        failure_ReadTimeoutError, failure_RemoteDisconnected, failure_SSLError, failure_FailedToDecode)
    #     )
    #
    # f = open('success_output.txt', 'a+')
    # f.write("\ntotal time: %f\n" % ((datetime.datetime.now() - begin).total_seconds()))
    # f.write(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
    # f.write("current thread numbers: %d\n"%thread_number)
    # f.write("total: %d, success: %d(empty:%d), failure: %d\n"%(total_item,success_item,empty_item,total_item-success_item))
    # f.write("ConnectionResetError: %d, ConnectTimeoutError: %d, NewConnectionError: %d, OSError: %d, ReadTimeoutError: %d, RemoteDisconnected: %d, SSLError: %d, FailedToDecode: %d"\
    #       %(failure_ConnectionResetError,failure_ConnectTimeoutError,failure_NewConnectionError,failure_OSError,failure_ReadTimeoutError,failure_RemoteDisconnected,failure_SSLError,failure_FailedToDecode)
    #       )
    # f.close()