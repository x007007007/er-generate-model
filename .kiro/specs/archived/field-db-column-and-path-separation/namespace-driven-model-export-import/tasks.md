# 实现计划：命名空间驱动的模型导入导出系统

## 概述

本实现计划将命名空间驱动的模型导入导出系统分解为可执行的编码任务。系统使用 Python 模块命名空间管理模型引用，支持项目内模型和第三方模型的隔离管理，并在 Export 和 Convert 阶段自动处理命名空间解析和 import 路径生成。

实现语言：Python
核心组件：5 个（NamespaceResolver, ImportPathGenerator, ModelClassifier, TOMLWriter, ConfigurationManager）
集成点：TomlERParser, MixinGenerator, TemplateRegistry, SQLAlchemy Renderer

## 任务列表

- [x] 1. 创建核心数据模型和异常类
  - 创建 `packages/er-gen-core/src/x007007007/er/namespace_models.py` 文件
  - 实现 ResolveResult, ImportSpec, EntityDefinition, ColumnDefinition, TemplateDefinition 数据类
  - 实现 NamespaceNotFoundError, CircularInheritanceError 异常类
  - 使用 Python dataclass 和类型注解
  - _需求: 1.1, 1.2, 6.6, 9.1, 9.4_

- [ ]* 1.1 为核心数据模型编写单元测试
  - 测试数据类的实例化和字段访问
  - 测试异常类的错误信息格式
  - _需求: 9.1, 9.4_

- [ ] 2. 实现 NamespaceResolver（命名空间解析器）
  - [x] 2.1 创建 NamespaceResolver 基础类
    - 创建 `packages/er-gen-core/src/x007007007/er/namespace_resolver.py` 文件
    - 实现 `__init__` 方法，接收 search_paths 和可选的 config 参数
    - 实现命名空间验证逻辑，防止路径遍历攻击
    - _需求: 1.4, 6.1, 6.2, 6.3_

  - [x] 2.2 实现命名空间到路径的转换逻辑
    - 实现 `_namespace_to_path` 方法，将点号转换为路径分隔符
    - 在路径末尾添加 `.toml` 扩展名
    - 处理边界情况（空命名空间、特殊字符等）
    - _需求: 6.1, 6.2, 6.3_


  - [x] 2.3 实现命名空间解析核心逻辑
    - 实现 `resolve` 方法，按优先级搜索 TOML 文件
    - 先搜索 `src/`，后搜索 `src/third/`
    - 返回 ResolveResult 对象，包含文件路径和位置类型
    - 如果未找到，抛出 NamespaceNotFoundError
    - _需求: 5.2, 5.3, 5.4, 6.4, 6.5_

  - [x] 2.4 实现批量解析和缓存机制
    - 实现 `resolve_batch` 方法，批量解析多个命名空间
    - 添加内部缓存字典，避免重复文件系统访问
    - 实现缓存失效机制
    - _需求: 5.2, 6.4_

  - [ ]* 2.5 为 NamespaceResolver 编写单元测试
    - 测试命名空间到路径的转换
    - 测试搜索路径优先级
    - 测试文件存在和不存在的情况
    - 测试缓存机制
    - 测试路径遍历防护
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.6, 9.1_

  - [ ]* 2.6 为 NamespaceResolver 编写属性测试
    - **属性 2: 命名空间到路径的转换**
    - **验证需求: 1.4, 6.1, 6.2, 6.3**
    - 使用 hypothesis 生成随机命名空间
    - 验证转换后的路径格式正确性

  - [ ]* 2.7 为 NamespaceResolver 编写属性测试
    - **属性 12: 搜索路径优先级**
    - **验证需求: 5.3, 5.4, 6.4**
    - 验证按配置顺序搜索并在第一个找到的路径停止

