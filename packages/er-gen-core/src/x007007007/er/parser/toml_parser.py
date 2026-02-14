"""
TOML格式ER图解析器，支持继承和模板功能。
"""
import toml
from typing import Dict, List, Optional, Any
from x007007007.er.base import Parser
from x007007007.er.models import ERModel, Entity, Column, Relationship


class TomlERParser(Parser):
    """
    TOML格式ER图解析器。
    
    支持特性：
    - 实体模板（templates）：可复用的字段集合，支持export_path配置
    - 实体继承（extends）：实体可以继承多个模板的字段（仅支持数组）
    - 多模板继承：extends必须是数组
    - 字段覆盖：继承的字段可以被覆盖，后面的模板覆盖前面的
    - 导出路径：模板和实体可以配置export_path，用于生成继承代码
    - 格式验证：使用断言进行数据验证
    """
    
    def parse(self, content: str) -> ERModel:
        """
        解析TOML格式的ER图内容。
        
        Args:
            content: TOML格式的字符串内容
            
        Returns:
            ERModel: 解析后的ER模型
            
        Raises:
            ValueError: 如果TOML格式错误或数据验证失败
        """
        assert isinstance(content, str), "content must be a string"
        assert len(content) > 0, "content cannot be empty"
        
        try:
            data = toml.loads(content)
        except toml.TomlDecodeError as e:
            raise ValueError(f"Invalid TOML format: {e}") from e
        
        model = ERModel()
        
        # 解析模板
        templates = self._parse_templates(data.get('templates', {}))
        # 保存模板信息到模型（供渲染器使用）
        model.templates = templates
        
        # 解析实体（支持继承）
        entities = self._parse_entities(data.get('entities', {}), templates)
        for entity in entities.values():
            model.add_entity(entity)
        
        # 解析关系
        relationships = self._parse_relationships(data.get('relationships', []))
        for rel in relationships:
            model.add_relationship(rel)
        
        return model
    
    def _parse_templates(self, templates_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        解析模板定义。
        
        Args:
            templates_data: 模板数据字典
            
        Returns:
            Dict[str, Dict]: 模板名称到模板信息的映射，包含columns和export_path
        """
        templates = {}
        for template_name, template_data in templates_data.items():
            assert isinstance(template_data, dict), f"Template '{template_name}' must be a dictionary"
            columns_data = template_data.get('columns', [])
            assert isinstance(columns_data, list), f"Template '{template_name}.columns' must be a list"
            
            columns = []
            for col_data in columns_data:
                assert isinstance(col_data, dict), f"Column in template '{template_name}' must be a dictionary"
                column = self._parse_column(col_data)
                columns.append(column)
            
            templates[template_name] = {
                'columns': columns,
                'export_path': template_data.get('export_path')
            }
        
        return templates
    
    def _parse_entities(
        self, 
        entities_data: Dict[str, Any], 
        templates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Entity]:
        """
        解析实体定义，支持继承多个模板（仅支持数组）。
        
        Args:
            entities_data: 实体数据字典
            templates: 模板字典（包含columns和export_path）
            
        Returns:
            Dict[str, Entity]: 实体名称到Entity对象的映射
        """
        entities = {}
        
        for entity_name, entity_data in entities_data.items():
            assert isinstance(entity_data, dict), f"Entity '{entity_name}' must be a dictionary"
            
            # 获取继承的模板（仅支持数组）
            extends = entity_data.get('extends')
            base_columns = []
            extends_list = []
            
            if extends:
                # 只支持数组
                if isinstance(extends, list):
                    extends_list = extends
                else:
                    raise ValueError(f"Entity '{entity_name}.extends' must be an array (list)")
                
                # 按顺序合并所有模板的字段
                for template_name in extends_list:
                    assert isinstance(template_name, str), f"Template name in extends must be a string"
                    if template_name not in templates:
                        raise ValueError(f"Entity '{entity_name}' extends unknown template '{template_name}'")
                    # 复制模板字段（深拷贝），按顺序添加
                    for col in templates[template_name]['columns']:
                        base_columns.append(Column(**col.__dict__))
            
            # 解析实体自己的字段
            columns_data = entity_data.get('columns', [])
            assert isinstance(columns_data, list), f"Entity '{entity_name}.columns' must be a list"
            
            # 合并字段：先添加继承的字段，再添加自己的字段
            # 如果字段名重复，后面的会覆盖前面的
            all_columns = {}
            for col in base_columns:
                all_columns[col.name] = col  # 后面的模板会覆盖前面的同名字段
            
            for col_data in columns_data:
                assert isinstance(col_data, dict), f"Column in entity '{entity_name}' must be a dictionary"
                column = self._parse_column(col_data)
                all_columns[column.name] = column  # 实体自己的字段会覆盖继承的字段
            
            entity = Entity(
                name=entity_name,
                columns=list(all_columns.values()),
                comment=entity_data.get('comment'),
                extends=extends_list,  # 保存继承的模板列表
                export_path=entity_data.get('export_path')  # 保存导出路径
            )
            
            entities[entity_name] = entity
        
        return entities
    
    def _parse_column(self, col_data: Dict[str, Any]) -> Column:
        """
        解析单个字段定义。
        
        Args:
            col_data: 字段数据字典
            
        Returns:
            Column: Column对象
        """
        assert 'name' in col_data, "Column must have 'name' field"
        assert 'type' in col_data, "Column must have 'type' field"
        
        return Column(
            name=str(col_data['name']),
            type=str(col_data['type']),
            is_pk=col_data.get('is_pk', False),
            is_fk=col_data.get('is_fk', False),
            nullable=col_data.get('nullable', True),
            comment=col_data.get('comment'),
            default=col_data.get('default'),
            max_length=col_data.get('max_length'),
            precision=col_data.get('precision'),
            scale=col_data.get('scale'),
            unique=col_data.get('unique', False),
            indexed=col_data.get('indexed', False)
        )
    
    def _parse_relationships(self, relationships_data: List[Any]) -> List[Relationship]:
        """
        解析关系定义。
        
        Args:
            relationships_data: 关系数据列表
            
        Returns:
            List[Relationship]: Relationship对象列表
        """
        relationships = []
        
        for rel_data in relationships_data:
            assert isinstance(rel_data, dict), "Relationship must be a dictionary"
            assert 'left' in rel_data, "Relationship must have 'left' field"
            assert 'right' in rel_data, "Relationship must have 'right' field"
            assert 'type' in rel_data, "Relationship must have 'type' field"
            
            # 映射关系类型
            type_mapping = {
                'one-to-one': 'one-to-one',
                'one-to-many': 'one-to-many',
                'many-to-many': 'many-to-many',
                'many-to-one': 'many-to-one',
                '1:1': 'one-to-one',
                '1:N': 'one-to-many',
                'N:1': 'many-to-one',
                'N:M': 'many-to-many',
            }
            
            rel_type = rel_data['type']
            if rel_type not in type_mapping:
                raise ValueError(f"Unknown relationship type: {rel_type}")
            
            relationship = Relationship(
                left_entity=str(rel_data['left']),
                right_entity=str(rel_data['right']),
                relation_type=type_mapping[rel_type],
                left_label=rel_data.get('left_label'),
                right_label=rel_data.get('right_label'),
                left_column=rel_data.get('left_column'),
                right_column=rel_data.get('right_column'),
                left_cardinality=rel_data.get('left_cardinality'),
                right_cardinality=rel_data.get('right_cardinality')
            )
            
            relationships.append(relationship)
        
        return relationships

