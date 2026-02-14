"""
迁移生成器 - 从ER图生成迁移文件
"""
from typing import Optional, List
from datetime import datetime
from x007007007.er.models import ERModel
from .converter import ERConverter
from .differ import ERDiffer
from .file_manager import FileManager
from .models import Migration, Operation, CreateTable, AddColumn, AddForeignKey, RemoveColumn, DropTable, AlterColumn, RenameTable


class MigrationGenerator:
    """迁移生成器"""
    
    def __init__(self, migrations_dir: str):
        """
        初始化迁移生成器
        
        Args:
            migrations_dir: 迁移文件根目录
        """
        self.migrations_dir = migrations_dir
        self.file_manager = FileManager(migrations_dir)
        self.converter = ERConverter()
        self.differ = ERDiffer()
    
    def generate(self, namespace: str, current_er: ERModel, name: Optional[str] = None) -> Optional[Migration]:
        """
        生成迁移
        
        Args:
            namespace: 命名空间
            current_er: 当前的ER模型
            name: 迁移名称（可选，如果不提供则自动生成）
            
        Returns:
            Migration对象，如果没有变更则返回None
        """
        # 1. 重建当前状态（从已有的迁移）
        previous_state = self._rebuild_state(namespace)
        
        # 2. 计算差异
        operations = self.differ.diff(previous_state, current_er)
        
        # 3. 如果没有变更，返回None
        if not operations:
            return None
        
        # 4. 生成迁移名称
        if name is None:
            name = self._generate_migration_name(operations, previous_state)
        
        # 5. 计算依赖
        dependencies = self._calculate_dependencies(namespace)
        
        # 6. 创建迁移对象
        migration = Migration(
            version="1.0",
            name=name,
            namespace=namespace,
            dependencies=dependencies,
            operations=operations,
            created_at=datetime.now()
        )
        
        return migration
    
    def _rebuild_state(self, namespace: str) -> ERModel:
        """
        从迁移历史重建ER状态
        
        Args:
            namespace: 命名空间
            
        Returns:
            重建的ERModel
        """
        # 加载所有迁移
        migrations = self.file_manager.load_namespace_migrations(namespace)
        
        # 如果没有迁移，返回空模型
        if not migrations:
            return ERModel()
        
        # TODO: 实现完整的状态重建逻辑
        # 现在简单实现：从最后一个迁移推断状态
        # 这是一个简化版本，完整版本需要state_builder.py
        
        from x007007007.er.models import Entity, Column, Relationship
        
        rebuilt_model = ERModel()
        
        # 遍历所有迁移的操作
        for migration in migrations:
            for op in migration.operations:
                if isinstance(op, CreateTable):
                    # 创建实体
                    columns = []
                    for col_def in op.columns:
                        col = Column(
                            name=col_def.name,
                            type=col_def.type,
                            is_pk=col_def.primary_key,
                            nullable=col_def.nullable,
                            default=col_def.default,
                            max_length=col_def.max_length,
                            precision=col_def.precision,
                            scale=col_def.scale,
                            unique=col_def.unique,
                            comment=col_def.comment
                        )
                        columns.append(col)
                    
                    # 转换表名为实体名（snake_case -> PascalCase）
                    entity_name = self._to_pascal_case(op.table_name)
                    entity = Entity(name=entity_name, columns=columns)
                    
                    # 避免重复添加
                    if entity_name not in rebuilt_model.entities:
                        rebuilt_model.add_entity(entity)
                
                elif isinstance(op, AddColumn):
                    # 添加列到现有实体
                    entity_name = self._to_pascal_case(op.table_name)
                    if entity_name in rebuilt_model.entities:
                        entity = rebuilt_model.entities[entity_name]
                        col = Column(
                            name=op.column.name,
                            type=op.column.type,
                            is_pk=op.column.primary_key,
                            nullable=op.column.nullable,
                            default=op.column.default,
                            max_length=op.column.max_length,
                            unique=op.column.unique
                        )
                        entity.columns.append(col)
                
                elif isinstance(op, RemoveColumn):
                    # 从实体中删除列
                    entity_name = self._to_pascal_case(op.table_name)
                    if entity_name in rebuilt_model.entities:
                        entity = rebuilt_model.entities[entity_name]
                        # 过滤掉要删除的列
                        entity.columns = [col for col in entity.columns if col.name != op.column_name]
                
                elif isinstance(op, DropTable):
                    # 删除实体
                    entity_name = self._to_pascal_case(op.table_name)
                    if entity_name in rebuilt_model.entities:
                        del rebuilt_model.entities[entity_name]
                
                elif isinstance(op, RenameTable):
                    # 重命名实体
                    old_entity_name = self._to_pascal_case(op.old_name)
                    new_entity_name = self._to_pascal_case(op.new_name)
                    if old_entity_name in rebuilt_model.entities:
                        entity = rebuilt_model.entities[old_entity_name]
                        # 更新实体名称
                        entity.name = new_entity_name
                        # 在字典中重命名
                        rebuilt_model.entities[new_entity_name] = entity
                        del rebuilt_model.entities[old_entity_name]
                
                elif isinstance(op, AlterColumn):
                    # 修改列属性
                    entity_name = self._to_pascal_case(op.table_name)
                    if entity_name in rebuilt_model.entities:
                        entity = rebuilt_model.entities[entity_name]
                        # 找到要修改的列
                        for col in entity.columns:
                            if col.name == op.column_name:
                                # 应用修改（只更新非None的字段）
                                if op.new_type is not None:
                                    col.type = op.new_type
                                if op.new_max_length is not None:
                                    col.max_length = op.new_max_length
                                if op.new_nullable is not None:
                                    col.nullable = op.new_nullable
                                if op.new_default is not None:
                                    col.default = op.new_default
                                if op.new_precision is not None:
                                    col.precision = op.new_precision
                                if op.new_scale is not None:
                                    col.scale = op.new_scale
                                break
                
                elif isinstance(op, AddForeignKey):
                    # 重建关系信息
                    # 从外键定义推断关系
                    left_entity = self._to_pascal_case(op.table_name)
                    right_entity = self._to_pascal_case(op.foreign_key.reference_table)
                    
                    # 创建关系对象
                    rel = Relationship(
                        left_entity=left_entity,
                        right_entity=right_entity,
                        relation_type="many-to-one",  # 外键通常表示多对一关系
                        left_column=op.foreign_key.column_name,
                        right_column=op.foreign_key.reference_column
                    )
                    
                    # 添加关系（避免重复）
                    # 检查是否已存在相同的关系
                    rel_exists = any(
                        r.left_entity == rel.left_entity and
                        r.right_entity == rel.right_entity and
                        r.left_column == rel.left_column and
                        r.right_column == rel.right_column
                        for r in rebuilt_model.relationships
                    )
                    
                    if not rel_exists:
                        rebuilt_model.add_relationship(rel)
        
        return rebuilt_model
    
    def _generate_migration_name(self, operations: List[Operation], previous_state: ERModel) -> str:
        """
        根据操作自动生成迁移名称
        
        Args:
            operations: 操作列表
            previous_state: 之前的状态
            
        Returns:
            迁移名称
        """
        # 如果是初始迁移
        if not previous_state.entities:
            return "initial"
        
        # 根据第一个操作生成名称
        if operations:
            first_op = operations[0]
            
            if isinstance(first_op, CreateTable):
                return f"create_{first_op.table_name}"
            elif isinstance(first_op, AddColumn):
                return f"add_{first_op.column.name}"
            elif isinstance(first_op, AddForeignKey):
                return f"add_foreign_key"
        
        # 默认名称
        return "auto_migration"
    
    def _calculate_dependencies(self, namespace: str) -> List[str]:
        """
        计算依赖关系
        
        Args:
            namespace: 命名空间
            
        Returns:
            依赖列表
        """
        # 获取当前命名空间的所有迁移
        migrations = self.file_manager.load_namespace_migrations(namespace)
        
        # 如果没有迁移，返回空列表
        if not migrations:
            return []
        
        # 依赖最后一个迁移
        last_migration = migrations[-1]
        
        # 获取最后一个迁移的文件名（不含扩展名）
        files = self.file_manager.list_migration_files(namespace)
        if files:
            last_file = files[-1]
            # 移除.yaml或.yml扩展名
            migration_id = last_file.replace('.yaml', '').replace('.yml', '')
            return [f"{namespace}.{migration_id}"]
        
        return []
    
    def _to_pascal_case(self, snake_str: str) -> str:
        """
        将snake_case转换为PascalCase
        
        Args:
            snake_str: snake_case字符串
            
        Returns:
            PascalCase字符串
        """
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
