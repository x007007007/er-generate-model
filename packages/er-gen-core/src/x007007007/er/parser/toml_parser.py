"""
TOML格式ER图解析器，支持继承和模板功能。

支持新旧两种TOML格式：
- 新格式：包含 [config] 段，使用 primary_key，数组表 [[entities.X.columns]]
- 旧格式：无 [config] 段，使用 is_pk，行内 columns = [{...}]
"""
import warnings
import toml
from typing import Dict, List, Optional, Any
from x007007007.er.base import Parser
from x007007007.er.models import ERModel, Entity, Column, Relationship


class TomlERParser(Parser):
    """
    TOML格式ER图解析器。
    
    支持特性：
    - [config] 段：namespace、base_package、extends_aliases
    - 实体模板（templates）：可复用的字段集合
    - 实体继承（extends）：支持别名解析（aliases → templates/entities → 完整路径）
    - 字段覆盖：继承的字段可以被覆盖，后面的模板覆盖前面的
    - 继承模式：支持reference和flatten两种模式
    - 向后兼容：支持旧格式（is_pk、行内columns、无config段）
    """
    
    def __init__(self, inheritance_mode: str = 'reference'):
        if inheritance_mode not in ('reference', 'flatten'):
            raise ValueError(f"Invalid inheritance_mode: {inheritance_mode}. Must be 'reference' or 'flatten'")
        self.inheritance_mode = inheritance_mode
    
    def parse(self, content: str) -> ERModel:
        assert isinstance(content, str), "content must be a string"
        assert len(content) > 0, "content cannot be empty"
        
        try:
            data = toml.loads(content)
        except toml.TomlDecodeError as e:
            raise ValueError(f"Invalid TOML format: {e}") from e
        
        model = ERModel()
        
        config = self._parse_config(data.get('config', {}))
        model.namespace = config.get('namespace')
        model.base_package = config.get('base_package')
        model.extends_aliases = config.get('extends_aliases', {})
        
        templates = self._parse_templates(data.get('templates', {}))
        model.templates = templates
        
        relationships = self._parse_relationships(data.get('relationships', []))
        
        entities = self._parse_entities(
            data.get('entities', {}), templates, config
        )
        
        self._mark_foreign_keys(entities, relationships)
        
        for entity in entities.values():
            model.add_entity(entity)
        
        for rel in relationships:
            model.add_relationship(rel)
        
        enums_data = data.get('enums', {})
        if enums_data and isinstance(enums_data, dict):
            model.enums = enums_data
        
        return model
    
    def _parse_config(self, config_data: Any) -> Dict[str, Any]:
        if not config_data or not isinstance(config_data, dict):
            return {}
        
        config = {
            'namespace': config_data.get('namespace'),
            'base_package': config_data.get('base_package'),
            'extends_aliases': dict(config_data.get('extends_aliases', {})),
        }
        
        return config
    
    def _resolve_extends(
        self, extends_list: List[str], templates: Dict[str, Dict[str, Any]],
        entities_data: Dict[str, Any], config: Dict[str, Any]
    ) -> List[str]:
        aliases = config.get('extends_aliases', {})
        resolved = []
        for name in extends_list:
            if name in aliases:
                resolved.append(aliases[name])
            elif name in templates:
                resolved.append(name)
            elif name in entities_data:
                resolved.append(name)
            else:
                resolved.append(name)
        return resolved
    
    def _resolve_package(
        self, entity_package: Optional[str], config: Dict[str, Any]
    ) -> Optional[str]:
        base_package = config.get('base_package')
        if not base_package:
            return entity_package
        if entity_package:
            return f"{base_package}.{entity_package}"
        return base_package
    
    def _parse_templates(self, templates_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        templates = {}
        for template_name, template_data in templates_data.items():
            assert isinstance(template_data, dict), f"Template '{template_name}' must be a dictionary"
            
            columns = self._parse_columns_list(template_data, template_name)
            
            templates[template_name] = {
                'columns': columns,
                'export_path': template_data.get('export_path'),
                'package': template_data.get('package'),
                'comment': template_data.get('comment')
            }
        
        return templates
    
    def _parse_columns_list(
        self, parent_data: Dict[str, Any], parent_name: str
    ) -> List[Column]:
        columns = []
        
        if 'columns' not in parent_data:
            return columns
        
        columns_data = parent_data['columns']
        
        if isinstance(columns_data, list):
            for col_data in columns_data:
                if isinstance(col_data, dict):
                    columns.append(self._parse_column(col_data))
        
        return columns
    
    def _parse_entities(
        self, 
        entities_data: Dict[str, Any], 
        templates: Dict[str, Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Entity]:
        entities = {}
        
        for entity_name, entity_data in entities_data.items():
            assert isinstance(entity_data, dict), f"Entity '{entity_name}' must be a dictionary"
            
            extends = entity_data.get('extends')
            base_columns = []
            extends_list = []
            
            if extends:
                if isinstance(extends, list):
                    extends_list = extends
                else:
                    raise ValueError(f"Entity '{entity_name}.extends' must be an array (list)")
                
                for template_name in extends_list:
                    assert isinstance(template_name, str), f"Template name in extends must be a string"
                    
                    resolved_name = self._resolve_extends(
                        [template_name], templates, entities_data, config
                    )[0]
                    
                    lookup_name = template_name
                    if template_name not in templates and resolved_name != template_name:
                        for tmpl_key in templates:
                            if resolved_name.endswith(tmpl_key):
                                lookup_name = tmpl_key
                                break
                    
                    if lookup_name in templates:
                        template = templates[lookup_name]
                        should_expand = False
                        
                        if self.inheritance_mode == 'flatten':
                            if template.get('columns'):
                                should_expand = True
                        else:
                            if not template.get('export_path'):
                                template['export_path'] = f'mixins.{lookup_name.lower()}'
                                should_expand = True
                        
                        if should_expand:
                            for col in template['columns']:
                                col_copy = Column(**col.__dict__)
                                if self.inheritance_mode == 'flatten':
                                    col_copy._source_template = lookup_name
                                base_columns.append(col_copy)
            
            own_columns = self._parse_columns_list(entity_data, entity_name)
            
            all_columns = {}
            for col in base_columns:
                all_columns[col.name] = col
            
            for col in own_columns:
                all_columns[col.name] = col
            
            table_name = entity_data.get('table_name')
            if table_name is None:
                raise ValueError(
                    f"Entity '{entity_name}' is missing required field 'table_name'. "
                    f"This TOML file was generated with an older version of er_export. "
                    f"Please regenerate it using: python manage.py er_export <app_label> --output-dir=src"
                )
            
            raw_package = entity_data.get('package')
            resolved_package = self._resolve_package(raw_package, config)
            
            entity = Entity(
                name=entity_name,
                columns=list(all_columns.values()),
                comment=entity_data.get('comment'),
                extends=extends_list,
                export_path=entity_data.get('export_path'),
                package=resolved_package,
                table_name=table_name
            )
            
            entities[entity_name] = entity
        
        return entities
    
    def _parse_column(self, col_data: Dict[str, Any]) -> Column:
        assert 'name' in col_data, "Column must have 'name' field"
        assert 'type' in col_data, "Column must have 'type' field"
        
        db_column = col_data.get('db_column', col_data['name'])
        
        return Column(
            name=str(col_data['name']),
            type=str(col_data['type']),
            db_column=str(db_column),
            is_pk=col_data.get('primary_key', col_data.get('is_pk', False)),
            is_fk=col_data.get('is_fk', False),
            nullable=col_data.get('nullable', True),
            comment=col_data.get('comment'),
            default=col_data.get('default'),
            max_length=col_data.get('max_length'),
            precision=col_data.get('precision'),
            scale=col_data.get('scale'),
            unique=col_data.get('unique', False),
            indexed=col_data.get('indexed', False),
            enum=col_data.get('enum'),
        )
    
    def _parse_relationships(self, relationships_data: List[Any]) -> List[Relationship]:
        relationships = []
        
        for rel_data in relationships_data:
            assert isinstance(rel_data, dict), "Relationship must be a dictionary"
            assert 'left' in rel_data, "Relationship must have 'left' field"
            assert 'right' in rel_data, "Relationship must have 'right' field"
            assert 'type' in rel_data, "Relationship must have 'type' field"
            
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
            
            if rel_type in ('1:1', '1:N', 'N:1', 'N:M'):
                warnings.warn(
                    f"Short-form relationship type '{rel_type}' is deprecated, "
                    f"use '{type_mapping[rel_type]}' instead",
                    DeprecationWarning,
                    stacklevel=2
                )
            
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
    
    def _mark_foreign_keys(
            self, 
            entities: Dict[str, Entity], 
            relationships: List[Relationship]
        ) -> None:
            for rel in relationships:
                if rel.relation_type in ['one-to-many', 'one-to-one', 'many-to-one']:
                    if rel.right_entity in entities and rel.right_column:
                        entity = entities[rel.right_entity]
                        ref_type = None
                        if rel.left_entity in entities and rel.left_column:
                            ref_entity = entities[rel.left_entity]
                            for ref_col in ref_entity.columns:
                                if ref_col.name == rel.left_column or ref_col.db_column == rel.left_column:
                                    ref_type = ref_col.type
                                    break

                        for col in entity.columns:
                            if col.name == rel.right_column or col.db_column == rel.right_column:
                                if col.is_pk:
                                    break
                                
                                col.is_fk = True

                                if col.db_column == col.name and not col.name.endswith('_id'):
                                    col.db_column = f"{col.name}_id"

                                if ref_type:
                                    col.type = ref_type
                                break
