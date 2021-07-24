## SQLAlchemy

1. [SQLAlchemy Core](https://github.com/hsxhr-10/Notes/blob/master/Python-Web/SQLAlchemy%E7%AC%94%E8%AE%B0.md#sqlalchemy-core)
2. [SQLAlchemy ORM](https://github.com/hsxhr-10/Notes/blob/master/Python-Web/SQLAlchemy%E7%AC%94%E8%AE%B0.md#sqlalchemy-orm)

![](https://raw.githubusercontent.com/hsxhr-10/Notes/master/image/pythonwebsqla-1.png)

- Core 提供了各种核心组件
- ORM 负责提供对象关系映射建模和一些高级的接口
- DBAPI 代表对应的数据库驱动

### 一些概念

#### Schema/Type：提供字段数据类型

- [Generic Types](https://docs.sqlalchemy.org/en/14/core/type_basics.html#generic-types)
- [SQL Standard and Multiple Vendor Types](https://docs.sqlalchemy.org/en/14/core/type_basics.html#sql-standard-and-multiple-vendor-types)
- [MySQL Data Types](https://docs.sqlalchemy.org/en/14/dialects/mysql.html#mysql-data-types)
- [Included Dialects](https://docs.sqlalchemy.org/en/13/dialects/index.html#included-dialects)

#### SQL Expression Language：提供 `in/or/and/not/desc/asc` 等操作

- [Column Element Foundational Constructors](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#column-element-foundational-constructors)
- [Column Element Modifier Constructors](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#column-element-modifier-constructors)
- [ColumnElement](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement)

#### Engine：提供连接池配置

![](https://raw.githubusercontent.com/hsxhr-10/Notes/master/image/pythonwebsqla-2.png)

```
⭐️ Engine 和连接池都是线程安全️

create_engine() 方法：用于创建 Engine 对象和配置连接池

- url：数据库连接 URL，格式 `dialect+driver://username:password@host:port/database`
  。具体参考 [这里](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)
- echo=False：是否开启 Engine 日志。对性能有比较大的影响，线上环境应该关闭
- echo_pool=False：是否开启连接池日志。对性能有比较大的影响，线上环境应该关闭
- isolation_level：事务隔离级别。取值 ("SERIALIZABLE", "REPEATABLE READ", "READ COMMITTED"
  , "READ UNCOMMITTED")，一般不需要主动设置
- pool_size=5：连接池中保持打开的连接数。QueuePool 下设置为 0 代表无限制
- max_overflow=10：在 pool_size 之外还能打开的连接数，也就是最大连接数，仅在 QueuePool 下有效
- pool_pre_ping：每次从池中取出连接时，是否检测连接的有效性。一般设置为 True 确保使用有效的连接
- pool_recycle=-1：主动回收连接的时长。MySQL 默认 8 小时后如果检测到空闲连接，就会主动断开连接
- pool_timeout=30：从池中获取连接的等待时间。单位秒
```

```
# autocommit 在 version1.4 之后被遗弃
# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Connection.execution_options.params.autocommit 
# https://docs.sqlalchemy.org/en/14/changelog/migration_20.html#library-level-but-not-driver-level-autocommit-removed-from-both-core-and-orm

with engine.connect() as connection:
    connection.execute(text("insert into table values ('foo')"))
    connection.commit()

with engine.connect() as conn:
    conn.execute(...)
    conn.execute(...)
    conn.commit()

    conn.execute(...)
    conn.execute(...)
    conn.commit()

# 事务
with engine.begin() as connection:
    connection.execute(text("insert into table values ('foo')"))
    
with engine.connect() as conn:
    with conn.begin():
        conn.execute(...)
        conn.execute(...)

    with conn.begin():
        conn.execute(...)
        conn.execute(...)

https://docs.sqlalchemy.org/en/14/core/future.html#sqlalchemy.future.Connection
```

#### Session 对象：代表一次 SQL 操作的会话，默认 autucommit 为 False

📢 Engine 线程安全，优先用 Engine。

```
⭐️ Session 不是线程安全，可以用 `contextmanager` 加 `yield` 解决️

from contextlib import contextmanager


@contextmanager
def session_factory():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


with session_factory() as session:
    # use session
    pass
```

```
sessionmaker()：用于创建 Session 对象

- bind：与 Session 关联的 Engine 对象
- autoflush=True：flush 之后 SQL 才会被执行。一般设置成 True，就不需要每条 SQL 后面 flush 一下
- autocommit=False：是否自动提交事务
- expire_on_commit=True：Session 是否在事务提交之后失效
```

### ORM 建模

factory 表和 product 表是一对多关系，orders 表和 product 表关系是多对多。

```sql
CREATE TABLE factory
(
    `id`          bigint(11) NOT NULL AUTO_INCREMENT,
    `is_deleted`  tinyint(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记, 0 是未删除, 1 是已删除',
    `create_time` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建的时间',
    `update_time` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改的时间',
    `factory_id`  varchar(255) NOT NULL UNIQUE COMMENT '生产厂家ID',
    `name`        varchar(45)  NOT NULL COMMENT '生产厂家名称',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产厂家信息';
```

```sql
CREATE TABLE product
(
    `id`          bigint(11) NOT NULL AUTO_INCREMENT,
    `is_deleted`  tinyint(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记, 0 是未删除, 1 是已删除',
    `create_time` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建的时间',
    `update_time` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改的时间',
    `product_id`  varchar(255) NOT NULL UNIQUE COMMENT '商品ID',
    `name`        varchar(45)  NOT NULL COMMENT '商品名称',
    `factory_id`  varchar(255) NOT NULL UNIQUE COMMENT '关联的生产厂家ID',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品信息';
```

```sql
CREATE TABLE orders
(
    `id`          bigint(11) NOT NULL AUTO_INCREMENT,
    `is_deleted`  tinyint(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记, 0 是未删除, 1 是已删除',
    `create_time` timestamp      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建的时间',
    `update_time` timestamp      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改的时间',
    `order_id`    varchar(255)   NOT NULL UNIQUE COMMENT '订单ID',
    `price`       decimal(13, 5) NOT NULL DEFAULT 0 COMMENT '订单金额',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单信息';
```

```sql
CREATE TABLE orders_product
(
    `id`          bigint(11) NOT NULL AUTO_INCREMENT,
    `is_deleted`  tinyint(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除标记, 0 是未删除, 1 是已删除',
    `create_time` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建的时间',
    `update_time` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改的时间',
    `order_id`    varchar(255) NOT NULL UNIQUE COMMENT '订单ID',
    `product_id`  varchar(255) NOT NULL UNIQUE COMMENT '商品ID',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表和商品表的多对多关系';
```

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    DECIMAL,
    text
)
from sqlalchemy.dialects.mysql import TINYINT

_Base = declarative_base()


class _BaseMixin(_Base):
    """ 基类 ORM, 包含一些必须的字段 """
    __abstract__ = True
    __bind_key__ = 'extension_model'

    id = Column(Integer, primary_key=True)
    is_deleted = Column(TINYINT, nullable=False, default=0)
    create_time = Column(DateTime, nullable=False,
                         default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False,
                         default=text("CURRENT_TIMESTAMP"))


class Factory(_BaseMixin):
    __tablename__ = "factory"

    factory_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(45), nullable=False)


class Product(_BaseMixin):
    """ Factory 和 Product 一对多 """
    __tablename__ = "product"

    product_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(45), nullable=False)
    factory_id = Column(String(255), nullable=False, unique=True)


class Orders(_BaseMixin):
    __tablename__ = "orders"

    order_id = Column(String(255), nullable=False, unique=True)
    price = Column(DECIMAL(13, 5), nullable=False, default=0)


class OrdersProduct(_BaseMixin):
    """ Orders 和 Product 多对多 """
    __tablename__ = "orders_product"

    order_id = Column(String(255), nullable=False, unique=True)
    product_id = Column(String(255), nullable=False, unique=True)
```

### 常见 SQL 操作

单表查询：

```
# select * from factory;
with session_factory() as session:
  session.query(Factory).all()

# select * from factory where name='工厂1号';     
with session_factory() as session:
  session.query(Factory).filter(Factory.name == "工厂1号").all()

# select * from factory where id='a1d760f2-275e-4efb-ae02-dc4d5434fb10' and name='工厂1号';
with session_factory() as session:
  session.query(Factory).filter(Factory.id == "a1d760f2-275e-4efb-ae02-dc4d5434fb10").filter(Factory.name == "工厂1号").all()

# select * from factory where id='a1d760f2-275e-4efb-ae02-dc4d5434fb10' or name='工厂1号';
from sqlalchemy import or_
with session_factory() as session:
  session.query(Factory).filter(or_(Factory.name == "工厂1号", Factory.name == "工厂2号")).all()
  
# select * from factory limit 1;
with session_factory() as session:
  session.query(Factory).first()

# select * from factory order by name desc limit 1;
with session_factory() as session:
  session.query(Factory).order_by(Factory.name.desc()).first()
```

连表查询：

```
# select p.name, f.name from product p inner join factory f on p.factory_id=f.factory_id;
with session_factory() as session:
  session.query(Factory.name, Product.name).join(Product, Factory.factory_id == Product.factory_id).all()

with session_factory() as session:
  session.query(Factory.name, Product.name).filter(Factory.factory_id == Product.factory_id).all()

# select p.name, f.name from product p inner join factory f on p.factory_id=f.factory_id where f.name='工厂2号'";
with session_factory() as session:
  session.query(Factory.name, Product.name).join(Product, Factory.factory_id == Product.factory_id).filter(Factory.name == "工厂2号").all()

# select t1.name, t2.name, t3.name from table1 t1 inner join t2 on t1.id=t2.id LEFT join table3 t3 on t2.id=t3.id where t1.name='aaa' and t3.name='ccc';
with session_factory() as session:
  session.query(table1.name, table2.name, table3.name)\
         .join(table2, table1.id == table2.id)\
         .outerjoin(table3, table2.id == table3.id)\
         .filter(table1.name == "aaa", table3.name == "ccc")\
         .all()
```

插入：

```
with engine.connect() as conn:
    conn.execute(Factory.insert(), factory_id=12345678, name="HuaWei")
    conn.commit()

# 批量
with engine.connect() as conn:
    conn.execute(Factory.insert(), [
        {"factory_id": 72361281, "name": "Apple"},
        {"factory_id": 12345678, "name": "HuaWei"},
        {"factory_id": 27387283, "name": "XiaoMi"},
    ])
    conn.commit()
```

raw SQL：

```python
from sqlalchemy.sql import text

sql = text("select * from factory where name=:name;")
with engine.connect() as conn:
    res = conn.execute(sql, {"name": "工厂1号"})

for row in res:
    for k, v in row.items():
        print("{}={}".format(k, v))
```

### 参考

- [Query API](https://docs.sqlalchemy.org/en/14/orm/query.html#query-api)
- [Multi-threaded use of SQLAlchemy](https://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy#:~:text=Session%20objects%20are%20not%20thread,%2C%20but%20are%20thread%2Dlocal.&text=If%20you%20don't%20want,object%20by%20default%20uses%20threading.)
