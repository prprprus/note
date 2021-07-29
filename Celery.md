![](https://raw.githubusercontent.com/hsxhr-10/Notes/master/image/pythonwebcelery-1.png)

- **Celery Broker**：Celery 本身不提供消息处理功能，需要依赖外部组件，比如 RabbitMQ、Redis。以 RabbitMQ
  为例，Broker 负责接收 Client 产生的消息， 根据规则转发到对应的队列，最后再发送给对应的 Worker
- **Celery Client**：Client 作为生产者生成任务，并发送到 Broker
- **Celery Worker**：Worker 作为消费者执行任务，并将结果写进 Backend（如果有的话）。Worker 进程可以根据需要水平扩展
- **Celery Backend**：Backend 负责保存任务的执行结果，这个组件不是必须的

Celery 支持的任务类型：

- 异步任务
- 固定时间间隔
- Cron

RMQ 基本命令：

- 前台启动 `sudo rabbitmq-server`
- 后台启动 `sudo rabbitmq-server -detached`
- 停止 `rabbitmqctl stop`

RabbitMQ 的连接 URL `amqp://<myuser>:<mypassword>@<localhost>:5672/<myvhost>` 配置：

- 添加用户 `sudo rabbitmqctl add_user <myuser> <mypassword>`
- 添加虚拟主机 `sudo rabbitmqctl add_vhost <myvhost>`
- 设置用户标签 `sudo rabbitmqctl set_user_tags <myuser> <mytag>`
- 设置用户权限（三种权限为配置、写、读）`sudo rabbitmqctl set_permissions -p <myvhost> <myuser> ".*" ".*" ".*"`

---

### Celery 对象

- Celery 对象用来配置 Broker、Backend 的连接，用来将普通函数装饰成任务
- [根据](https://docs.celeryproject.org/en/stable/userguide/application.html#application) Celery 对象线程安全
- `Celery()` 构造函数
  - main=None：入口模块的名字（用项目名也可以）
  - broker=None：Broker 的连接 URL，格式 `transport://userid:password@hostname:port/virtual_host`。 [更多](https://kombu.readthedocs.io/en/latest/userguide/connections.html#urls)
  - backend=None：Backend 的连接 URL，格式 `db+scheme://user:password@host:port/dbname`。 [更多](https://docs.celeryproject.org/en/stable/userguide/configuration.html#database-backend-settings)
  - timezone：设置时区。比如 `Asia/Shanghai`
  - autofinalize=True：如果为 True，那么在 Celery 对象完成前，如果注册任务，就会抛出 RuntimeError。一般保持默认值就行
  - set_as_current=True：标记 Celery 对象为全局对象。一般保持默认值就行

---

### 任务

#### Task 装饰器

- bind=True：将普通函数封装成任务
- name：任务名字。根据实际情况命名即可
- **acks_late=False：消息的确认机制，默认是任务执行之前就确认，缺点是万一 Worker 中途崩溃，会导致消息丢失、任务漏执行。
    设置成 True，消息会在任务执行完毕之后才确认，提高了可靠性，同时要确保任务的幂等性**
- **max_retries=3**：最大重试次数，仅在调用 `retry()` 时才生效，`None` 代表一直重试直到成功为止
- **soft_time_limit**：预估任务的执行时间，如果在给定时间内还没执行完，则主动结束
- **ignore_result**=True：当任务没有返回值时，标注为 True
- default_retry_delay=180：每次重试的间隔时间，单位秒
- rate_limit：任务执行频率限制，`None` 代表无限制，`100/s` 代表每秒最多执行 100 个此类任务，`100/m` 和 `100/h` 以此类推
- track_started=False：将正在运行的任务的状态改成 started。对于长时间运行的任务会有比较好的监控效果
- request：任务的详细描述。 [详见](https://docs.celeryproject.org/en/stable/userguide/tasks.html#task-request)
- serializer="JSON"：任务默认的序列化方式
- compression：任务的压缩方式。对体积比较大的任务会有一定好处，取值有 gzip、bzip2 等
- backend：任务结果的存储地方。一般在 Celery 对象统一指定即可

```python
@app.task(
    bind=True,
    name="celery_demo.task.task1.add",
    acks_late=True,
    max_retries=5,
    default_retry_delay=60,
    rate_limit="10/s"
)
def task(self):
    print(self.requests)
    pass
```

#### Task 类

```python
class CustomTask(app.Task):
    def run(self):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        print(retval)
        print(task_id)
        print(args)
        print(kwargs)
        print("---> 任务执行成功")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(exc)
        print(task_id)
        print(args)
        print(kwargs)
        print(einfo)
        print("---> 任务执行失败")

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print(status)
        print(retval)
        print(task_id)
        print(args)
        print(kwargs)
        print(einfo)
        print("---> 任务返回后执行")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print(exc)
        print(task_id)
        print(args)
        print(kwargs)
        print(einfo)
        print("---> 任务重试")


@app.task(
    bind=True,
    name="celery_demo.task.task1.custom_task",
    acks_late=True,
    max_retries=3,
    default_retry_delay=3,
    rate_limit="10/s",
    autoretry_for=(ZeroDivisionError,),
    base=CustomTask
)
def task(self, x, y):
    # 1/0
    print("Run task(x, y)!")
    return x + y
```

使用场景：

- 将每个任务都有的重复功能抽出来，比如重试、成功、失败后发送邮件通知
- 将大型任务封装成类的形式（但是不能有返回值）

#### 任务的状态

- PENDING：表示正在执行，或者未知状态的任务
- STARTED：表示任务已经启动执行，默认情况下不会显示，可以通过任务的 `track_started` 参数设置
- SUCCESS：表示任务执行成功
- FAILURE：表示任务执行失败
- RETRY：表示任务正在重试
- REVOKED：表示任务已经取消了
- [自定义任务状态](https://docs.celeryproject.org/en/stable/userguide/tasks.html#custom-states)

#### Retry

- 可以对执行失败的任务进行重试，Celery 会确保每次重试使用相同的任务 ID

```python
# 写法一
@app.task(
    bind=True,
    name="celery_demo.task.task1.add",
    acks_late=True,
    max_retries=3,
    default_retry_delay=3,
    rate_limit="10/s"
)
def add(self, x, y):
    try:
        1/0
        print("Run add(x, y)!")
        print(self.request)
        return x + y
    except ZeroDivisionError as exc:
        # exc=None：异常
        # max_retries=None：最大重试次数，会覆盖掉 `max_retries`
        # countdown=None：重试的时间间隔，会覆盖掉 `default_retry_delay`
        self.retry(exc=exc, countdown=6, max_retries=6)


# 写法二
@app.task(
    bind=True,
    name="celery_demo.task.task1.add",
    acks_late=True,
    max_retries=3,
    default_retry_delay=3,
    rate_limit="10/s",
    autoretry_for=(ZeroDivisionError,),
    retry_kwargs={"countdown":6, "max_retries": 6}
)
def add(self, x, y):
    1/0
    print("Run add(x, y)!")
    print(self.request)
    return x + y
```

#### 有先后关系的任务

```python
res = (add.s(2, 2) | add.s(4) | add.s(8))()
print(res.get())
```

#### 周期性任务

- 需要在启动 Worker 的时候加上 `--beat` 参数
- [更多例子](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#crontab-schedules) 

```python
# 固定时间间隔，每 60 秒执行一次
app.conf.beat_schedule = {
    'every-60-second': {
        'task': 'celery_demo.task.task1.add',
        'schedule': 60.0,
        'args': (16, 16)
    },
}
```

```python
from celery.schedules import crontab

# Cron，每天凌晨 03:30 执行一次
app.conf.beat_schedule = {
    'every-3:30AM': {
        'task': 'celery_demo.task.task1.add',
        'schedule': crontab(hour=3, minute=30),
        'args': (16, 16),
    },
}
```

---

### 发送任务

#### apply_async() 方法

- args=None：单值形式的传参
- kwargs=None：键值对形式的传参
- **retry=True：当消息发送失败时，是否进行重试**
- **retry_policy：设置重试策略。取值例子 {"max_retries": 3, "interval_start": 30}**
- **exchange：设置投放的交换机名称**
- **queue：设置投放的队列名称**
- **routing_key：设置投放的 routing_key**
- countdown=None：任务延迟执行的时间，默认立即执行
- expires：任务的过期时间，如果在给定时间内还没执行，将不会再执行，单位秒
- priority：任务优先级。对于 RabbitMQ 和 Redis，0 是最高优先级
- headers：自定义的消息头。字典形式

---

### 路由消息（RMQ）

#### 消息的处理流程

1. Client 将消息发送到交换机
2. 交换机根据自身类型，将消息发送到绑定的队列中
3. 消息在队列中等待被 Worker 消费，一旦消息被确认消费，将会从队列中删除

#### 交换机和队列

交换机的类型：

- direct：直连交换机。直连交换机会精准匹配 routing_key 对应的队列名字
- topic：主题交换机。可以进行模糊匹配
    ```
    app.conf.task_queues = (
        Queue(name='news', exchange=Exchange(name='cn.*', type='topic'), routing_key='cn.news'),
        Queue(name='weather', exchange=Exchange(name='cn.*', type='topic'), routing_key='cn.weather'),
    )
    ```

```python
# 创建交换机和队列
from kombu import Exchange, Queue

app.conf.task_queues = (
    # 默认交换机 celery, 类型 direct, 绑定了队列 celery
    Queue(name='celery', exchange=Exchange(name='celery', type='direct'), routing_key='celery'),
    # 交换机 media, 类型 direct, 绑定了队列 videos, routing_key 是 media.video
    Queue(name='videos', exchange=Exchange(name='media', type='direct'), routing_key='media.video'),
    # 交换机 media, 类型 direct, 绑定了队列 images, routing_key 是 media.image
    Queue(name='images', exchange=Exchange(name='media', type='direct'), routing_key='media.image'),
)
```

---

### Worker

- Worker 可以绑定到一个或者多个队列，根据需要可以水平扩展，默认的并发处理模式是 prefork，可以选择异步模式
- 常用配置参数
    - **--pool**：设置并发模式。取值 `prefork|eventlet|gevent|solo`
    - **--concurrency**：设置进程或者协程的数量
    - **--queues**：设置需要绑定的队列
    - **--max-tasks-per-child**：设置单个进程/协程可以处理的任务数量，当超过这个限制后，会产生新的进程/协程去替代旧的。是一种简单粗暴的处理内存泄漏的方法，旧进程执行的任务会确保被执行完，再被替换
    - **--max-memory-per-child**：设置单个子进程/协程能够占用的内存，当超过这个限制后，会产生新的进程/协程去替代旧的。也是一种简单粗暴的处理内存泄漏的方法，旧进程执行的任务会确保被执行完，再被替换
    - **--autoscale**：设置 `--concurrency` 弹性扩容的范围。比如 `--autoscale=10,3` 表示最少 3 个最多 10 个
    - --loglevel：设置日志等级。取值 `DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL`
    - --beat：设置执行定时任务
- 使用建议
    - 使用 RabbitMQ 作为 broker（稳定）
    - 根据业务划分交换机、队列、绑定 worker 
        ```
        app.conf.task_queues = (
            Queue(name='celery', exchange=Exchange(name='celery', type='direct'), routing_key='celery'),
            Queue(name='videos', exchange=Exchange(name='media', type='direct'), routing_key='media.video'),
            Queue(name='images', exchange=Exchange(name='media', type='direct'), routing_key='media.image'),
        )
      
        celery --app=task worker --concurrency=2 --queues=celery
        celery --app=task worker --concurrency=3 --queues=videos
        celery --app=task worker --concurrency=4 --queues=images
        ```
    - 按照待处理的任务的特点设置 worker 类型
        ```
        celery --app=task worker --concurrency=2 --queues=celery
        celery --app=task worker --pool=eventlet --concurrency=1000 --queues=io_bound
        celery --app=task worker --concurrency=7 --queues=cpu_bound
        ```
    - 如果不需要关注任务的结果，主动设置忽略，避免那部分 Backend 不必要的消耗 `@app.task(bind=True, ignore_result=True)`
    - 如果并发模式选用了协程，需要注意任务不能有阻塞代码，避免影响并发效果
    - 发送任务要设置重试
    - 任务本身要设置重试和次数
    - 对于一些很有可能会失败，而且失败的过程耗时比较长的任务，主动设置 `soft_time_limit` 参数
    - 任务本身要设置 `acks_late=True`，确保消息在任务执行完成后才删除