- [ ] 3. 实现 ImportPathGenerator（导入路径生成器）
  - [x] 3.1 创建 ImportPathGenerator 类
    - 创建 `packages/er-gen-core/src/x007007007/er/import_path_generator.py` 文件
    - 实现 `__init__` 方法，接收 third_party_dir 参数（默认 "third"）
    - _需求: 3.3, 3.4, 5.6_

  - [x] 3.2 实现 import 语句生成逻辑
    - 实现 `generate` 方法，接收 namespace, location_type, model_name
    - 对于 project 类型，生成 `from {namespace} import {ModelName}`
    - 对于 third-party 类型，生成 `from {third_party_dir}.{namespace} import {ModelName}`
    - _需求: 5.6, 5.7, 5.8_


  - [x] 3.3 实现批量生成功能
    - 实现 `generate_batch` 方法，接收 ImportSpec 列表
    - 返回 import 语句列表
    - _需求: 5.6_

  - [ ]* 3.4 为 ImportPathGenerator 编写单元测试
    - 测试项目模型的 import 生成
    - 测试第三方模型的 import 生成
    - 测试自定义第三方目录名称
    - 测试批量生成功能
    - _需求: 3.3, 3.4, 5.6, 5.7, 5.8_

  - [ ]* 3.5 为 ImportPathGenerator 编写属性测试
    - **属性 14: 项目模型导入格式**
    - **验证需求: 5.6, 5.7**
    - 验证项目模型 import 语句不包含目录前缀

  - [ ]* 3.6 为 ImportPathGenerator 编写属性测试
    - **属性 15: 第三方模型导入格式**
    - **验证需求: 5.6, 5.8**
    - 验证第三方模型 import 语句包含正确的目录前缀

  - [ ]* 3.7 为 ImportPathGenerator 编写属性测试
    - **属性 6: 配置驱动的目录命名**
    - **验证需求: 3.3, 7.1**
    - 验证使用配置的第三方目录名称而非硬编码

- [ ] 4. 实现 ModelClassifier（模型分类器）
  - [x] 4.1 创建 ModelClassifier 类
    - 创建 `packages/er-gen-core/src/x007007007/er/model_classifier.py` 文件
    - 实现 `__init__` 方法，接收 project_root 参数
    - _需求: 4.5, 4.6_

  - [x] 4.2 实现模型分类逻辑
    - 实现 `classify` 方法，接收 Django 模型类
    - 使用 `inspect.getfile()` 获取源文件路径
    - 判断路径是否在项目 `src/` 目录下
    - 返回 "project" 或 "third-party"
    - _需求: 4.5, 4.6_

  - [x] 4.3 实现命名空间提取逻辑
    - 实现 `get_namespace` 方法，从模型类的 `__module__` 属性提取命名空间
    - 处理边界情况（内置模块、动态生成的类等）
    - _需求: 1.1, 4.2_


  - [ ]* 4.4 为 ModelClassifier 编写单元测试
    - 测试项目内模型的分类
    - 测试第三方模型的分类
    - 测试命名空间提取
    - 测试边界情况处理
    - _需求: 4.5, 4.6, 1.1_

  - [ ]* 4.5 为 ModelClassifier 编写属性测试
    - **属性 10: 模型分类正确性**
    - **验证需求: 4.5, 4.6**
    - 验证源代码路径在 src/ 外的模型被分类为第三方

- [ ] 5. 实现 TOMLWriter（TOML 写入器）
  - [x] 5.1 创建 TOMLWriter 类
    - 创建 `packages/er-gen-core/src/x007007007/er/toml_writer.py` 文件
    - 实现 `__init__` 方法，接收 base_dir 参数
    - _需求: 2.1, 3.1, 3.2_

  - [x] 5.2 实现文件路径生成逻辑
    - 实现 `_get_file_path` 方法，根据命名空间生成文件路径
    - 创建必要的目录结构
    - 使用原子性写入（临时文件 + 重命名）
    - _需求: 2.1, 3.5_

  - [x] 5.3 实现实体写入逻辑
    - 实现 `write_entity` 方法，接收 namespace 和 EntityDefinition
    - 将实体序列化为 TOML 格式
    - 处理同一命名空间的多个实体（追加到同一文件）
    - 使用命名空间格式表示 extends 引用
    - _需求: 1.2, 2.2, 2.5, 4.1_

  - [x] 5.4 实现模板写入逻辑
    - 实现 `write_template` 方法，接收 namespace 和 TemplateDefinition
    - 将模板序列化为 TOML 格式
    - 导出抽象类的字段定义
    - _需求: 2.3, 4.4_

  - [ ]* 5.5 为 TOMLWriter 编写单元测试
    - 测试文件路径生成
    - 测试实体写入
    - 测试模板写入
    - 测试同一命名空间多个模型的处理
    - 测试原子性写入
    - _需求: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2_

  - [ ]* 5.6 为 TOMLWriter 编写属性测试
    - **属性 3: 命名空间唯一性**
    - **验证需求: 2.1, 2.5**
    - 验证同一命名空间只创建一个 TOML 文件


  - [ ]* 5.7 为 TOMLWriter 编写属性测试
    - **属性 4: 项目模型位置**
    - **验证需求: 3.1**
    - 验证项目模型的 TOML 文件路径以 src/ 开头

  - [ ]* 5.8 为 TOMLWriter 编写属性测试
    - **属性 5: 第三方模型位置**
    - **验证需求: 3.2, 3.5**
    - 验证第三方模型的 TOML 文件路径以 src/third/ 开头

