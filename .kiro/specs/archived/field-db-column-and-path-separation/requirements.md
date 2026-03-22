# Requirements Document

## Introduction

本文档定义了ER模型生成工具中字段数据库列名支持和路径分离功能的需求。该功能旨在解决三个核心问题：正确处理Django字段的db_column参数、分离三方包输出路径以避免包名冲突、以及分离扫描路径与输出路径以提供更灵活的配置选项。

## Glossary

- **ER_Tool**: ER模型生成工具系统
- **Django_Field**: Django模型中的字段定义
- **db_column**: Django字段参数，用于指定数据库表中的实际列名
- **Business_Field_Name**: 模型中使用的字段业务名称
- **Database_Column_Name**: 数据库表中的实际列名
- **Third_Party_Package**: 安装在Python环境中的外部依赖包
- **Output_Path**: 生成代码的输出目录路径
- **Third_Party_Output_Path**: 三方包代码的专用输出目录路径
- **Scan_Path**: 扫描Django模型的源代码目录路径
- **Package_Name**: Python包的完整导入名称

## Requirements

### Requirement 1: Django字段db_column参数支持

**User Story:** 作为开发者，我希望ER工具能够正确识别和处理Django字段的db_column参数，以便生成的ER模型能够准确反映数据库表结构。

#### Acceptance Criteria

1. WHEN Django_Field指定了db_column参数，THE ER_Tool SHALL使用db_column的值作为Database_Column_Name
2. WHEN Django_Field未指定db_column参数，THE ER_Tool SHALL使用Business_Field_Name作为Database_Column_Name
3. WHEN解析Django模型时，THE ER_Tool SHALL正确提取db_column参数值
4. WHEN生成ER模型输出时，THE ER_Tool SHALL在输出中区分Business_Field_Name和Database_Column_Name
5. WHEN验证字段映射时，THE ER_Tool SHALL确保Database_Column_Name与实际数据库表结构一致

### Requirement 2: 三方包输出路径分离

**User Story:** 作为开发者，我希望三方包的生成代码能够输出到独立的目录中，以避免与项目代码的包名冲突，并保持清晰的代码组织结构。

#### Acceptance Criteria

1. THE ER_Tool SHALL支持Third_Party_Output_Path配置参数
2. WHEN用户未指定Third_Party_Output_Path，THE ER_Tool SHALL默认使用Output_Path下的third子目录
3. WHEN用户指定了Third_Party_Output_Path，THE ER_Tool SHALL使用用户指定的路径
4. WHEN输出Third_Party_Package代码时，THE ER_Tool SHALL添加third前缀到Package_Name
5. WHEN Third_Party_Package原始包名为aaa.bbb，THE ER_Tool SHALL转换为third.aaa.bbb
6. WHEN用户指定了自定义Third_Party_Output_Path，THE ER_Tool SHALL允许用户指定自定义的包名前缀
7. WHEN未指定自定义包名前缀，THE ER_Tool SHALL使用Third_Party_Output_Path的最后一个目录名作为包名前缀
8. WHEN生成导入语句时，THE ER_Tool SHALL使用带前缀的Package_Name

### Requirement 3: 扫描路径与输出路径分离

**User Story:** 作为开发者，我希望能够独立配置扫描路径和输出路径，以便在不同的项目结构中灵活使用ER工具。

#### Acceptance Criteria

1. THE ER_Tool SHALL支持Scan_Path配置参数
2. THE ER_Tool SHALL支持Output_Path配置参数
3. WHEN用户未指定Scan_Path，THE ER_Tool SHALL默认使用src目录
4. WHEN用户未指定Output_Path，THE ER_Tool SHALL使用Scan_Path作为Output_Path
5. WHEN用户未指定Third_Party_Output_Path，THE ER_Tool SHALL使用Output_Path下的third子目录
6. WHEN Scan_Path和Output_Path不同，THE ER_Tool SHALL从Scan_Path读取源代码并输出到Output_Path
7. WHEN配置路径参数时，THE ER_Tool SHALL验证路径的有效性
8. WHEN Scan_Path不存在，THE ER_Tool SHALL返回明确的错误信息

### Requirement 4: 路径配置继承关系

**User Story:** 作为开发者，我希望路径配置具有合理的默认值和继承关系，以便在大多数情况下只需要最少的配置。

#### Acceptance Criteria

1. WHEN仅指定Scan_Path，THE ER_Tool SHALL使用Scan_Path作为Output_Path和Third_Party_Output_Path的基础
2. WHEN指定Scan_Path和Output_Path，THE ER_Tool SHALL使用Output_Path作为Third_Party_Output_Path的基础
3. WHEN所有路径参数都指定，THE ER_Tool SHALL使用用户指定的所有路径值
4. WHEN路径参数使用相对路径，THE ER_Tool SHALL相对于当前工作目录解析
5. WHEN Third_Party_Output_Path使用相对路径，THE ER_Tool SHALL相对于Output_Path解析

### Requirement 5: 配置参数验证

**User Story:** 作为开发者，我希望在配置错误时能够获得清晰的错误提示，以便快速定位和修复配置问题。

#### Acceptance Criteria

1. WHEN路径配置冲突时，THE ER_Tool SHALL返回描述性错误信息
2. WHEN路径不存在且无法创建时，THE ER_Tool SHALL返回明确的错误信息
3. WHEN路径权限不足时，THE ER_Tool SHALL返回权限相关的错误信息
4. WHEN包名前缀无效时，THE ER_Tool SHALL返回包名验证错误信息
5. WHEN配置参数类型错误时，THE ER_Tool SHALL返回类型验证错误信息


