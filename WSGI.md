## WSGI

WSGI 是 Python Web 的一种协议和规范，分为应用端（Flask、Tornado、Django 等 Web
框架）和服务端（Gunicorn、uWSGI 等应用服务器）。 WSGI 解耦了应用端和服务端，让它们可以灵活搭配使用，比如 Flask 既可以运行在
Gunicorn 上，也可以运行在 uWSGI 上。其他编程语言也有类似的协议，像 Java 的 Servlet

> uwsgi 是另一种 Python Web 协议，而 uWSGI 是既实现了 WSGI 协议，又实现了 uwsgi 协议的应用服务器

WSGI 应用端：

```python
class AppClass:

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b"Hello WSGI"]
```

- 定义 callable 对象，比如函数，或者实现了 `__call__()` 的类。callable 对象接收 `environ`
  和 `start_response()` 两个参数
- 返回一个可迭代对象

WSGI 服务端：

```python
def run_wsgi(application):
    # 解析 environ 字典
    environ = {k: unicode_to_wsgi(v) for k, v in os.environ.items()}
    environ['wsgi.input'] = sys.stdin.buffer
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once'] = True

    if environ.get('HTTPS', 'off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    headers_set = []
    headers_sent = []

    # 定义 write()
    def write(data):
        out = sys.stdout.buffer

        if not headers_set:
            raise AssertionError("write() before start_response()")

        elif not headers_sent:
            status, response_headers = headers_sent[:] = headers_set
            out.write(wsgi_to_bytes('Status: %s\r\n' % status))
            for header in response_headers:
                out.write(wsgi_to_bytes('%s: %s\r\n' % header))
            out.write(wsgi_to_bytes('\r\n'))

        out.write(data)
        out.flush()

    # 定义 start_response()
    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info = None
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]

        return write

    # 调用应用端
    result = application(environ, start_response)

    # 利用 write() 返回结果
    try:
        for data in result:
            if data:
                write(data)
        if not headers_sent:
            write('')
    finally:
        if hasattr(result, 'close'):
            result.close()
```

- 从 HTTP 请求中解析出 `environ`
- 定义用于设置 status、headers 的 `start_response()`
- 定义用于发送数据的 `write()`
- 调用应用端的 callable 对象，传入 `environ` 和 `start_response()`，并获取处理结果
- 利用 `write()` 返回结果

### Flask 中的 WSGI

```python
from flask import Flask

app = Flask(__name__)


@app.route('/hello')
def hello_world():
    return 'Hello, World!'


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=12345)
```

```BASH
write, serving.py:265
execute, serving.py:315
run_wsgi, serving.py:323
handle_one_request, serving.py:379  # 从这个地方开始，下面的堆栈信息是请求转发过来的路径，不是这次分析的重点
handle, server.py:426
handle, serving.py:345
__init__, socketserver.py:720
finish_request, socketserver.py:360
process_request_thread, socketserver.py:650
run, threading.py:870
_bootstrap_inner, threading.py:926
_bootstrap, threading.py:890
```

```python
def handle_one_request(self):
    self.raw_requestline = self.rfile.readline()
    if not self.raw_requestline:
        self.close_connection = 1
    # 判断是否有效的请求
    elif self.parse_request():
        # 重点是这里，调用 run_wsgi() 方法
        return self.run_wsgi()
```

```python
def run_wsgi(self):
    # 忽略一些检查
    # ...

    # 1. 解析 environ
    self.environ = environ = self.make_environ()
    # 存放 status, headers 的容器, 给 start_response() 使用
    headers_set = []
    headers_sent = []

    # 2. 定义用于发送数据的 write() 函数
    def write(data):
        assert headers_set, "write() before start_response"
        if not headers_sent:
            status, response_headers = headers_sent[:] = headers_set
            try:
                code, msg = status.split(None, 1)
            except ValueError:
                code, msg = status, ""
            code = int(code)
            # 发送 HTTP 响应状态行
            self.send_response(code, msg)
            # 忽略大段大段的 headers 处理 
            # ...
            # 发送 HTTP headers
            self.end_headers()

        assert isinstance(data, bytes), "applications must write bytes"
        # 发送数据
        if data:
            self.wfile.write(data)
        self.wfile.flush()

    # 3. 定义用于设置 status、headers 的 start_response() 函数
    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    reraise(*exc_info)
            finally:
                exc_info = None
        elif headers_set:
            raise AssertionError("Headers already set")
        headers_set[:] = [status, response_headers]
        return write

    def execute(app):
        # 4. 调用应用端获取结果
        application_iter = app(environ, start_response)
        try:
            # 5. 调用 write() 将结果返回给请求方
            for data in application_iter:
                write(data)
            if not headers_sent:
                write(b"")
        finally:
            if hasattr(application_iter, "close"):
                application_iter.close()

    try:
        # 入口
        execute(self.server.app)
    except (_ConnectionError, socket.timeout) as e:
        self.connection_dropped(e, environ)
    except Exception:
# 忽略大段大段的异常处理
# ...
```

### 参考

- [PEP-3333](https://www.python.org/dev/peps/pep-3333/#environ-variables)
