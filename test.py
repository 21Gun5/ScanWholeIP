# 1
# from queue import Queue
# import threading
#
# class server(threading.Thread):
#     def __init__(self, t_name, queue):
#         threading.Thread.__init__(self, name=t_name)
#         self.data = queue
#
#     def run(self):
#         for i in range(5):
#             print("+ %d\n" % ( i))
#             self.data.put(i)  # 将生产的数据放入队列
#         print("%s finished!\n" % self.getName())
#
# class Consumer(threading.Thread):
#     def __init__(self, t_name, queue):
#         threading.Thread.__init__(self, name=t_name)
#         self.data = queue
#
#     def run(self):
#         for i in range(5):
#             val = self.data.get()  # 拿出已经生产好的数据
#             print("- %d\n" % ( val))
#             self.data.task_done()  # 告诉队列有关这个数据的任务已经处理完成
#         print("%s finished!\n" %  self.getName())
#
# # 主线程
# def main():
#     queue = Queue()
#     server = server('Pro.', queue)
#     consumer = Consumer('Con.', queue)
#     server.start()
#     consumer.start()
#
#     queue.join()  # 阻塞，直到生产者生产的数据全都被消费掉
#     server.join()  # 等待生产者线程结束
#     consumer.join()  # 等待消费者线程结束
#     print('All threads terminate!')
#
# if __name__ == '__main__':
#     main()


# # 2
# #encoding=utf-8
# import threading
# import time
#
#
# #python3中
# from queue import Queue
#
# class server(threading.Thread):
#     def run(self):
#         global queue,ip_list
#         count = 0
#         for i in ip_list:
#             # if queue.qsize() < 5:
#             item = '产品' + str(i+1)
#             print(item)
#             queue.put(item)
#             time.sleep(0.1)
#
#
# class Consumer(threading.Thread):
#     def __init__(self,queue):
#         threading.Thread.__init__(self)
#         self.queue = queue
#
#     #     def run(self):
#     #         while True:
#     #             sleep(0.1)
#     #             if self.queue.empty():
#     #                 break
#     #             item = self.queue.get()
#     #             print("%s %s\n"%(self.getName(),item))
#     #             self.queue.task_done()
#     #         return
#     def run(self):
#         while True:
#             if self.queue.qsize() > 0:
#                 time.sleep(0.5)
#                 if self.queue.empty():
#                     break
#                 item = self.name + '消费了 ' + self.queue.get()
#                 print(item)
#                 self.queue.task_done()  # 告诉队列有关这个数据的任务已经处理完成
#         return
#
#
# if __name__ == '__main__':
#     queue = Queue()
#
#     # ip_list = range(10)
#
#     # for i in range(50):
#     #     queue.put('初始产品'+str(i))
#
#     # p = server()
#     # p.start()
#     # p.join()
#
#     for i in range(10):
#         queue.put(str(i))
#
#     for i in range(2):
#         c = Consumer(queue)
#         c.start()
#         # c.join()
#
#     queue.join()  # 阻塞，直到生产者生产的数据全都被消费掉
#     print(123123)


# # 3
# import threading
# from queue import Queue
#
# class Consumer(threading.Thread):
#     def __init__(self, queue):
#         super().__init__()
#         self.queue = queue
#
#     def run(self):
#         while True:
#             ip = self.queue.get()
#             print("%s消费%s"%(self.getName(),ip))
#             if isinstance(ip, str) and ip == 'end':
#                 break
#         print('%s Bye'%self.getName())
#
#
# def server():
#     list = range(10)
#     queue = Queue()
#
#     # 创建3个客户端
#     client_list = []
#     for i in range(3):
#         client = Consumer(queue)
#         client.start()
#         client_list.append(client)
#
#     # 将IP添加到队列
#     for ip in list:
#         queue.put(ip)
#
#     for client in client_list:
#         queue.put('end')
#     for client in client_list:
#         # join的作用就是为了保证所有的子线程都结束了，再结束父线程
#         client.join()
#
#     print("Done")
#
# if __name__ == '__main__':
#     server()




# 4
import threading
import queue
import time

class server(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.queue = que
    def run(self):
        global ip_list
        count = 0
        for i in ip_list:
            # if queue.qsize
            item = "产品%s\n"%str(i)

            self.queue.put(item)
            print(item)
            time.sleep(0.1)

class Consumer(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.queue = que
    def run(self):
        while True:
            time.sleep(0.5)
            if self.queue.empty():
                break
            item = self.queue.get()
            print("%s 消耗 %s\n"%(self.getName(),item))
            self.queue.task_done()
        return

if __name__ == '__main__':
    queue = queue.Queue()

    task_list = []
    for i in range(2):
        task = Consumer(queue)
        task_list.append(task)

    ip_list = range(10)

    p = server(queue)
    p.start()

    for i in task_list:
        con = Consumer(queue)
        con.start()

    queue.join()

    print('Done')
