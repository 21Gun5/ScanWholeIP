#coding=utf-8
import threading
# import queue
import Queue
import time
import scanNetgear
import multiprocessing
import os
import random

from multiprocessing import Manager,Pool
from time import sleep, time

# 产生B类IP

def generate_BClass_ip(a, b, max_num=10):
    # 网络: 2^14-1=16383, 128.1-191.255

    # start = a<<24+b<<16
    # print(start)
    # ret = []
    # for i in range(1, max_num+1):
    #     ret.append(socket.inet_(start + i)
    # return ret

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
                url = "http://" + ip + ":80"
                B_host_list.append(url)
                # 产生指定个数的IP
                if len(B_host_list) == max_num:
                    return B_host_list

# class Server(threading.Thread):
#     global ip_list
#     def __init__(self,que):
#         threading.Thread.__init__(self)
#         self.queue = que
#     def run(self):
#         for ip in ip_list:
#             sleep(0.1) # 控制生产者速度
#             item = "%-10s产生IP  %s" % (self.getName(),str(ip))
#             self.queue.put(item)
#             print(item)
#             # print(self.queue.qsize())
# class Client(threading.Thread):
#     def __init__(self,que):
#         threading.Thread.__init__(self)
#         self.queue = que
#     def run(self):
#         while True:
#             sleep(0.5)
#             if self.queue.empty():
#                 break
#             item = self.queue.get()
#             ip = item.split()[2]
#             print("%-10s处理IP  %-30s 还有%d个\n"%(self.getName(),ip,self.queue.qsize()))
#             scanNetgear.main(ip)
#             self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
#         return

CONSUMER_QUEUE_LIST = {}    # 每个消费者子进程对应一个queue
MAX_CONSUMER_NUM = 4    # 消费者子进程个数
BATCH_NUM = 10 # 一批共有多少个


def producer():
    global ip_list
    # 列表分批处理
    ip_list_batch = []
    for i in range(0, len(ip_list), BATCH_NUM):
        ip_list_batch.append(ip_list[i:i + BATCH_NUM])
    # 为每个消费者分配任务，形式如[1,2,3,4,5,6]，3个消费者子进程分得[1,4][2,5][3,6]
    index = 0
    for data_list in ip_list_batch:
        # sleep(0.1)
        print('生产: %s\n' % (data_list))
        q = CONSUMER_QUEUE_LIST[index % MAX_CONSUMER_NUM]
        q.put(data_list)
        index += 1
    # 添加结束的标记
    for q in CONSUMER_QUEUE_LIST.itervalues():
        q.put(None)
def consumer(consumer_id):
    while True:
        # sleep(0.3)
        q = CONSUMER_QUEUE_LIST[consumer_id]
        data_list = q.get()
        if data_list == None:
            print('consumer_%s消费结束\n'%consumer_id)
            break
        print('consumer_%s 消费: %s\n' % (consumer_id, data_list))
        scanNetgear.main(data_list)
        # scanNetgear2.main(data_list)

if __name__ == '__main__':
    # 生成IP
    # ip_list = generate_BClass_ip(0,0,1000)
    # ip_list = range(1000)
    ip_list = []
    fp = open("NetGear.txt", "r")
    lines = fp.readlines()
    fp.close()
    for line in lines:
        (ip, port, isHttps) = line.split()
        if isHttps == 'TRUE':
            url = "https://%s:%s" % (ip, port)
        else:
            url = "http://%s:%s" % (ip, port)
        # ip_list.append(url)
        if len(ip_list) < 1000:
            ip_list.append(url)

    # 进程池的方式
    start_time = time()
    # 每一个consumer对应一个queue
    for i in range(0, MAX_CONSUMER_NUM):
        CONSUMER_QUEUE_LIST[i] = Manager().Queue()
    # 创建进程池并添加target
    po = Pool(MAX_CONSUMER_NUM + 2)
    po.apply_async(producer)
    for i in range(0, MAX_CONSUMER_NUM):
        po.apply_async(consumer, args=(i,))
    # 关闭进程池、等待所有子进程结束
    po.close()
    po.join()
    print('Total time: %ss' % (time() - start_time))

