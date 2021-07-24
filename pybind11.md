## 安装

1. 确保已经安装这些组件：Python3.x、cmake、支持 C++11 的编译器

下面是我在 macOS 上各个组件的相关信息:

```BASH
(lab) ~ ➤ python -V
Python 3.6.9 :: Anaconda, Inc.

(lab) ~ ➤ cmake -version
cmake version 3.19.7
CMake suite maintained and supported by Kitware (kitware.com/cmake).

(lab) ~ ➤ clang++ -v
Apple LLVM version 10.0.1 (clang-1001.0.46.4)
Target: x86_64-apple-darwin18.6.0
Thread model: posix
InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin
```

> [pybind11 支持的编译器种类](https://github.com/pybind/pybind11#supported-compilers)

2. 直接用 pip 安装 pybind11 最方便：

```BASH
pip install pybind11
```

## HelloWorld

1. 写一个扩展，实现两个整数相加的功能，并暴露这个函数接口。代码文件保存为 example.cpp，如下：

```C++
#include <pybind11/pybind11.h>

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

// define the module name as example
PYBIND11_MODULE(example, m) {
    // optional module docstring
    m.doc() = "pybind11 example plugin";

    // bindings C++ function
    m.def("add", &add, "A function which adds two numbers");
}
```

2. 命令行执行编译

```BASH
c++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup $(python3 -m pybind11 --includes) example.cpp -o example$(python3-config --extension-suffix)
```

3. 编译成功后会得到一个名为 `example.cpython-36m-darwin.so` 的文件，在该文件的同级目录下进入 Python
   交互环境，并尝试使用扩展

```BASH
(lab) pybind11_example ➤ ls
example.cpp                   example.cpython-36m-darwin.so
(lab) pybind11_example ➤ python
Python 3.6.9 |Anaconda, Inc.| (default, Jul 30 2019, 13:42:17)
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import example
>>> example.add(1, 2)
3
>>>
```

---

```C++
// example1.cpp
#include <string>

#include <pybind11/pybind11.h>

const std::string MODULE_NAME = "example1";
const std::string AUTHOR = "tiger";

int add(int i, int j) {
    return i + j;
}

int add1(int i, int j) {
    return i + j;
}

int add2(int i = 1, int j = 2) {
    return i + j;
}

namespace py = pybind11;

// 模块名叫 example1
PYBIND11_MODULE(example1, m) {
    // 模块文档(非必须)
    m.doc() = "pybind11 example1 plugin";

    // 暴露 add() 函数
    m.def("add", &add, "function bindings: int add(int i, int j)",
          py::arg("i"), py::arg("j"));

    // 暴露 add1() 函数, 指定参数名称 i 和 j
    m.def("add1", &add1, "function bindings: int add1(int i, int j)",
          py::arg("i"), py::arg("j"));

    // 暴露 add2() 函数, 指定参数名称 i 和 j, 并指定参数默认值
    m.def("add2", &add2, "function bindings: int add2(int i = 1, int j = 2)",
        py::arg("i") = 1, py::arg("j") = 2);

    // 暴露全局变量(放在全局区~)
    m.attr("__module_name__") = MODULE_NAME;
    m.attr("__author__") = AUTHOR;
}
```

编译：`c++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup $(python3 -m pybind11 --includes) example1.cpp -o example1$(python3-config --extension-suffix)`

使用扩展：

```
(lab) pybind11_example ➤ python
Python 3.6.9 |Anaconda, Inc.| (default, Jul 30 2019, 13:42:17)
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import example1
>>> dir(example1)
['__author__', '__doc__', '__file__', '__loader__', '__module_name__', '__name__', '__package__', '__spec__', 'add', 'add1', 'add2']
>>> example1.__module_name__
'example1'
>>> example1.__author__
'tiger'
>>> example1.add(1, 2)
3
>>> example1.add1(1, 3)
4
>>> example1.add1(i=1, j=3)
4
>>> example1.add2()
3
>>>
```

---

