from functools import wraps
from time import perf_counter, sleep
def timer(logger=None):
    def timer_deco(func):
        wraps(func)
        def wrapper(*args, **kwargs):
            startTime = perf_counter()
            res = func(*args, **kwargs)
            endTime = perf_counter()
            if logger is None:
                print("FUNCTION [{}] using time: {}".format(func.__name__, endTime-startTime))
            else:
                with open(logger, "w") as f:
                    f.write("FUNCTION [{}] using time: {}\n".format(func.__name__, endTime-startTime))
            return res
        return wrapper
    return timer_deco

@timer(logger="test.log")
def cal(num):
    res = 0
    for i in range(num):
        res += i
        sleep(0.1)
    return res

if __name__=="__main__":
    cal(10)