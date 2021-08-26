![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/mysql-1.png)

### InnoDB vs. MyISAM

InnoDB：

- 支持事务
- 支持行锁
- 支持数据缓存
- 存储容量上限为 64TB
- 支持外键

MyISAM：

- 不支持事务
- 只支持表锁
- 不支持数据缓存
- 存储容量上限为 256TB
- 不支持外键

### 日常 SQL

```
# 创建用户
create user '$user'@'$ip' identified by '$password';
# 删除用户
drop user '$user'@'$ip';
# 授权用户（全部权限）
grant all privileges on *.* to '$user'@'$ip' identified by '$password'; flush privileges;
# 查看用户授权情况
select * from information_schema.user_privileges;
# 查看支持的存储引擎
show engines \g;
# 查看某个系统变量
show variables like '%<variable>%';
# 全局修改某个系统变量
set global $variable=$value;
```

---

## SQL

### DDL

库：

-

创建数据库：`CREATE DATABASE IF NOT EXISTS <database_name> CHARACTER SET <charset_name>;`

- 显示数据库：`SHOW DATABASES;`
- 删除数据库：`DROP DATABASE <database_name>;`
- 选择数据库：`USE <database_>name;`

表：

- 显示所有表：`SHOW TABLES`;
- 显示表结构：`DESCRIBE <table_name>;`
- 显示建表定义：`SHOW CREATE TABLE <table_name>\G;`
- 删除列：`ALTER TABLE <table_name> DROP COLUMN <column_name>;`
- 给表改名：`ALTER TABLE <old_name> RENAME TO <new_name>;`
- 删除表：`DROP TABLE IF EXISTS <table_name>;`
- 建表
    ```sql
    CREATE TABLE user (
        `id` bigint(11) NOT NULL AUTO_INCREMENT,
        `user_id` bigint(11) NOT NULL COMMENT '用户id',
        `username` varchar(45) NOT NULL COMMENT '真实姓名',
        `email` varchar(30) NOT NULL COMMENT '用户邮箱',
        `nickname` varchar(45) NOT NULL COMMENT '昵称',
        `avatar` int(11) NOT NULL COMMENT '头像',
        `birthday` date NOT NULL COMMENT '生日',
        `sex` tinyint(4) NOT NULL DEFAULT 0 COMMENT '性别',
        `short_introduce` varchar(150) NOT NULL DEFAULT '' COMMENT '一句话介绍自己, 最多50个汉字',
        `user_resume` varchar(300) NOT NULL COMMENT '用户提交的简历存放地址',
        `user_register_ip` int NOT NULL COMMENT '用户注册时的源ip',
        `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '用户记录创建的时间',
        `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '用户资料修改的时间',
        `user_review_status` tinyint NOT NULL COMMENT '用户资料审核状态, 1为通过, 2为审核中, 3为未通过, 4为还未提交审核',
        PRIMARY KEY (`id`),
        UNIQUE KEY `uq_user_id` (`user_id`),
        KEY `idx_username` (`username`),
        KEY `idx_mul_create_time` (`create_time`,`user_review_status`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网站用户基本信息';
    ```

列：

- 新加一个列：`ALTER TABLE <table_name> ADD <column_name> <column_definition>;`
-

新加多个列：`ALTER TABLE <table_name> ADD <column_name> <column_definition>, ADD <column_name> <column_definition>, ...;`

- 修改一个列：`ALTER TABLE <table_name> MODIFY <column_name> <column_definition>;`
-

修改多个列：`ALTER TABLE <table_name> MODIFY <column_name> <column_definition>, MODIFY <column_name> <column_definition>, ...;`
-
给列改名：`ALTER TABLE <table_name> CHANGE COLUMN <old_name> <new_name> <column_definition>;`

### DML

SELECT 执行顺序：

```SQL
SELECT < column_name >, [AGG_FUNC(< column_name >/< expression >)]
FROM < table_name >
    JOIN <other_table_name>
ON < table_name >.< column_name > = <other_table_name>.< column_name >
WHERE <filter_expression>
GROUP BY < column_name >
HAVING <filter_expression>
ORDER BY < column_name > ASC / DESC
    LIMIT < count >;
```

1. `from ... join ... on`
2. `where`
    - `=` / `!=` / `>` / `>=` / `<` / `<=`
    - `and` / `or` / `not`
    - `in` / `not in`
    - `between` / `not between`
    - `like` / `not like`
    - `is null` / `is not null`
3. `select ... agg_func`
    - `SUM()` / `COUNT()` / `MAX()` / `MIN()` / `AVG()`
4. `group by`
5. `having`
    - 对 `group by` 结果过滤
6. `order by`
7. `limit`

连接查询：

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/SQL%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0-1.png)