- [ ] 6. 实现 ConfigurationManager（配置管理器）
  - [~] 6.1 创建 ConfigurationManager 类
    - 创建 `packages/er-gen-core/src/x007007007/er/configuration_manager.py` 文件
    - 实现 `__init__` 方法，接收可选的 config_path 参数
    - 定义默认配置：third_party_dir="third", search_paths=["src/", "src/third/"]
    - _需求: 7.1, 7.2, 7.3_

  - [~] 6.2 实现配置加载逻辑
    - 实现 `_load_config` 方法，从 TOML 文件加载配置
    - 处理配置文件不存在的情况，使用默认配置
    - 合并用户配置和默认配置
    - _需求: 7.3, 7.4_

  - [~] 6.3 实现配置验证逻辑
    - 实现 `validate` 方法，验证配置的路径是否存在
    - 如果路径不存在，记录警告但继续运行
    - 返回警告信息列表
    - _需求: 7.5, 7.6_

  - [~] 6.4 实现配置访问接口
    - 实现 `get_search_paths` 方法
    - 实现 `get_third_party_dir` 方法
    - 实现其他配置访问方法
    - _需求: 7.1, 7.2_

  - [ ]* 6.5 为 ConfigurationManager 编写单元测试
    - 测试默认配置
    - 测试配置文件加载
    - 测试配置验证
    - 测试配置访问接口
    - _需求: 7.1, 7.2, 7.3, 7.5, 7.6_

  - [ ]* 6.6 为 ConfigurationManager 编写属性测试
    - **属性 16: 配置路径验证**
    - **验证需求: 7.2, 7.5**
    - 验证不存在的路径记录警告但继续运行


- [ ] 7. 实现循环继承检测算法
  - [~] 7.1 创建循环检测模块
    - 创建 `packages/er-gen-core/src/x007007007/er/inheritance_checker.py` 文件
    - 实现 `detect_circular_inheritance` 函数，使用深度优先搜索
    - 接收实体字典，返回循环路径或 None
    - _需求: 9.4_

  - [ ]* 7.2 为循环检测编写单元测试
    - 测试无循环的情况
    - 测试简单循环（A -> B -> A）
    - 测试复杂循环（A -> B -> C -> A）
    - 测试多个独立继承链
    - _需求: 9.4_

  - [ ]* 7.3 为循环检测编写属性测试
    - **属性 20: 循环继承检测**
    - **验证需求: 9.4**
    - 验证存在循环时能检测到并报告循环路径

- [ ] 8. 集成 NamespaceResolver 到 TomlERParser
  - [~] 8.1 修改 TomlERParser 构造函数
    - 在 `packages/er-gen-core/src/x007007007/er/parser/toml_parser.py` 中修改 `__init__` 方法
    - 添加 namespace_resolver 可选参数
    - 如果未提供，创建默认的 NamespaceResolver 实例
    - _需求: 5.1, 5.2_

  - [~] 8.2 修改 extends 引用解析逻辑
    - 在 `_parse_entities` 方法中，解析 extends 引用时调用 namespace_resolver.resolve()
    - 记录解析结果（文件路径和位置类型）
    - 处理 NamespaceNotFoundError，提供详细错误信息
    - _需求: 5.1, 5.2, 5.5, 6.6_

  - [~] 8.3 添加向后兼容性支持
    - 检测 extends 引用是否为旧的文件路径格式
    - 如果是文件路径格式，发出弃用警告
    - 仍然支持解析旧格式，但建议迁移
    - _需求: 10.1, 10.2, 9.3_

  - [ ]* 8.4 为 TomlERParser 集成编写单元测试
    - 测试使用命名空间格式的 extends 解析
    - 测试 NamespaceNotFoundError 处理
    - 测试向后兼容性（旧格式警告）
    - _需求: 5.1, 5.2, 9.3, 10.1, 10.2_


