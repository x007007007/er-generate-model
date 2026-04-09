# TOML 格式迁移至新规范 — TODO List

## 目标

将 er-generate-model 中的 TOML 格式从当前旧格式迁移到 er-graph-gen-code 定义的新规范（`toml-format-spec.md`）。

## 新旧格式核心差异

| 差异点 | 旧格式 | 新规范 |
|--------|--------|--------|
| **[config] 部分** | 无 | 必需，含 `namespace`、`base_package`、`extends_aliases` |
| **columns 语法** | 行内 `columns = [{...}]` | 数组表 `[[entities.X.columns]]` |
| **is_pk / is_fk** | `is_pk = true` | `primary_key = true`（去掉 is_fk，由关系推断） |
| **extends 路径** | 完整路径 | 支持 `extends_aliases` 别名 |
| **package 拼接** | 完整路径 | `base_package + "." + package` |
| **模板 export_path** | 有 `export_path` 字段 | 无（模板只有 `comment` 和 `columns`） |
| **关系 type** | 支持 `1:1`, `1:N` 等简写 | 仅 `one-to-one` 等全称 |

---

## 1. 分层任务总览

### 1.1 核心解析器改造（er-gen-core）

- [ ] 1.1.1 更新 `TomlERParser.parse()` 支持 `[config]` 段解析
- [ ] 1.1.2 新增 `extends_aliases` 别名解析逻辑
- [ ] 1.1.3 新增 `base_package` + `entity.package` 拼接逻辑
- [ ] 1.1.4 支持数组表 `[[entities.X.columns]]` 语法
- [ ] 1.1.5 `is_pk` → `primary_key` 字段名映射（兼容双写）
- [ ] 1.1.6 移除 `is_fk` 字段（由关系推断，不再人工标注）
- [ ] 1.1.7 模板 `export_path` 字段废弃（不再解析）
- [ ] 1.1.8 关系 type 简写（`1:1`, `1:N` 等）标记为 deprecated

### 1.2 数据模型适配（er-gen-core）

- [x] 1.2.1 `ERModel` 新增 `namespace`、`base_package`、`extends_aliases` 属性
- [x] 1.2.2 `Column` 模型适配（`primary_key` 别名）— 解析器层面兼容，Column 内部保持 is_pk
- [x] 1.2.3 `Entity` 模型适配（`package` 拼接后的完整路径存储）— 解析器层面处理

### 1.3 TOML 写入器改造（er-gen-core）

- [ ] 1.3.1 `TOMLWriter` 输出 `[config]` 段
- [ ] 1.3.2 `TOMLWriter` 输出数组表 `[[entities.X.columns]]` 格式
- [ ] 1.3.3 `TOMLWriter` 使用 `primary_key` 替代 `is_pk`
- [ ] 1.3.4 `TOMLWriter` 不再输出 `is_fk`
- [ ] 1.3.5 `TOMLWriter` 不再输出模板 `export_path`
- [ ] 1.3.6 `TOMLWriter` 输出 `extends_aliases` 和 `base_package`

### 1.4 Django 渲染器改造（er-django）

- [ ] 1.4.1 `TOMLRenderer` 输出新格式（`[config]`、`primary_key`、数组表）

### 1.5 测试资源文件迁移（全部 .toml 文件）

- [ ] 1.5.1 er-gen-core/tests/assets/ 下的测试 TOML 文件
- [ ] 1.5.2 er-gen-tool/tests/assets/ 下的测试 TOML 文件
- [ ] 1.5.3 examples/ 下的示例 TOML 文件

### 1.6 测试代码适配

- [ ] 1.6.1 er-gen-core 测试用例适配新格式
- [ ] 1.6.2 er-gen-tool 测试用例适配新格式
- [ ] 1.6.3 er-django 测试用例适配新格式
- [ ] 1.6.4 顶层 tests/ 适配

### 1.7 其他引用模块适配

- [ ] 1.7.1 er-gen-tool `convert.py`
- [ ] 1.7.2 er-gen-tool-ai `validator.py`
- [ ] 1.7.3 er-gen-mcp `server.py`
- [ ] 1.7.4 er-django `er_convert.py`

---

## 2. 详细 Checklist（含依赖顺序）

> 依赖关系：1.2 → 1.1 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7

### Phase 0: 数据模型准备（无依赖）

- [x] 2.0.1 `ERModel` 新增属性：`namespace: str`, `base_package: str`, `extends_aliases: Dict[str, str]`
- [x] 2.0.2 `Column` 数据类：确保 `is_pk` 可从 `primary_key` 映射（读取时兼容两种名称）

### Phase 1: 解析器改造（依赖 Phase 0）

