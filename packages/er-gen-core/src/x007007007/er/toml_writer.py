"""
TOML Writer for namespace-driven model export

This module provides the TOMLWriter class for writing model definitions to TOML files
during the Export stage. Key features:
- Atomic file writes (temp file + rename)
- Directory creation as needed
- Multiple entities/templates in same namespace go to same file
- Use namespace format for extends references (not file paths)
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import toml

from x007007007.er.namespace_models import (
    EntityDefinition,
    TemplateDefinition,
    ColumnDefinition,
)


class TOMLWriter:
    """TOML 写入器
    
    负责将模型定义写入到正确的 TOML 文件中。
    
    Features:
    - 根据命名空间确定文件路径
    - 创建必要的目录结构
    - 将模型定义序列化为 TOML 格式
    - 处理同一命名空间的多个模型（追加到同一文件）
    - 使用原子性写入（临时文件 + 重命名）
    
    Attributes:
        base_dir: 基础目录，"src/" 或 "src/third/"
    """
    
    def __init__(self, base_dir: str):
        """初始化 TOML 写入器
        
        Args:
            base_dir: 基础目录，例如 "src/" 或 "src/third/"
        """
        self.base_dir = base_dir
        # Cache to track which files have been written to avoid redundant reads
        self._file_cache: Dict[str, Dict] = {}
    
    def _get_file_path(self, namespace: str) -> str:
        """根据命名空间生成文件路径
        
        将命名空间转换为文件路径，例如：
        "kinkotech.common.models.base" -> "src/kinkotech/common/models/base.toml"
        
        Args:
            namespace: Python 模块命名空间
            
        Returns:
            完整的文件路径
        """
        # Convert namespace dots to path separators
        relative_path = namespace.replace('.', os.sep) + '.toml'
        
        # Combine with base directory
        file_path = os.path.join(self.base_dir, relative_path)
        
        return file_path
    
    def _ensure_directory(self, file_path: str) -> None:
        """确保文件所在目录存在
        
        Args:
            file_path: 文件路径
        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, mode=0o755, exist_ok=True)
    
    def _read_existing_file(self, file_path: str) -> Dict:
        """读取现有的 TOML 文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            TOML 文件内容字典，如果文件不存在则返回空字典
        """
        # Check cache first
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        
        # Read from file if exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                self._file_cache[file_path] = data
                return data
        
        # Return empty structure
        empty_data = {}
        self._file_cache[file_path] = empty_data
        return empty_data
    
    def _write_file_atomically(self, file_path: str, data: Dict) -> None:
        """原子性写入 TOML 文件
        
        使用临时文件 + 重命名的方式确保写入的原子性，
        避免在写入过程中出错导致文件损坏。
        
        Args:
            file_path: 目标文件路径
            data: 要写入的数据字典
        """
        # Ensure directory exists
        self._ensure_directory(file_path)
        
        # Create temporary file in the same directory
        directory = os.path.dirname(file_path)
        fd, temp_path = tempfile.mkstemp(
            suffix='.toml.tmp',
            dir=directory if directory else '.'
        )
        
        try:
            # Write to temporary file
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                toml.dump(data, f)
            
            # Set file permissions
            os.chmod(temp_path, 0o644)
            
            # Atomic rename
            os.replace(temp_path, file_path)
            
            # Update cache
            self._file_cache[file_path] = data
            
        except Exception:
            # Clean up temporary file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    
    def _column_to_dict(self, column: ColumnDefinition) -> Dict:
        """将 ColumnDefinition 转换为字典格式
        
        Args:
            column: 字段定义对象
            
        Returns:
            字段的字典表示
        """
        col_dict = {
            'name': column.name,
            'type': column.type,
        }
        
        # Add optional fields only if they have non-default values
        if column.db_column != column.name:
            col_dict['db_column'] = column.db_column
        
        if column.is_pk:
            col_dict['is_pk'] = True
        
        if column.is_fk:
            col_dict['is_fk'] = True
        
        if not column.nullable:
            col_dict['nullable'] = False
        
        if column.comment:
            col_dict['comment'] = column.comment
        
        if column.default is not None:
            col_dict['default'] = column.default
        
        if column.max_length is not None:
            col_dict['max_length'] = column.max_length
        
        if column.unique:
            col_dict['unique'] = True
        
        if column.indexed:
            col_dict['indexed'] = True
        
        return col_dict
    
    def write_entity(self, namespace: str, entity: EntityDefinition) -> str:
        """写入实体定义
        
        将实体序列化为 TOML 格式并写入文件。
        如果同一命名空间已有其他实体，则追加到同一文件中。
        使用命名空间格式表示 extends 引用。
        
        Args:
            namespace: 实体的命名空间
            entity: 实体定义对象
            
        Returns:
            写入的文件路径
        """
        file_path = self._get_file_path(namespace)
        
        # Read existing file content
        data = self._read_existing_file(file_path)
        
        # Ensure entities section exists
        if 'entities' not in data:
            data['entities'] = {}
        
        # Build entity data
        entity_data = {}
        
        # Add comment if present
        if entity.comment:
            entity_data['comment'] = entity.comment
        
        # Add table name if different from entity name
        if entity.table_name != entity.name.lower():
            entity_data['table_name'] = entity.table_name
        
        # Add extends if present (using namespace format)
        if entity.extends:
            entity_data['extends'] = entity.extends
        
        # Add columns
        entity_data['columns'] = [
            self._column_to_dict(col) for col in entity.columns
        ]
        
        # Add package if present
        if entity.package:
            entity_data['package'] = entity.package
        
        # Add entity to data
        data['entities'][entity.name] = entity_data
        
        # Write file atomically
        self._write_file_atomically(file_path, data)
        
        return file_path
    
    def write_template(self, namespace: str, template: TemplateDefinition) -> str:
        """写入模板定义
        
        将模板序列化为 TOML 格式并写入文件。
        模板用于表示抽象类或 Mixin 类的字段定义。
        
        Args:
            namespace: 模板的命名空间
            template: 模板定义对象
            
        Returns:
            写入的文件路径
        """
        file_path = self._get_file_path(namespace)
        
        # Read existing file content
        data = self._read_existing_file(file_path)
        
        # Ensure templates section exists
        if 'templates' not in data:
            data['templates'] = {}
        
        # Build template data
        template_data = {}
        
        # Add package if present
        if template.package:
            template_data['package'] = template.package
        
        # Add export_path if present
        if template.export_path:
            template_data['export_path'] = template.export_path
        
        # Add columns
        template_data['columns'] = [
            self._column_to_dict(col) for col in template.columns
        ]
        
        # Add template to data
        data['templates'][template.name] = template_data
        
        # Write file atomically
        self._write_file_atomically(file_path, data)
        
        return file_path
