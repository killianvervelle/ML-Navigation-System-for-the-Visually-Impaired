import time
from concurrent.futures import ThreadPoolExecutor

def a(i):
    time.sleep(i)
    print(i)

ThreadPoolExecutor().submit(a, 3)
print("abc")