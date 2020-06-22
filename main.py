import threading
import queue
import time


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

# 解决RemoteDisconnected/SSLError所需
CIPHERS = ('ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5')
class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests.
    """
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)
class Ssl3HttpAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use SSLv3."""

    def init_poolmanager(self, connections, maxsize, block=False):
        # self.poolmanager = PoolManager(
        #     num_pools=connections, maxsize=maxsize,
        #     block=block, ssl_version=ssl.PROTOCOL_SSLv3)
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_TLS)
        # PROTOCOL_SSLv23
        # PROTOCOL_SSLv2
        # PROTOCOL_SSLv3
        # PROTOCOL_TLSv1
        # PROTOCOL_TLSv1_1
        # PROTOCOL_TLSv1_2
        # PROTOCOL_TLS
        # PROTOCOL_TLS_CLIENT
        # PROTOCOL_TLS_SERVER

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
def send_request_OSError(url, index,timeout):
    global empty_item
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15}"
    }
    try:
        if url.find("https") != -1:
            response = requests.get(url + '/currentsetting.htm', headers=header,timeout=timeout, verify=False)
        else:
            response = requests.get(url + '/currentsetting.htm', headers=header,timeout=timeout)
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
def send_request_RemoteDisconnected(url, index,timeout):

    global empty_item

    s = requests.Session()
    s.mount('https://some-3des-only-host.com', DESAdapter())

    try:
        if url.find("https") != -1:
            response = s.get(url + '/currentsetting.htm', timeout=timeout, verify=False)
        else:
            response = s.get(url + '/currentsetting.htm', timeout=timeout)
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
def send_request_SSLError(url, index,timeout):
    global empty_item

    s = requests.Session()
    s.mount(url, Ssl3HttpAdapter())

    try:
        if url.find("https") != -1:
            response = s.get(url + '/currentsetting.htm', timeout=timeout, verify=False)
        else:
            response = s.get(url + '/currentsetting.htm', timeout=timeout)
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
            empty_item += 1
        return save_success_info(index, url, Firmware, RegionTag)

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

# 重试Error的请求
def handle_timeout_error(timeout):
    f = open('success_output.txt', 'a+')
    f.write(
        "--------------------------------- retry Connect/ReadTimeoutError (timeout: %d)--------------------------------\n\n" % timeout)
    f.close()

    print(
        "--------------------------------- retry Connect/ReadTimeoutError (timeout: %d)--------------------------------\n\n" % timeout)

    fp = open("failure_ConnectTimeoutError.txt", "r")
    lines = fp.readlines()
    fp.close()

    fp2 = open("failure_Readtimedout.txt", "r")
    lines2 = fp2.readlines()
    fp2.close()

    clear_file_content("failure_ConnectTimeoutError.txt")
    clear_file_content("failure_Readtimedout.txt")
    global failure_ConnectTimeoutError,failure_ReadTimeoutError
    failure_ConnectTimeoutError=0
    failure_ReadTimeoutError=0

    global thread_number
    executor = ThreadPoolExecutor(max_workers=thread_number)
    url_dict = {}
    for line in lines:
        index = line.split()[0]
        url = line.split()[1]
        url_dict[index] = url
    for line in lines2:
        index = line.split()[0]
        url = line.split()[1]
        url_dict[index] = url
    task_list = []
    for item in url_dict.items():
        task = executor.submit(send_request, item[1],item[0],timeout)
        # print(item[0],item[1])
        task_list.append(task)

    wait(task_list, return_when=ALL_COMPLETED)
    return
def handle_SSL_error():
    f = open('success_output.txt', 'a+')
    f.write("--------------------------------- retry SSLError--------------------------------\n\n")
    f.close()

    print("--------------------------------- retry SSLError--------------------------------\n\n")

    fp = open("failure_SSLError.txt", "r")
    lines = fp.readlines()
    fp.close()


    clear_file_content("failure_SSLError.txt")
    global failure_SSLError
    failure_SSLError=0

    global thread_number

    executor = ThreadPoolExecutor(max_workers=thread_number)
    url_dict = {}
    for line in lines:
        index = line.split()[0]
        url = line.split()[1]
        url_dict[index] = url
    task_list = []
    for item in url_dict.items():
        pass
        # print(item[0],item[1])
        # task = executor.submit(send_request_SSLError, item[1], item[0], 3)
        # task_list.append(task)

    wait(task_list, return_when=ALL_COMPLETED)
    return
def handle_OS_error():
    f = open('success_output.txt', 'a+')
    f.write("--------------------------------- retry OSError--------------------------------\n\n")
    f.close()

    print("--------------------------------- retry OSError--------------------------------\n\n")

    fp = open("failure_OSError.txt", "r")
    lines = fp.readlines()
    fp.close()


    clear_file_content("failure_OSError.txt")
    global failure_OSError
    failure_OSError=0

    global thread_number
    executor = ThreadPoolExecutor(max_workers=thread_number)
    url_dict = {}
    for line in lines:
        index = line.split()[0]
        url = line.split()[1]
        url_dict[index] = url
    task_list = []
    for item in url_dict.items():
        # print(item[0],item[1])
        task = executor.submit(send_request_OSError, item[1], item[0], 3)
        # print(item[0],item[1])
        task_list.append(task)

    wait(task_list, return_when=ALL_COMPLETED)
    return
