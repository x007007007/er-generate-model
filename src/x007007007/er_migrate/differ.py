"""
ER差异检测器 - 比较两个ER模型，生成操作列表
"""
from typing import List, Dict, Set, Any
from x007007007.er.models import ERModel, Entity, Column
from .converter import ERConverter
from .models import (
    Operation,
    CreateTable,
    DropTable,
    AddColumn,
    RemoveColumn,
    AlterColumn,
    AddIndex,
    RemoveIndex,
    ColumnDefinition,
)


class ERDiffer:
    """ER模型差异检测器"""
    
    def __init__(self):
        self.converter = ERConverter()
    
    def diff(self, old_model: ERModel, new_model: ERModel) -> List[Operation]:
        """
        比较两个ER模型，生成操作列表
        
        Args:
            old_model: 旧的ER模型
            new_model: 新的ER模型
            
        Returns:
            操作列表
        """
        operations = []
        
        # 转换实体名为表名
        old_tables = {self.converter._to_snake_case(name): entity 
                     for name, entity in old_model.entities.items()}
        new_tables = {self.converter._to_snake_case(name): entity 
                     for name, entity in new_model.entities.items()}
        
        old_table_names = set(old_tables.keys())
        new_table_names = set(new_tables.keys())
        
        # 检测可能的表重命名
        dropped_tables = old_table_names - new_table_names
        created_tables = new_table_names - old_table_names
        
        rename_mapping = self._detect_table_renames(
            {name: old_tables[name] for name in dropped_tables},
            {name: new_tables[name] for name in created_tables}
        )
        
        # 1. 处理重命名的表
        from .models import RenameTable
        for old_name, new_name in rename_mapping.items():
            operations.append(RenameTable(old_name=old_name, new_name=new_name))
            
            # 重命名后，检测列变更
            old_entity = old_tables[old_name]
            new_entity = new_tables[new_name]
            
            col_ops = self._diff_columns(new_name, old_entity, new_entity)
            operations.extend(col_ops)
            
            idx_ops = self._diff_indexes(new_name, old_entity, new_entity)
            operations.extend(idx_ops)
        
        # 2. 检测删除的表（排除已重命名的）
        for table_name in dropped_tables:
            if table_name not in rename_mapping:
                operations.append(DropTable(table_name=table_name))
        
        # 3. 检测新增的表（排除已重命名的）
        for table_name in created_tables:
            if table_name not in rename_mapping.values():
                entity = new_tables[table_name]
                table_name_converted, columns = self.converter.convert_entity(entity)
                operations.append(CreateTable(
                    table_name=table_name_converted,
                    columns=columns
                ))
                
                # 添加索引
                indexes = self.converter.extract_indexes(entity)
                for idx in indexes:
                    operations.append(AddIndex(
                        table_name=table_name_converted,
                        index=idx
                    ))
        
        # 4. 检测现有表的变更（未重命名的）
        for table_name in old_table_names & new_table_names:
            old_entity = old_tables[table_name]
            new_entity = new_tables[table_name]
            
            # 检测列变更
            col_ops = self._diff_columns(table_name, old_entity, new_entity)
            operations.extend(col_ops)
            
            # 检测索引变更
            idx_ops = self._diff_indexes(table_name, old_entity, new_entity)
            operations.extend(idx_ops)
        
        # 5. 检测外键关系
        fk_ops = self._diff_relationships(old_model, new_model)
        operations.extend(fk_ops)
        
        return operations
    
    def _diff_columns(self, table_name: str, old_entity: Entity, new_entity: Entity) -> List[Operation]:
        """
        检测列的变更
        
        Args:
            table_name: 表名
            old_entity: 旧实体
            new_entity: 新实体
            
        Returns:
            操作列表
        """
        operations = []
        
        # 构建列字典
        old_cols = {col.name: col for col in old_entity.columns}
        new_cols = {col.name: col for col in new_entity.columns}
        
        old_col_names = set(old_cols.keys())
        new_col_names = set(new_cols.keys())
        
        # 检测删除的列
        for col_name in old_col_names - new_col_names:
            operations.append(RemoveColumn(
                table_name=table_name,
                column_name=col_name
            ))
        
        # 检测新增的列
        for col_name in new_col_names - old_col_names:
            col = new_cols[col_name]
            col_def = self.converter.convert_column(col)
            operations.append(AddColumn(
                table_name=table_name,
                column=col_def
            ))
        
        # 检测修改的列
        for col_name in old_col_names & new_col_names:
            old_col = old_cols[col_name]
            new_col = new_cols[col_name]
            
            alter_op = self._diff_column_properties(table_name, old_col, new_col)
            if alter_op:
                operations.append(alter_op)
        
        return operations
    
    def _diff_column_properties(self, table_name: str, old_col: Column, new_col: Column) -> Operation:
        """
        检测单个列的属性变更
        
        Args:
            table_name: 表名
            old_col: 旧列
            new_col: 新列
            
        Returns:
            AlterColumn操作，如果没有变更则返回None
        """
        changes = {}
        
        # 检测类型变更
        if old_col.type != new_col.type:
            changes['new_type'] = new_col.type
        
        # 检测长度变更
        if old_col.max_length != new_col.max_length:
            changes['new_max_length'] = new_col.max_length
        
        # 检测可空性变更
        if old_col.nullable != new_col.nullable:
            changes['new_nullable'] = new_col.nullable
        
        # 检测默认值变更
        if old_col.default != new_col.default:
            changes['new_default'] = new_col.default
        
        # 检测精度变更
        if old_col.precision != new_col.precision:
            changes['new_precision'] = new_col.precision
        
        # 检测小数位数变更
        if old_col.scale != new_col.scale:
            changes['new_scale'] = new_col.scale
        
        # 如果有变更，创建AlterColumn操作
        if changes:
            return AlterColumn(
                table_name=table_name,
                column_name=new_col.name,
                **changes
            )
        
        return None
    
    def _diff_indexes(self, table_name: str, old_entity: Entity, new_entity: Entity) -> List[Operation]:
        """
        检测索引的变更
        
        Args:
            table_name: 表名
            old_entity: 旧实体
            new_entity: 新实体
            
        Returns:
            操作列表
        """
        operations = []
        
        # 提取索引信息
        old_indexes = self._extract_index_info(old_entity)
        new_indexes = self._extract_index_info(new_entity)
        
        # 检测删除的索引
        for col_name in old_indexes - new_indexes:
            idx_name = f"idx_{table_name}_{col_name}"
            if old_entity.columns:
                old_col = next((c for c in old_entity.columns if c.name == col_name), None)
                if old_col and old_col.unique:
                    idx_name = f"idx_{table_name}_{col_name}_unique"
            
            operations.append(RemoveIndex(
                table_name=table_name,
                index_name=idx_name
            ))
        
        # 检测新增的索引
        for col_name in new_indexes - old_indexes:
            new_col = next(c for c in new_entity.columns if c.name == col_name)
            
            # 确定索引名称和类型
            if new_col.unique:
                idx_name = f"idx_{table_name}_{col_name}_unique"
                unique = True
            else:
                idx_name = f"idx_{table_name}_{col_name}"
                unique = False
            
            from .models import IndexDefinition
            operations.append(AddIndex(
                table_name=table_name,
                index=IndexDefinition(
                    name=idx_name,
                    columns=[col_name],
                    unique=unique
                )
            ))
        
        return operations
    
    def _extract_index_info(self, entity: Entity) -> Set[str]:
        """
        提取实体中有索引的列名
        
        Args:
            entity: 实体
            
        Returns:
            有索引的列名集合
        """
        indexed_cols = set()
        
        for col in entity.columns:
            if col.indexed or col.unique:
                indexed_cols.add(col.name)
        
        return indexed_cols
    
    def _detect_table_renames(self, dropped_tables: Dict[str, Entity], 
                             created_tables: Dict[str, Entity]) -> Dict[str, str]:
        """
        检测表重命名（启发式算法）
        
        如果一个表被删除，另一个表被创建，且列结构相似度>80%，
        则推断为重命名操作
        
        Args:
            dropped_tables: 被删除的表字典 {table_name: entity}
            created_tables: 被创建的表字典 {table_name: entity}
            
        Returns:
            重命名映射 {old_name: new_name}
        """
        rename_mapping = {}
        
        # 对每个被删除的表，找最相似的被创建的表
        for old_name, old_entity in dropped_tables.items():
            best_match = None
            best_similarity = 0.0
            
            for new_name, new_entity in created_tables.items():
                # 如果新表已经被匹配过，跳过
                if new_name in rename_mapping.values():
                    continue
                
                # 计算列结构相似度
                similarity = self._calculate_column_similarity(old_entity, new_entity)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = new_name
            
            # 如果相似度超过阈值（80%），认为是重命名
            if best_match and best_similarity >= 0.8:
                rename_mapping[old_name] = best_match
        
        return rename_mapping
    
    def _calculate_column_similarity(self, entity1: Entity, entity2: Entity) -> float:
        """
        计算两个实体的列结构相似度
        
        Args:
            entity1: 实体1
            entity2: 实体2
            
        Returns:
            相似度（0.0-1.0）
        """
        # 提取列名集合
        cols1 = {col.name for col in entity1.columns}
        cols2 = {col.name for col in entity2.columns}
        
        # 如果任一实体没有列，返回0
        if not cols1 or not cols2:
            return 0.0
        
        # 计算交集和并集
        intersection = cols1 & cols2
        union = cols1 | cols2
        
        # Jaccard相似度
        return len(intersection) / len(union)
    
    def _diff_relationships(self, old_model: ERModel, new_model: ERModel) -> List[Operation]:
        """
        检测关系（外键）的变更
        
        Args:
            old_model: 旧模型
            new_model: 新模型
            
        Returns:
            操作列表
        """
        operations = []
        
        # 转换关系为外键
        old_fks = self._extract_foreign_keys(old_model)
        new_fks = self._extract_foreign_keys(new_model)
        
        # 检测新增的外键
        for fk_key, fk_def in new_fks.items():
            if fk_key not in old_fks:
                from .models import AddForeignKey
                operations.append(AddForeignKey(
                    table_name=fk_def.table_name,
                    foreign_key=fk_def.fk
                ))
        
        # TODO: 检测删除的外键
        # for fk_key in old_fks:
        #     if fk_key not in new_fks:
        #         operations.append(RemoveForeignKey(...))
        
        return operations
    
    def _extract_foreign_keys(self, model: ERModel) -> Dict[str, Any]:
        """
        从模型中提取外键信息
        
        Args:
            model: ER模型
            
        Returns:
            外键字典，key为(table_name, column_name)
        """
        from dataclasses import dataclass
        from .models import ForeignKeyDefinition
        
        @dataclass
        class FKInfo:
            table_name: str
            fk: ForeignKeyDefinition
        
        fks = {}
        
        for rel in model.relationships:
            # 转换关系为外键
            fk = self.converter.convert_relationship(rel)
            
            # 根据关系类型确定外键所在的表
            if rel.relation_type == "one-to-many":
                # 外键在right_entity (many side)
                fk_table = rel.right_entity
            elif rel.relation_type == "many-to-one":
                # 外键在left_entity (many side)
                fk_table = rel.left_entity
            elif rel.relation_type == "one-to-one":
                # 外键在有FK列的一侧
                if rel.right_column:
                    fk_table = rel.right_entity
                elif rel.left_column:
                    fk_table = rel.left_entity
                else:
                    # 默认：外键在left_entity
                    fk_table = rel.left_entity
            else:  # many-to-many
                # 默认：外键在left_entity
                fk_table = rel.left_entity
            
            table_name = self.converter._to_snake_case(fk_table)
            
            # 使用(table_name, column_name)作为key
            fk_key = (table_name, fk.column_name)
            fks[fk_key] = FKInfo(table_name=table_name, fk=fk)
        
        return fks
