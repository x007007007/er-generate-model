# ER Migrations - 任务列表

## Phase 1: 核心功能 (P0)

### 1. 数据模型定义
- [ ] 1.1 创建 `src/x007007007/er_migrate/models.py`
  - [ ] 1.1.1 定义 `ColumnType` 枚举
  - [ ] 1.1.2 定义 `OnDeleteAction` 和 `OnUpdateAction` 枚举
  - [ ] 1.1.3 定义 `ColumnDefinition` 模型
  - [ ] 1.1.4 定义 `IndexDefinition` 模型
  - [ ] 1.1.5 定义 `ForeignKeyDefinition` 模型
  - [ ] 1.1.6 定义所有 `Operation` 类型
  - [ ] 1.1.7 定义 `Migration` 模型
  - [ ] 1.1.8 编写单元测试 `tests/test_er_migrate/test_models.py`

### 2. 文件管理器
- [ ] 2.1 创建 `src/x007007007/er_migrate/file_manager.py`
  - [ ] 2.1.1 实现 `FileManager` 类
  - [ ] 2.1.2 实现 YAML 文件读写
  - [ ] 2.1.3 实现 TOML 文件读写
  - [ ] 2.1.4 实现命名空间管理
  - [ ] 2.1.5 实现迁移文件列表和排序
  - [ ] 2.1.6 编写单元测试 `tests/test_er_migrate/test_file_manager.py`

### 3. Differ算法
- [ ] 3.1 创建 `src/x007007007/er_migrate/differ.py`
  - [ ] 3.1.1 实现 `ERDiffer` 类
  - [ ] 3.1.2 实现表级别差异检测
  - [ ] 3.1.3 实现列级别差异检测
  - [ ] 3.1.4 实现操作优化和排序
  - [ ] 3.1.5 编写单元测试 `tests/test_er_migrate/test_differ.py`
    - [ ] 3.1.5.1 测试检测新增表
    - [ ] 3.1.5.2 测试检测删除表
    - [ ] 3.1.5.3 测试检测新增列
    - [ ] 3.1.5.4 测试检测删除列
    - [ ] 3.1.5.5 测试检测修改列

### 4. StateBuilder
- [ ] 4.1 创建 `src/x007007007/er_migrate/state_builder.py`
  - [ ] 4.1.1 实现 `StateBuilder` 类
  - [ ] 4.1.2 实现操作应用逻辑
  - [ ] 4.1.3 实现拓扑排序
  - [ ] 4.1.4 编写单元测试 `tests/test_er_migrate/test_state_builder.py`
    - [ ] 4.1.4.1 测试应用 CreateTable 操作
    - [ ] 4.1.4.2 测试应用 AddColumn 操作
    - [ ] 4.1.4.3 测试应用 RemoveColumn 操作
    - [ ] 4.1.4.4 测试拓扑排序

### 5. 迁移生成器
- [ ] 5.1 创建 `src/x007007007/er_migrate/generator.py`
  - [ ] 5.1.1 实现 `MigrationGenerator` 类
  - [ ] 5.1.2 实现迁移编号生成
  - [ ] 5.1.3 实现依赖关系确定
  - [ ] 5.1.4 实现自动命名
  - [ ] 5.1.5 编写单元测试 `tests/test_er_migrate/test_generator.py`

### 6. CLI基础框架
- [ ] 6.1 创建 `src/x007007007/er_migrate/cli.py`
  - [ ] 6.1.1 实现主命令组
  - [ ] 6.1.2 实现 `makemigrations` 命令
  - [ ] 6.1.3 实现 `showmigrations` 命令
  - [ ] 6.1.4 实现 `rebuild-state` 命令
  - [ ] 6.1.5 编写CLI测试 `tests/test_er_migrate/test_cli.py`

### 7. 项目配置
- [ ] 7.1 更新 `pyproject.toml`
  - [ ] 7.1.1 添加 `er-migrate` 命令入口点
  - [ ] 7.1.2 添加依赖: pyyaml
  - [ ] 7.1.3 更新测试配置

### 8. 集成测试
- [ ] 8.1 创建 `tests/test_er_migrate/test_integration.py`
  - [ ] 8.1.1 测试完整的迁移生成流程
  - [ ] 8.1.2 测试状态重建流程
  - [ ] 8.1.3 测试多命名空间场景

## Phase 2: 完整功能 (P1)

### 9. 完整操作类型支持
- [ ] 9.1 实现索引操作
  - [ ] 9.1.1 在 Differ 中支持索引检测
  - [ ] 9.1.2 在 StateBuilder 中支持索引应用
  - [ ] 9.1.3 编写测试

- [ ] 9.2 实现外键操作
  - [ ] 9.2.1 在 Differ 中支持外键检测
  - [ ] 9.2.2 在 StateBuilder 中支持外键应用
  - [ ] 9.2.3 编写测试

- [ ] 9.3 实现表重命名
  - [ ] 9.3.1 在 Differ 中支持表重命名检测
  - [ ] 9.3.2 在 StateBuilder 中支持表重命名应用
  - [ ] 9.3.3 编写测试

### 10. 依赖关系管理
- [ ] 10.1 创建 `src/x007007007/er_migrate/dependency.py`
  - [ ] 10.1.1 实现依赖解析
  - [ ] 10.1.2 实现循环依赖检测
  - [ ] 10.1.3 实现跨命名空间依赖
  - [ ] 10.1.4 编写测试

### 11. 命名空间管理
- [ ] 11.1 创建 `src/x007007007/er_migrate/namespace.py`
  - [ ] 11.1.1 实现命名空间类
  - [ ] 11.1.2 实现 glob 模式匹配
  - [ ] 11.1.3 实现命名空间配置
  - [ ] 11.1.4 编写测试

### 12. 错误处理
- [ ] 12.1 创建 `src/x007007007/er_migrate/exceptions.py`
  - [ ] 12.1.1 定义异常类
  - [ ] 12.1.2 实现错误消息格式化
  - [ ] 12.1.3 编写测试

### 13. 文档
- [ ] 13.1 编写用户文档
  - [ ] 13.1.1 更新 README.md
  - [ ] 13.1.2 创建使用示例
  - [ ] 13.1.3 创建 API 文档

## Phase 3: 高级功能 (P2)

### 14. 迁移合并
- [ ] 14.1 实现 `squashmigrations` 命令
  - [ ] 14.1.1 实现迁移合并算法
  - [ ] 14.1.2 实现冲突检测
  - [ ] 14.1.3 编写测试

### 15. 数据库适配器
- [ ] 15.1 创建 `src/x007007007/er_migrate/adapters/`
  - [ ] 15.1.1 实现基础适配器接口
  - [ ] 15.1.2 实现 PostgreSQL 适配器
  - [ ] 15.1.3 实现 MySQL 适配器
  - [ ] 15.1.4 编写测试

### 16. 性能优化
- [ ] 16.1 实现缓存机制
- [ ] 16.2 实现并行处理
- [ ] 16.3 性能基准测试

### 17. 插件机制
- [ ] 17.1 设计插件接口
- [ ] 17.2 实现插件加载器
- [ ] 17.3 编写示例插件
- [ ] 17.4 编写插件文档

## 测试覆盖率目标

- [ ] 整体测试覆盖率 >= 90%
- [ ] 核心模块 (models, differ, state_builder) >= 95%
- [ ] 所有测试通过
- [ ] 无 lint 错误

## 文档完成标准

- [ ] README 包含完整的使用说明
- [ ] 所有公共 API 有文档字符串
- [ ] 包含至少 3 个完整的使用示例
- [ ] 包含故障排除指南