- [ ] 9. 集成 ImportPathGenerator 到 MixinGenerator
  - [~] 9.1 修改 MixinGenerator 构造函数
    - 在 `packages/er-gen-core/src/x007007007/er/mixin_generator.py` 中修改 `__init__` 方法
    - 添加 import_path_generator 可选参数
    - 如果未提供，创建默认的 ImportPathGenerator 实例
    - _需求: 5.6_

  - [~] 9.2 修改 import 语句生成逻辑
    - 在 `generate_mixin_file` 方法中，使用 import_path_generator.generate() 生成 import 语句
    - 根据模板的位置类型（从 NamespaceResolver 获取）生成正确的 import
    - 收集所有 import 语句并传递给模板
    - _需求: 5.6, 5.7, 5.8_

  - [ ]* 9.3 为 MixinGenerator 集成编写单元测试
    - 测试项目模型的 import 生成
    - 测试第三方模型的 import 生成
    - 测试混合项目和第三方模型的情况
    - _需求: 5.6, 5.7, 5.8_

- [ ] 10. 集成 NamespaceResolver 到 TemplateRegistry
  - [~] 10.1 修改 TemplateRegistry 构造函数
    - 在 `packages/er-gen-core/src/x007007007/er/template_registry.py` 中修改 `__init__` 方法
    - 添加 namespace_resolver 可选参数
    - _需求: 5.2_

  - [~] 10.2 实现延迟加载机制
    - 修改 `resolve_template` 方法，首先在已加载的模板中查找
    - 如果未找到，使用 namespace_resolver.resolve() 查找 TOML 文件
    - 加载并缓存模板
    - _需求: 5.2, 5.3, 5.4_

  - [ ]* 10.3 为 TemplateRegistry 集成编写单元测试
    - 测试延迟加载机制
    - 测试跨目录搜索（src/ 和 src/third/）
    - 测试缓存机制
    - _需求: 5.2, 5.3, 5.4_

- [ ] 11. 修改 SQLAlchemy Renderer 以支持命名空间 import
  - [~] 11.1 修改 render_entity 方法签名
    - 在 `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/` 中修改渲染器
    - 添加 imports 参数，接收 import 语句列表
    - _需求: 5.6, 8.2_

  - [~] 11.2 更新 Jinja2 模板
    - 修改 `sqlalchemy_model.j2` 和 `sqlalchemy_single_model.j2` 模板
    - 在文件开头添加 imports 循环，输出所有 import 语句
    - 确保 import 语句在其他导入之前
    - _需求: 5.6, 8.2_


  - [ ]* 11.3 为 SQLAlchemy Renderer 集成编写单元测试
    - 测试 import 语句的正确插入
    - 测试生成代码的语法正确性
    - _需求: 5.6, 8.1, 8.2_

- [ ] 12. 实现 Django 模型导出功能（Export 阶段）
  - [~] 12.1 创建 Django 模型提取器
    - 创建 `packages/er-django/src/x007007007/er_django/model_extractor.py` 文件
    - 实现 `extract_models` 函数，遍历 Django 应用的所有模型
    - 提取模型的字段、关系和元数据
    - 识别继承关系（从 `__bases__` 提取）
    - _需求: 4.1_

  - [~] 12.2 集成 ModelClassifier 到导出流程
    - 在模型提取过程中，使用 ModelClassifier 分类每个模型
    - 记录模型的命名空间（从 `__module__` 获取）
    - 区分项目模型和第三方模型
    - _需求: 4.5, 4.6_

  - [~] 12.3 使用 TOMLWriter 写入 TOML 文件
    - 根据分类结果，将项目模型写入 `src/`
    - 将第三方模型写入 `src/third/`
    - 使用命名空间格式表示 extends 引用
    - 导出抽象类的字段定义
    - _需求: 1.2, 3.1, 3.2, 4.2, 4.4_

  - [~] 12.4 修改 er_export 命令
    - 在 `packages/er-django/src/x007007007/er_django/management/commands/er_export.py` 中集成新功能
    - 添加命令行选项：--output-dir, --third-party-dir
    - 调用模型提取器和 TOMLWriter
    - 输出导出统计信息
    - _需求: 3.3, 4.1_

  - [ ]* 12.5 为 Django 导出功能编写单元测试
    - 测试模型提取
    - 测试模型分类
    - 测试 TOML 文件生成
    - 测试继承关系保留
    - _需求: 4.1, 4.2, 4.4, 4.5, 4.6_

  - [ ]* 12.6 为 Django 导出功能编写属性测试
    - **属性 1: 命名空间引用格式**
    - **验证需求: 1.1, 1.2, 1.3, 4.2, 4.3**
    - 验证 extends 字段使用命名空间格式

  - [ ]* 12.7 为 Django 导出功能编写属性测试
    - **属性 8: 继承关系保留**
    - **验证需求: 4.1, 8.5**
    - 验证导出和解析往返后继承关系保持不变


  - [ ]* 12.8 为 Django 导出功能编写属性测试
    - **属性 9: 抽象类字段展开**
    - **验证需求: 4.4**
    - 验证继承自抽象类的模型导出包含抽象类字段

