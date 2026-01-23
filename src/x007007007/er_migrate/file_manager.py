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
        
        # 序列化为字典
        data = migration.model_dump(exclude_none=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return file_path
    
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
