import threading
import time

def api_mock(text):
    time.sleep(1)
    print(text, "\a")

def thread_test(text):
    for i in range(6):
        api_mock(text)

thread1 = threading.Thread(target=thread_test, args=("HEJ!",))
thread1.start()
time.sleep(1.4)
thread1 = threading.Thread(target=thread_test, args=("KORV",))
thread1.start()

for i in range(100):
    time.sleep(0.1)
    print(i)