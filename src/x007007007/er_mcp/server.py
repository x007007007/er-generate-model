"""
MCP Server implementation for ER Diagram Converter.

This server exposes the following tools:
- convert_er_diagram: Convert ER diagrams between formats
- parse_er_diagram: Parse ER diagram from various formats
- render_er_model: Render ER model to code (Django/SQLAlchemy)
- validate_er_model: Validate ER model
"""

import json
import sys
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.db_parser import DBParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer
from x007007007.er.converters import MermaidConverter, PlantUMLConverter
from x007007007.er.models import ERModel

logger = logging.getLogger(__name__)


class ERMCPServer:
    """MCP Server for ER Diagram Converter."""
    
    def __init__(self):
        self.server_info = {
            "name": "er-diagram-converter",
            "version": "0.1.0"
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.debug(f"Handling request: method={method}, id={request_id}")
        
        try:
            if method == "initialize":
                logger.debug("Processing initialize request")
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                logger.debug("Processing tools/list request")
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                tool_name = params.get("name", "unknown")
                logger.debug(f"Processing tools/call request for tool: {tool_name}")
                return self._handle_tool_call(request_id, params)
            elif method == "ping":
                logger.debug("Processing ping request")
                return {"jsonrpc": "2.0", "id": request_id, "result": "pong"}
            else:
                logger.warning(f"Unknown method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as e:
            logger.exception(f"Error handling request: method={method}, id={request_id}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                    "data": {
                        "type": type(e).__name__,
                        "method": method
                    }
                }
            }
    
    def _handle_initialize(self, request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": self.server_info
            }
        }
    
    def _handle_tools_list(self, request_id: Optional[str]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "convert_er_diagram",
                        "description": "Convert ER diagram between different formats (Mermaid, PlantUML, Django, SQLAlchemy)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "ER diagram content or file path"
                                },
                                "input_type": {
                                    "type": "string",
                                    "enum": ["mermaid", "plantuml", "toml", "db"],
                                    "description": "Input format type",
                                    "default": "mermaid"
                                },
                                "output_format": {
                                    "type": "string",
                                    "enum": ["django", "sqlalchemy", "mermaid", "plantuml"],
                                    "description": "Output format",
                                    "default": "django"
                                },
                                "app_label": {
                                    "type": "string",
                                    "description": "Django app label (for Django output)"
                                },
                                "table_prefix": {
                                    "type": "string",
                                    "description": "Table name prefix"
                                }
                            },
                            "required": ["content"]
                        }
                    },
                    {
                        "name": "parse_er_diagram",
                        "description": "Parse ER diagram from various formats and return the model structure",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "ER diagram content or file path"
                                },
                                "input_type": {
                                    "type": "string",
                                    "enum": ["mermaid", "plantuml", "toml", "db"],
                                    "description": "Input format type",
                                    "default": "mermaid"
                                }
                            },
                            "required": ["content"]
                        }
                    },
                    {
                        "name": "render_er_model",
                        "description": "Render ER model to code (Django or SQLAlchemy)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model_json": {
                                    "type": "string",
                                    "description": "ER model as JSON string"
                                },
                                "output_format": {
                                    "type": "string",
                                    "enum": ["django", "sqlalchemy"],
                                    "description": "Output format",
                                    "default": "django"
                                },
                                "app_label": {
                                    "type": "string",
                                    "description": "Django app label (for Django output)"
                                },
                                "table_prefix": {
                                    "type": "string",
                                    "description": "Table name prefix"
                                }
                            },
                            "required": ["model_json", "output_format"]
                        }
                    },
                    {
                        "name": "validate_er_model",
                        "description": "Validate ER model and return validation errors",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model_json": {
                                    "type": "string",
                                    "description": "ER model as JSON string"
                                }
                            },
                            "required": ["model_json"]
                        }
                    }
                ]
            }
        }
    
    def _handle_tool_call(self, request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.debug(f"Executing tool: {tool_name} with arguments: {list(arguments.keys())}")
        
        try:
            if tool_name == "convert_er_diagram":
                logger.debug("Calling _convert_er_diagram")
                result = self._convert_er_diagram(arguments)
            elif tool_name == "parse_er_diagram":
                logger.debug("Calling _parse_er_diagram")
                result = self._parse_er_diagram(arguments)
            elif tool_name == "render_er_model":
                logger.debug("Calling _render_er_model")
                result = self._render_er_model(arguments)
            elif tool_name == "validate_er_model":
                logger.debug("Calling _validate_er_model")
                result = self._validate_er_model(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            logger.debug(f"Tool {tool_name} executed successfully, result length: {len(result)}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        except AssertionError as e:
            logger.warning(f"Assertion error in tool {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Invalid parameters: {str(e)}"
                }
            }
        except ValueError as e:
            logger.warning(f"Value error in tool {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Invalid value: {str(e)}"
                }
            }
        except FileNotFoundError as e:
            logger.error(f"File not found in tool {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"File not found: {str(e)}"
                }
            }
        except Exception as e:
            logger.exception(f"Error executing tool: {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}",
                    "data": {
                        "type": type(e).__name__,
                        "tool": tool_name
                    }
                }
            }
    
    def _convert_er_diagram(self, args: Dict[str, Any]) -> str:
        """Convert ER diagram between formats."""
        content = args.get("content", "")
        input_type = args.get("input_type", "mermaid")
        output_format = args.get("output_format", "django")
        app_label = args.get("app_label")
        table_prefix = args.get("table_prefix", "")
        
        assert isinstance(content, str), "content must be a string"
        assert len(content) > 0, "content cannot be empty"
        
        # Check if content is a file path
        if Path(content).exists() and Path(content).is_file():
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Parse input
        if input_type == "db":
            parser = DBParser()
            model = parser.parse(content)
        else:
            if input_type == "mermaid":
                parser = MermaidAntlrParser()
            elif input_type == "plantuml":
                parser = PlantUMLAntlrParser()
            elif input_type == "toml":
                parser = TomlERParser()
            else:
                raise ValueError(f"Unknown input type: {input_type}")
            
            model = parser.parse(content)
        
        # Render or convert output
        if output_format == "django":
            if app_label is None:
                app_label = "app"
            renderer = DjangoRenderer(app_label=app_label, table_prefix=table_prefix)
            result = renderer.render(model)
        elif output_format == "sqlalchemy":
            renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
            result = renderer.render(model)
        elif output_format == "mermaid":
            converter = MermaidConverter()
            result = converter.convert(model)
        elif output_format == "plantuml":
            converter = PlantUMLConverter()
            result = converter.convert(model)
        else:
            raise ValueError(f"Unknown output format: {output_format}")
        
        return result
    
    def _parse_er_diagram(self, args: Dict[str, Any]) -> str:
        """Parse ER diagram and return model structure."""
        content = args.get("content", "")
        input_type = args.get("input_type", "mermaid")
        
        assert isinstance(content, str), "content must be a string"
        assert len(content) > 0, "content cannot be empty"
        
        # Check if content is a file path
        if Path(content).exists() and Path(content).is_file():
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Parse input
        if input_type == "db":
            parser = DBParser()
            model = parser.parse(content)
        else:
            if input_type == "mermaid":
                parser = MermaidAntlrParser()
            elif input_type == "plantuml":
                parser = PlantUMLAntlrParser()
            elif input_type == "toml":
                parser = TomlERParser()
            else:
                raise ValueError(f"Unknown input type: {input_type}")
            
            model = parser.parse(content)
        
        # Convert model to JSON
        model_dict = {
            "entities": {
                name: {
                    "name": entity.name,
                    "columns": [
                        {
                            "name": col.name,
                            "type": col.type,
                            "is_pk": col.is_pk,
                            "is_fk": col.is_fk,
                            "nullable": col.nullable,
                            "comment": col.comment,
                            "default": col.default,
                            "max_length": col.max_length,
                            "precision": col.precision,
                            "scale": col.scale,
                            "unique": col.unique,
                            "indexed": col.indexed
                        }
                        for col in entity.columns
                    ],
                    "comment": entity.comment,
                    "extends": entity.extends,
                    "export_path": entity.export_path
                }
                for name, entity in model.entities.items()
            },
            "relationships": [
                {
                    "left_entity": rel.left_entity,
                    "right_entity": rel.right_entity,
                    "relation_type": rel.relation_type,
                    "left_label": rel.left_label,
                    "right_label": rel.right_label,
                    "left_column": rel.left_column,
                    "right_column": rel.right_column,
                    "left_cardinality": rel.left_cardinality,
                    "right_cardinality": rel.right_cardinality
                }
                for rel in model.relationships
            ]
        }
        
        return json.dumps(model_dict, indent=2, ensure_ascii=False)
    
    def _render_er_model(self, args: Dict[str, Any]) -> str:
        """Render ER model to code."""
        model_json = args.get("model_json", "")
        output_format = args.get("output_format", "django")
        app_label = args.get("app_label", "app")
        table_prefix = args.get("table_prefix", "")
        
        assert isinstance(model_json, str), "model_json must be a string"
        assert len(model_json) > 0, "model_json cannot be empty"
        
        # Parse model from JSON
        try:
            model_dict = json.loads(model_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Reconstruct ERModel from JSON
        from x007007007.er.models import Entity, Column, Relationship
        
        model = ERModel()
        
        # Reconstruct entities
        for name, entity_data in model_dict.get("entities", {}).items():
            columns = [
                Column(
                    name=col_data.get("name", ""),
                    type=col_data.get("type", "string"),
                    is_pk=col_data.get("is_pk", False),
                    is_fk=col_data.get("is_fk", False),
                    nullable=col_data.get("nullable", True),
                    comment=col_data.get("comment"),
                    default=col_data.get("default"),
                    max_length=col_data.get("max_length"),
                    precision=col_data.get("precision"),
                    scale=col_data.get("scale"),
                    unique=col_data.get("unique", False),
                    indexed=col_data.get("indexed", False)
                )
                for col_data in entity_data.get("columns", [])
            ]
            entity = Entity(
                name=entity_data.get("name", name),
                columns=columns,
                comment=entity_data.get("comment"),
                extends=entity_data.get("extends", []),
                export_path=entity_data.get("export_path")
            )
            model.add_entity(entity)
        
        # Reconstruct relationships
        for rel_data in model_dict.get("relationships", []):
            rel = Relationship(
                left_entity=rel_data.get("left_entity", ""),
                right_entity=rel_data.get("right_entity", ""),
                relation_type=rel_data.get("relation_type", "one-to-many"),
                left_label=rel_data.get("left_label"),
                right_label=rel_data.get("right_label"),
                left_column=rel_data.get("left_column"),
                right_column=rel_data.get("right_column"),
                left_cardinality=rel_data.get("left_cardinality"),
                right_cardinality=rel_data.get("right_cardinality")
            )
            model.add_relationship(rel)
        
        # Render
        if output_format == "django":
            renderer = DjangoRenderer(app_label=app_label, table_prefix=table_prefix)
            result = renderer.render(model)
        elif output_format == "sqlalchemy":
            renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
            result = renderer.render(model)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        return result
    
    def _validate_er_model(self, args: Dict[str, Any]) -> str:
        """Validate ER model."""
        model_json = args.get("model_json", "")
        
        assert isinstance(model_json, str), "model_json must be a string"
        assert len(model_json) > 0, "model_json cannot be empty"
        
        # Parse model from JSON (reuse _render_er_model logic)
        try:
            model_dict = json.loads(model_json)
        except json.JSONDecodeError as e:
            return json.dumps({
                "valid": False,
                "errors": [f"Invalid JSON format: {str(e)}"]
            }, indent=2)
        
        # Reconstruct ERModel from JSON
        from x007007007.er.models import Entity, Column, Relationship
        
        model = ERModel()
        errors = []
        
        try:
            # Reconstruct entities
            for name, entity_data in model_dict.get("entities", {}).items():
                columns = [
                    Column(
                        name=col_data.get("name", ""),
                        type=col_data.get("type", "string"),
                        is_pk=col_data.get("is_pk", False),
                        is_fk=col_data.get("is_fk", False),
                        nullable=col_data.get("nullable", True),
                        comment=col_data.get("comment"),
                        default=col_data.get("default"),
                        max_length=col_data.get("max_length"),
                        precision=col_data.get("precision"),
                        scale=col_data.get("scale"),
                        unique=col_data.get("unique", False),
                        indexed=col_data.get("indexed", False)
                    )
                    for col_data in entity_data.get("columns", [])
                ]
                entity = Entity(
                    name=entity_data.get("name", name),
                    columns=columns,
                    comment=entity_data.get("comment"),
                    extends=entity_data.get("extends", []),
                    export_path=entity_data.get("export_path")
                )
                model.add_entity(entity)
            
            # Reconstruct relationships
            for rel_data in model_dict.get("relationships", []):
                rel = Relationship(
                    left_entity=rel_data.get("left_entity", ""),
                    right_entity=rel_data.get("right_entity", ""),
                    relation_type=rel_data.get("relation_type", "one-to-many"),
                    left_label=rel_data.get("left_label"),
                    right_label=rel_data.get("right_label"),
                    left_column=rel_data.get("left_column"),
                    right_column=rel_data.get("right_column"),
                    left_cardinality=rel_data.get("left_cardinality"),
                    right_cardinality=rel_data.get("right_cardinality")
                )
                model.add_relationship(rel)
            
            # Validate model
            validation_errors = model.validate()
            
            return json.dumps({
                "valid": len(validation_errors) == 0,
                "errors": validation_errors
            }, indent=2)
        except Exception as e:
            errors.append(f"Error reconstructing model: {str(e)}")
            return json.dumps({
                "valid": False,
                "errors": errors
            }, indent=2)


def create_mcp_server() -> ERMCPServer:
    """Create and return MCP server instance."""
    return ERMCPServer()


def main():
    """Main entry point for MCP server (stdio mode)."""
    import sys
    import os
    
    # Configure logging based on environment variable
    log_level = os.environ.get("MCP_LOG_LEVEL", "INFO").upper()
    log_format = os.environ.get(
        "MCP_LOG_FORMAT",
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable debug logging if MCP_DEBUG is set
    if os.environ.get("MCP_DEBUG", "").lower() in ("1", "true", "yes"):
        log_level = "DEBUG"
        log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    
    # Log to stderr so stdout is only used for JSON-RPC communication
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        stream=sys.stderr,
        force=True
    )
    
    logger.info("MCP Server starting...")
    logger.debug(f"Log level: {log_level}")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    server = create_mcp_server()
    
    # Read from stdin, write to stdout (stdio transport)
    logger.info("MCP Server ready, waiting for requests...")
    for line_num, line in enumerate(sys.stdin, 1):
        try:
            line = line.strip()
            if not line:
                continue
                
            logger.debug(f"Received request (line {line_num}): {line[:200]}...")
            
            request = json.loads(line)
            request_id = request.get("id", "unknown")
            method = request.get("method", "unknown")
            
            logger.debug(f"Processing request ID={request_id}, method={method}")
            
            response = server.handle_request(request)
            
            logger.debug(f"Sending response ID={response.get('id', 'unknown')}")
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON on line {line_num}: {str(e)}")
            logger.debug(f"Problematic line: {line[:200]}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            break
        except Exception as e:
            logger.exception(f"Unexpected error processing request on line {line_num}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                    "data": {
                        "type": type(e).__name__,
                        "traceback": str(e)
                    }
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()

