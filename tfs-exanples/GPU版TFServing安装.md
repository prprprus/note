## 安装 GPU 版 TFServing

1. 安装 Docker-CE, 版本 18.06 或以上, 建议 20.10.0
    ```bash
    $ curl https://get.docker.com | sh \
        && sudo systemctl start docker \
        && sudo systemctl enable docker
    ```

2. 安装 nvidia-docker
    ```bash
    # 如果之前安装过nvidia-docker 1.0，那么需要卸载它以及已经创建的容器
    $ sudo docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
    $ sudo apt-get purge -y nvidia-docker
    
    $ distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
        && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
        && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
        
    $ sudo apt-get update -y
    $ sudo apt-get install -y nvidia-docker2
    
    $ sudo systemctl restart docker
    $ sudo docker run --rm --gpus all nvidia/cuda:10.1-base nvidia-smi
    ```

   安装成功会有类似 `nvidia-smi` 命令的输出:
    ```bash
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 450.51.06    Driver Version: 450.51.06    CUDA Version: 11.0     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |                               |                      |               MIG M. |
    |===============================+======================+======================|
    |   0  Tesla T4            On   | 00000000:00:1E.0 Off |                    0 |
    | N/A   34C    P8     9W /  70W |      0MiB / 15109MiB |      0%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+
    
    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
    |        ID   ID                                                   Usage      |
    |=============================================================================|
    |  No running processes found                                                 |
    +-----------------------------------------------------------------------------+
    ```

   > nvidia/cuda 的 Docker 镜像版本需要和 CUDA 驱动版本对应, [参考](https://github.com/NVIDIA/nvidia-docker/wiki/CUDA#requirements)

3. 安装 GPU 版本的 Tensorflow Serving
    ```bash
    $ sudo docker pull tensorflow/serving:latest-gpu
    ```

## 参考

- [官网](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
- [在Docker中使用Tensorflow Serving](http://fancyerii.github.io/books/tfserving-docker/#%E4%BD%BF%E7%94%A8gpu)
- [--gpus all 替代 --runtime=nvidia](https://github.com/NVIDIA/nvidia-docker/issues/838#issuecomment-558962338)
