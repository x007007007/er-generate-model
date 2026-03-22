# 需求文档

## 简介

命名空间驱动的模型导入导出系统是一个增强型的模型转换工具，它使用 Python 模块命名空间来管理模型引用和继承关系，而不是依赖文件路径。该系统支持项目内模型和第三方库模型的隔离管理，并在导出（er_export）和转换（er_convert）阶段自动处理命名空间解析和 import 路径生成。

## 术语表

- **System**: 命名空间驱动的模型导入导出系统
- **Namespace**: Python 模块命名空间，例如 `kinkotech.common.infrastructure.models.base`
- **TOML_File**: 包含模型定义的 TOML 格式文件
- **Entity**: 具体的数据模型定义
- **Template**: 抽象模型或 Mixin 类定义
- **Extends_Reference**: 模型继承关系中使用的命名空间引用
- **Project_Model**: 位于 `src/` 目录下的项目内模型
- **Third_Party_Model**: 位于 `src/third/` 目录下的第三方库模型
- **Export_Stage**: 从 Django 模型导出到 TOML 文件的阶段（er_export）
- **Convert_Stage**: 从 TOML 文件转换到 SQLAlchemy 模型的阶段（er_convert）
- **Namespace_Resolver**: 根据命名空间搜索对应 TOML 文件的组件
- **Import_Path_Generator**: 根据模型位置生成正确 import 语句的组件

## 需求

### 需求 1: 命名空间驱动的引用系统

**用户故事:** 作为开发者，我希望使用 Python 命名空间来引用模型继承关系，这样可以避免文件路径的硬编码，提高代码的可维护性。

#### 验收标准

1. THE System SHALL 使用 Python 模块命名空间表示所有模型的 extends 引用
2. WHEN 模型定义包含继承关系时，THE System SHALL 在 TOML 文件中使用 `extends = ["namespace.path.to.Model"]` 格式
3. THE System SHALL NOT 在 extends 引用中使用文件路径或相对路径
4. WHEN 解析 extends 引用时，THE System SHALL 将命名空间转换为对应的 TOML 文件路径

### 需求 2: TOML 文件组织结构

**用户故事:** 作为开发者，我希望按照命名空间组织 TOML 文件，这样可以清晰地管理不同模块的模型定义。

#### 验收标准

1. THE System SHALL 为每个命名空间（文件夹）创建一个 TOML_File
2. THE TOML_File SHALL 支持包含 Entity 定义
3. THE TOML_File SHALL 支持包含 Template 定义
4. THE TOML_File SHALL 支持包含关系定义（relationships）
5. WHEN 同一命名空间包含多个模型时，THE System SHALL 将它们放在同一个 TOML_File 中

### 需求 3: 第三方库隔离机制

**用户故事:** 作为开发者，我希望将第三方库的模型与项目内模型分开存储，这样可以清晰地区分依赖关系。

#### 验收标准

1. THE System SHALL 将 Project_Model 存储在 `src/` 目录下
2. THE System SHALL 将 Third_Party_Model 存储在 `src/third/` 目录下
3. THE System SHALL 支持通过配置文件自定义第三方目录名称
4. WHEN 配置文件未指定第三方目录名称时，THE System SHALL 使用 `third` 作为默认值
5. THE System SHALL 按照命名空间结构在 `src/` 和 `src/third/` 目录下组织 TOML_File

### 需求 4: Export 阶段的继承关系保留

**用户故事:** 作为开发者，我希望在导出 Django 模型时保留完整的继承关系信息，包括抽象类的字段定义。

#### 验收标准

1. WHEN 执行 Export_Stage 时，THE System SHALL 保留模型的继承关系
2. THE System SHALL 在 extends 字段中使用命名空间表示继承关系
3. THE System SHALL NOT 在 extends 字段中使用文件路径
4. WHEN 模型继承自抽象类或 Mixin 时，THE System SHALL 导出抽象类的字段定义到 TOML_File
5. WHEN 模型来自第三方库时，THE System SHALL 自动识别并将其导出到 `src/third/` 目录
6. THE System SHALL 识别模型是否为第三方库，通过检查其源代码路径是否在项目 `src/` 目录外

### 需求 5: Convert 阶段的命名空间解析

**用户故事:** 作为开发者，我希望在转换阶段系统能自动解析命名空间引用，生成正确的 import 路径。

#### 验收标准

