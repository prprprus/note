## TFServing

Tensorflow Serving（简称 TFServing）是谷歌开源的一个用于模型部署的服务组件，功能丰富、生产就绪，主要用于 Tensorflow
训练的模型。相比用原生的 Tensorflow API 加载模型和预测，TFServing
提供比较丰富的开箱即用功能，省去自行开发的工作量，对开发周期短、需要快速落地的场景很有帮助。

TFServing 提供的功能：

- 支持多模型、多版本部署
- 提供 gRPC、HTTP 两种服务形式
- 支持 GPU 批处理
- 支持无需中断服务的模型热加载

### 安装

```bash
docker pull tensorflow/serving
```

> 也支持编译安装，通过配置某些 CPU 指令集，可以在一定程度上提升 TFServing 的性能

### 导出模型

```bash
├── model_name
│   └── 100002
│       ├── saved_model.pb
│       └── variables
```

> 这块主要是算法工程师去操作，TFServing 要求模型以 saved_model 格式导出，后台工程师需要在模型交付的时候确保模型文件的格式

### 配置文件

```bash
# models.config

model_config_list:{
    config:{                              // 每个模型对应一个 config 配置块
        name:'model_name1',               // 模型名称
        base_path:'/models/model_name1',  // 模型在容器内的路径
        model_platform:'tensorflow',      // 模型的训练框架
        model_version_policy:{            // 模型的版本
            specific:{
                versions:100000,          // 版本号 100000, 可以有多个
                versions:100001
            }
        }
        version_labels:{                  // 模型额外的标签, 需要和版本号对应, 这个不是必须的
            key:'canary',                 
            value:100000
        }
        version_labels:{
            key:'stable',
            value:100001
        }
    },
    config:{                              // 另一个模型配置
        name:'model_name2',
        base_path:'/models/model_name2',
        model_platform:'tensorflow',
        model_version_policy:{
            specific:{
                versions:100000,
                versions:100001,
                versions:100002,
                versions:100003
            }
        }
    },
}
```

### 启动

```bash
docker run \
    -t \
    -p 8501:8501 \
    -p 8500:8500 \
    --name tf_serving \
    -v /local_model_path:/models \
    tensorflow/serving \
    --model_config_file=/models/models.config \
    --model_config_file_poll_wait_seconds=60
```

- name：容器名字
- v：目录映射
- p：端口映射（8501 是 HTTP 服务，8500 是 gRPC 服务，建议一并开启）
- model_config_file：配置文件路径
- model_config_file_poll_wait_seconds：自动热加载的时间间隔

> 除了这些基本参数外还有其他参数

### 模型的输入输出结构

安装 saved_model_cli：`pip install tensorflow-serving-api==2.5.1`

到模型所在的目录下（也就是 saved_model.pb 文件所在的目录）执行：`saved_model_cli show --dir ./ --all`

```bash
MetaGraphDef with tag-set: 'serve' contains the following SignatureDefs:

signature_def['__saved_model_init_op']:
  The given SavedModel SignatureDef contains the following input(s):
  The given SavedModel SignatureDef contains the following output(s):
    outputs['__saved_model_init_op'] tensor_info:
        dtype: DT_INVALID
        shape: unknown_rank
        name: NoOp
  Method name is:

signature_def['serving_default']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['input_1'] tensor_info:
        dtype: DT_INT32
        shape: (-1, 1)
        name: serving_default_input_1:0
    inputs['input_2'] tensor_info:
        dtype: DT_INT32
        shape: (-1, 1)
        name: serving_default_input_2:0
    inputs['input_3'] tensor_info:
        dtype: DT_INT32
        shape: (-1, 15)
        name: serving_default_input_3:0
    inputs['input_4'] tensor_info:
        dtype: DT_INT32
        shape: (-1, 1)
        name: serving_default_input_4:0
    inputs['input_5'] tensor_info:
        dtype: DT_INT32
        shape: (-1, 7)
        name: serving_default_input_5:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['output_1'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 1)
        name: StatefulPartitionedCall:0
    outputs['output_2'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 1)
        name: StatefulPartitionedCall:1
  Method name is: tensorflow/serving/predict
```

- serving_default：默认的模型签名，可以在训练时自定义
- inputs[input_xxx]：模型的输入参数，`input_xxx` 是参数名称，可以在训练时自定义
    - dtype：参数类型
    - shape：参数的行数和列数。(-1, 1) 代表行数不限制，1 列；(-1, 15) 代表行数不限制，15 列
- outputs[output_xxx]：模型的输出参数，`output_xxx` 是参数名称，可以在训练时自定义

### TFServing 客户端

HTTP 客户端：

以上面的输入输出结构为例，假设行数是 10

```python
import requests

# 模拟输入
inputs = {
    'input_1': [[0]] * 10,
    'input_2': [[0]] * 10,
    'input_3': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] * 10,
    'input_4': [[0]] * 10,
    'input_5': [[0, 0, 0, 0, 0, 0, 0]] * 10
}

url = "http://<host>:8501/v1/models/<model_name>/versions/<model_version>:predict"
res = requests.post(url, json={'inputs': inputs}, timeout=1)

print(res.status_code)
print(res.json()["outputs"]["output_1"])
print(res.json()["outputs"]["output_2"])
```

gRPC 客户端：

```python
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc
from tensorflow.contrib.util import make_tensor_proto
from tensorflow.core.framework import types_pb2
import grpc

config = {
    "hostport": "<host>:8500",
    "max_message_length": 500 * 1024 * 1024,
    "timeout": 1000,
    "signature_name": "serving_default",
    "model_name": "<model_name>",
    "model_version": "stable"  # gRPC 方式的版本号需要用模型标签
}

channel = grpc.insecure_channel(config['hostport'])
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

request = predict_pb2.PredictRequest()
request.model_spec.name = config['model_name']
request.model_spec.signature_name = config['signature_name']
request.model_spec.version_label = config["model_version"]

input_1 = [[0]] * 10,
input_2 = [[0]] * 10,
input_3 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] * 10,
input_4 = [[0]] * 10,
input_5 = [[0, 0, 0, 0, 0, 0, 0]] * 10

request.inputs['input_1'].CopyFrom(
    make_tensor_proto(input_1, shape=[10, 1], dtype=types_pb2.DT_INT32))
request.inputs['input_2'].CopyFrom(
    make_tensor_proto(input_2, shape=[10, 1], dtype=types_pb2.DT_INT32))
request.inputs['input_3'].CopyFrom(
    make_tensor_proto(input_3, shape=[10, 15], dtype=types_pb2.DT_INT32))
request.inputs['input_4'].CopyFrom(
    make_tensor_proto(input_4, shape=[10, 1], dtype=types_pb2.DT_INT32))
request.inputs['input_5'].CopyFrom(
    make_tensor_proto(input_5, shape=[10, 1], dtype=types_pb2.DT_FLOAT))

result = stub.Predict(request, config['timeout'])
channel.close()
```
