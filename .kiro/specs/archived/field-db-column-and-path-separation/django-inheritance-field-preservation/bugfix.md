# Bugfix Requirements Document

## Introduction

当 Django ORM models 通过 TOML 中间格式转换为 SQLAlchemy models 时，如果 Django model 存在继承关系（通过 `extends` 字段在 TOML 中表示），转换后的 SQLAlchemy model 会丢失从父类继承的字段。这导致生成的 SQLAlchemy model 不完整，缺少关键的字段定义（如时间戳字段 `created_at`、`modified_at` 等）。

转换流程：Django models → TOML 格式 → SQLAlchemy models

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN TOML 文件中的 entity 包含 `extends` 字段（表示继承关系）THEN 转换为 SQLAlchemy model 时丢失父类定义的字段

1.2 WHEN Django model 继承自包含字段的 mixin 类（如 `CreateModifyMixinModel`）THEN 生成的 SQLAlchemy model 中不包含这些 mixin 字段

1.3 WHEN 生成的 SQLAlchemy model 缺少继承字段 THEN 数据库操作可能失败或产生运行时错误

### Expected Behavior (Correct)

2.1 WHEN TOML 文件中的 entity 包含 `extends` 字段 THEN 转换为 SQLAlchemy model 时 SHALL 包含所有父类和 mixin 类定义的字段

2.2 WHEN Django model 继承自包含字段的 mixin 类 THEN 生成的 SQLAlchemy model SHALL 包含所有 mixin 字段的完整定义（包括字段类型、约束等）

2.3 WHEN 处理继承关系时 THEN 系统 SHALL 正确解析 `extends` 数组中的所有父类，并合并它们的字段定义

### Unchanged Behavior (Regression Prevention)

3.1 WHEN TOML 文件中的 entity 不包含 `extends` 字段（无继承关系）THEN 系统 SHALL CONTINUE TO 正确生成 SQLAlchemy model，包含所有直接定义的字段

3.2 WHEN 转换包含关系（relationships）的 entity THEN 系统 SHALL CONTINUE TO 正确生成外键和关系定义

3.3 WHEN 转换包含各种字段类型（string, text, bigint 等）的 entity THEN 系统 SHALL CONTINUE TO 正确映射字段类型到 SQLAlchemy 类型

3.4 WHEN 转换包含字段属性（nullable, unique, primary_key 等）的 entity THEN 系统 SHALL CONTINUE TO 正确应用这些属性到 SQLAlchemy 字段定义

3.5 WHEN 生成 Django 风格的关系命名 THEN 系统 SHALL CONTINUE TO 使用逻辑名称（如 `code`）而不是实体名称（如 `i18ncode_rel`）
