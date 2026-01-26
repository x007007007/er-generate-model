"""
Migration file manager - handles reading and writing migration files
"""
import re
from pathlib import Path
from typing import List, Optional
import yaml
from .models import Migration


class FileManager:
    """迁移文件管理器"""
    
    def __init__(self, migrations_dir: str):
        """
        初始化文件管理器
        
        Args:
            migrations_dir: 迁移文件根目录
        """
        self.migrations_dir = Path(migrations_dir)
    
    def get_namespace_dir(self, namespace: str) -> Path:
        """获取命名空间目录"""
        return self.migrations_dir / namespace
    
    def list_migration_files(self, namespace: str) -> List[str]:
        """
        列出命名空间下的所有迁移文件
        
        Args:
            namespace: 命名空间名称
            
        Returns:
            排序后的迁移文件名列表
        """
        namespace_dir = self.get_namespace_dir(namespace)
        if not namespace_dir.exists():
            return []
        
        # 查找所有.yaml和.yml文件
        files = []
        for ext in ['.yaml', '.yml']:
            files.extend(namespace_dir.glob(f'*{ext}'))
        
        # 按文件名排序
        files.sort(key=lambda f: f.name)
        return [f.name for f in files]
    
    def load_migration(self, namespace: str, filename: str) -> Migration:
        """
        加载单个迁移文件
        
        Args:
            namespace: 命名空间名称
            filename: 迁移文件名
            
        Returns:
            Migration对象
            
        Raises:
            FileNotFoundError: 文件不存在
            ValidationError: 文件格式错误
        """
        file_path = self.get_namespace_dir(namespace) / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Migration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 确保namespace字段正确
        if 'namespace' not in data:
            data['namespace'] = namespace
        
        return Migration(**data)
    
    def load_namespace_migrations(self, namespace: str) -> List[Migration]:
        """
        加载命名空间下的所有迁移
        
        Args:
            namespace: 命名空间名称
            
        Returns:
            Migration对象列表，按文件名排序
        """
        filenames = self.list_migration_files(namespace)
        migrations = []
        
        for filename in filenames:
            migration = self.load_migration(namespace, filename)
            migrations.append(migration)
        
        return migrations
    
    def save_migration(self, migration: Migration) -> Path:
        """
        保存迁移文件
        
        Args:
            migration: Migration对象
            
        Returns:
            保存的文件路径
        """
        namespace_dir = self.get_namespace_dir(migration.namespace)
        namespace_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = self._generate_filename(migration)
        file_path = namespace_dir / filename
        
        # 序列化为字典，保证字段顺序
        data = self._serialize_migration(migration)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return file_path
    
    def _serialize_migration(self, migration: Migration) -> dict:
        """
        序列化Migration对象为有序字典
        
        Args:
            migration: Migration对象
            
        Returns:
            字典（Python 3.7+保持插入顺序）
        """
        # 按照固定顺序构建字典（Python 3.7+的dict保持插入顺序）
        data = {}
        data['version'] = migration.version
        data['name'] = migration.name
        data['namespace'] = migration.namespace
        data['dependencies'] = migration.dependencies
        
        # 序列化operations
        operations = []
        for op in migration.operations:
            op_dict = self._serialize_operation(op)
            operations.append(op_dict)
        data['operations'] = operations
        
        if migration.created_at:
            data['created_at'] = migration.created_at
        
        return data
    
    def _serialize_operation(self, operation) -> dict:
        """
        序列化Operation对象为字典
        
        Args:
            operation: Operation对象
            
        Returns:
            字典
        """
        op_dict = {}
        op_dict['type'] = operation.type
        
        # 根据操作类型添加字段
        if operation.type == 'CreateTable':
            op_dict['table_name'] = operation.table_name
            op_dict['columns'] = [self._serialize_column(col) for col in operation.columns]
        elif operation.type == 'DropTable':
            op_dict['table_name'] = operation.table_name
        elif operation.type == 'RenameTable':
            op_dict['old_name'] = operation.old_name
            op_dict['new_name'] = operation.new_name
        elif operation.type == 'AddColumn':
            op_dict['table_name'] = operation.table_name
            op_dict['column'] = self._serialize_column(operation.column)
        elif operation.type == 'RemoveColumn':
            op_dict['table_name'] = operation.table_name
            op_dict['column_name'] = operation.column_name
        elif operation.type == 'AlterColumn':
            op_dict['table_name'] = operation.table_name
            op_dict['column_name'] = operation.column_name
            if operation.new_type is not None:
                op_dict['new_type'] = operation.new_type
            if operation.new_max_length is not None:
                op_dict['new_max_length'] = operation.new_max_length
            if operation.new_nullable is not None:
                op_dict['new_nullable'] = operation.new_nullable
            if operation.new_default is not None:
                op_dict['new_default'] = operation.new_default
            if operation.new_precision is not None:
                op_dict['new_precision'] = operation.new_precision
            if operation.new_scale is not None:
                op_dict['new_scale'] = operation.new_scale
        elif operation.type == 'AddIndex':
            op_dict['table_name'] = operation.table_name
            op_dict['index'] = self._serialize_index(operation.index)
        elif operation.type == 'RemoveIndex':
            op_dict['table_name'] = operation.table_name
            op_dict['index_name'] = operation.index_name
        elif operation.type == 'AddForeignKey':
            op_dict['table_name'] = operation.table_name
            op_dict['foreign_key'] = self._serialize_foreign_key(operation.foreign_key)
        elif operation.type == 'RemoveForeignKey':
            op_dict['table_name'] = operation.table_name
            op_dict['constraint_name'] = operation.constraint_name
        
        return op_dict
    
    def _serialize_column(self, column) -> dict:
        """序列化列定义"""
        col_dict = {}
        col_dict['name'] = column.name
        col_dict['type'] = column.type
        col_dict['primary_key'] = column.primary_key
        col_dict['nullable'] = column.nullable
        col_dict['unique'] = column.unique
        
        if column.default is not None:
            col_dict['default'] = column.default
        if column.max_length is not None:
            col_dict['max_length'] = column.max_length
        if column.precision is not None:
            col_dict['precision'] = column.precision
        if column.scale is not None:
            col_dict['scale'] = column.scale
        if column.comment is not None:
            col_dict['comment'] = column.comment
        
        return col_dict
    
    def _serialize_index(self, index) -> dict:
        """序列化索引定义"""
        idx_dict = {}
        idx_dict['name'] = index.name
        idx_dict['columns'] = index.columns
        idx_dict['unique'] = index.unique
        
        return idx_dict
    
    def _serialize_foreign_key(self, fk) -> dict:
        """序列化外键定义"""
        fk_dict = {}
        fk_dict['column_name'] = fk.column_name
        fk_dict['reference_table'] = fk.reference_table
        fk_dict['reference_column'] = fk.reference_column
        fk_dict['on_delete'] = fk.on_delete
        fk_dict['on_update'] = fk.on_update
        
        return fk_dict
    
    def _generate_filename(self, migration: Migration) -> str:
        """
        生成迁移文件名
        
        格式: NNNN_name.yaml
        其中NNNN是4位数字序号
        
        Args:
            migration: Migration对象
            
        Returns:
            文件名
        """
        # 获取当前命名空间下的最大序号
        existing_files = self.list_migration_files(migration.namespace)
        max_number = 0
        
        for filename in existing_files:
            match = re.match(r'^(\d{4})_', filename)
            if match:
                number = int(match.group(1))
                max_number = max(max_number, number)
        
        # 生成新序号
        new_number = max_number + 1
        
        # 清理名称（移除特殊字符）
        clean_name = re.sub(r'[^\w\s-]', '', migration.name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name).lower()
        
        return f"{new_number:04d}_{clean_name}.yaml"
    
    def get_next_migration_number(self, namespace: str) -> int:
        """
        获取下一个迁移序号
        
        Args:
            namespace: 命名空间名称
            
        Returns:
            下一个序号
        """
        existing_files = self.list_migration_files(namespace)
        max_number = 0
        
        for filename in existing_files:
            match = re.match(r'^(\d{4})_', filename)
            if match:
                number = int(match.group(1))
                max_number = max(max_number, number)
        
        return max_number + 1
