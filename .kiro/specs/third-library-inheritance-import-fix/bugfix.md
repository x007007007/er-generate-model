# Bugfix Requirements Document

## Introduction

当使用 `er_convert` 命令生成 SQLAlchemy 模型时，如果模型继承自第三方库（third目录）中的抽象基类，存在两个关键问题：

1. 生成的导入语句缺少了 `third.` 前缀
2. 系统没有在 `third/` 目录中生成对应的 `*_sqlalchemy.py` 文件

这导致生成的代码无法正确导入第三方库的基类，造成运行时导入错误。

例如，对于 `oauth2_provider.models.AbstractAccessToken` 这样的第三方基类：

**当前错误行为：**
- 导入语句：`from oauth2_provider.models_sqlalchemy import AbstractAccessToken`
- 没有生成 `third/oauth2_provider/models_sqlalchemy.py` 文件

**期望正确行为：**
- 导入语句：`from third.oauth2_provider.models_sqlalchemy import AbstractAccessToken`
- 生成 `third/oauth2_provider/models_sqlalchemy.py` 文件，包含 `AbstractAccessToken` 类

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN 实体的 `extends` 字段包含第三方库的抽象基类（如 `oauth2_provider.models.AbstractAccessToken`）且使用 `inheritance_mode='reference'` 和 `target_framework='sqlalchemy'` 时 THEN 生成的导入语句缺少 `third.` 前缀（例如：`from oauth2_provider.models_sqlalchemy import AbstractAccessToken`）

1.2 WHEN 第三方库的命名空间有3个或更多部分（如 `oauth2_provider.models.AbstractAccessToken`）时 THEN 系统无法识别这是第三方库，不添加 `third.` 前缀

1.3 WHEN 实体继承自第三方库的抽象基类时 THEN 系统不会在 `third/` 目录中生成对应的 `*_sqlalchemy.py` 文件（例如：不生成 `third/oauth2_provider/models_sqlalchemy.py`）

1.4 WHEN 生成的导入语句缺少 `third.` 前缀且没有生成对应的文件时 THEN 运行时会发生 `ModuleNotFoundError`，因为实际的第三方模块应该位于 `third/` 目录下

### Expected Behavior (Correct)

2.1 WHEN 实体的 `extends` 字段包含第三方库的抽象基类（如 `oauth2_provider.models.AbstractAccessToken`）且使用 `inheritance_mode='reference'` 和 `target_framework='sqlalchemy'` 时 THEN 生成的导入语句应该包含 `third.` 前缀（例如：`from third.oauth2_provider.models_sqlalchemy import AbstractAccessToken`）

2.2 WHEN 第三方库的命名空间有3个或更多部分（如 `oauth2_provider.models.AbstractAccessToken`）时 THEN 系统应该识别这是第三方库，并自动添加 `third.` 前缀

2.3 WHEN 实体继承自第三方库的抽象基类时 THEN 系统应该在 `third/` 目录中生成对应的 `*_sqlalchemy.py` 文件（例如：生成 `third/oauth2_provider/models_sqlalchemy.py`，包含 `AbstractAccessToken` 类定义）

2.4 WHEN 生成第三方库的 SQLAlchemy 模型文件时 THEN 文件应该包含必要的导入和类定义，使其可以被其他模型正确继承

2.5 WHEN 生成的导入语句包含正确的 `third.` 前缀且对应文件已生成时 THEN 运行时能够成功导入第三方模块，不会发生 `ModuleNotFoundError`

### Unchanged Behavior (Regression Prevention)

3.1 WHEN 实体继承自项目内部的模板或mixin（如 `mixins.TimestampMixin`）时 THEN 系统应该继续生成不带 `third.` 前缀的导入语句

3.2 WHEN 实体继承自项目内部的基类（命名空间少于3个部分）时 THEN 系统应该继续生成不带 `third.` 前缀的导入语句

3.3 WHEN 使用 `inheritance_mode='flatten'` 时 THEN 系统应该继续按照flatten模式处理继承，不生成外部类导入

3.4 WHEN 命名空间转换为SQLAlchemy格式时（添加 `_sqlalchemy` 后缀）THEN 转换逻辑应该继续正常工作，无论是否有 `third.` 前缀

3.5 WHEN 生成内部mixin文件到 `mixins/` 目录时 THEN 系统应该继续正常生成，不受此修复影响

3.6 WHEN 生成第三方mixin文件到 `third/` 目录时 THEN 系统应该继续正常生成，不受此修复影响
