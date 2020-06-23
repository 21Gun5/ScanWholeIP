#encoding=utf-8
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




# # 4
# import threading
# import queue
# import time
#
# class server(threading.Thread):
#     def __init__(self,que):
#         threading.Thread.__init__(self)
#         self.queue = que
#     def run(self):
#         global ip_list
#         count = 0
#         for i in ip_list:
#             # if queue.qsize
#             item = "产品%s\n"%str(i)
#
#             self.queue.put(item)
#             print(item)
#             time.sleep(0.1)
#
# class Consumer(threading.Thread):
#     def __init__(self,que):
#         threading.Thread.__init__(self)
#         self.queue = que
#     def run(self):
#         while True:
#             time.sleep(0.5)
#             if self.queue.empty():
#                 break
#             item = self.queue.get()
#             print("%s 消耗 %s\n"%(self.getName(),item))
#             self.queue.task_done()
#         return
#
# if __name__ == '__main__':
#     queue = queue.Queue()
#
#     task_list = []
#     for i in range(2):
#         task = Consumer(queue)
#         task_list.append(task)
#
#     ip_list = range(10)
#
#     p = server(queue)
#     p.start()
#
#     for i in task_list:
#         con = Consumer(queue)
#         con.start()
#
#     queue.join()
#
#     print('Done')

# # 5
# from multiprocessing import Pool, Manager
# from time import sleep, time
# import csv
#
# # def init_consumer_data():
# #     for i in range(0, max_consumer_num):
# #         consumer_data[i] = Manager().Queue()
#
# def producer():
#     index = 0
#     for data in ip_list:
#         sleep(0.0003)
#         print('生产: %s' % (data))
#         q = consumer_data[index % max_consumer_num]
#         q.put(data)
#         index += 1
#     for q in consumer_data.itervalues():
#         q.put(None)
#
# def consumer(consumer_id):
#     while True:
#         sleep(0.3)
#         queue = consumer_data[consumer_id]
#         data = queue.get()
#         if data == None:
#             print('结束')
#             result_queue.put(data)
#             break
#         print('consumer_%s 消费: %s' % (consumer_id, data))
#         result_queue.put(data)
#
# # def handler_result():
# #     f = open('test.csv', 'w')
# #     writer = csv.writer(f)
# #     writer.writerow('data')
# #     while True:
# #         data = result_queue.get()
# #         if data == None:
# #             print('结束')
# #             f.close()
# #             break
# #         writer.writerow([data])
# #         print('处理结果:%s' % (data,))
#
#
# ip_list = (i for i in range(0,10))
# consumer_data = {}
# max_consumer_num = 3
# result_queue = Manager().Queue()
#
# if __name__ == '__main__':
#     start_time = time()
#
#     for i in range(0, 3):
#         consumer_data[i] = Manager().Queue()
#
#     pool = Pool(3 + 1)
#     pool.apply_async(producer)
#     for i in range(0, 3):
#         pool.apply_async(consumer, args=(i,))
#     # pool.apply_async(handler_result)
#
#     pool.close()
#     pool.join()
#
#     print('Done:%ss' % (time() - start_time))
#


