## 介绍和安装

Cython 是一种 Python 性能优化工具，用来提升 Python 的运行效率。在语法上是 Python
的超集，允许为数据添加类型，同时也是一个编译器，通过将 Cython 代码转换成经过优化的 C/C++ 代码来达到性能提升的目的。

> 平时说的 Python 一般指的是 CPython，也就是 C 实现的 Python。
> 除了这个之外，还有 Jython（Java 实现）、IronPython（C# 实现）、pypy（Python 实现）等。
> 这些不同版本的实现很大原因是为了解决性能问题（如消除 GIL、引入 JIT 等）。
> 但是，非官方实现要么是比较非主流，要么是对 Python/C API 的兼容性不是很好，
> 导致很多 CPython 下的好库无法使用

### 使用场景和优缺点

使用场景：

- 优化 CPU 密集型任务
- 作为胶水连接 Python 和 C/C++
- 消除 GIL（限制较多，比较鸡肋）

优点：

- 相比用 Python/C API 来写 C 扩展，Cython 的使用要容易很多
- 提供了 C 标准库、C++ 标准库（部分）、posix、Numpy（部分）等常用的库
- 能用较少的成本较明显地提升代码性能

缺点：

- 不适合大范围的优化。大范围的代码往往包含各种纯 Python 写的第三方库，Cython 代码中包含的纯 Python
  越多，优化效果越差，这时可能会面临重写第三方库的窘境
- 提供的常用库有些比较旧。比如 libcpp 中的 `vector.pxd`，并没有提供 C++11 中的 `emplace_back()` 方法
- 对于 Python2.x 和 Python3.x 的一些处理不一样。比如 Python2.x 中的字符串可以直接对应 libcpp 中的 `string`
  类型，Python3.x 中的字符串是一个 Unicode 容器， 需要先转换成 `bytes`
- 开发配套跟不上，像主流的 IDE Pycharm 最多只支持语法高亮，智能提示几乎没有（有一些 hack 可以缓解），大范围使用、调试、测试都比较不方便

### 安装

- 如果需要将 Cython 代码翻译成 C 代码，需要安装 C 编译器；如果需要翻译成 C++ 代码，则需要安装 C++ 编译器
- 通过 pip 安装 cython：`pip install cython`
- 验证是否安装成功：`cython -V`

---

## 使用例子

### 使用 Cython 的步骤

1. 分析代码，定位到需要优化的代码，并用 Cython 进行重写
2. 借助标准库中的 distutils（可以将 C/C++ 代码编译成扩展模块），编写 `setup.py` 用于后续编译
3. 执行 `python setup.py build_ext --inplace` 编译扩展模块
4. `import` 使用扩展模块
5. 分析优化效果，不断调整（本次略）

### 例子

一个找素数的程序，比较典型的 CPU 密集型任务，用 cProfile 做基准测试，耗时大概 16s：

```Python
# test.py

def primes_python(nb_primes):
    p = []
    n = 2
    while len(p) < nb_primes:
        for i in p:
            if n % i == 0:
                break
        else:
            p.append(n)
        n += 1
    return p


def main():
    nb_primes = 19999
    primes_python(nb_primes)


if __name__ == "__main__":
    main()
```

1. 分析代码，定位到需要优化的代码，并用 Cython 进行重写：

```Cython
# hello_cython.pyx

# 使用 C++ 标准库
from libcpp.vector cimport vector

def primes_cython(int nb_primes):
    # 添加类型
    cdef vector[int] p
    cdef int n, i

    n = 2

    while p.size() < nb_primes:
        for i in p:
            if n % i == 0:
                break
        else:
            p.push_back(n)
        n += 1

    return p
```

2. 编写 `setup.py` 用于后续编译：

```Python
# setup.py

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension(
    # Cython 扩展模块名称
    name="hello_cython",
    # Cython 源代码文件名称
    sources=["hello_cython.pyx"],
    # 生命需要翻译成 C++
    language="c++",
    # 编译参数
    extra_compile_args=["-Wno-cpp", "-Wno-unused-function", "-O2",
                        "-march=native", '-stdlib=libc++', '-std=c++11'],
    extra_link_args=["-O3", "-march=native", '-stdlib=libc++'],
)]
setup(
    name="hello_cython pyx",
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
)
```

