"""
命名空间驱动的模型导入导出系统的核心数据模型和异常类

该模块定义了系统中使用的所有数据类和异常类，包括：
- ResolveResult: 命名空间解析结果
- ImportSpec: 导入规范
- EntityDefinition: 实体定义
- ColumnDefinition: 字段定义
- TemplateDefinition: 模板定义
- NamespaceNotFoundError: 命名空间未找到错误
- CircularInheritanceError: 循环继承错误
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ResolveResult:
    """命名空间解析结果
    
    包含命名空间解析后的完整信息，包括文件路径、位置类型和元数据。
    
    Attributes:
        namespace: 原始命名空间字符串
        file_path: 解析得到的 TOML 文件路径
        location_type: 位置类型，'project' 或 'third-party'
        exists: 文件是否存在
        search_path: 找到文件的搜索路径
        metadata: 额外的元数据字典
    """
    
    namespace: str
    file_path: str
    location_type: str
    exists: bool
    search_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportSpec:
    """Import 语句规范
    
    描述一个 Python import 语句的完整信息。
    
    Attributes:
        namespace: 模型的命名空间
        model_name: 模型类名
        location_type: 位置类型，'project' 或 'third-party'
        alias: 可选的别名
    """
    
    namespace: str
    model_name: str
    location_type: str
    alias: Optional[str] = None


@dataclass
class ColumnDefinition:
    """字段定义
    
    描述实体或模板中的一个字段的完整信息。
    
    Attributes:
        name: 字段名称（Python 属性名）
        type: 字段类型
        db_column: 数据库列名
        is_pk: 是否为主键
        is_fk: 是否为外键
        nullable: 是否可为空
        comment: 注释
        default: 默认值
        max_length: 最大长度
        unique: 是否唯一
        indexed: 是否索引
    """
    
    name: str
    type: str
    db_column: str
    is_pk: bool = False
    is_fk: bool = False
    nullable: bool = True
    comment: Optional[str] = None
    default: Optional[Any] = None
    max_length: Optional[int] = None
    unique: bool = False
    indexed: bool = False


@dataclass
class EntityDefinition:
    """实体定义
    
    描述一个实体（数据模型）的完整信息，用于 Export 阶段。
    
    Attributes:
        name: 实体名称
        namespace: 实体的命名空间
        table_name: 数据库表名
        columns: 字段列表
        extends: 继承的模板/基类命名空间列表
        comment: 注释
        package: Python 包路径
    """
    
    name: str
    namespace: str
    table_name: str
    columns: List[ColumnDefinition]
    extends: List[str] = field(default_factory=list)
    comment: Optional[str] = None
    package: Optional[str] = None


@dataclass
class TemplateDefinition:
    """模板定义
    
    描述一个模板（抽象模型或 Mixin 类）的完整信息，用于 Export 阶段。
    
    Attributes:
        name: 模板名称
        namespace: 模板的命名空间
        columns: 字段列表
        package: Python 包路径
        export_path: 导出路径
    """
    
    name: str
    namespace: str
    columns: List[ColumnDefinition]
    package: Optional[str] = None
    export_path: Optional[str] = None


class NamespaceNotFoundError(Exception):
    """命名空间未找到错误
    
    当命名空间无法在任何搜索路径中解析时抛出此异常。
    
    Attributes:
        namespace: 未找到的命名空间
        search_paths: 已搜索的路径列表
    """
    
    def __init__(self, namespace: str, search_paths: List[str]):
        """初始化命名空间未找到错误
        
        Args:
            namespace: 未找到的命名空间
            search_paths: 已搜索的路径列表
        """
        self.namespace = namespace
        self.search_paths = search_paths
        
        # 构造详细的错误信息
        message = (
            f"Namespace '{namespace}' not found in any search path.\n"
            f"Searched paths: {', '.join(search_paths)}"
        )
        super().__init__(message)


class CircularInheritanceError(Exception):
    """循环继承错误
    
    当检测到模型之间存在循环继承关系时抛出此异常。
    
    Attributes:
        cycle_path: 循环路径，包含形成循环的所有模型名称
    """
    
    def __init__(self, cycle_path: List[str]):
        """初始化循环继承错误
        
        Args:
            cycle_path: 循环路径，包含形成循环的所有模型名称
        """
        self.cycle_path = cycle_path
        
        # 构造详细的错误信息
        message = (
            f"Circular inheritance detected: {' -> '.join(cycle_path)}"
        )
        super().__init__(message)
