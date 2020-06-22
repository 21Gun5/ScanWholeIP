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
import csv

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
                ip = "http://" + ip
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
            sleep(0.1) # 控制生产者速度
            item = "%-10s产生IP  %s" % (self.getName(),str(ip))
            self.queue.put(item)
            print(item)
            # print(self.queue.qsize())
class Client(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.queue = que
    def run(self):
        while True:
            sleep(0.5)
            if self.queue.empty():
                break
            item = self.queue.get()
            ip = item.split()[2]
            print("%-10s处理IP  %-30s 还有%d个\n"%(self.getName(),ip,self.queue.qsize()))
            scanNetgear.main(ip)
            self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
        return

class Server_P(multiprocessing.Process):
    global ip_list
    def __init__(self,que):
        multiprocessing.Process.__init__(self)
        self.queue = que
    def run(self):
        for ip in ip_list:
            time.sleep(0.1) # 控制生产者速度
            # item = "%-10s产生IP  %s" % (self.getName(),str(ip))
            item = "%-10s产生IP  %s" % (os.getpid(), str(ip))
            self.queue.put(item)
            print(item)
            # print(self.queue.qsize())
class Client_P(multiprocessing.Process):
    def __init__(self,que):
        multiprocessing.Process.__init__(self)
        self.queue = que
    def run(self):
        while True:
            time.sleep(0.5)
            if self.queue.empty():
                break
            item = self.queue.get_nowait()
            ip = item.split()[2]
            print("%-10s处理IP  %-24s 还有%d个\n"%(os.getpid(),ip,self.queue.qsize()))
            # scanNetgear.main(ip)
            self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
        return



CONSUMER_QUEUE_LIST = {}
MAX_CONSUMER_NUM = 3
# RESULT_QUEUE = Manager().Queue()


def producer():
    global ip_list
    # 如[1,2,3,4,5,6]，3个消费者子进程分得[1,4][2,5][3,6]
    index = 0
    for data in ip_list:
        sleep(0.1)
        print('生产: %s\n' % (data))
        q = CONSUMER_QUEUE_LIST[index % MAX_CONSUMER_NUM]
        q.put(data)
        index += 1
    # 添加结束的标记
    for q in CONSUMER_QUEUE_LIST.itervalues():
        q.put(None)

def consumer(consumer_id):
    global ip_list
    while True:
        sleep(0.3)
        q = CONSUMER_QUEUE_LIST[consumer_id]
        data = q.get()
        if data == None:
            print('consumer_%s消费结束\n'%consumer_id)
            # RESULT_QUEUE.put(data)
            break
        print('consumer_%s 消费: %s\n' % (consumer_id, data))
        scanNetgear.main(data)
        # 将3个队列的汇总，好像没什么必要
        # RESULT_QUEUE.put(data)




if __name__ == '__main__':
    # 生成IP
    # ip_list = generate_BClass_ip(10)
    # ip_list = range(1,11)

    fp = open("NetGear.txt", "r")
    lines = fp.readlines()
    fp.close()
    ip_list = []
    for line in lines:
        (ip, port, isHttps) = line.split()
        if isHttps == 'TRUE':
            url = "https://%s:%s" % (ip, port)
        else:
            url = "http://%s:%s" % (ip, port)
        ip_list.append(url)

    # # 多线程的方式
    # queue = Queue.Queue()
    # # queue_P = multiprocessing.Queue()
    #
    # # 服务端，分配IP
    # s = Server(queue)
    # # s = Server_P(queue)
    # s.start()
    #
    # # 多个客户端，处理IP
    # client_list = []
    # for i in range(10):
    #     c = Client(queue)
    #     # c = Client_P(queue)
    #     client_list.append(c)
    # for c in client_list:
    #     c.start()
    # # 等待s和queue自动结束，c通过break手动结束
    # s.join()
    # queue.join()
    # # queue_P.join()
    # print('Done')

    # 进程池的方式
    start_time = time()
    # 产生IP
    # ip_list = range(0, 10)
    # 每一个consumer对应一个queue
    for i in range(0, MAX_CONSUMER_NUM):
        # key = "consumer" + str(i+1)
        # CONSUMER_QUEUE_LIST[key] = Manager().Queue()
        CONSUMER_QUEUE_LIST[i] = Manager().Queue()
    # 创建进程池并添加target
    po = Pool(MAX_CONSUMER_NUM + 2)
    po.apply_async(producer)
    for i in range(0, MAX_CONSUMER_NUM):
        po.apply_async(consumer, args=(i,))
    # po.apply_async(handle_result)
    # 关闭进程池、等待所有子进程结束
    po.close()
    po.join()
    print('Total time: %ss' % (time() - start_time))