3. 执行 `python setup.py build_ext --inplace` 编译扩展模块

4. `import` 使用扩展模块：

```Python
# test.py

# 导入扩展模块
import hello_cython


# def primes_python(nb_primes):
#     p = []
#     n = 2
#     while len(p) < nb_primes:
#         for i in p:
#             if n % i == 0:
#                 break
#         else:
#             p.append(n)
#         n += 1
#     return p


def main():
    nb_primes = 19999
    # primes_python(nb_primes)

    # 使用扩展
    hello_cython.primes_cython(nb_primes)


if __name__ == "__main__":
    main()
```

再次用 cProfile 做基准测试，耗时大概 800ms，效果拔群~!

---

## 自动类型转换

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/cython-12.png)

---

## 优化效果分析

1. 执行：`cython hello_cython.pyx -a`
2. 执行之后，可以得到一个 HTML 文件，浏览器打开：
   ![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/cython-2.png)
3. 白色代表已经优化成纯 C/C++ 代码，优化效果最好（点开行数前面的 + 号，可以看到对应的 C/C++ 代码）； 黄色代表和 Python
   发生了交互，颜色越深代表交互越多，优化效果越差

> 这个例子的优化效果已经不错了，头一行黄色基本上是跑不掉的，最后一行因为要返回对象到 Python 环境，也是跑不掉的。
> % 那一行也会黄色是编译器的一些问题，官方给出了解决方法：https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives

---

## 函数定义

Cython 提供三个函数定义关键字：`def`、`cdef`、`cpdef`

- 如果函数不需要跟纯 Python 代码交互，用 `cdef` 性能最好
- 如果函数需要跟纯 Python 代码交互，而且被频繁调用，用 `cpdef` 性能最好
- 如果函数需要跟纯 Python 代码交互，不会被频繁调用，用 `cpdef` 或者 `def` 都可以

---

## 类定义

```cython
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

cdef class SomeMemory:
    cdef double*data
    cdef double*mem

    def __cinit__(self, int number):
        self.data = <double*> PyMem_Malloc(number * sizeof(double))
        if not self.data:
            raise MemoryError()

    def __dealloc__(self):
        PyMem_Free(self.data)

    def resize(self, int new_number):
        mem = <double*> PyMem_Realloc(self.data, new_number * sizeof(double))
        if not mem:
            raise MemoryError()
        self.data = mem

    def test(self, content):
        self.data = content
```

可以用 `cdef` 关键字定义类，`__cinit__` 和 `__dealloc__` 是类的两个特殊方法，用于资源管理，效果类似 C++ 中的 RAII
概念，初始化对象时自动自行申请资源， 销毁对象时自动执行释放资源。

由于 Cython 一般用于局部优化，代码量一般不会太大，在实际使用中，感觉用结构体会比类方便。

---

## 突破 GIL 限制

- TODO

---

## libcpp 容器类型

### vector

在 Cython 代码中可以用 vector 代替 Python list，vector 支持 `[]` 操作符。

#### 对标 list.append(x)

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i

    for i in range(100):
        vec.push_back(i)
```

#### 对标遍历 list

```cython
# 方法一
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef int size

    for i in range(100):
        vec.push_back(i)

    i = 0
    size = vec.size()
    while i < size:
        print(vec[i])
        i += 1
```

````cython
# 方法二
from libcpp.vector cimport vector
from cython.operator cimport preincrement, dereference

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef vector[int].iterator it
    cdef vector[int].iterator it_end

    for i in range(100):
        vec.push_back(i)

    it = vec.begin()
    it_end = vec.end()
    while it != it_end:
        print(dereference(it))
        preincrement(it)
````

#### 对标 list.extend(iterator)

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef vector[int] sub_vec
    cdef int i

    for i in range(100):
        vec.push_back(i)

    for i in range(100):
        sub_vec.push_back(i)

    vec.insert(vec.end(), sub_vec.begin(), sub_vec.end())
```

