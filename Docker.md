## 简介

Docker 是一种虚拟化技术，基于 Linux 的 cgroup、namespace、OverlayFS 等技术，对进程进行封装隔离，属于操作系统级别的虚拟化

使用 Docker 的好处：

- 轻量级（省资源、启动快、同时运行的数量多）
- 提供一致的运行环境（开发、测试、运维）
- 方便迁移
- 可以搭配 CI/CD 使用
- 对于 Dockerfile 定义的运行环境，开发和运维都看得懂，消除两者的隔阂

Docker 核心概念：

- 镜像：一种特殊的文件系统，包含容器运行所需的各种文件，镜像是分层存储的
- 容器：本质就是一个有独立命名空间的进程，容器内存储的数据会随着容器的消亡而消亡
- 仓库：集中存储、分发镜像的地方，分为私有仓库和公共仓库两种

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/docker-1.png)

## 常用 docker 命令

镜像：

- 拉取镜像：`docker pull [options] [Docker Registry <host>[:port]] <image>[:<tag>]`
- 列出镜像：`docker images -a`、`docker image ls`、`docker image ls -a`
  、`docker image ls -q`
- 列出悬虚镜像：`docker image ls -f dangling=true`
- 清理悬虚镜像：`docker image prune`
- 删除镜像：`docker image rm <image>`

容器：

- 启动容器：`docker run [options] <image> [command] [arg]`
    - `--name` 设置容器名称
    - `-d` 设置是否后台运行容器
    - `-i` 设置交互式启动容器
    - `-t` 分配终端，一般 `-it` 搭配起来用
    - `-p` 设置端口映射（宿主机端口：容器端口）
    - `v` 设置目录影射（宿主机目录路径：容器目录路径）
    - `--net` 设置容器网络（bridge、host）
    - `--link` 连接其他容器
    - `--rm` 设置容器停止后自动删除
    - `-m` 设置容器内存上限
    - `--cpuset` 设置容器可以使用哪些 CPU
    - `--dns` 设置 DNS 服务器
    - `--restart` 设置容器停止后是否自动重启（no、on-failure、always）
    - `--privileged` 设置是否特权容器
- 列出容器：`docker ps -a`，`docker container ps -a`
- 重启容器：`docker restart <container>`
- 产看后台容器的日志：`docker logs <container>`
- 进入容器：`docker exec -it <container> <command>`
- 删除容器：`docker rmi <container>`，`docker rmi $(docker ps -a -q)`
- 清理所有已经停止的容器：`docker system prune`，`docker container prune`

目录影射：

- 旧版本是通过 `docker run` 的 `-v` 参数来挂载数据卷，新版本可以通过 `--mount`
  实现，额外提供了一些新的功能，比如设置 `readonly`
  ```
  # 将 /src/webapp 设置成只读
  docker run -d -P \
      --name web \
      # -v /src/webapp:/usr/share/nginx/html:ro \
      --mount type=bind,source=/src/webapp,target=/usr/share/nginx/html,readonly \
      nginx:alpine
  ```

端口映射：

- `P` 随机映射
- `-p 80:80` 将宿主机任意地址的 80 端口映射到容器的 80 端口
- `-p 127.0.0.1:80:80` 将宿主机 127.0.0.1 地址的 80 端口映射到容器的 80 端口
- `-p 127.0.0.1::80` 将宿主机 127.0.0.1 的任意端口映射到容器的 80 端口

容器互连：

- 可以使用 Docker Compose

## Dockerfile

相关命令：

- `FROM <base_image>`：指定基础镜像，Dockerfile 的第一条指令，每个 Dockerfile
  都必须存在该指令，可以用 `FROM scratch` 指定空的基础镜像
- `EVN <key>=<VALUE>`：设置环境变量
- `USER <user>[:group]`：切换指定的用户、组
- `WORKDIR <path>`：设置工作目录
- `RUN <command>`：执行命令行命令
- `COPY [--chown=<user>:<group>] <source> <target>`
  ：将源文件复制到目标路径下，源文件的路径是 `docker build` 所在的目录，目标路径是容器内的绝对路径；
  如果源文件是目录，则不会复制目录本身，而是复制目录下的所有文件；源文件的元数据会被保留
- `ADD [--chown=<user>:<group>] <source> <target>`：功能和 `COPY` 差不多，区别是 `COPY`
  是单纯复制文件，`ADD` 带有自动解压功能；`ADD` 会让构建缓存失效，可能会令构建时间增加
- `VOLUME ["<path1>", "<path2>"...]`：设置要挂载的数据卷
- `EXPOSE <port1>, <port2>, ...`：声明要暴露的端口号
- `CMD ["executable", "arg1", "arg2", ...]`：设置容器的主进程启动

一些技巧：

- 使用 `RUN` 命令时能作为一层就尽量作为一层，避免多个 `RUN`
- 每一层没用的文件要删除，减少镜像体积
- 镜像构建上下文是指 `docker build` 所在的目录。`ADD`、`COPY`
  等命令需要额外赋值对应文件到上下文目录下，也可以通过 `.dockerignore` 忽略需要上传到 Docker 服务端的文件

例子：

```dockerfile
FROM python:3.7.9

USER root

ENV project_dir="/opt/src"
ENV project_name="python-app"

ADD $project_name.tar.gz $project_dir

RUN pip install -r $project_dir/$project_name/requirements.txt -i https://pypi.doubanio.com/simple/

WORKDIR $project_dir/$project_name

EXPOSE 2333

CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:2333", "main:app"]
```

## 配置 DNS

- 配置局部 DNS，通过启动参数针对某个容器配置
- 配置全局 DNS：通过 `/etc/docker/daemon.json` 文件
    ```
    {
      "dns" : [
        "114.114.114.114",
        "8.8.8.8"
      ]
    }
    ```

## 监控 Docker

监控命令：

- `docker ps`
- `docker images`
- `docker stats`
- `docker inspect <image/container>`
- `docker top <container>`
- `docker port <container>`

监控工具：

- datadog
- prometheus