- [ ] 13. 实现 TOML 到 SQLAlchemy 转换功能（Convert 阶段）
  - [~] 13.1 创建转换协调器
    - 创建 `packages/er-gen-core/src/x007007007/er/namespace_converter.py` 文件
    - 实现 `convert_with_namespace` 函数，协调整个转换流程
    - 初始化 NamespaceResolver, ImportPathGenerator
    - _需求: 5.1, 5.6_

  - [~] 13.2 实现命名空间解析和 import 生成
    - 解析所有 TOML 文件，提取 extends 引用
    - 对每个引用调用 NamespaceResolver.resolve()
    - 对每个解析结果调用 ImportPathGenerator.generate()
    - 收集所有 import 语句
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [~] 13.3 集成循环继承检测
    - 在转换前，调用 detect_circular_inheritance()
    - 如果检测到循环，抛出 CircularInheritanceError
    - 在错误信息中包含循环路径
    - _需求: 9.4_

  - [~] 13.4 调用 SQLAlchemy Renderer 生成代码
    - 将 import 语句传递给渲染器
    - 生成 SQLAlchemy 模型代码
    - 写入输出文件
    - _需求: 8.1, 8.2_

  - [~] 13.5 修改 er_convert 命令
    - 在 `packages/er-gen-tool/src/x007007007/er_tool/convert.py` 中集成新功能
    - 添加命令行选项：--input-dir, --output-dir, --config
    - 调用转换协调器
    - 输出转换统计信息和错误报告
    - _需求: 5.1, 8.1, 9.1, 9.2, 9.4_

  - [ ]* 13.6 为转换功能编写单元测试
    - 测试命名空间解析
    - 测试 import 生成
    - 测试循环检测
    - 测试错误处理
    - _需求: 5.1, 5.2, 5.6, 9.1, 9.4_

  - [ ]* 13.7 为转换功能编写属性测试
    - **属性 11: 命名空间解析调用**
    - **验证需求: 5.1, 5.2**
    - 验证所有 extends 引用都调用 NamespaceResolver


  - [ ]* 13.8 为转换功能编写属性测试
    - **属性 13: 位置类型记录**
    - **验证需求: 5.5, 6.5**
    - 验证解析结果包含正确的位置类型信息

  - [ ]* 13.9 为转换功能编写属性测试
    - **属性 19: 引用完整性**
    - **验证需求: 8.3**
    - 验证所有 extends 引用都能解析或报告错误