#### 对标 list.insert(i, x)

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef vector[int].iterator it
    cdef int size
    cdef int value
    cdef int index

    for i in range(10):
        vec.push_back(i)

    it = vec.begin()
    index = 3
    value = 999
    if index < vec.size():
        vec.insert(it + index, value)

    it = vec.begin()
    index = 300
    value = 777
    if index < vec.size():
        vec.insert(it + 300, value)
```

#### 对标 list.remove(x)

```cython
from libcpp.vector cimport vector
from cython.operator cimport preincrement, dereference

cdef remove(vector[int]& vec, int value):
    cdef vector[int].iterator it
    cdef vector[int].iterator it_end

    it = vec.begin()
    it_end = vec.end()
    while it != it_end:
        if dereference(it) == value:
            vec.erase(it)
            return
        preincrement(it)

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef int value

    for i in range(10):
        vec.push_back(i)

    value = 3
    remove(vec, value)
```

#### 对标 list.pop()

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i

    for i in range(3):
        vec.push_back(i)

    if vec.size() > 0:
        vec.pop_back()

    if vec.size() > 0:
        vec.pop_back()

    if vec.size() > 0:
        vec.pop_back()

    if vec.size() > 0:
        vec.pop_back()
```

#### 对标 list.pop(i)

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef int index
    cdef vector[int].iterator it
    cdef int result

    for i in range(2):
        vec.push_back(i)

    it = vec.begin()
    index = 3121
    if vec.size() > 0 and index < vec.size():
        vec.erase(it + index)

    it = vec.begin()
    index = 0
    if vec.size() > 0 and index < vec.size():
        result = vec[index]
        vec.erase(it + index)

    it = vec.begin()
    index = 1
    if vec.size() > 0 and index < vec.size():
        result = vec[index]
        vec.erase(it + index)

    return result
```

#### 对标 list.clear()

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i

    for i in range(10):
        vec.push_back(i)

    vec.clear()
```

#### 对标 list.index(x)

```cython
from libcpp.vector cimport vector

cdef int index(vector[int]& vec, int value):
    cdef int i = 0
    cdef int size = vec.size()

    while i < size:
        if vec[i] == value:
            return i
        i += 1

    return -1

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef int value

    for i in range(10):
        vec.push_back(i)

    value = 8
    index(vec, value)
```

#### 对标 list.count(x)

```cython
from libcpp.vector cimport vector

cdef int count(vector[int]& vec, int value):
    cdef int i = 0
    cdef int size = vec.size()
    cdef int count = 0

    while i < size:
        if vec[i] == value:
            count += 1
        i += 1

    return count

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef int value

    for i in range(10):
        vec.push_back(i)

    value = 7
    count(vec, value)
```

#### 对标 list.sort()

```cython
from libcpp.vector cimport vector
from libcpp.algorithm cimport make_heap, sort_heap
from libcpp cimport bool

cdef inline bool greater(const int & x, const int & y):
    return x > y

cpdef test_vector():
    cdef vector[int] vec
    cdef int i

    for i in range(10):
        vec.push_back(i)

    make_heap(vec.begin(), vec.end(), &greater)
    sort_heap(vec.begin(), vec.end(), &greater)
```

#### 对标 list.reverse()

```cython
from libcpp.vector cimport vector

cpdef test_vector():
    cdef vector[int] vec
    cdef int i
    cdef vector[int] reverse_vec
    cdef int j

    for i in range(10):
        vec.push_back(i)

    j = vec.size() - 1
    while j >= 0:
        reverse_vec.push_back(vec[j])
        j -= 1
```

### map

在 Cython 代码中可以用 map 代替 Python dict，map 支持 `[]` 操作符。

#### 对标 dict[k] = v

````cython
# 方法一
from libcpp.map cimport map

cpdef test_map():
    cdef map[int, int] m

    for i in range(10):
        m[i] = i
````

