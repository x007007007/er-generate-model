# ANTLR解析器使用指南

## 概述

本项目使用ANTLR4来解析Mermaid ER图，提供比正则表达式更强大和准确的解析能力。

## 目录结构

```
src/x007007007/er/parser/antlr/
├── MermaidER.g4              # ANTLR语法文件
├── mermaid_antlr_parser.py   # ANTLR解析器实现
├── __init__.py
└── generated/                 # ANTLR生成的代码（需要生成）
    ├── MermaidERLexer.py
    ├── MermaidERParser.py
    └── MermaidERVisitor.py
```

## 生成ANTLR解析器代码

### 前置要求

- Java 11+ (ANTLR 4.13.2要求)
- ANTLR JAR文件已放置在 `tools/antlr-4.13.2-complete.jar`

### Windows

```bash
tools\generate_antlr.bat
```

### Linux/Mac

```bash
chmod +x tools/generate_antlr.sh
./tools/generate_antlr.sh
```

### 手动生成

```bash
java -jar tools/antlr-4.13.2-complete.jar \
  -Dlanguage=Python3 \
  -visitor \
  -o src/x007007007/er/parser/antlr/generated \
  src/x007007007/er/parser/antlr/MermaidER.g4
```

## 使用ANTLR解析器

### 在代码中使用

```python
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser

parser = MermaidAntlrParser()
model = parser.parse(mermaid_content)
```

### 在CLI中使用

```bash
# 使用ANTLR解析器
er-convert convert diagram.mermaid --use-antlr

# 使用正则表达式解析器（默认）
er-convert convert diagram.mermaid
```

## 自动回退机制

如果ANTLR生成的代码不可用，解析器会自动回退到正则表达式解析器，确保功能正常。

## 通过测试驱动开发g4文件

项目包含完整的单元测试来驱动g4文件的开发：

```bash
# 运行所有ANTLR相关测试
uv run pytest tests/test_antlr_parser.py -v

# 如果ANTLR代码未生成，测试会被跳过
# 生成ANTLR代码后，测试会自动运行
```

## 语法文件开发

### 当前支持的语法

- 实体定义：`EntityName { ... }`
- 列定义：`type name [PK] [FK] "comment"`
- 关系定义：`Entity1 ||--o{ Entity2 : label`

### 关系类型

- `||--||` : 一对一
- `||--o{` 或 `||--}o` : 一对多
- `}|--|{` 或 `}o--o{` : 多对多
- `}o--||` : 多对一

### 修改语法文件

1. 编辑 `src/x007007007/er/parser/antlr/MermaidER.g4`
2. 重新生成解析器代码
3. 运行测试验证修改
4. 根据测试结果调整语法

## 故障排除

### Java版本问题

如果遇到 `UnsupportedClassVersionError`，说明Java版本过低：

- **解决方案1**: 升级到Java 11+
- **解决方案2**: 使用ANTLR 4.9.3（支持Java 8），修改生成脚本中的JAR文件名

### 导入错误

如果遇到 `ImportError: cannot import name 'MermaidERLexer'`：

1. 确保已运行生成脚本
2. 检查 `generated/` 目录是否存在
3. 确认生成的文件完整

### 解析错误

如果解析失败：

1. 检查语法文件是否正确
2. 查看ANTLR生成的错误消息
3. 使用测试用例验证语法

## 优势

相比正则表达式解析器，ANTLR解析器具有以下优势：

1. **更准确的语法解析**：基于正式语法定义
2. **更好的错误报告**：提供详细的语法错误信息
3. **更容易扩展**：添加新语法规则更简单
4. **更好的维护性**：语法和解析逻辑分离

## 未来改进

- [ ] 支持更多Mermaid ER图特性
- [ ] 添加语法错误恢复机制
- [ ] 支持语法高亮和验证
- [ ] 创建PlantUML的ANTLR语法文件