def handle_RemoteDisconnected_error():
    f = open('success_output.txt', 'a+')
    f.write("--------------------------------- retry RemoteDisconnected--------------------------------\n\n")
    f.close()

    print("--------------------------------- retry RemoteDisconnected--------------------------------\n\n")

    fp = open("failure_RemoteDisconnected.txt", "r")
    lines = fp.readlines()
    fp.close()


    clear_file_content("failure_RemoteDisconnected.txt")
    global failure_RemoteDisconnected
    failure_RemoteDisconnected=0

    global thread_number
    executor = ThreadPoolExecutor(max_workers=thread_number)
    url_dict = {}
    for line in lines:
        index = line.split()[0]
        url = line.split()[1]
        url_dict[index] = url
    task_list = []
    for item in url_dict.items():
        # print(item[0],item[1])

        task = executor.submit(send_request_RemoteDisconnected, item[1], item[0], 3)
        task_list.append(task)

    wait(task_list, return_when=ALL_COMPLETED)
    return
def handle_ConnectionResetError_error():
    f = open('success_output.txt', 'a+')
    f.write("--------------------------------- retry ConnectionResetError--------------------------------\n\n")
    f.close()

    print("--------------------------------- retry ConnectionResetError--------------------------------\n\n")

    fp = open("failure_ConnectionResetError.txt", "r")
    lines = fp.readlines()
    fp.close()


    clear_file_content("failure_ConnectionResetError.txt")
    global failure_ConnectionResetError
    failure_ConnectionResetError=0

    global thread_number
    executor = ThreadPoolExecutor(max_workers=thread_number)
    url_dict = {}
    for line in lines:
        index = line.split()[0]
        url = line.split()[1]
        url_dict[index] = url
    task_list = []
    for item in url_dict.items():
        pass
        # print(item[0],item[1])

        # task = executor.submit(send_request3, item[1], item[0], 3)
        # task_list.append(task)

    wait(task_list, return_when=ALL_COMPLETED)
    return

def scan_netgear(ip):
    executor = ThreadPoolExecutor(max_workers=thread_number)
    executor.submit(send_request, ip, 0, 3)











# 全局变量
# client_num = 10

# 产生B类IP
def generate_BClass_ip(max_num=10):
    # 网络: 2^14-1=16383, 128.1-191.255
    B_net_list = []
    for a in range(128,192):
        for b in range(0,256):
            # B类网络号从128.1开始
            if a==128 and b==0:
                continue
            net = str(a)+'.' + str(b)
            B_net_list.append(net)
    # print(len(B_net_list))

    # 主机: 2^16-2, 0.0-255.255
    B_host_list = []
    for net in B_net_list:
        for c in range(0,256):
            for d in range(0,256):
                # 排除本网络及广播地址
                if (c==0 and d==0) or(c==1 and d==1):
                    continue
                ip = net + '.' + str(c) + '.' + str(d)
                B_host_list.append(ip)
                # 产生指定个数的IP
                if len(B_host_list) == max_num:
                    return B_host_list

class Server(threading.Thread):
    global ip_list
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.queue = que
    def run(self):
        for ip in ip_list:
            time.sleep(0.1) # 控制生产者速度
            item = "IP %-15s" % str(ip)
            self.queue.put(item)
            print(item)
            # print(self.queue.qsize())


class Client(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.queue = que
    def run(self):
        while True:
            time.sleep(0.5)
            if self.queue.empty():
                break
            item = self.queue.get()
            print("%-20s 处理 %s 还有%d个\n"%(self.getName(),item,self.queue.qsize()))
            # ip = "http://" + item.split(" ")[1]
            ip = item.split(" ")[1]
            # print(ip)
            scan_netgear(ip)
            self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
        return

if __name__ == '__main__':
    # 生成IP
    # ip_list = generate_BClass_ip(10)
    # ip_list = range(1,11)
    fp = open("NetGear.txt", "r")
    lines = fp.readlines()
    fp.close()
    ip_list = []
    for line in lines:
        total_item += 1
        (ip, port, isHttps) = line.split()
        if isHttps == 'TRUE':
            url = "https://%s:%s" % (ip, port)
        else:
            url = "http://%s:%s" % (ip, port)
        ip_list.append(url)


    queue = queue.Queue()
    # 服务端，分配IP
    s = Server(queue)
    s.start()

    # 多个客户端，处理IP
    client_list = []
    for i in range(10):
        c = Client(queue)
        client_list.append(c)
    for c in client_list:
        c.start()
    
    # 等待s和queue自动结束，c通过break手动结束
    s.join()
    queue.join()
    print('Done')