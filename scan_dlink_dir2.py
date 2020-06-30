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

# 全局变量
mutex = threading.Lock()
thread_number = 300  # 控制线程数
total_item = 0
success_item = 0
FINGER_PRINT = "/HNAP1/"
OUTPUT_FILE = "output_dlink_dir2.txt"

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

def is_host_alive(url):
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

def is_dlink_dir(url):
    res = requests.get(url, timeout=3, verify=False)
    path = "" # 重定向的路径

    # js实现重定向
    if str(res.content).find("window.location.href") > -1:
        path = get_string(str(res.content), 'href = "', '";')  # /cgi-bin/webproc
    elif str(res.content).find("location.replace") > -1:
        # 此情况又有两种：MobileLogin.html和Login.html
        path = get_string(str(res.content), 'else{location.replace("', '")')  # /info/Login.html
    else:
        pass

    # 请求重定向后的真实地址
    res_real = requests.get(url + path, timeout=3, verify=False)
    # 有的能直接搜到字符串，如黄色页面的
    if(str(res_real.content).find("DIR-")) > -1:
        # <a href="http://support.dlink.com" target="_blank">DIR-816</a>
        # <span class="version" id = "Span_FirmwareVersion">1.01TO</span>
        model = get_string(str(res_real.content),'target="_blank">','</a>')
        version = get_string(str(res_real.content),'Span_FirmwareVersion">','</span>')
        return (url,model,version)
    # 有的不能直接搜到，"DIR-"是通过js得到的，如蓝色页面的
    else:
        # 先将HNAP1写死，发现其他的再说
        res_real_2 = requests.get(url+"/HNAP1",timeout=3, verify=False)
        if(str(res_real_2.content).find("DIR-")) > -1:
            model = get_string(str(res_real_2.content), '<ModelName>', '</ModelName>')
            version = get_string(str(res_real_2.content),'<FirmwareVersion>','</FirmwareVersion>')
            return (url,model,version)
        else:
            return False

    # elif(str(res_real.content).find("/js/SOAP/SOAPAction.js")) > -1:
        # # 提取参数，形式：src = "/js/SOAP/SOAPAction.js?v=20190424161124" >
        # # 也不完美，还有这样的/hnap/GetDeviceSettings.xml?v=20140612202951
        # js_args = get_string(str(res_real.content),'/js/SOAP/SOAPAction.js?','"')
        # res_js = requests.get(url+"/js/SOAP/SOAPAction.js?"+js_args,timeout=3, verify=False)
        # # 提取类似HNAP1的path，尽量不写死，万一是其他呢，形式：$.ajax({url:"/HNAP1/",
        # hnap_like_path = get_string(str(res_js.content),'$.ajax({url:"','",')
        # res_real_2 = requests.get(url+hnap_like_path,timeout=3, verify=False)
        # if(str(res_real_2.content).find("DIR-")) > -1:
        #     return True
        # else:
        #     return False

def send_request(url, timeout):
    # 主机是否存活
    if not is_host_alive(url):
        return
    try:
        ret = is_dlink_dir(url)
        if not ret:
            return
    except Exception as e:
        return
    else:
        return save_info(url, ret[1], ret[2])

def save_info(url, model, version):
    mutex.acquire()
    with open(OUTPUT_FILE, 'a+') as f:
        f.write("%-30s %-20s %s\n" % (url, model, version))
        f.close()
    mutex.release()

# def save_failure_reason(url, errorInfo,index):
#     mutex.acquire()
#     with open(OUTPUT_FILE, 'a+') as f:
#         f.write("%-5s %-30s ---- %s \n" % (index, url, errorInfo))
#         f.close()
#     mutex.release()

def main(url_list):
    executor = ThreadPoolExecutor(max_workers=thread_number)
    task_list = []
    for url in url_list:
        task = executor.submit(send_request, url, 3)
        task_list.append(task)
    wait(task_list, return_when=ALL_COMPLETED)

if __name__ == '__main__':
    # pass
    # send_request("http://66.183.0.10",0,3)
    send_request("http://66.183.152.90:8080", 3)  # 可成功，注意端口8080
    # res = requests.get("http://66.183.152.90:8080/HNAP1/",verify=False)
    # print(res.content)

