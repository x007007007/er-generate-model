"""
TOML Writer for namespace-driven model export

Outputs TOML files in the new format per toml-format-spec.md:
- [config] section with namespace, base_package, extends_aliases
- [[entities.X.columns]] array-table syntax
- primary_key instead of is_pk
- No is_fk output
- No template export_path output
"""

import datetime
import os
import tempfile
from typing import Dict, List, Optional

from x007007007.er.namespace_models import (
    EntityDefinition,
    TemplateDefinition,
    ColumnDefinition,
)


def _toml_escape_string(s: str) -> str:
    return (
        s
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('\n', '\\n')
        .replace('\r', '\\r')
        .replace('\t', '\\t')
    )


def _format_value(val) -> str:
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return str(val)
    if isinstance(val, str):
        return f'"{_toml_escape_string(val)}"'
    if isinstance(val, datetime.timedelta):
        return f'"{val}"'
    raise ValueError(f"Unsupported TOML value type: {type(val)}")


def _serialize_toml_new_format(data: Dict, config: Optional[Dict] = None) -> str:
    lines = []
    
    if config:
        lines.append("[config]")
        if config.get('namespace'):
            lines.append(f'namespace = "{_toml_escape_string(config["namespace"])}"')
        if config.get('base_package'):
            lines.append(f'base_package = "{_toml_escape_string(config["base_package"])}"')
        aliases = config.get('extends_aliases', {})
        if aliases:
            lines.append("")
            for alias_name, alias_path in aliases.items():
                lines.append(f'[config.extends_aliases]')
                lines.append(f'{alias_name} = "{_toml_escape_string(alias_path)}"')
        lines.append("")
    
    templates = data.get('templates', {})
    for tmpl_name, tmpl_data in templates.items():
        lines.append(f"[templates.{tmpl_name}]")
        if tmpl_data.get('comment'):
            lines.append(f'comment = "{_toml_escape_string(tmpl_data["comment"])}"')
        if tmpl_data.get('package'):
            lines.append(f'package = "{_toml_escape_string(tmpl_data["package"])}"')
        lines.append("")
        
        for col in tmpl_data.get('columns', []):
            lines.append(f"[[templates.{tmpl_name}.columns]]")
            _write_column(lines, col)
            lines.append("")
    
    entities = data.get('entities', {})
    for ent_name, ent_data in entities.items():
        lines.append(f"[entities.{ent_name}]")
        
        if ent_data.get('extends'):
            extends = ent_data['extends']
            extends_str = ', '.join(f'"{_toml_escape_string(e)}"' for e in extends)
            lines.append(f'extends = [{extends_str}]')
        
        if ent_data.get('table_name'):
            lines.append(f'table_name = "{_toml_escape_string(ent_data["table_name"])}"')
        
        if ent_data.get('package'):
            lines.append(f'package = "{_toml_escape_string(ent_data["package"])}"')
        
        if ent_data.get('comment'):
            lines.append(f'comment = "{_toml_escape_string(ent_data["comment"])}"')
        
        lines.append("")
        
        for col in ent_data.get('columns', []):
            lines.append(f"[[entities.{ent_name}.columns]]")
            _write_column(lines, col)
            lines.append("")
    
    relationships = data.get('relationships', [])
    for rel in relationships:
        lines.append("[[relationships]]")
        lines.append(f'left = "{_toml_escape_string(rel["left"])}"')
        lines.append(f'right = "{_toml_escape_string(rel["right"])}"')
        lines.append(f'type = "{_toml_escape_string(rel["type"])}"')
        if rel.get('left_column'):
            lines.append(f'left_column = "{_toml_escape_string(rel["left_column"])}"')
        if rel.get('right_column'):
            lines.append(f'right_column = "{_toml_escape_string(rel["right_column"])}"')
        lines.append("")
    
    enums = data.get('enums', {})
    for enum_name, enum_values in enums.items():
        lines.append(f'[enums.{enum_name}]')
        for val, label in enum_values.items():
            lines.append(f'{_toml_escape_string(val)} = "{_toml_escape_string(label)}"')
        lines.append("")
    
    return '\n'.join(lines)


