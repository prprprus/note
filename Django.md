- [pycharm中django的objects无代码提示、自动补全的真香方案](https://blog.csdn.net/ch_improve/article/details/110182289)
- [解决 Django 时区设置不生效问题](https://stackoverflow.com/questions/30588926/why-the-time-is-different-from-my-time-zone-in-settings-py)
- Django 的其中一个理念：提供各种抽象层封装、框架，目的是隔离应用代码和底层平台，方便切换不同平台时，无需修改上层代码
- Django 更像是 它给你设想好了需求，然后它根据这些需求，设计、实现好了对应的框架和工具。如果你的需求能够被设想的需求所覆盖，那么用 Django
  会很爽；如果你的需求超出了设想的需求，那么用 Django 会比较别扭

---

## 常用命令

### django-admin

- 创建项目：django-admin startproject $project_name
- 根据模板创建子应用：django-admin startapp --template $app_template_dir $app_name

### manage.py

- 创建超级用户：python manage.py createsuperuser
- 同步数据表：python manage.py makemigrations && python manage.py migrate
- 运行测试：python manage.py test
- 运行服务：python manage.py runserver

---

## 模型层

### 模型定义

- [普通字段类型](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#field-types)
    - [BigAutoField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#bigautofield)
    - [IntegerField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#integerfield)
    - [FloatField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#floatfield)
    - [DecimalField(max_digits=10, decimal_places=5)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#decimalfield)
    - [BooleanField(default=False)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#booleanfield)
    - [CharField(max_length=10)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#charfield)
    - [EmailField(max_length=10)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#emailfield)
    - [DateField(auto_now_add=True), DateField(auto_now=True)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#datefield)
    - [DateTimeField(auto_now_add=True), DateTimeField(auto_now=True)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#datetimefield)
    - [FileField(upload_to=$func_return_file_save_path)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#filefield)
    - [ImageField(upload_to=$func_return_file_save_path, height_field=10, width_field=10)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#imagefield)
    - [GenericIPAddressField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#genericipaddressfield)
    - [TextField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#textfield)
    - [URLField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#urlfield)
    - [UUIDField()](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#uuidfield)
- [关系字段类型](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#module-django.db.models.fields.related)
    - 一对多
        - [ForeignKey('$app.$model', on_delete=models.CASCADE, db_index=True)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#foreignkey)
        - ForeignKey('$app.$model', on_delete=models.RESTRICT, db_index=True)
        - ForeignKey('$app.$model', on_delete=models.SET_NULL, blank=True,
          null=True, db_index=True)
        - [What does on_delete do on Django models?](https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models)
    - 多对多
        - [ManyToManyField('$app.$model')](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#manytomanyfield)
        - 自定义包含额外字段的多对多中间表：ManyToManyField('$app.$model',
          through='$Model1Model2')
        - [The right way to use a ManyToManyField in Django](https://www.sankalpjonna.com/learn-django/the-right-way-to-use-a-manytomanyfield-in-django)
    - 一对一
        - [OneToOneField(...)](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#onetoonefield)
- [字段约束](https://docs.djangoproject.com/zh-hans/3.2/ref/models/fields/#field-options)
    - 字段约束的一些默认值：null=False, blank=False, unique=False
- [抽象基类](https://docs.djangoproject.com/zh-hans/3.2/topics/db/models/#abstract-base-classes)

### migration

使用步骤：

1. 更改 model
2. 创建迁移：python manage.py makemigrations
3. 应用到数据库：python manage.py migrate

使用 migrations 查看对应的实际 SQL：

- python manage.py sqlmigrate $app_name $migration_name

### CRUD

- 增：
    - $model.objects.create(**kw)
    - [创建对象](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#creating-objects)
    - [保存 ForeignKey 和 ManyToManyField 字段](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#saving-foreignkey-and-manytomanyfield-fields)
- 删：
    - $instance.delete(**kw)
    - [删除对象](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#deleting-objects)
- 查：
    - 基本用法：
        - [检索对象](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#retrieving-objects)
        - [$model.objects.all()](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#retrieving-all-objects)
        - [$model.objects.filter(**kw)](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#retrieving-specific-objects-with-filters)
        - [$model.objects.get(**kw)](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#retrieving-a-single-object-with-get)
        - [限制 QuerySet 条目数](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#limiting-querysets)
        - [字段查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#field-lookups)
        - [跨关系查询/join](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#lookups-that-span-relationships)
        - [过滤器条件的值可以指定为模型的字段](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#filters-can-reference-fields-on-the-model)
        - [主键 (pk) 查询快捷方式](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#the-pk-lookup-shortcut)
        - Q
            - [通过 Q 对象完成复杂查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#complex-lookups-with-q-objects)
            - [Django: 使用 Q 对象构建复杂的查询语句](https://mozillazg.com/2015/11/django-the-power-of-q-objects-and-how-to-use-q-object.html#hidor)
        - 关联对象查询
            - [一对多关联查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#related-objects)
            - [多对多关联查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#many-to-many-relationships)
            - [一对一关联查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#one-to-one-relationships)
        - [执行原生 SQL 查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/sql/#performing-raw-sql-queries)
    - 其他参考：
        - [每个 QuerySet 都是唯一的](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#filtered-querysets-are-unique)
        - [QuerySet 是惰性的](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#querysets-are-lazy)
        - [缓存和 QuerySet](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#caching-and-querysets)
        - [执行查询](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#making-queries)
        - [QuerySet API 参考](https://docs.djangoproject.com/zh-hans/3.2/ref/models/querysets/#queryset-api-reference)
        - [模型关联 API 用法示例](https://docs.djangoproject.com/zh-hans/3.2/topics/db/examples/#examples-of-model-relationship-api-usage)
- 改：
    - $instance.attr = value
    - [将修改保存至对象](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#saving-changes-to-objects)
    - [一次修改多个对象](https://docs.djangoproject.com/zh-hans/3.2/topics/db/queries/#updating-multiple-objects-at-once)

### 事务

- [显式控制事务](https://docs.djangoproject.com/zh-hans/3.2/topics/db/transactions/#controlling-transactions-explicitly)
- Django 中的查询相关事务采用自动提交方式
- [事务提交成功对应的 hook](https://docs.djangoproject.com/zh-hans/3.2/topics/db/transactions/#django.db.transaction.on_commit)
- [savepoint 和 hook](https://docs.djangoproject.com/zh-hans/3.2/topics/db/transactions/#savepoints)

### 数据库访问优化

- [数据库访问优化](https://docs.djangoproject.com/zh-hans/3.2/topics/db/optimization/#database-access-optimization)

### 问题

- [Django model “doesn't declare an explicit app_label”](https://stackoverflow.com/questions/40206569/django-model-doesnt-declare-an-explicit-app-label)
- [How to revert the last migration?](https://stackoverflow.com/questions/32123477/how-to-revert-the-last-migration)
- [【Django Models】虚拟化提取Models公共的功能](https://www.cnblogs.com/inns/p/5562162.html)
- [Django South - table already exists](https://stackoverflow.com/questions/3090648/django-south-table-already-exists)
- [多对多中间表中, 解决 Django 自动创建索引造成的冗余索引问题](https://stackoverflow.com/questions/31095950/does-django-manytomanyfield-create-table-with-a-redundant-index)
- [多 model 管理](https://docs.djangoproject.com/zh-hans/3.2/topics/db/models/#organizing-models-in-a-package)

---