1. WHEN 执行 Convert_Stage 时，THE System SHALL 读取 TOML_File 中的 extends 引用
2. WHEN 遇到 Extends_Reference 时，THE Namespace_Resolver SHALL 解析命名空间
3. THE Namespace_Resolver SHALL 首先在 `src/` 目录下搜索对应的 TOML_File
4. IF 在 `src/` 目录下未找到 TOML_File，THEN THE Namespace_Resolver SHALL 在 `src/third/` 目录下搜索
5. WHEN 找到 TOML_File 时，THE System SHALL 记录其位置类型（project 或 third-party）
6. THE Import_Path_Generator SHALL 根据位置类型生成正确的 import 语句
7. WHEN 模型为 Project_Model 时，THE Import_Path_Generator SHALL 生成 `from namespace.path import Model` 格式的 import 语句
8. WHEN 模型为 Third_Party_Model 时，THE Import_Path_Generator SHALL 生成 `from third.namespace.path import Model` 格式的 import 语句

### 需求 6: 命名空间搜索机制

**用户故事:** 作为开发者，我希望系统能够智能地搜索命名空间对应的 TOML 文件，无论它是项目内模型还是第三方模型。

#### 验收标准

1. WHEN 给定一个 Namespace 时，THE Namespace_Resolver SHALL 将其转换为文件路径
2. THE Namespace_Resolver SHALL 将命名空间中的点号（.）转换为路径分隔符（/）
3. THE Namespace_Resolver SHALL 在转换后的路径末尾添加 `.toml` 扩展名
4. THE Namespace_Resolver SHALL 按照优先级顺序搜索：先 `src/` 后 `src/third/`
5. WHEN 在任一搜索路径中找到 TOML_File 时，THE Namespace_Resolver SHALL 返回文件的完整路径和位置类型
6. IF 在所有搜索路径中都未找到 TOML_File，THEN THE Namespace_Resolver SHALL 返回错误信息，指明未找到的命名空间

### 需求 7: 配置支持

**用户故事:** 作为开发者，我希望能够配置系统的行为，例如第三方目录名称和搜索路径。

#### 验收标准

1. THE System SHALL 支持通过配置文件指定第三方目录名称
2. THE System SHALL 支持通过配置文件指定搜索路径列表
3. WHEN 配置文件不存在时，THE System SHALL 使用默认配置：第三方目录为 `third`，搜索路径为 `["src/", "src/third/"]`
4. THE System SHALL 在启动时加载配置文件
5. THE System SHALL 验证配置文件中的路径是否存在
6. IF 配置的路径不存在，THEN THE System SHALL 记录警告信息但继续运行

### 需求 8: 端到端工作流集成

**用户故事:** 作为开发者，我希望能够无缝地执行从 Django 模型导出到 SQLAlchemy 模型转换的完整流程。

#### 验收标准

1. WHEN 执行完整的 Export_Stage 和 Convert_Stage 流程时，THE System SHALL 生成可直接运行的 SQLAlchemy 模型代码
2. THE System SHALL 确保生成的 import 语句与文件系统结构一致
3. THE System SHALL 确保所有 Extends_Reference 都能正确解析
4. WHEN 模型引用不存在的命名空间时，THE System SHALL 在 Convert_Stage 报告错误
5. THE System SHALL 在生成的代码中保留原始的继承层次结构

### 需求 9: 错误处理和诊断

**用户故事:** 作为开发者，我希望在出现问题时能够获得清晰的错误信息，帮助我快速定位和解决问题。

#### 验收标准

1. WHEN Namespace_Resolver 无法找到命名空间对应的 TOML_File 时，THE System SHALL 报告详细的错误信息，包括搜索的命名空间和已搜索的路径
2. WHEN TOML_File 格式不正确时，THE System SHALL 报告文件路径和具体的格式错误
3. WHEN extends 引用包含文件路径而非命名空间时，THE System SHALL 报告警告信息
4. WHEN 循环继承被检测到时，THE System SHALL 报告错误并列出循环路径
5. THE System SHALL 在详细模式下输出命名空间解析的完整过程

### 需求 10: 向后兼容性

**用户故事:** 作为开发者，我希望新系统能够与现有的 TOML 文件格式兼容，避免大规模的迁移工作。

#### 验收标准

1. THE System SHALL 支持读取现有的 TOML_File 格式
2. WHEN TOML_File 中的 extends 使用旧的文件路径格式时，THE System SHALL 发出弃用警告
3. THE System SHALL 提供迁移工具，将旧格式的 extends 引用转换为命名空间格式
4. THE System SHALL 在迁移过程中保留所有模型定义和关系定义
5. THE System SHALL 生成迁移报告，列出所有转换的引用
