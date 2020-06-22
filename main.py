import threading
import queue
import time

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
            self.queue.task_done()  # 此次任务结束，所有任务结束时触发join
        return

if __name__ == '__main__':
    ip_list = generate_BClass_ip(10)
    # ip_list = range(1,11)
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