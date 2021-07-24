# WSGI 服务器压测

对一些常用的应用服务器进行简单的压测，有个大概参考

基础信息：

- WSGI 应用端：Flask
- 待测 WSGI 应用端：Gunicorn、uWSGI、Tornado
- 测试工具：wrk
- 网络环境：本地内网
- 操作系统：Ubuntu 18.04 LTS
- 硬件配置：4 核 8G

其他信息：

- 测试场景比较简单，返回一个大约 4KB 的数据，单纯对比纯 IO 表现
- 压测前用 ulimit -n 临时调大了可以打开的文件描述符个数
- 测试命令 `wrk -t8 -c400 -d30s http://127.0.0.1:12345/hello`
- 结果取平均情况

```python
import json

from flask import Flask, Response

app = Flask(__name__)
data = "ok" * 2000


@app.route("/hello", methods=["GET"])
def handle():
    resp = Response(json.dumps({"code": 0, "message": "success", "data": data},
                               ensure_ascii=False))
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp
```

## Gunicorn

### (1) 多进程

`gunicorn -w 8 -b 0.0.0.0:12345 demo1:app`

```BASH
Running 30s test @ http://127.0.0.1:12345/hello
  8 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    77.05ms   15.68ms 242.36ms   86.94%
    Req/Sec   248.60    145.53   620.00     68.15%
  15808 requests in 30.06s, 63.42MB read
  Socket errors: connect 155, read 1037, write 94, timeout 0
Requests/sec:    525.96
Transfer/sec:      2.11MB
```

- 并发 525.96
- 延迟 77.05ms
- 错误 connect 155, read 1037, write 94, timeout 0

### (2) 多进程 + 多线程

`gunicorn -w 8 --threads 2 -b 0.0.0.0:12345 demo1:app`

```BASH
Running 30s test @ http://127.0.0.1:12345/hello
  8 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   152.58ms  104.07ms 829.05ms   64.87%
    Req/Sec   220.10    150.52   820.00     62.80%
  48223 requests in 30.09s, 193.71MB read
  Socket errors: connect 155, read 95, write 0, timeout 0
Requests/sec:   1602.59
Transfer/sec:      6.44MB
```

- 并发 1602.59
- 延迟 152.58ms
- 错误 connect 155, read 95, write 0, timeout 0

### (3) 多进程 + gevent

`gunicorn -w 8 -k gevent -b 0.0.0.0:12345 demo1:app`

```BASH
Running 30s test @ http://127.0.0.1:12345/hello
  8 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     5.18ms   28.75ms   1.97s    97.02%
    Req/Sec   542.62    463.09     2.49k    78.26%
  53758 requests in 30.10s, 215.94MB read
  Socket errors: connect 155, read 129, write 5, timeout 119
Requests/sec:   1785.80
Transfer/sec:      7.17MB
```

- 并发 1785.80
- 延迟 5.18ms
- 错误 connect 155, read 129, write 5, timeout 119

## uWSGI

`uwsgi --socket 0.0.0.0:12345 --wsgi-file ./demo1.py --master --processes 8 --threads 2`

- TODO

## Tornado

### 单进程

```python
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from demo1 import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(12345)
IOLoop.instance().start()
```

```BASH
Running 30s test @ http://127.0.0.1:12345/hello
  8 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   211.60ms   84.75ms 732.69ms   87.88%
    Req/Sec   183.70    134.47   505.00     64.48%
  34502 requests in 30.09s, 136.88MB read
  Socket errors: connect 155, read 109, write 1, timeout 0
Requests/sec:   1146.52
Transfer/sec:      4.55MB
```

- 并发 1146.52
- 延迟 211.60ms
- 错误 connect 155, read 109, write 1, timeout 0

### 多进程

```python
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from demo1 import app

http_server = HTTPServer(WSGIContainer(app))
http_server.bind(12345)
http_server.start(8)
IOLoop.instance().start()
```

```BASH
Running 30s test @ http://127.0.0.1:12345/hello
  8 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    88.36ms   72.63ms 412.15ms   52.11%
    Req/Sec   352.91    295.83     1.27k    59.86%
  83716 requests in 30.10s, 332.13MB read
  Socket errors: connect 155, read 0, write 0, timeout 0
Requests/sec:   2781.25
Transfer/sec:     11.03MB
```

- 并发 2781.25
- 延迟 88.36ms
- 错误 connect 155, read 0, write 0, timeout 0

## FastAPI

- TODO
