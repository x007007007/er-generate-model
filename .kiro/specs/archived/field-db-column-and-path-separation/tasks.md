# Implementation Plan: Field DB Column and Path Separation

## Overview

本实施计划将分三个主要阶段实现功能：
1. 扩展Column模型以支持db_column
2. 实现PathConfiguration和路径分离功能
3. 集成所有组件并更新命令行接口

每个阶段都包含相应的属性测试和单元测试，确保增量验证。

## Tasks

- [ ] 1. 扩展Column模型以支持db_column
  - [x] 1.1 在Column数据类中添加db_column字段和database_column_name属性
    - 修改`packages/er-gen-core/src/x007007007/er/models.py`
    - 将`db_column: Optional[str] = None`改为`db_column: str`（必需字段）
    - 简化`database_column_name`属性方法，直接返回db_column
    - 将Entity的`table_name: Optional[str] = None`改为`table_name: str`（必需字段）
    - _Requirements: 1.1, 1.2_
  
  - [x] 1.2 编写属性测试：字段名回退正确性
    - **Property 2: 字段名回退正确性**
    - **Validates: Requirements 1.2**
    - 生成随机Column对象，验证database_column_name等于db_column
    - _Requirements: 1.2_
  
  - [x] 1.3 编写单元测试：Column模型基本功能
    - 测试db_column必需字段
    - 测试database_column_name属性返回db_column
    - 测试Entity的table_name必需字段
    - _Requirements: 1.1, 1.2_

- [ ] 2. 扩展Django解析器以提取db_column参数
  - [x] 2.1 更新DjangoModelParser的_convert_field_to_column方法
    - 修改`packages/er-django/src/x007007007/er_django/parser.py`
    - 从Django字段提取db_column（如果字段有db_column属性则使用，否则使用field.column或field.name）
    - 确保db_column始终有值（必需字段）
    - _Requirements: 1.1, 1.3_
  
  - [x] 2.2 更新DjangoModelParser的_convert_model_to_entity方法
    - 移除table_name的fallback逻辑
    - 直接从model._meta.db_table获取table_name（必需）
    - 如果无法获取则抛出错误
    - _Requirements: 1.1, 1.3_
  
  - [x] 2.3 编写属性测试：db_column参数提取正确性
    - **Property 1: db_column参数提取正确性**
    - **Validates: Requirements 1.1, 1.3**
    - 生成随机的Django字段定义（包含db_column），验证解析正确
    - _Requirements: 1.1, 1.3_
  
  - [x] 2.4 编写单元测试：db_column解析边缘情况
    - 测试字段有db_column属性的情况
    - 测试字段没有db_column但有column属性的情况
    - 测试字段只有name的情况
    - 测试model._meta.db_table不存在时抛出错误
    - _Requirements: 1.3_

- [ ] 3. 扩展TOML渲染器以输出db_column
  - [x] 3.1 更新TOMLRenderer的render_column方法
    - 修改TOML渲染器代码
    - 添加db_column字段输出逻辑（仅当与name不同时输出）
    - 同时输出table_name字段（始终输出，因为是必需字段）
    - _Requirements: 1.4_
  
  - [x] 3.2 编写属性测试：TOML输出条件包含db_column
    - **Property 3: TOML输出条件包含db_column**
    - **Validates: Requirements 1.4**
    - 生成随机Column对象，验证当db_column与name不同时输出db_column，相同时不输出
    - 生成随机Entity对象，验证TOML输出始终包含table_name
    - _Requirements: 1.4_
  
  - [x] 3.3 编写单元测试：TOML输出格式
    - 测试db_column与name不同时输出db_column字段
    - 测试db_column与name相同时不输出db_column字段
    - 测试Entity输出始终包含table_name字段
    - _Requirements: 1.4_

- [ ] 4. 扩展代码生成器以使用db_column
  - [x] 4.1 更新DjangoCodeGenerator的generate_field_definition方法
    - 修改Django代码生成器
    - 仅当db_column与name不同时添加db_column参数到生成的字段定义
    - 始终添加db_table参数到生成的Meta类（因为是必需字段）
    - _Requirements: 1.4_
  
  - [x] 4.2 编写单元测试：Django代码生成
    - 测试db_column与name不同时生成的字段定义包含db_column参数
    - 测试db_column与name相同时生成的字段定义不包含db_column参数
    - 测试生成的Meta类始终包含db_table参数
    - _Requirements: 1.4_

- [x] 5. Checkpoint - 确保db_column功能测试通过
  - 运行所有db_column相关的测试
  - 确保所有测试通过，如有问题请询问用户