# # 6
# # encoding=utf-8
# from multiprocessing import Pool, Manager
# from time import sleep, time
# import csv
#
# EMAIL_SOURCE = (i for i in range(0,10))
#
# EMAIL_WORKER_DATA = {}
# MAX_WORKER_NUM = 3
# RESULT_DATA = Manager().Queue()
#
#
#
# def _init_worker_data():
#     for i in range(0, MAX_WORKER_NUM):
#         EMAIL_WORKER_DATA[i] = Manager().Queue()
#
# def _read_email_data():
#     index = 0
#     for data in EMAIL_SOURCE:
#         sleep(0.0003)
#         print('load data: %s' % (data))
#         q = EMAIL_WORKER_DATA[index % MAX_WORKER_NUM]
#         q.put(data)
#         index += 1
#     for q in EMAIL_WORKER_DATA.itervalues():
#         q.put(None)
#
# def _read_worker_data(worker_id):
#     while True:
#         sleep(0.003)
#         q = EMAIL_WORKER_DATA[worker_id]
#         data = q.get()
#         if data == None:
#             print('finished')
#             RESULT_DATA.put(data)
#             break
#         print('%s gets data: %s' % (worker_id, data))
#         RESULT_DATA.put(data)
#
# def _read_result_data():
#     file_name = 'test.csv'
#     f = open(file_name, 'w')
#     writer = csv.writer(f)
#     writer.writerow('data')
#     while True:
#         data = RESULT_DATA.get()
#         if data == None:
#             print('finished')
#             f.close()
#             break
#         writer.writerow([data])
#         print('handled result data:%s' % (data,))
#
# if __name__ == '__main__':
#     start_time = time()
#     _init_worker_data()
#     p = Pool(MAX_WORKER_NUM + 2)
#     p.apply_async(_read_email_data)
#     for i in range(0, MAX_WORKER_NUM):
#         p.apply_async(_read_worker_data, args=(i,))
#     p.apply_async(_read_result_data)
#     p.close()
#     p.join()
#     end_time = time()
#     print('handle time:%ss' % (end_time - start_time))

# # 7
# # encoding=utf-8
# from multiprocessing import Pool, Manager
# from time import sleep, time
# import csv
#
#
# CONSUMER_QUEUE_LIST = {}
# MAX_CONSUMER_NUM = 3
# # RESULT_QUEUE = Manager().Queue()
#
#
# def producer():
#     global ip_list
#     # 如[1,2,3,4,5,6]，3个消费者子进程分得[1,4][2,5][3,6]
#     index = 0
#     for data in ip_list:
#         sleep(0.01)
#         print('生产: %s\n' % (data))
#         q = CONSUMER_QUEUE_LIST[index % MAX_CONSUMER_NUM]
#         q.put(data)
#         index += 1
#     # 添加结束的标记
#     for q in CONSUMER_QUEUE_LIST.itervalues():
#         q.put(None)
#
# def consumer(consumer_id):
#     global ip_list
#     while True:
#         sleep(0.03)
#         q = CONSUMER_QUEUE_LIST[consumer_id]
#         data = q.get()
#         if data == None:
#             print('consumer_%s消费结束\n'%consumer_id)
#             # RESULT_QUEUE.put(data)
#             break
#         print('consumer_%s 消费: %s\n' % (consumer_id, data))
#         # 将3个队列的汇总，好像没什么必要
#         # RESULT_QUEUE.put(data)
#
# # def handle_result():
# #     while True:
# #         data = RESULT_QUEUE.get()
# #         if data == None:
# #             print('处理结束')
# #             break
# #         print('处理结果:%s' % (data,))
#
# if __name__ == '__main__':
#     start_time = time()
#     # 产生IP
#     ip_list = range(0, 10)
#     # 每一个consumer对应一个queue
#     for i in range(0, MAX_CONSUMER_NUM):
#         # key = "consumer" + str(i+1)
#         # CONSUMER_QUEUE_LIST[key] = Manager().Queue()
#         CONSUMER_QUEUE_LIST[i] = Manager().Queue()
#     # 创建进程池并添加target
#     po = Pool(MAX_CONSUMER_NUM + 2)
#     po.apply_async(producer)
#     for i in range(0, MAX_CONSUMER_NUM):
#         po.apply_async(consumer, args=(i,))
#     # po.apply_async(handle_result)
#     # 关闭进程池、等待所有子进程结束
#     po.close()
#     po.join()
#     print('Total time: %ss' % (time() - start_time))

# # 其他测试
# import requests
# url = "http://128.1.0.10"
# response = requests.get(url + '/currentsetting.htm', timeout=0)
# print(response)


# 探测端口是否开启