- [x] 2.1.1 `TomlERParser._parse_config()` — 解析 `[config]` 表，提取 `namespace`、`base_package`、`extends_aliases`
- [x] 2.1.2 `TomlERParser._resolve_extends()` — 实现 extends 别名解析优先级：aliases → templates/entities → 完整路径
- [x] 2.1.3 `TomlERParser._resolve_package()` — 实现 `base_package + entity.package` 拼接
- [x] 2.1.4 `TomlERParser._parse_column()` — 支持 `primary_key` 字段名（兼容旧 `is_pk`）
- [x] 2.1.5 `TomlERParser._parse_column()` — 移除对 `is_fk` 的直接读取（FK 由关系推断）
- [x] 2.1.6 `TomlERParser._parse_templates()` — 不再解析 `export_path`
- [x] 2.1.7 `TomlERParser._parse_relationships()` — 保留 `1:1` 简写兼容但标记 deprecated warning
- [x] 2.1.8 `TomlERParser.parse()` — 支持同时解析行内 `columns = [{...}]` 和数组表 `[[entities.X.columns]]`

### Phase 2: 写入器改造（依赖 Phase 0）

- [x] 2.2.1 `TOMLWriter._write_config()` — 输出 `[config]` 段（namespace, base_package, extends_aliases）
- [x] 2.2.2 `TOMLWriter._column_to_dict()` — 输出 `primary_key` 替代 `is_pk`
- [x] 2.2.3 `TOMLWriter._column_to_dict()` — 不再输出 `is_fk`
- [x] 2.2.4 `TOMLWriter.write_entity()` — 输出 `[[entities.X.columns]]` 数组表格式
- [x] 2.2.5 `TOMLWriter.write_template()` — 不再输出 `export_path`
- [x] 2.2.6 `TOMLWriter` — 输出 `base_package`，entity.package 只输出相对部分

### Phase 3: Django 渲染器（依赖 Phase 0）

- [x] 2.3.1 `TOMLRenderer.render()` — 输出 `[config]` 段
- [x] 2.3.2 `TOMLRenderer.render()` — 输出 `primary_key` 替代 `is_pk`
- [x] 2.3.3 `TOMLRenderer.render()` — 输出数组表 `[[entities.X.columns]]` 格式

### Phase 4: 测试 TOML 文件迁移（依赖 Phase 1, 2）

- [x] **2.4.1** `packages/er-gen-core/tests/assets/toml_basic/input.toml` — 添加 `[config]`
- [x] **2.4.2** `packages/er-gen-core/tests/assets/toml_with_template/input.toml`
- [x] **2.4.3** `packages/er-gen-core/tests/assets/toml_multiple_templates/input.toml`
- [x] **2.4.4** `packages/er-gen-core/tests/assets/toml_template_override_order/input.toml`
- [x] **2.4.5** `packages/er-gen-core/tests/assets/toml_field_override/input.toml`
- [x] **2.4.6** `packages/er-gen-core/tests/assets/complex_toml/input.toml`
- [x] **2.4.7** `packages/er-gen-core/tests/assets/toml_invalid_template/input.toml`
- [x] **2.4.8** `packages/er-gen-core/tests/assets/toml_export_path/input.toml`
- [x] **2.4.9** `packages/er-gen-core/tests/assets/toml_relationship_types/input.toml`
- [x] **2.4.10** `packages/er-gen-core/tests/assets/toml_single_extends_not_allowed/input.toml`
- [x] **2.4.11** `packages/er-gen-core/tests/assets/toml_django_single_inheritance/input.toml`
- [x] **2.4.12** `packages/er-gen-core/tests/assets/toml_django_multiple_inheritance/input.toml`
- [x] **2.4.13** `packages/er-gen-core/tests/assets/toml_django_no_inheritance/input.toml`
- [x] **2.4.14** `packages/er-gen-core/tests/assets/toml_django_inheritance_without_export_path/input.toml`
- [x] **2.4.15** `packages/er-gen-core/tests/assets/toml_sqlalchemy_no_inheritance/input.toml`
- [x] **2.4.16** `packages/er-gen-core/tests/assets/toml_sqlalchemy_multiple_inheritance/input.toml`
- [x] **2.4.17** `packages/er-gen-core/tests/assets/toml_multiple_entities_different_inheritance/input.toml`
- [x] **2.4.18** `packages/er-gen-core/tests/assets/django_fk_basic/input.toml`
- [x] **2.4.19** `packages/er-gen-core/tests/assets/django_fk_complex/input.toml`
- [x] **2.4.20** `packages/er-gen-core/tests/assets/django_fk_implicit_db_column/input.toml`
- [x] **2.4.21** `packages/er-gen-core/tests/assets/django_fk_attributes/input.toml`
- [x] **2.4.22** `packages/er-gen-core/tests/assets/django_fk_with_prefix/input.toml`
- [x] **2.4.23** `packages/er-gen-core/tests/assets/django_fk_self_referential/input.toml`
- [x] **2.4.24** `packages/er-gen-core/tests/assets/django_fk_multiple/input.toml`
- [x] **2.4.25** `packages/er-gen-tool/tests/assets/` 下所有 TOML 文件（与 er-gen-core 镜像同步）
- [x] **2.4.26** `examples/bug/django/rfc_order/models.toml`
- [x] **2.4.27** `examples/toml-to-output/django/01-simple-model/input.toml`
- [x] **2.4.28** `examples/toml-to-output/django/02-relationships/input.toml`
- [ ] **2.4.29** `examples/toml-to-output/django/03-all-data-types/input.toml`
- [ ] **2.4.30** `examples/toml-to-output/mermaid/01-simple-model/input.toml`
- [ ] **2.4.31** `examples/toml-to-output/mermaid/02-relationships/input.toml`
- [ ] **2.4.32** `examples/toml-to-output/mermaid/03-all-data-types/input.toml`
- [ ] **2.4.33** `examples/toml-to-output/sqlalchemy/01-simple-model/input.toml`
- [ ] **2.4.34** `examples/toml-to-output/sqlalchemy/02-relationships/input.toml`
- [ ] **2.4.35** `examples/toml-to-output/sqlalchemy/03-all-data-types/input.toml`
- [ ] **2.4.36** `examples/toml-to-output/sqlalchemy/04-templates-single-file/input.toml`
- [ ] **2.4.37** `examples/toml-to-output/sqlalchemy/05-templates-cross-file/base_templates.toml`
- [ ] **2.4.38** `examples/toml-to-output/sqlalchemy/05-templates-cross-file/entities.toml`
- [ ] **2.4.39** `examples/toml-to-output/sqlalchemy/06-templates-explicit-export/input.toml`
- [ ] **2.4.40** `examples/input-to-toml/` 下所有 TOML 文件