- [ ] 6. 实现PathConfiguration类
  - [x] 6.1 创建PathConfiguration数据类
    - 在`packages/er-django/src/x007007007/er_django/`下创建`path_configuration.py`
    - 实现PathConfiguration数据类及其字段
    - _Requirements: 2.1, 3.1, 3.2_
  
  - [x] 6.2 实现from_options类方法
    - 实现配置继承规则（scan_path → output_path → third_party_output_path）
    - 实现相对路径解析逻辑
    - 实现包名前缀推导逻辑
    - _Requirements: 2.2, 2.3, 2.7, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 6.3 实现validate方法
    - 验证scan_path存在性
    - 验证包名前缀格式
    - 返回描述性错误消息
    - _Requirements: 3.8, 5.4_
  
  - [x] 6.4 编写属性测试：默认Third_Party_Output_Path推导
    - **Property 4: 默认Third_Party_Output_Path推导**
    - **Validates: Requirements 2.2**
    - 生成随机配置（不含third_party_output_path），验证推导正确
    - _Requirements: 2.2_
  
  - [x] 6.5 编写属性测试：自定义Third_Party_Output_Path优先级
    - **Property 5: 自定义Third_Party_Output_Path优先级**
    - **Validates: Requirements 2.3**
    - 生成随机配置（含third_party_output_path），验证使用用户值
    - _Requirements: 2.3_
  
  - [x] 6.6 编写属性测试：默认包名前缀推导
    - **Property 8: 默认包名前缀推导**
    - **Validates: Requirements 2.7**
    - 生成随机路径，验证前缀为最后一个目录名
    - _Requirements: 2.7_
  
  - [x] 6.7 编写属性测试：默认Scan_Path值
    - **Property 10: 默认Scan_Path值**
    - **Validates: Requirements 3.3**
    - 生成不含scan_path的配置，验证默认为'src'
    - _Requirements: 3.3_
  
  - [x] 6.8 编写属性测试：Output_Path继承Scan_Path
    - **Property 11: Output_Path继承Scan_Path**
    - **Validates: Requirements 3.4**
    - 生成仅含scan_path的配置，验证output_path继承
    - _Requirements: 3.4_
  
  - [x] 6.9 编写属性测试：仅Scan_Path配置的继承链
    - **Property 13: 仅Scan_Path配置的继承链**
    - **Validates: Requirements 4.1**
    - 生成仅含scan_path的配置，验证完整继承链
    - _Requirements: 4.1_
  
  - [x] 6.10 编写属性测试：Scan_Path和Output_Path配置的继承链
    - **Property 14: Scan_Path和Output_Path配置的继承链**
    - **Validates: Requirements 4.2**
    - 生成含scan_path和output_path的配置，验证third_party继承
    - _Requirements: 4.2_
  
  - [x] 6.11 编写属性测试：完整配置优先级
    - **Property 15: 完整配置优先级**
    - **Validates: Requirements 4.3**
    - 生成完整配置，验证所有值使用用户指定值
    - _Requirements: 4.3_
  
  - [x] 6.12 编写属性测试：相对路径解析基准
    - **Property 16: 相对路径解析基准**
    - **Validates: Requirements 4.4**
    - 生成相对路径配置，验证相对于工作目录解析
    - _Requirements: 4.4_
  
  - [x] 6.13 编写属性测试：Third_Party相对路径解析基准
    - **Property 17: Third_Party相对路径解析基准**
    - **Validates: Requirements 4.5**
    - 生成third_party相对路径配置，验证相对于output_path解析
    - _Requirements: 4.5_
  
  - [x] 6.14 编写单元测试：PathConfiguration错误处理
    - 测试scan_path不存在的错误（示例）
    - 测试无效包名前缀的错误（示例）
    - 测试配置类型错误（示例）
    - _Requirements: 3.8, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. 扩展PathResolver以支持新配置
  - [x] 7.1 修改PathResolver构造函数以接受PathConfiguration
    - 修改`packages/er-django/src/x007007007/er_django/path_resolver.py`
    - 添加config参数（必需参数）
    - _Requirements: 3.6_
  
  - [x] 7.2 更新resolve_output_path方法以支持is_third_party参数
    - 添加is_third_party可选参数
    - 根据is_third_party选择base_dir
    - _Requirements: 2.4, 3.6_
  
  - [x] 7.3 实现resolve_package_name方法
    - 添加新方法以解析包名
    - 支持三方包前缀添加
    - _Requirements: 2.4, 2.6, 2.7_
  
  - [x] 7.4 实现get_scan_path方法
    - 添加新方法返回扫描路径
    - _Requirements: 3.6_
  
  - [x] 7.5 编写属性测试：三方包名前缀添加
    - **Property 6: 三方包名前缀添加**
    - **Validates: Requirements 2.4**
    - 生成随机应用配置，验证三方包名添加前缀
    - _Requirements: 2.4_
  
  - [x] 7.6 编写属性测试：自定义包名前缀使用
    - **Property 7: 自定义包名前缀使用**
    - **Validates: Requirements 2.6**
    - 生成自定义前缀配置，验证使用自定义前缀
    - _Requirements: 2.6_
  
  - [x] 7.7 编写属性测试：路径分离功能正确性
    - **Property 12: 路径分离功能正确性**
    - **Validates: Requirements 3.6**
    - 生成不同的scan_path和output_path，验证读写位置正确
    - _Requirements: 3.6_
  
  - [x] 7.8 编写单元测试：PathResolver基本功能
    - 测试三方包和非三方包的路径解析
    - 测试包名转换
    - _Requirements: 2.4, 3.6_

