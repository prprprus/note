## threading

### Python 中的并发处理策略

- 如果是 IO 密集型任务、每个 IO 操作较慢、并发量较大，则使用协程方案（asyncio、gevent、Tornado 等）
- 如果是 IO 密集型任务、每个 IO 操作较快、并发较有限，则使用协程或者线程都行
- 如果是 CPU 密集型任务、使用多进程（必要时候上 Cython 优化单个任务的耗时）

### threading 使用例子

```python
# 模块级别函数
import threading


def main():
    t = threading.Thread(target=lambda: print("Hello threading"))
    t.start()

    print("当前活动线程总数:", threading.active_count())
    print(threading.current_thread() == threading.main_thread())
    print("主线程 ID:", threading.get_ident())
    print("活动线程列表:", threading.enumerate())
    print("锁的最大超时时间:", threading.TIMEOUT_MAX)
    print("main thread done.")


main()
```

```python
# 线程对象
import threading
import time


def task(i):
    time.sleep(2)
    print("task {} done.".format(i))


def main():
    # 创建线程对象
    t = threading.Thread(target=task, args=(-1,))

    print("线程对象名字:", t.name)  # Thread-1
    t.name = "ooxoo"
    print("新的线程对象名字:", t.name)  # ooxoo
    print("线程对象 ID:", t.ident)  # None
    print("线程对象是否已启动:", t.is_alive())  # False

    # 启动线程, start() 调用 run() 方法, run() 会执行 task() 函数
    t.start()

    print("线程对象是否已启动:", t.is_alive())  # True
    print("线程对象 ID:", t.ident)  # 123145445199872

    # 等待线程 t 执行完毕
    t.join()

    print("main thread done.")


main()
```

```python
# daemon：主线程结束后，如果想让其创建的子线程跟着自动结束，可以通过设置守护线程实现
import threading
import time


def task(i):
    time.sleep(2)
    print("task {} done.".format(i))


def main():
    workers = []
    for i in range(5):
        t = threading.Thread(target=task, args=(i,))

        # 设置成守护线程
        t.daemon = True

        workers.append(t)

    for worker in workers:
        worker.start()

    print("main thread done.")


main()
```

### 线程同步

#### 锁

- `threading.Lock()`：可以创建锁对象，自动返回当前系统所支持的锁类型
- `acquire(blocking=True, timeout=-1)`
    - 将锁对象状态设置成 locked（申请锁），如果成功则返回 True，否则返回 False
    - blocking 为 True 代表阻塞等待，直到申请锁成功，或者超时为止；为 False 代表如果不能立即申请锁，则不等待直接返回
    - timeout 为 -1 代表一直等待下去，`threading.TIMEOUT_MAX` 可以获取系统支持的最大等待时间
- `release()`
    - 将锁对象状态设置成 unlocked（释放锁），可以在任意线程中执行，不一定是持有锁的线程。该函数没有返回值
    - 如果有多个线程在等待锁，会随机选择一个线程持有锁
    - 如果释放 unlocked 的锁对象，则会抛出 RuntimeError
- `locked()`：如果锁对象状态为 locked 则返回 True，否则返回 False

```python
import threading
import time

lock = threading.Lock()


def main():
    try:
        # 阻塞等待
        res = lock.acquire()
        print("第一次申请锁结果:", res)  # True

        # 不等待
        res = lock.acquire(blocking=False)
        print("第二次申请锁结果:", res)  # False

        print("当前锁对象状态:", lock.locked())  # True

        # do something
        time.sleep(1)
        print("task done.")
    except:
        raise
    finally:
        lock.release()
        print("释放锁成功")


main()
```

#### 可重入锁

```python
import threading
import time

rlock = threading.RLock()


def task(i):
    try:
        # 阻塞等待
        res = rlock.acquire()
        print("{} 第一次申请锁结果: {}".format(i, res))

        # 不等待
        res = rlock.acquire(blocking=False)
        print("{} 第二次申请锁结果: {}".format(i, res))

        # 阻塞等待
        res = rlock.acquire()
        print("{} 第三次申请锁结果: {}".format(i, res))

        # do something
        time.sleep(1)
        print("task {} done.".format(i))
    except:
        raise
    finally:
        # 需要释放相应次数，否则另外一个线程会一直等到
        rlock.release()
        rlock.release()
        rlock.release()
        print("{} 释放锁成功".format(i))


def main():
    workers = []
    for i in range(2):
        t = threading.Thread(target=task, args=(i,))
        workers.append(t)

    for worker in workers:
        worker.start()

    print("main thread done.")


main()
```

#### 条件变量

- `threading.Condition(lock=None)`：可以创建 condition 对象，如果 lock 为 `None`
  ，会默认创建一个 `RLock` 对象
- `acquire(*args)`：会去调用对应锁对象的 `acquire()` 方法
- `release()`：会去调用对应锁对象的 `release()` 方法
- `wait(timeout=None)`：主动释放锁，并进入等待状态，直到被唤醒或者超时
- `wait_for(predicate, timeout=None)`：主动释放锁，并进入等待状态，直到被唤醒或者超时，而且被唤醒后必须满足条件（也就是
  predicate 必须是 True）才能继续往下执行， 否则又会调用 `wait()`
  进入等待状态。也就是相当于 `while not predicate: wait()` 的语法糖
