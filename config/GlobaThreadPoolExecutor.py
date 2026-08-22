import atexit
from concurrent.futures.thread import ThreadPoolExecutor

"""定义全局线程池"""
GLOBAL_EXECUTOR = ThreadPoolExecutor(max_workers=3, thread_name_prefix="Global_Thread_")

"""注册退出钩子（程序结束时自动清理线程资源）"""
atexit.register(GLOBAL_EXECUTOR.shutdown, wait=True)

"""提供获取出口"""
def get_executor():
    return GLOBAL_EXECUTOR