- [x] 8. 更新代码生成器以使用带前缀的包名
  - [x] 8.1 修改导入语句生成逻辑
    - 更新代码生成器以使用PathResolver.resolve_package_name
    - 确保三方包引用使用带前缀的包名
    - _Requirements: 2.8_
  
  - [x] 8.2 编写属性测试：导入语句使用带前缀包名
    - **Property 9: 导入语句使用带前缀包名**
    - **Validates: Requirements 2.8**
    - 生成随机三方包引用，验证导入语句使用带前缀包名
    - _Requirements: 2.8_
  
  - [x] 8.3 编写单元测试：导入语句生成
    - 测试三方包导入语句格式
    - 测试非三方包导入语句格式
    - _Requirements: 2.8_

- [x] 9. Checkpoint - 确保路径配置功能测试通过
  - 运行所有路径配置相关的测试
  - 确保所有测试通过，如有问题请询问用户

- [x] 10. 更新er_export命令以支持新参数
  - [x] 10.1 在er_export命令中添加新的命令行参数
    - 添加--scan-path参数
    - 添加--output-dir参数（已存在，确保语义正确）
    - 添加--third-party-output-dir参数
    - 添加--third-party-prefix参数
    - _Requirements: 2.1, 3.1, 3.2_
  
  - [x] 10.2 在er_export命令中集成PathConfiguration
    - 使用PathConfiguration.from_options创建配置对象
    - 调用validate方法验证配置
    - 处理验证错误
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 10.3 更新er_export命令以使用新的PathResolver
    - 创建PathResolver实例并传入配置
    - 更新所有路径解析调用
    - _Requirements: 3.6_

- [x] 11. 更新er_convert命令以支持新参数
  - [x] 11.1 在er_convert命令中添加新的命令行参数
    - 添加--scan-path参数
    - 更新--output-dir参数语义
    - 添加--third-party-output-dir参数
    - 添加--third-party-prefix参数
    - _Requirements: 2.1, 3.1, 3.2_
  
  - [x] 11.2 在er_convert命令中集成PathConfiguration
    - 使用PathConfiguration.from_options创建配置对象
    - 调用validate方法验证配置
    - 处理验证错误
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 11.3 更新er_convert命令以使用新的PathResolver
    - 创建PathResolver实例并传入配置
    - 更新所有路径解析调用
    - _Requirements: 3.6_

- [x] 12. 集成测试
  - [x] 12.1 编写端到端集成测试
    - 创建测试Django项目
    - 测试完整的导出和转换流程
    - 测试db_column功能
    - 测试路径分离功能
    - 测试三方包输出
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.2, 2.3, 2.4, 3.3, 3.4, 3.6_

- [x] 13. 文档更新
  - [x] 13.1 更新README文档
    - 添加新参数的说明
    - 添加db_column功能的示例
    - 添加路径配置的示例
    - _Requirements: 所有_
  
  - [x] 13.2 更新TOML格式文档
    - 说明db_column字段
    - 提供示例
    - _Requirements: 1.4_
  
- [x] 14. Final Checkpoint - 确保所有测试通过
  - 运行完整的测试套件
  - 确保所有测试通过，如有问题请询问用户

## Notes

- 任务标记为`*`的是可选的测试任务，可以跳过以加快MVP开发
- 每个任务都引用了具体的需求以确保可追溯性
- Checkpoint任务确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边缘情况
- 集成测试验证端到端功能