- [ ] 14. 实现 TOML 迁移工具
  - [~] 14.1 创建 TOMLMigrationTool 类
    - 创建 `packages/er-gen-tool/src/x007007007/er_tool/toml_migration.py` 文件
    - 实现 `__init__` 方法
    - 定义 MigrationReport 数据类
    - _需求: 10.3_

  - [~] 14.2 实现文件路径到命名空间的转换
    - 实现 `_convert_path_to_namespace` 方法
    - 移除相对路径前缀（../, ./）
    - 移除文件扩展名（.toml）
    - 将斜杠替换为点号
    - _需求: 10.3, 10.4_

  - [~] 14.3 实现 TOML 文件迁移逻辑
    - 实现 `migrate_file` 方法，读取旧格式 TOML 文件
    - 遍历所有 extends 引用，检测文件路径格式
    - 转换为命名空间格式
    - 写入新格式 TOML 文件
    - 生成迁移报告
    - _需求: 10.3, 10.4, 10.5_

  - [~] 14.4 实现批量迁移功能
    - 实现 `migrate_directory` 方法，递归处理目录中的所有 TOML 文件
    - 保持目录结构
    - 汇总迁移报告
    - _需求: 10.3_

  - [~] 14.5 创建 er_migrate 命令
    - 在 `packages/er-gen-tool/src/x007007007/er_tool/migrate.py` 中实现命令
    - 添加命令行选项：--input, --output, --dry-run
    - 调用 TOMLMigrationTool
    - 输出迁移报告
    - _需求: 10.3, 10.5_

  - [ ]* 14.6 为迁移工具编写单元测试
    - 测试路径到命名空间的转换
    - 测试单文件迁移
    - 测试批量迁移
    - 测试迁移报告生成
    - _需求: 10.3, 10.4, 10.5_


  - [ ]* 14.7 为迁移工具编写属性测试
    - **属性 22: 迁移工具转换正确性**
    - **验证需求: 10.3, 10.4**
    - 验证旧格式转换为命名空间格式后保留所有定义

- [ ] 15. 实现错误处理和日志系统
  - [~] 15.1 创建统一的日志配置
    - 创建 `packages/er-gen-core/src/x007007007/er/logging_config.py` 文件
    - 配置日志级别：ERROR, WARNING, INFO, DEBUG
    - 实现详细模式支持
    - _需求: 9.5_

  - [~] 15.2 在 NamespaceResolver 中添加详细日志
    - 记录命名空间解析过程
    - 记录搜索路径和结果
    - 在详细模式下输出完整过程
    - _需求: 9.5_

  - [~] 15.3 在 ModelClassifier 中添加详细日志
    - 记录模型分类过程
    - 记录源文件路径和分类结果
    - _需求: 9.5_

  - [~] 15.4 在 ImportPathGenerator 中添加详细日志
    - 记录 import 生成过程
    - 记录命名空间、位置类型和生成的 import 语句
    - _需求: 9.5_

  - [~] 15.5 改进错误信息格式
    - 确保 NamespaceNotFoundError 包含搜索的命名空间和路径
    - 确保 CircularInheritanceError 包含循环路径
    - 确保 TOML 格式错误包含文件路径和行号
    - _需求: 9.1, 9.2, 9.4_

  - [ ]* 15.6 为错误处理编写单元测试
    - 测试各种错误场景
    - 测试错误信息格式
    - 测试日志输出
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 16. 端到端集成测试
  - [ ]* 16.1 编写完整的 Export 到 Convert 端到端测试
    - 创建测试 Django 项目和模型
    - 执行 Export 阶段，验证 TOML 文件生成
    - 执行 Convert 阶段，验证 SQLAlchemy 代码生成
    - 验证生成的代码可以导入和执行
    - **验证需求: 8.1, 8.2, 8.3, 8.5**


  - [ ]* 16.2 编写第三方模型处理端到端测试
    - 创建继承自第三方库（如 Django AbstractUser）的测试模型
    - 验证第三方模型被导出到 src/third/
    - 验证生成的 import 语句包含 third 前缀
    - **验证需求: 3.2, 4.5, 5.8**

  - [ ]* 16.3 编写迁移工具端到端测试
    - 创建旧格式的 TOML 文件
    - 运行迁移工具
    - 验证新格式正确性
    - 验证迁移报告
    - **验证需求: 10.3, 10.4, 10.5**

  - [ ]* 16.4 编写属性测试：端到端代码可执行性
    - **属性 17: 端到端代码可执行性**
    - **验证需求: 8.1**
    - 验证生成的 SQLAlchemy 代码语法正确且可导入

  - [ ]* 16.5 编写属性测试：导入语句与文件系统一致性
    - **属性 18: 导入语句与文件系统一致性**
    - **验证需求: 8.2**
    - 验证生成的 import 语句对应实际存在的文件

  - [ ]* 16.6 编写属性测试：命名空间结构映射
    - **属性 7: 命名空间结构映射**
    - **验证需求: 3.5**
    - 验证命名空间的层次结构反映在文件系统中

  - [ ]* 16.7 编写属性测试：向后兼容性
    - **属性 21: 向后兼容性**
    - **验证需求: 10.1**
    - 验证系统能正确解析旧 TOML 格式

