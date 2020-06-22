import threading
import queue
import time
import scanNetgear
import multiprocessing
import os
import random

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
            time.sleep(0.1) # 控制生产者速度
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
            time.sleep(0.5)
            if self.queue.empty():
                break
            item = self.queue.get()
            ip = item.split()[2]
            print("%-10s处理IP  %-24s 还有%d个\n"%(self.getName(),ip,self.queue.qsize()))
            # scanNetgear.main(ip)
            self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
        return

# class Server_P(multiprocessing.Process):
#     global ip_list
#     def __init__(self,que):
#         multiprocessing.Process.__init__(self)
#         self.queue = que
#     def run(self):
#         for ip in ip_list:
#             time.sleep(0.1) # 控制生产者速度
#             # item = "%-10s产生IP  %s" % (self.getName(),str(ip))
#             item = "%-10s产生IP  %s" % (os.getpid(), str(ip))
#             self.queue.put(item)
#             print(item)
#             # print(self.queue.qsize())
# class Client_P(multiprocessing.Process):
#     def __init__(self,que):
#         multiprocessing.Process.__init__(self)
#         self.queue = que
#     def run(self):
#         while True:
#             time.sleep(0.5)
#             if self.queue.empty():
#                 break
#             item = self.queue.get_nowait()
#             ip = item.split()[2]
#             print("%-10s处理IP  %-24s 还有%d个\n"%(os.getpid(),ip,self.queue.qsize()))
#             # scanNetgear.main(ip)
#             self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
#         return


def producer(name, food, q):
    global ip_list
    for ip in ip_list:
        time.sleep(0.1)  # 控制生产者速度
        item = "%-10s产生IP  %s" % (os.getpid(), str(ip))
        q.put(item)
        print(item)
        # print(self.queue.qsize())


    # for i in range(4):
    #     time.sleep(0.1)
    #     f = '%s生产了%s%s'%(name, i, food)
    #     print(f)
    #     q.put(f)

def consumer(name, q):
    # while True:
    #     food = q.get()
    #     # if q.empty():
    #     #     break
    #     if food is None:
    #         print('%s没有获取到东西！' %(name))
    #         break
    #     print('%s消费了%s' %(name, food))
    #     time.sleep(0.5)


    while True:
        item = q.get()
        #
        # if q.empty():
        #     break
        if item is None:
            break
        ip = item
        print("%-10s处理IP  %-24s 还有%d个\n" % (os.getpid(), ip, -1))
        # scanNetgear.main(ip)
        # q.task_done()  # 此次任务结束，所有任务结束时触发join
        time.sleep(0.5)


# ip_list = generate_BClass_ip(10)

if __name__ == '__main__':
    # 生成IP
    ip_list = generate_BClass_ip(10)
    # ip_list = range(1,11)
    # fp = open("NetGear.txt", "r")
    # lines = fp.readlines()
    # fp.close()
    # ip_list = []
    # for line in lines:
    #     (ip, port, isHttps) = line.split()
    #     if isHttps == 'TRUE':
    #         url = "https://%s:%s" % (ip, port)
    #     else:
    #         url = "http://%s:%s" % (ip, port)
    #     ip_list.append(url)


    # queue = queue.Queue()
    # # queue_P = multiprocessing.Queue()
    #
    # # 服务端，分配IP
    # s = Server(queue)
    # # s = Server_P(queue_P)
    # s.start()
    #
    # # 多个客户端，处理IP
    # client_list = []
    # for i in range(10):
    #     c = Client(queue)
    #     # c = Client_P(queue_P)
    #     client_list.append(c)
    # for c in client_list:
    #     c.start()
    #
    # # 等待s和queue自动结束，c通过break手动结束
    # s.join()
    # queue.join()
    # # queue_P.join()
    # print('Done')

    q = multiprocessing.Queue(20)
    p1 = multiprocessing.Process(target=producer, args=('p1', '包子', q))
    p1.start()
    c1 = multiprocessing.Process(target=consumer, args=('c1', q))
    c2 = multiprocessing.Process(target=consumer, args=('c2', q))
    c1.start()
    c2.start()
    p1.join()
    q.put(None)
    q.put(None)