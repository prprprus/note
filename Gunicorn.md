## Gunicorn

Gunicorn + gevent 时，monkey path 的时机：

- 如果 worker 类型选择了 gevent，Gunicorn 在初始化进程时就会执行 `monkey.patch_all()`
- https://github.com/benoitc/gunicorn/blob/master/gunicorn/workers/ggevent.py#L143
- https://github.com/benoitc/gunicorn/blob/master/gunicorn/workers/ggevent.py#L38

### Gunicorn + gevent + SQLAlchemy 协程之间的非阻塞

版本信息：

- SQLAlchemy 版本是 1.4.15
- pymysql 版本是 1.0.2

测试代码：

```
@app.route("/A")
def handle():
    def _db_sleep():
        sql = text("SELECT SLEEP(5);")
        res = dbengine.execute(sql)
        print(res)

    s = time.time()
    _db_sleep()
    total = time.time() - s

    data = {"code": 0, "message": "success", "data": total}
    result = json.dumps(data, ensure_ascii=False)
    response = Response(result, content_type="application/json; charset=utf-8")
    return response


@app.route("/B")
def handle1():
    def _db_sleep():
        sql = text("SELECT SLEEP(20);")
        res = dbengine.execute(sql)
        print(res)

    s = time.time()
    _db_sleep()
    total = time.time() - s

    data = {"code": 0, "message": "success", "data": total}
    result = json.dumps(data, ensure_ascii=False)
    response = Response(result, content_type="application/json; charset=utf-8")
    return response
```

测试步骤：

1. 避免其他因素影响，Gunicorn 单进程启动、SQLAlchemy 连接池大小设置为 1
2. 先调用 B，再调用 A

结果：

1. 接口 A 先返回，接口 B 后返回，耗时约 20s，能实现非阻塞效果
2. gevent 在 Gunicorn 中的表现和一般的使用基本没什么不同，最大区别是不需要手动执行 `monkey.patch_all()`，一旦
   Gunicorn 在 gevent 模式下启动完成，IO 库就会被替换成非阻塞版本。也就是 IO 库的函数会变成 gevent 协程，可以被 gevent
   的事件循环调度（类似 asyncio）
3. gevent 能确保 Gunicorn 请求之间的非阻塞效果（一个请求对应一个 gevent 协程）