```
select t3.imageid, t2.ProductCode, t3.filepath, t2.name, t2.defaultimage
from table1 t1
inner join table2 t2 on t2.ProductCode=t1.ProductCode
inner join table3 t3 on t2.ProductID=t3.ProductID
where t1.adddatetime>"{}";
```

insert | update | delete：

```
insert into $table(c1, c2, ...)
values 
   (v1, v2, ...),
   ...;
   
update $table set c1=v1, c2=v2 where ...

delete from $table where ...;
```

事务：

```
BEGIN;
...
COMMIT;

BEGIN;
...
ROLLBACK;
```

---

## 执行计划

- 分析索引使用情况，提供优化依据
- 连接查询时，显示驱动表是哪个，被驱动表是哪个（驱动表在前面，被驱动表在后面），从而可以分析被驱动表的连接列上有没有用到索引

```SQL
mysql
> explain
select *
from employees
where first_name = "Georgi";
+----+-------------+-----------+------------+------+---------------+------+---------+------+--------+----------+-------------+
| id | select_type | table     | partitions | type | possible_keys | key  | key_len | ref  | rows   | filtered | Extra       |
+----+-------------+-----------+------------+------+---------------+------+---------+------+--------+----------+-------------+
|  1 | SIMPLE      | employees | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 299379 |    10.00 | Using where |
+----+-------------+-----------+------------+------+---------------+------+---------+------+--------+----------+-------------+
1 row in set, 1 warning (0.00 sec)
```

- 一般看 `possible_keys`、`key`、`type`、`rows` 这几个字段
- `possible_keys`：候选的索引
- `key`：实际走的索引
- `type`：索引的效果指标，`const` > `ref` > `range` > `index` ~= `ALL`
    - `const`：聚簇索引或者二级索引 + `where` 等值匹配 + 单表查询 + 查询结果只有单行匹配
    - `ref`：二级索引 + `where` 等值匹配 + 查询结果有多行匹配
    - `range`：二级索引 + `where` 范围匹配
    - `index`：扫描聚簇索引的所有叶子结点（效果约等于全表扫描）
    - `ALL`：全表扫描
- `row`：需要扫描的总行数（当然越少越好）

---

## 事务

事务特性：

- A：原子性。事务里的多个 SQL 要么都成功，要么都失败
- C：一致性。事务发生之前数据是正确的，事务之后也是正确的
- I：隔离性。不同事务之间互相独立、互不影响
- D：持久性。事务的修改是永久的，不会因为关机、重启等情况而倒退

事务隔离级别：

- S > RR > RU > RC
- 脏写：两个事务可以修改相同的数据
- 脏读：可以读到未提交的数据
- 不可重复读：可以读取已提交的数据
- 幻读：同一条 SQL 多次查询结果不一样

使用建议：

- 事务隔离级别为 RR
- 事务里面的 SQL 不超过 5 个
- 将外部依赖调用移出事务，避免外部依赖发生问题导致事务执行时间过长
- 对于一致性要求高的业务场景，应该开启事务并访问主库

---

## 索引

InnoDB 索引：

- 索引对应的数据结构是什么：B+ 树
- 为什么不用 B 树：B 树的非叶子节点即保存索引列，也保存数据列，而 B+ 树只保存索引列，也就是 B+ 树可以加载更多索引列到内存中
- 为什么不用红黑树：当数据量太大时，内存不能放下整棵 B+ 树，剩下的部分就需要在磁盘中进行读取，树太高会导致所需要的磁盘随机 IO 次数越多
- 为什么不用哈希表：哈希表适合做等值查询、一般不适合范围查询
- 一颗 B+ 树可以存放多少行数据：树高为 3 一般可以存放两千万左右

### 索引结构

聚簇索引：

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/mysql-2.png)

单列二级索引：

**※️ 二级索引一般都要回表，除非符合覆盖索引**

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/mysql-3.png)

联合二级索引：

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/mysql-4.png)

---

## 锁

### 表锁 vs. 行锁

- 表锁：锁的粒度大，发生锁冲突的概率大，并发程度低，不会出现死锁，开销小，加锁快。一般出现在 DDL
- 行锁：锁的粒度小，发生锁冲突的概率相对小，并发程度高，会出现死锁，开销大，加锁慢。一般出现在 DML

### 行锁

重要特性：

- 行锁指的是加在索引列上的锁
- 一般用于事务中的 SQL 语句
-

行锁可以细分为：记录锁（Record-Lock）、间隔锁（Gap-Lock）、next-key-lock（记录锁+间隔锁）、插入意向锁（LOCK_INSERT_INTENSION
，只用于 INSERT 语句，是一种特殊的间隔锁）

- InnoDB 在 RR 隔离级别下默认加的行锁是 next-key-lock，具体要看索引类型是什么
- InnoDB 下的读操作是快照读，默认不加锁，而写操作则是默认加写锁
- 如果是二级索引，会涉及回表加锁
  ![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/mysql-19.png)