- `notify(n=1)`：打算唤醒 n 个等待线程，该方法被调用后，线程并不会立即被唤醒，还是要等到 `release()`
  被调用之后。必须是持有锁的线程调用，否则抛出 RuntimeError 异常
- `notify_all()`：打算唤醒所有等待线程，该方法被调用后，线程并不会立即被唤醒，还是要等到 `release()`
  被调用之后。必须是持有锁的线程调用，否则抛出 RuntimeError 异常

```python
# 基本使用
import threading
import time

lock = threading.Lock()
cond = threading.Condition(lock)


def task1():
    try:
        cond.acquire()
        print("线程 1 进入等待")
        cond.wait()
        print("线程 1 被唤醒")

        # do something
        time.sleep(1)
        print("线程 1 执行成功")
    except:
        raise
    finally:
        cond.release()
        print("线程 1 释放锁成功")


def task2():
    try:
        cond.acquire()
        # do something
        time.sleep(1)
        print("线程 2 执行成功")
        cond.notify_all()
        print("线程 2 唤醒线程 1")
    except:
        raise
    finally:
        cond.release()
        print("线程 2 释放锁成功")


def main():
    t1 = threading.Thread(target=task1)
    t1.start()
    t2 = threading.Thread(target=task2)
    t2.start()

    print("main thread done.")


main()
```

```
线程 1 进入等待
main thread done.
线程 2 执行成功
线程 2 唤醒线程 1
线程 2 释放锁成功
线程 1 被唤醒)
线程 1 执行成功
线程 1 释放锁成功
```

```python
# `wait_for()`：被唤醒后，还需要满足条件，否则继续等待
import threading
import time

lock = threading.Lock()
cond = threading.Condition(lock)
flag = 0


def predicate():
    return True if flag == 1 else False


def task1():
    try:
        cond.acquire()
        print("线程 1 不满足条件，进入等待")
        cond.wait_for(predicate)
        print("线程 1 满足条件")

        # do something
        time.sleep(1)
        print("线程 1 执行成功")
    except:
        raise
    finally:
        cond.release()
        print("线程 1 释放锁成功")


def task2():
    try:
        cond.acquire()
        # do something
        time.sleep(1)
        global flag

        # case1: 满足条件的修改，线程 1 被唤醒后可以继续往下执行
        flag += 1
        # case2: 不满足条件的修改，线程 1 被唤醒不能往下执行，继续调用 wait() 等待
        # flag += 10

        print("线程 2 执行成功")
        cond.notify_all()
        print("线程 2 唤醒线程 1")
    except:
        raise
    finally:
        cond.release()
        print("线程 2 释放锁成功")


def main():
    t1 = threading.Thread(target=task1)
    t1.start()
    t2 = threading.Thread(target=task2)
    t2.start()

    print("main thread done.")


main()
```

#### Semaphore

- 在并发环境下，Semaphore 用于保护数量有限的资源
- `BoundedSemaphore` 继承于 `Semaphore`，两者区别在于 `release()`
  方法，`BoundedSemaphore` 在释放锁时会对比释放次数 `self._value` 和
  初始化时指定的次数 `self._initial_value`，确保了释放次数不会超过指定的次数，否则抛出 ValueError 异常，更加方便可靠

```python
import threading
import time

max_connections = 3
pool = threading.BoundedSemaphore(max_connections)


def task3(i):
    try:
        pool.acquire()
        print("线程 {} 获取到资源".format(i))
        # do something
        time.sleep(1)
    except:
        raise
    finally:
        pool.release()


def main():
    workers = []
    for i in range(9):
        t = threading.Thread(target=task3, args=(i,))
        # t.daemon = True
        workers.append(t)

    for worker in workers:
        worker.start()

    print("main thread done.")


main()
```

> 输出是三个一组，说明限制有效

#### Timer

```python
# 可以用来实现简单的定时任务
import threading

timer = threading.Timer(3, lambda: print("Hello Timer"))
timer.start()
```

#### queue 的使用

- [queue](https://docs.python.org/3/library/queue.html) 模块提供了多种线程安全的队列
- [SimpleQueue](https://docs.python.org/3/library/queue.html#simplequeue-objects)
  比较常用，标准库不少需要线程间通信的地方也是用的 SimpleQueue

```python
# 简单的生产者消费者模型
import queue
import threading
import time

_queue = queue.SimpleQueue()


def producer():
    for i in range(5):
        time.sleep(2)
        _queue.put(i)
        print("生产数据 {}".format(i))

    print("生产数据完毕")


def consumer():
    while True:
        print("等待数据...")
        data = _queue.get()
        time.sleep(0.5)
        print("消费数据 {}".format(data))


producer = threading.Thread(target=producer)
consumer = threading.Thread(target=consumer)

consumer.start()
producer.start()
```

```
等待数据...
生产数据 0
消费数据 0
等待数据...
生产数据 1
消费数据 1
等待数据...
生产数据 2
消费数据 2
等待数据...
生产数据 3
消费数据 3
等待数据...
生产数据 4
消费数据 4
等待数据...
生产数据完毕
```

### 其他

- 在 threading 源码中看到一个小技巧，在 Python 程序退出之前执行一个处理函数
  ```
  import atexit
  
    
  def _python_exit():
      print("自定义退出回调函数")
  
  
  atexit.register(_python_exit)
  ```