### Phase 5: 测试代码适配（依赖 Phase 1, 2, 4）

- [ ] **2.5.1** `packages/er-gen-core/tests/test_toml_parser.py` — 适配新格式断言
- [ ] **2.5.2** `packages/er-gen-core/tests/test_toml_writer_*.py` — 适配新输出格式
- [ ] **2.5.3** `packages/er-gen-core/tests/test_integration_*.py` — 适配
- [ ] **2.5.4** `packages/er-gen-core/tests/test_unit_*.py` — 适配
- [ ] **2.5.5** `packages/er-gen-core/tests/test_preservation_*.py` — 适配
- [ ] **2.5.6** `packages/er-gen-core/tests/test_property_*.py` — 适配
- [ ] **2.5.7** `packages/er-gen-core/tests/test_bugfix_*.py` — 适配
- [ ] **2.5.8** `packages/er-gen-tool/tests/test_integration_pipeline.py` — 适配
- [ ] **2.5.9** `packages/er-django/tests/test_toml_*.py` — 适配
- [ ] **2.5.10** `packages/er-django/tests/test_task_7_*.py` — 适配
- [ ] **2.5.11** `packages/er-django/tests/test_task_14_2_*.py` — 适配
- [ ] **2.5.12** `packages/er-django/tests/test_field_db_column_*.py` — 适配
- [ ] **2.5.13** `tests/test_*.py`（顶层） — 适配

### Phase 6: 其他模块适配（依赖 Phase 1）

- [ ] **2.6.1** `packages/er-gen-tool/src/.../convert.py` — 适配新解析结果
- [ ] **2.6.2** `packages/er-gen-tool-ai/src/.../validator.py` — 适配新格式校验
- [ ] **2.6.3** `packages/er-gen-mcp/src/.../server.py` — 适配
- [ ] **2.6.4** `packages/er-django/src/.../er_convert.py` — 适配

### Phase 7: 验证与回归测试

- [ ] **2.7.1** 运行 er-gen-core 全部测试
- [ ] **2.7.2** 运行 er-gen-tool 全部测试
- [ ] **2.7.3** 运行 er-django 全部测试
- [ ] **2.7.4** 运行顶层 tests/ 全部测试
- [ ] **2.7.5** 验证 golden files（如 regenerate_golden_files.py）

---

## 依赖关系图

```
Phase 0 (数据模型)
  ├─→ Phase 1 (解析器)
  ├─→ Phase 2 (写入器)
  └─→ Phase 3 (Django 渲染器)

Phase 1 + Phase 2
  └─→ Phase 4 (TOML 文件迁移)
       └─→ Phase 5 (测试代码)

Phase 1
  └─→ Phase 6 (其他模块)

Phase 1~6 全部完成
  └─→ Phase 7 (回归测试)
```

## 执行策略

1. **先改模型和解析器**（Phase 0-1），保持向后兼容（旧格式仍可解析）
2. **改写入器和渲染器**（Phase 2-3），输出新格式
3. **批量迁移 TOML 文件**（Phase 4）
4. **适配测试**（Phase 5）
5. **适配其他模块**（Phase 6）
6. **回归测试**（Phase 7）