def _write_column(lines: list, col: dict) -> None:
    lines.append(f'name = "{_toml_escape_string(col["name"])}"')
    lines.append(f'type = "{_toml_escape_string(col["type"])}"')
    
    if col.get('primary_key'):
        lines.append('primary_key = true')
    
    if 'db_column' in col:
        lines.append(f'db_column = "{_toml_escape_string(col["db_column"])}"')
    
    if 'nullable' in col and not col['nullable']:
        lines.append('nullable = false')
    
    if 'unique' in col and col['unique']:
        lines.append('unique = true')
    
    if 'default' in col and col['default'] is not None:
        lines.append(f'default = {_format_value(col["default"])}')
    
    if 'max_length' in col and col['max_length'] is not None:
        lines.append(f'max_length = {col["max_length"]}')
    
    if 'precision' in col and col['precision'] is not None:
        lines.append(f'precision = {col["precision"]}')
    
    if 'scale' in col and col['scale'] is not None:
        lines.append(f'scale = {col["scale"]}')
    
    if col.get('comment'):
        lines.append(f'comment = "{_toml_escape_string(col["comment"])}"')
    
    if col.get('enum'):
        lines.append(f'enum = "{_toml_escape_string(col["enum"])}"')


class TOMLWriter:
    """TOML 写入器（新格式）
    
    输出符合 toml-format-spec.md 的 TOML 文件格式：
    - 包含 [config] 段
    - 使用 [[entities.X.columns]] 数组表语法
    - 使用 primary_key 替代 is_pk
    - 不输出 is_fk
    - 不输出模板 export_path
    """
    
    def __init__(self, base_dir: str, namespace: Optional[str] = None,
                 base_package: Optional[str] = None,
                 extends_aliases: Optional[Dict[str, str]] = None):
        self.base_dir = base_dir
        self.namespace = namespace
        self.base_package = base_package
        self.extends_aliases = extends_aliases or {}
        self._file_cache: Dict[str, Dict] = {}
        self._config_cache: Dict[str, Dict] = {}
    
    def _get_file_path(self, namespace: str) -> str:
        relative_path = namespace.replace('.', os.sep) + '.toml'
        file_path = os.path.join(self.base_dir, relative_path)
        return file_path
    
    def _ensure_directory(self, file_path: str) -> None:
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, mode=0o755, exist_ok=True)
    
    def _read_existing_file(self, file_path: str) -> Dict:
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        
        if os.path.exists(file_path):
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                self._file_cache[file_path] = data
                return data
        
        empty_data = {}
        self._file_cache[file_path] = empty_data
        return empty_data
    
    def _write_file_atomically(self, file_path: str, content: str) -> None:
        self._ensure_directory(file_path)
        
        directory = os.path.dirname(file_path)
        fd, temp_path = tempfile.mkstemp(
            suffix='.toml.tmp',
            dir=directory if directory else '.'
        )
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            
            os.chmod(temp_path, 0o644)
            os.replace(temp_path, file_path)
            self._file_cache.pop(file_path, None)
            
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    
    def _column_to_dict(self, column: ColumnDefinition) -> Dict:
        col_dict = {
            'name': column.name,
            'type': column.type,
        }
        
        if column.db_column != column.name:
            col_dict['db_column'] = column.db_column
        
        if column.is_pk:
            col_dict['primary_key'] = True
        
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
        
        if column.precision is not None:
            col_dict['precision'] = column.precision
        
        if column.scale is not None:
            col_dict['scale'] = column.scale
        
        if column.enum is not None:
            col_dict['enum'] = column.enum
        
        return col_dict
    
    def _extract_base_package_info(
        self, entities: Dict[str, dict], templates: Dict[str, dict]
    ) -> tuple:
        all_packages = []
        for ent_data in entities.values():
            pkg = ent_data.get('package')
            if pkg:
                all_packages.append(pkg)
        
        if not all_packages:
            return None, {}
        
        parts_list = [pkg.split('.') for pkg in all_packages]
        common_parts = []
        for segments in zip(*parts_list):
            if len(set(segments)) == 1:
                common_parts.append(segments[0])
            else:
                break
        
        base_pkg = '.'.join(common_parts) if common_parts else None
        
        if not base_pkg or '.' not in base_pkg:
            return None, {}
        
        aliases = {}
        all_extends = set()
        for ent_data in entities.values():
            for ext in ent_data.get('extends', []):
                all_extends.add(ext)
        
        for ext in all_extends:
            if '.' in ext:
                short = ext.rsplit('.', 1)[-1]
                if short not in entities and short not in templates:
                    aliases[short] = ext
        
        return base_pkg, aliases
    
    def _compute_relative_packages(
        self, entities: Dict[str, dict], base_pkg: Optional[str]
    ) -> Dict[str, dict]:
        if not base_pkg:
            return entities
        
        prefix = base_pkg + '.'
        result = {}
        for name, ent_data in entities.items():
            new_data = dict(ent_data)
            pkg = ent_data.get('package')
            if pkg and pkg.startswith(prefix):
                relative = pkg[len(prefix):]
                if relative:
                    new_data['package'] = relative
                else:
                    new_data.pop('package', None)
            result[name] = new_data
        return result
    
    def _compute_alias_extends(
        self, entities: Dict[str, dict], aliases: Dict[str, str]
    ) -> Dict[str, dict]:
        if not aliases:
            return entities
        
        reverse = {v: k for k, v in aliases.items()}
        result = {}
        for name, ent_data in entities.items():
            new_data = dict(ent_data)
            extends = ent_data.get('extends', [])
            new_extends = []
            for ext in extends:
                new_extends.append(reverse.get(ext, ext))
            if new_extends:
                new_data['extends'] = new_extends
            result[name] = new_data
        return result
    
    def write_entity(self, namespace: str, entity: EntityDefinition) -> str:
        file_path = self._get_file_path(namespace)
        data = self._read_existing_file(file_path)
        
        if 'entities' not in data:
            data['entities'] = {}
        if 'relationships' not in data:
            data['relationships'] = []
        
        entity_data = {}
        
        if entity.comment:
            entity_data['comment'] = entity.comment
        
        entity_data['table_name'] = entity.table_name
        
        if entity.extends:
            entity_data['extends'] = entity.extends
        
        entity_data['columns'] = [
            self._column_to_dict(col) for col in entity.columns
        ]
        
        if entity.package:
            entity_data['package'] = entity.package
        
        data['entities'][entity.name] = entity_data
        
        self._serialize_and_write(file_path, data, namespace)
        
        return file_path
    
    def write_template(self, namespace: str, template: TemplateDefinition) -> str:
        file_path = self._get_file_path(namespace)
        data = self._read_existing_file(file_path)
        
        if 'templates' not in data:
            data['templates'] = {}
        
        template_data = {}
        
        if template.comment:
            template_data['comment'] = template.comment
        
        if template.package:
            template_data['package'] = template.package
        
        template_data['columns'] = [
            self._column_to_dict(col) for col in template.columns
        ]
        
        data['templates'][template.name] = template_data
        
        self._serialize_and_write(file_path, data, namespace)
        
        return file_path
    
    def _serialize_and_write(self, file_path: str, data: Dict, namespace: str) -> None:
        base_pkg, aliases = self._extract_base_package_info(
            data.get('entities', {}), data.get('templates', {})
        )
        
        config = {
            'namespace': namespace,
            'base_package': base_pkg,
            'extends_aliases': aliases,
        }
        
        entities = data.get('entities', {})
        entities = self._compute_relative_packages(entities, base_pkg)
        entities = self._compute_alias_extends(entities, aliases)
        
        output_data = {
            'templates': data.get('templates', {}),
            'entities': entities,
            'relationships': data.get('relationships', []),
        }
        
        content = _serialize_toml_new_format(output_data, config)
        self._write_file_atomically(file_path, content)
