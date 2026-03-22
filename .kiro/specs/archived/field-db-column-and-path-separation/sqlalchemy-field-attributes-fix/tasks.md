# Implementation Plan: SQLAlchemy Field Attributes Fix

## Overview

本实现计划旨在修复 Django 到 SQLAlchemy 模型转换过程中字段属性丢失的问题。主要工作集中在更新两个 Jinja2 模板文件，确保 `unique`、`indexed` 和 `nullable` 属性被正确渲染到生成的 SQLAlchemy 代码中。

## Tasks

- [ ] 1. 修复 sqlalchemy_single_model.j2 模板
  - [x] 1.1 更新普通字段的参数列表构建逻辑
    - 在 param_list 构建部分添加 unique 和 index 参数的处理
    - 确保参数按照正确顺序添加：primary_key, nullable, unique, index, default, comment
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 7.1_
  
  - [x] 1.2 修复外键字段的参数处理
    - 将外键字段的内联参数改为使用 param_list
    - 添加 unique 和 index 参数的处理
    - 确保外键字段也遵循相同的参数顺序
    - _Requirements: 6.3, 7.1_
  
  - [x] 1.3 确保带 max_length 字段的参数完整性
    - 验证带有 max_length 的字段在类型参数之后正确包含所有属性
    - 确保 nullable、unique、index 等参数不会被遗漏
    - _Requirements: 3.1, 3.2, 6.4_
  
  - [ ]* 1.4 编写属性测试验证模板修复
    - **Property 1: Unique 属性渲染**
    - **Property 2: Index 属性渲染**
    - **Property 3: Nullable 属性渲染一致性**
    - **Property 4: 多属性组合渲染**
    - **Property 5: 外键字段属性保留**
    - **Property 6: 参数顺序一致性**
    - **Property 7: 参数格式正确性**
    - **Property 11: 带 max_length 字段的属性保留**
    - **Validates: Requirements 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3, 6.3, 6.4, 7.1, 7.3**

- [ ] 2. 修复 sqlalchemy_model.j2 模板
  - [x] 2.1 更新普通字段的参数列表构建逻辑
    - 在 param_list 构建部分添加 unique 和 index 参数的处理
    - 确保参数按照正确顺序添加
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 7.1_
  
  - [x] 2.2 修复外键字段的参数处理
    - 将外键字段的内联参数改为使用 param_list
    - 添加 unique 和 index 参数的处理
    - _Requirements: 6.3, 7.1_
  
  - [x] 2.3 确保带 max_length 字段的参数完整性
    - 验证带有 max_length 的字段在类型参数之后正确包含所有属性
    - _Requirements: 3.1, 3.2, 6.4_
  
  - [ ]* 2.4 编写属性测试验证模板一致性
    - **Property 10: 模板一致性**
    - 验证两个模板生成的代码包含相同的字段属性
    - **Validates: Requirements 6.1, 6.2**

- [x] 3. Checkpoint - 验证模板修复
  - 运行现有的 test_field_attributes.py 测试
  - 确保所有测试通过
  - 如有问题，请向用户报告

- [ ] 4. 验证解析器的正确性
  - [x] 4.1 检查 DjangoModelParser 的字段属性提取
    - 验证 unique、db_index 和 null 属性被正确提取
    - 确认 introspector 方法返回正确的值
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 4.2 编写属性测试验证解析器
    - **Property 8: 解析器属性提取完整性**
    - 测试解析器正确提取所有字段属性
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 5. 端到端集成测试
  - [ ]* 5.1 编写端到端属性测试
    - **Property 9: 端到端属性保留**
    - 创建 Django 模型，完整转换后验证生成的 SQLAlchemy 代码
    - 测试各种字段类型和属性组合
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
  
  - [ ]* 5.2 编写单元测试验证特定场景
    - 测试带有 unique=True 的字段
    - 测试带有 db_index=True 的字段
    - 测试带有 null=False 的字段
    - 测试多个属性组合的字段
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6. Final Checkpoint - 确保所有测试通过
  - 运行所有新增的属性测试和单元测试
  - 运行现有的回归测试
  - 确保没有破坏现有功能
  - 如有问题，请向用户报告

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求，便于追溯
- Checkpoint 任务确保增量验证
- 属性测试使用 Python 的 hypothesis 库，每个测试至少运行 100 次迭代
- 单元测试专注于特定示例和边缘情况
- 两个模板文件的修复逻辑相同，可以参考第一个模板的修复方式
