# ANTLR解析器实现总结

**最后更新**: 2024年12月

## 完成的工作

### 1. ✅ 依赖配置
- 确认 `pyproject.toml` 中已包含所有必要依赖
- `antlr4-python3-runtime>=4.13.1` 已在依赖列表中
- 测试依赖（pytest, pytest-cov）已配置

### 2. ✅ 目录结构创建
```
src/x007007007/er/parser/antlr/
├── MermaidER.g4              # Mermaid ANTLR语法文件
├── PlantUMLER.g4              # PlantUML ANTLR语法文件
├── mermaid_antlr_parser.py    # Mermaid ANTLR解析器实现
├── plantuml_antlr_parser.py   # PlantUML ANTLR解析器实现
├── __init__.py
└── generated/                 # ANTLR生成的代码
    ├── MermaidERLexer.py
    ├── MermaidERParser.py
    ├── MermaidERVisitor.py
    ├── PlantUMLERLexer.py
    ├── PlantUMLERParser.py
    └── PlantUMLERVisitor.py

tools/
├── antlr-4.13.2-complete.jar # ANTLR工具
├── generate_antlr.bat        # Windows生成脚本
└── generate_antlr.sh          # Linux/Mac生成脚本
```

### 3. ✅ ANTLR语法文件

#### MermaidER.g4
创建了完整的Mermaid ER图语法定义，支持：
- 实体定义：`EntityName { ... }`
- 列定义：`type name [PK] [FK] "comment"`
- 关系定义：`Entity1 ||--o{ Entity2 : label`
- 关系类型：一对一、一对多、多对多、多对一
- 注释支持：`//` 风格注释
- 错误恢复：`invalidLine` 规则处理格式错误

#### PlantUMLER.g4
创建了完整的PlantUML ER图语法定义，支持：
- 实体定义：`entity EntityName { ... }` 或 `class EntityName { ... }`
- 实体别名：`entity User as "User Table"`
- 列定义：`* id : int`（PK标记），`user_id : int <<FK>>`（FK标记）
- 枚举支持：`status : string <<enum:draft,published>>`
- 关系定义：支持所有PlantUML关系语法
- 基数支持：`User "1" -- "0..*" Post`
- 关系标签：`User ||--o{ Post : writes`

### 4. ✅ ANTLR解析器实现

#### MermaidAntlrParser
- 创建了 `MermaidAntlrParser` 类
- 实现了 `MermaidERModelVisitor` 来构建ERModel
- 两阶段解析：先收集实体，再处理关系
- 自定义 ErrorListener 记录语法错误但不中断解析
- **覆盖率：89%**

#### PlantUMLAntlrParser
- 创建了 `PlantUMLAntlrParser` 类
- 实现了 `PlantUMLERModelVisitor` 来构建ERModel
- 支持实体别名（作为注释）
- 支持列标记（PK, FK, enum）
- 完整的关系类型和基数解析
- **覆盖率：84%**

### 5. ✅ 生成脚本
- Windows: `tools/generate_antlr.bat`（已修复路径问题）
- Linux/Mac: `tools/generate_antlr.sh`
- 包含Java版本检查和错误处理
- 支持同时生成 Mermaid 和 PlantUML 解析器代码

### 6. ✅ CLI集成
- **已移除 `--use-antlr` 选项**：ANTLR 现在是默认和唯一的解析器
- **已移除正则表达式解析器**：`parsers.py` 和 `plantuml_parser.py` 已删除
- **自动检测 ANTLR 可用性**：如果 ANTLR 代码未生成，会抛出清晰的错误信息

### 7. ✅ 单元测试
创建了完整的测试套件：
- `tests/test_antlr_parser.py`：Mermaid ANTLR 解析器测试
- `tests/test_er.py`：包含 PlantUML ANTLR 解析器测试
- 测试覆盖：
  - 简单ER图解析
  - 关系解析
  - 复杂ER图解析
  - 列注释
  - 外键
  - 空内容
  - 关系类型
  - 格式错误恢复

**测试结果**: 37个测试全部通过 ✅

### 8. ✅ 文档
- 创建了 `docs/ANTLR_PARSER.md` 使用指南
- 更新了 `README.md` 添加 ANTLR 使用说明
- 更新了项目结构说明

## 使用方法

### 生成ANTLR代码

**Windows:**
```bash
tools\generate_antlr.bat
```

**Linux/Mac:**
```bash
chmod +x tools/generate_antlr.sh
./tools/generate_antlr.sh
```

**注意**: 
- 需要Java 11+（ANTLR 4.13.2要求）
- 如果只有Java 8，可以使用ANTLR 4.9.3（需要修改脚本中的JAR文件名）
- **必须生成ANTLR代码才能使用解析器**，项目已完全移除正则表达式解析器

### 使用ANTLR解析器

**代码中:**
```python
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser

# Mermaid
mermaid_parser = MermaidAntlrParser()
model = mermaid_parser.parse(mermaid_content)

# PlantUML
plantuml_parser = PlantUMLAntlrParser()
model = plantuml_parser.parse(plantuml_content)
```

**CLI中:**
```bash
# Mermaid（默认）
er-convert convert diagram.mermaid --format django

# PlantUML
er-convert convert diagram.puml --input-type plantuml --format sqlalchemy
```

## 测试驱动开发

通过单元测试驱动g4文件的开发：

1. 编写测试用例定义期望行为
2. 运行测试（如果ANTLR代码未生成，会抛出 RuntimeError）
3. 生成ANTLR代码
4. 运行测试验证语法
5. 根据测试结果调整g4文件
6. 重复直到所有测试通过

## 当前状态

- ✅ **语法文件已创建**：MermaidER.g4 和 PlantUMLER.g4
- ✅ **解析器实现完成**：MermaidAntlrParser 和 PlantUMLAntlrParser
- ✅ **测试套件完整**：37个测试全部通过
- ✅ **正则表达式解析器已移除**：完全依赖 ANTLR4
- ✅ **错误处理完善**：自定义 ErrorListener 和清晰的错误信息
- ✅ **覆盖率良好**：Mermaid 89%, PlantUML 84%

## 优势

相比正则表达式解析器：
- ✅ **更准确的语法解析**：ANTLR 提供完整的语法树
- ✅ **更好的错误报告**：精确的语法错误位置和消息
- ✅ **更容易扩展和维护**：语法和解析逻辑分离
- ✅ **支持复杂语法**：注释、基数、关系标签等
- ✅ **错误恢复**：能够处理格式错误并继续解析

## 兼容性

- ✅ **完全迁移**：已移除所有正则表达式解析器代码
- ✅ **向后兼容**：所有现有测试继续通过
- ✅ **API兼容**：解析器接口保持不变
- ⚠️ **要求**：必须生成 ANTLR 代码才能使用（不再有回退机制）

## 下一步

1. ✅ **已完成**：Mermaid 和 PlantUML 的 ANTLR 实现
2. ✅ **已完成**：移除正则表达式解析器
3. ⚠️ **待改进**：提高测试覆盖率（db_parser.py, type_mapper.py）
4. ⚠️ **待添加**：更多边界情况测试
5. ⚠️ **待优化**：解析性能优化（如果需要）
