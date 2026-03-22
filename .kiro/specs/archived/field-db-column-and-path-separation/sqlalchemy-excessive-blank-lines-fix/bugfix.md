# Bugfix Requirements Document

## Introduction

SQLAlchemy 模型生成器在渲染模型文件时产生过多的空行，导致生成的代码格式不符合 PEP 8 标准。这个问题影响代码的可读性和专业性，需要修复模板文件中的空行控制逻辑。

问题根源在于 Jinja2 模板文件 `sqlalchemy_single_model.j2` 中的空行控制不当，特别是在条件语句和循环之间缺少适当的空白符控制标记。

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN 模板渲染 import 语句块时 THEN 在 `from sqlalchemy.orm import relationship` 和后续的 base model import 之间产生 7 个空行

1.2 WHEN 模板渲染外部类或 mixin 导入后 THEN 在导入语句和类定义之间产生 6 个空行

1.3 WHEN 模板渲染类定义中的字段时 THEN 在每个字段定义之间产生 3 个空行

1.4 WHEN 模板渲染 relationship 定义时 THEN 在每个 relationship 之间产生 3 个空行

1.5 WHEN 模板渲染字段和 relationship 之间的过渡时 THEN 产生 2 个空行

### Expected Behavior (Correct)

2.1 WHEN 模板渲染 import 语句块时 THEN 在 `from sqlalchemy.orm import relationship` 和后续的 base model import 之间应该只有 1 个空行

2.2 WHEN 模板渲染外部类或 mixin 导入后 THEN 在最后一个导入语句和类定义之间应该只有 2 个空行（符合 PEP 8）

2.3 WHEN 模板渲染类定义中的字段时 THEN 字段定义之间应该没有空行

2.4 WHEN 模板渲染 relationship 定义时 THEN relationship 定义之间应该没有空行

2.5 WHEN 模板渲染字段和 relationship 之间的过渡时 THEN 应该只有 1 个空行

### Unchanged Behavior (Regression Prevention)

3.1 WHEN 模板渲染类定义的 `__tablename__` 属性时 THEN 应该继续在类声明后的下一行渲染，没有空行

3.2 WHEN 模板渲染第一个字段定义时 THEN 应该继续在 `__tablename__` 后有 1 个空行

3.3 WHEN 模板处理继承模式（flatten/reference）时 THEN 应该继续正确处理字段的包含和排除逻辑

3.4 WHEN 模板渲染外键约束和类型时 THEN 应该继续生成正确的 ForeignKey 和 Column 定义

3.5 WHEN 模板渲染 relationship 的 back_populates 和 foreign_keys 参数时 THEN 应该继续生成正确的参数值

3.6 WHEN 模板处理 Django 风格的命名（使用逻辑名称而非 db_column）时 THEN 应该继续使用正确的命名策略

3.7 WHEN 模板渲染不同关系类型（one-to-one, one-to-many, many-to-many）时 THEN 应该继续生成正确的 relationship 配置
