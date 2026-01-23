"""
ER模型转换器 - 将现有的ERModel转换为迁移系统格式
"""
import re
from typing import List, Dict, Tuple, Any
from x007007007.er.models import Entity, Column, Relationship, ERModel
from .models import ColumnDefinition, IndexDefinition, ForeignKeyDefinition


class ERConverter:
    """ER模型转换器"""
    
    def convert_column(self, column: Column) -> ColumnDefinition:
        """
        转换列定义
        
        Args:
            column: 原始Column对象
            
        Returns:
            ColumnDefinition对象
        """
        return ColumnDefinition(
            name=column.name,
            type=column.type,
            primary_key=column.is_pk,
            nullable=column.nullable,
            default=column.default,
            max_length=column.max_length,
            precision=column.precision,
            scale=column.scale,
            unique=column.unique,
            comment=column.comment
        )
    
    def convert_entity(self, entity: Entity) -> Tuple[str, List[ColumnDefinition]]:
        """
        转换实体为表定义
        
        Args:
            entity: 原始Entity对象
            
        Returns:
            (table_name, columns)元组
        """
        # 转换表名为snake_case
        table_name = self._to_snake_case(entity.name)
        
        # 转换所有列
        columns = [self.convert_column(col) for col in entity.columns]
        
        return table_name, columns
    
    def extract_indexes(self, entity: Entity) -> List[IndexDefinition]:
        """
        从实体提取索引定义
        
        Args:
            entity: 原始Entity对象
            
        Returns:
            索引定义列表
        """
        indexes = []
        table_name = self._to_snake_case(entity.name)
        
        for col in entity.columns:
            # 唯一索引
            if col.unique and not col.is_pk:
                idx_name = f"idx_{table_name}_{col.name}_unique"
                indexes.append(IndexDefinition(
                    name=idx_name,
                    columns=[col.name],
                    unique=True
                ))
            
            # 普通索引
            elif col.indexed:
                idx_name = f"idx_{table_name}_{col.name}"
                indexes.append(IndexDefinition(
                    name=idx_name,
                    columns=[col.name],
                    unique=False
                ))
        
        return indexes
    
    def convert_relationship(self, relationship: Relationship) -> ForeignKeyDefinition:
        """
        转换关系为外键定义
        
        Args:
            relationship: 原始Relationship对象
            
        Returns:
            ForeignKeyDefinition对象
        """
        # 转换表名为snake_case
        reference_table = self._to_snake_case(relationship.right_entity)
        
        # 如果没有明确的列名，使用默认的命名规则
        column_name = relationship.left_column
        if not column_name:
            # 默认使用 {reference_table}_id
            column_name = f"{reference_table}_id"
        
        reference_column = relationship.right_column
        if not reference_column:
            # 默认使用 id
            reference_column = "id"
        
        return ForeignKeyDefinition(
            column_name=column_name,
            reference_table=reference_table,
            reference_column=reference_column,
            on_delete="CASCADE",
            on_update="CASCADE"
        )
    
    def convert_model(self, er_model: ERModel) -> Dict[str, Any]:
        """
        转换完整的ER模型
        
        Args:
            er_model: 原始ERModel对象
            
        Returns:
            包含tables和foreign_keys的字典
        """
        result = {
            "tables": {},
            "foreign_keys": []
        }
        
        # 转换所有实体
        for entity_name, entity in er_model.entities.items():
            table_name, columns = self.convert_entity(entity)
            result["tables"][table_name] = {
                "columns": columns,
                "indexes": self.extract_indexes(entity)
            }
        
        # 转换所有关系
        for rel in er_model.relationships:
            fk = self.convert_relationship(rel)
            result["foreign_keys"].append(fk)
        
        return result
    
    def _to_snake_case(self, name: str) -> str:
        """
        将CamelCase或PascalCase转换为snake_case
        
        Args:
            name: 原始名称
            
        Returns:
            snake_case格式的名称
        """
        # 在大写字母前插入下划线
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        # 在小写字母和大写字母之间插入下划线
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        # 转换为小写
        return s2.lower()