- MySQL 的加锁步骤是按照查询结果一条条加的，比如 `update students set level = 3 where score >= 60;`
  查询出来 100 条，而且 score 是二级索引， 那么理论上就要进行 200 次的加锁操作（二级索引和聚簇索引各 100 次）
- 间隔锁之间不会发生冲突，间隔锁只会和插入意向锁发生冲突。间隔锁和插入意向锁共同防止幻读发生

加锁方法：

```
# 读锁
select...lock in share mode;
# 写锁
select...for update;
```

读写锁规则：

- 读锁：加了读锁的数据，其他 SQL 可以读，可以加读锁
- 写锁：加了写锁的数据，其他 SQL 可以快照度

锁释放时机：

- 提交事务
- 回滚事务
- 事务进程被 kill

加锁分析：

- 确认事务隔离级别（RR 有间隔锁、RC 没有间隔锁）
- 确认是否用到索引
    - 如果没用到索引，那么全表记录加 next-key-lock
    - 如果用到索引，那么确认索引种类
        - 聚簇索引
            - 查询命中，`WHERE` 等值运算符，聚簇索引列加记录锁
            - 查询命中，`WHERE` 范围运算符，聚簇索引列加 next-key-lock
            - 查询没命中，聚簇索引列加间隔锁
        - 二级唯一索引
            - 查询命中，`WHERE` 等值运算符，二级索引列加记录锁，回表时聚簇索引列加记录锁
            - 查询命中，`WHERE` 范围运算符，二级索引列加 next-key-lock，回表时聚簇索引列加记录锁
            - 查询没命中，二级索引列加间隔锁，回表时聚簇索引列不用加锁
        - 二级非唯一索引
            - 查询命中，`WHERE` 等值运算符，二级索引列加 next-key-lock，回表是聚簇索引列加记录锁
            - 查询命中，`WHERE` 范围运算符，二级索引列加 next-key-lock，回表是聚簇索引列加记录锁
            - 查询没命中，二级索引列加间隔锁，回表时聚簇索引列不用加锁

排查死锁：

1. 确保开启死锁日志、binlog
2. 通过死锁日志初步了解涉及的事务有哪些、事务持有的锁是什么、等待的锁是什么、相关的 SQL 是什么
3. 通过死锁日志中死锁发生的时间，或者 SQL，到 binlog 中找到其中一个事务的完整 SQL（注意，因为只有提交了的事务才会记录到
   binlog，回滚的不会被记录， 所以在设置了超时的情况下，一般只会有一个阻塞事务的完整 SQL 被记录到 binlog）
4. 根据这一组完整的 SQL 到应用程序的代码中找到相关的逻辑，结合死锁日志中另一个事务的 SQL，一般就可以推理出另一个事务在哪里
5. 尝试重现死锁的发生，根据实际情况解决

---

## SQL 优化

1. 硬件（CPU、内存、磁盘、网络、带宽）
2. 操作系统
3. InnoDB
4. 表结构
5. 索引
6. 应用程序驱动

---

## 表设计

三范式：

- 第一范式：列不能再拆
- 第二范式：表不能再拆
- 第三范式：表不能冗余

数据类型存储大小参考：

![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/%E6%95%B0%E6%8D%AE%E5%BA%93%E8%AE%BE%E8%AE%A1-3.png)
![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/%E6%95%B0%E6%8D%AE%E5%BA%93%E8%AE%BE%E8%AE%A1-4.png)
![](https://raw.githubusercontent.com/hsxhr-10/Blog/master/image/%E6%95%B0%E6%8D%AE%E5%BA%93%E8%AE%BE%E8%AE%A1-5.png)

常用约束：

- 主键约束
- 非空约束
- 默认值约束
- 唯一约束
- 检查约束
- 外键约束

---

## 参考

-

MySQL数据库设计规范：https://github.com/jly8866/archer/blob/master/src/docs/mysql_db_design_guide.md#mysql%E6%95%B0%E6%8D%AE%E5%BA%93%E8%AE%BE%E8%AE%A1%E8%A7%84%E8%8C%83

- [一张图彻底搞懂 MySQL 的锁机制](https://learnku.com/articles/39212?order_by=vote_count&)
- [为什么开发人员必须要了解数据库锁？](https://mp.weixin.qq.com/s/yzXbbutzVJ1hIZgVszIBgw)
- [MySQL死锁系列-线上死锁问题排查思路](https://cloud.tencent.com/developer/article/1722416)
- [开启 MySQL 的 binlog 日志](https://blog.csdn.net/king_kgh/article/details/74800513)
- [Mysql事务和锁（四） 死锁](https://www.zbpblog.com/blog-208.html)