```cython
# 方法二
from libcpp.map cimport map
from libcpp.pair cimport pair

cpdef test_map():
    cdef map[int, int] m
    cdef pair[int, int] _pair

    for i in range(10):
        _pair.first = i
        _pair.second = i
        m.insert(_pair)
```

#### 对标遍历 dict

````cython
# 方法一
from libcpp.map cimport map
from libcpp.pair cimport pair

cpdef test_map():
    cdef map[int, int] m
    cdef pair[int, int] _pair

    for i in range(10):
        m[i] = i

    for _pair in m:
        print(_pair.first, _pair.second)
````

```cython
# 方法二
from libcpp.map cimport map
from libcpp.pair cimport pair
from cython.operator cimport preincrement, dereference

cpdef test_map():
    cdef map[int, int] m
    cdef pair[int, int] _pair
    cdef int i
    cdef map[int, int].iterator it

    for i in range(10):
        _pair.first = i
        _pair.second = i
        m.insert(_pair)

    it = m.begin()
    while it != m.end():
        print(dereference(it).first, dereference(it).second)
        preincrement(it)
```

#### 对标 del dict[k]

```cython
from libcpp.map cimport map
from libcpp.pair cimport pair

cdef remove(map[int, int]& m, int key):
    cdef map[int, int].iterator it
    cdef pair[int, int] _pair

    for _pair in m:
        if key == _pair.first:
            it = m.find(key)
            m.erase(it)

cpdef test_map():
    cdef map[int, int] m
    cdef int i
    cdef int key

    for i in range(10):
        m[i] = i

    key = 3
    remove(m, key)

    key = 700
    remove(m, key)
```

#### 对标 dict.clear()

```cython
from libcpp.map cimport map

cpdef test_map():
    cdef map[int, int] m
    cdef int i

    for i in range(10):
        m[i] = i

    m.clear()
```

#### 对标 dict.pop(k)

```cython
from libcpp.map cimport map
from libcpp.pair cimport pair
from cython.operator cimport dereference

cdef pair[int, int] pop_by_key(map[int, int]& m, int key):
    cdef map[int, int].iterator it
    cdef pair[int, int] result
    cdef pair[int, int] _pair

    if m.size() > 0:
        for _pair in m:
            if key == _pair.first:
                it = m.find(key)
                result.first = dereference(it).first
                result.second = dereference(it).second
                m.erase(it)
                return result

    result.first = -1
    result.second = -1
    return result

cpdef test_map():
    cdef map[int, int] m
    cdef int i
    cdef pair[int, int] result
    cdef int key

    for i in range(3):
        m[i] = i

    key = 0
    result = pop_by_key(m, key)
    print(result)
    print(m)

    key = 600
    result = pop_by_key(m, key)
    print(result)
    print(m)

    key = 1
    result = pop_by_key(m, key)
    print(result)
    print(m)

    key = -8989
    result = pop_by_key(m, key)
    print(result)
    print(m)

    key = 2
    result = pop_by_key(m, key)
    print(result)
    print(m)

    key = 0
    result = pop_by_key(m, key)
    print(result)
    print(m)

    key = 0
    result = pop_by_key(m, key)
    print(result)
    print(m)

    return result
```

#### 对标 dict.popitem()

```cython
from libcpp.map cimport map
from libcpp.pair cimport pair
from cython.operator cimport dereference

cdef pair[int, int] popitem(map[int, int]& m):
    cdef map[int, int].iterator it
    cdef pair[int, int] result

    if m.size() > 0:
        it = m.begin()
        result.first = dereference(it).first
        result.second = dereference(it).second

        m.erase(it)

        return result

    result.first = -1
    result.second = -1
    return result

cpdef test_map():
    cdef map[int, int] m
    cdef int i
    cdef pair[int, int] result

    for i in range(3):
        m[i] = i

    result = popitem(m)
    result = popitem(m)
    result = popitem(m)
    result = popitem(m)

    return result
```

#### 对标 dict[k]