- [ ] 17. 性能优化和测试
  - [~] 17.1 实现和测试缓存机制
    - 验证 NamespaceResolver 的缓存有效性
    - 测试缓存命中率
    - 测试缓存失效机制
    - _需求: 6.4_

  - [~] 17.2 实现批量操作优化
    - 优化 resolve_batch 和 generate_batch 方法
    - 减少重复的文件系统访问
    - _需求: 5.2, 5.6_


  - [ ]* 17.3 编写性能测试
    - 测试大量命名空间解析的性能（1000+ 命名空间）
    - 测试大型 TOML 文件的解析性能
    - 确保合理的性能指标（如 < 5 秒处理 1000 个命名空间）

- [ ] 18. 创建示例和文档
  - [~] 18.1 创建基础使用示例
    - 在 `examples/namespace-driven/` 目录下创建示例项目
    - 包含简单的 Django 模型和导出/转换流程
    - 添加 README 说明
    - _需求: 1.1, 2.1, 3.1, 3.2_

  - [~] 18.2 创建第三方模型示例
    - 创建继承自 Django AbstractUser 的示例
    - 展示第三方模型的隔离和 import 生成
    - _需求: 3.2, 4.5, 5.8_

  - [~] 18.3 创建配置文件示例
    - 创建 `namespace_config.toml` 示例文件
    - 包含所有配置选项的说明
    - _需求: 7.1, 7.2, 7.3_

  - [~] 18.4 创建迁移工具使用示例
    - 展示如何使用 er_migrate 命令
    - 包含迁移前后的 TOML 文件对比
    - _需求: 10.3, 10.5_

  - [~] 18.5 更新用户文档
    - 更新 `docs/` 目录下的文档
    - 添加命名空间驱动系统的使用指南
    - 添加配置指南
    - 添加迁移指南
    - 添加故障排除指南

  - [~] 18.6 更新 API 文档
    - 为所有新增的公共接口添加 docstring
    - 使用 Sphinx 或类似工具生成 API 文档
    - 包含类型注解和示例

- [~] 19. 最终检查点 - 确保所有测试通过
  - 运行所有单元测试，确保通过率 > 90%
  - 运行所有属性测试，确保覆盖所有 22 个正确性属性
  - 运行所有集成测试，确保端到端流程正常
  - 检查代码覆盖率，确保核心组件覆盖率 > 90%
  - 如有问题，询问用户并解决


## 注意事项

### 测试标记说明

- 标记 `*` 的子任务为可选测试任务，可以跳过以加快 MVP 开发
- 未标记 `*` 的任务为核心实现任务，必须完成
- 所有属性测试都标记为可选，但建议实现以确保系统正确性

### 实现顺序建议

1. 首先实现核心数据模型和基础组件（任务 1-7）
2. 然后集成到现有系统（任务 8-11）
3. 实现 Export 和 Convert 功能（任务 12-13）
4. 实现迁移工具（任务 14）
5. 完善错误处理和日志（任务 15）
6. 进行端到端测试（任务 16）
7. 性能优化（任务 17）
8. 创建文档和示例（任务 18）

### 依赖关系

- 任务 8-11 依赖任务 1-7
- 任务 12 依赖任务 4, 5
- 任务 13 依赖任务 2, 3, 7, 8
- 任务 14 独立，可以并行开发
- 任务 16 依赖任务 12, 13
- 任务 18 可以在开发过程中逐步完成

### 属性测试配置

所有属性测试应使用以下配置：
- 测试库：hypothesis
- 最小迭代次数：100
- 标签格式：`# Feature: namespace-driven-model-export-import, Property N: 属性名称`

### 代码质量要求

- 所有公共接口必须有类型注解
- 所有公共接口必须有 docstring
- 遵循 PEP 8 代码风格
- 使用 dataclass 定义数据模型
- 实现原子性文件写入（临时文件 + 重命名）
- 实现路径遍历防护

### 错误处理要求

- 所有错误信息必须包含足够的上下文信息
- 支持详细模式，输出调试信息
- 对于可恢复的错误，记录警告并继续
- 对于不可恢复的错误，立即失败并提供清晰的错误信息

