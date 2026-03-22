# 需求文档

## 简介

本规范解决 Django 模型代码生成中的命名问题：
1. 包模式下生成的文件名中存在冗余的实体名（例如 `model_model.py`）
2. ManyToMany 字段名使用完整的 snake_case 实体名（例如 `rolemodel_set`），应该去掉 `Model` 后缀
3. `related_name` 属性应该包含实体名前缀以提高可读性

## 术语表

- **Django_Renderer**: 生成 Django 模型文件的代码生成组件
- **Entity**: ER 图中的数据模型类（例如 User、Post、RoleModel）
- **Package_Mode**: 每个实体生成三个独立文件（model、manager、queryset）的输出格式
- **Related_Name**: Django 的 ForeignKey 和 ManyToMany 字段的反向关系访问器名称
- **Snake_Case**: 小写加下划线的命名方式（例如 `user_profile`）

## 需求

### 需求 1: 简化包模式文件名

**用户故事：** 作为开发者，我希望生成的 Django 包文件使用简单的实体名，不带冗余后缀，这样当实体名已经包含常见术语时，文件名更清晰，避免重复。

#### 验收标准

1. 当在包模式下生成文件时，Django_Renderer 应将模型文件命名为 `{entity_name}.py` 而不是 `{entity_name}_model.py`
2. 当在包模式下生成文件时，Django_Renderer 应将管理器文件命名为 `{entity_name}_manager.py`
3. 当在包模式下生成文件时，Django_Renderer 应将查询集文件命名为 `{entity_name}_queryset.py`
4. 当实体名为 "Model" 时，Django_Renderer 应生成名为 `model.py`、`model_manager.py` 和 `model_queryset.py` 的文件
5. 当生成 `__init__.py` 文件时，Django_Renderer 应从正确的简化文件名导入

### 需求 2: 优化 ManyToMany 字段命名

**用户故事：** 作为开发者，我希望 ManyToMany 字段名更简洁，去掉 `Model` 后缀，同时 `related_name` 包含实体名前缀以便于理解反向关系。

#### 验收标准

1. 当生成 ManyToMany 字段时，如果目标实体名以 `Model` 结尾，字段名应去掉 `Model` 后缀
   - 例如：`RoleModel` → 字段名为 `role_set`，而不是 `rolemodel_set`
2. 当生成 ForeignKey 字段时，Django_Renderer 应设置 `related_name` 为 `{entity_name}_set` 而不是 `_set`
3. 当生成 ManyToManyField 时，Django_Renderer 应设置 `related_name` 为 `{entity_name}_set` 而不是 `_set`
4. 当生成 OneToOneField 时，Django_Renderer 应设置 `related_name` 为 `{entity_name}_rel` 而不是 `_rel`
5. Django_Renderer 应在单文件模式和包模式模板中都应用这些命名规则

### 需求 3: 保持向后兼容性

**用户故事：** 作为开发者，我希望在命名更改后，现有的测试和功能继续正常工作，以确保重构是安全和可预测的。

#### 验收标准

1. 当应用命名更改时，Django_Renderer 应继续生成有效的 Django 模型代码
2. 当运行现有测试时，系统应在更新预期的文件名和 related name 后通过所有测试
3. 当生成带关系的模型时，Django_Renderer 应在命名更改后保持正确的关系语义