```cython
from libcpp.map cimport map
from libcpp.pair cimport pair
from cython.operator cimport dereference

cdef pair[int, int] get(map[int, int]& m, int key):
    cdef map[int, int].iterator it
    cdef pair[int, int] result
    cdef pair[int, int] _pair

    for _pair in m:
        if key == _pair.first:
            it = m.find(key)
            result.first = dereference(it).first
            result.second = dereference(it).second
            return result

    result.first = -1
    result.second = -1
    return result

cpdef test_map():
    cdef map[int, int] m
    cdef int i
    cdef pair[int, int] result
    cdef int key

    for i in range(10):
        m[i] = i

    key = 5
    result = get(m, key)

    key = 500
    result = get(m, key)

    return result
```

#### 对标 len(dict)

````cython
from libcpp.map cimport map

cpdef test_map():
    cdef map[int, int] m
    cdef int i

    for i in range(10):
        m[i] = i

    m.size()
````

#### 对标 k in dict

```cython
from libcpp.map cimport map
from libcpp.pair cimport pair

cdef int _in(map[int, int]& m, int key):
    cdef map[int, int].iterator it
    cdef pair[int, int] _pair

    for _pair in m:
        if key == _pair.first:
            return 1

    return -1

cpdef test_map():
    cdef map[int, int] m
    cdef int i
    cdef int result
    cdef int key

    for i in range(10):
        m[i] = i

    key = 7
    result = _in(m, key)

    key = 71
    result = _in(m, key)

    return result
```

### set

在 Cython 代码中可以用 set 代替 Python set。

#### 对标 set.add(x)

```cython
from libcpp.set cimport set

def test_set():
    cdef set[int] s
    cdef int i

    for i in range(10):
        s.insert(i)
```

#### 对标遍历 set

```cython
# 方法一
from libcpp.set cimport set

def test_set():
    cdef set[int] s
    cdef int i
    cdef int item

    for i in range(10):
        s.insert(i)

    for item in s:
        print(item)
```

```cython
# 方法二
from libcpp.set cimport set
from cython.operator cimport preincrement, dereference

def test_set():
    cdef set[int] s
    cdef set[int].iterator it
    cdef int i

    for i in range(10):
        s.insert(i)

    it = s.begin()
    while it != s.end():
        print(dereference(it))
        preincrement(it)
```

#### 对标 set.remove(x)

```cython
from libcpp.set cimport set

cdef remove(set[int]& s, int value):
    cdef set[int].iterator it
    cdef int item

    for item in s:
        if item == value:
            it = s.find(value)
            s.erase(it)

def test_set():
    cdef set[int] s
    cdef int i
    cdef int value

    for i in range(10):
        s.insert(i)

    value = 3
    remove(s, value)

    value = 113
    remove(s, value)
```

#### 对标 set.pop()

```cython
from libcpp.set cimport set
from cython.operator cimport dereference

cdef int pop(set[int]& s):
    cdef set[int].iterator it
    cdef int result

    if s.size() > 0:
        it = s.begin()
        result = dereference(it)
        s.erase(it)
        return result

    return -1

def test_set():
    cdef set[int] s
    cdef int i
    cdef int result

    for i in range(3):
        s.insert(i)

    result = pop(s)

    result = pop(s)

    result = pop(s)

    result = pop(s)

    return result
```

#### 对标 set.clear()

```cython
from libcpp.set cimport set

def test_set():
    cdef set[int] s
    cdef int i

    for i in range(10):
        s.insert(i)

    s.clear()

    s.clear()
```

#### 对标 len(set)

```cython
from libcpp.set cimport set

def test_set():
    cdef set[int] s
    cdef int i

    for i in range(10):
        s.insert(i)

    s.size()
```

#### 对标 x in set

```cython
from libcpp.set cimport set

cdef int _in(set[int]& s, int value):
    cdef int item

    for item in s:
        if item == value:
            return 1

    return -1

def test_set():
    cdef set[int] s
    cdef int i
    cdef int result
    cdef int value

    for i in range(10):
        s.insert(i)

    value = 1
    result = _in(s, value)

    value = 1111
    result = _in(s, value)

    return result
```

### 参考

- [详细](https://github.com/cython/cython/tree/master/Cython/Includes/libcpp)
- [Using C++ in Cython](https://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html#using-c-in-cython)

---


