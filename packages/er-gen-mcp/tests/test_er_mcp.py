"""
Unit tests for MCP server implementation.
"""
import pytest
import json
import os
from x007007007.er_mcp.server import ERMCPServer, create_mcp_server
from x007007007.er.models import ERModel, Entity, Column, Relationship


def get_asset_path(case_name: str, filename: str) -> str:
    """Get path to asset file."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(assets_dir, case_name, filename)


class TestERMCPServer:
    """Test cases for ERMCPServer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = create_mcp_server()
    
    def test_initialize(self):
        """Test initialize request."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response["result"]
        assert "serverInfo" in response["result"]
        assert response["result"]["serverInfo"]["name"] == "er-diagram-converter"
    
    def test_tools_list(self):
        """Test tools/list request."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "tools" in response["result"]
        
        tools = response["result"]["tools"]
        assert len(tools) == 4
        
        tool_names = [tool["name"] for tool in tools]
        assert "convert_er_diagram" in tool_names
        assert "parse_er_diagram" in tool_names
        assert "render_er_model" in tool_names
        assert "validate_er_model" in tool_names
    
    def test_convert_er_diagram_mermaid_to_django(self):
        """Test convert_er_diagram tool with Mermaid input and Django output."""
        mermaid_content = """erDiagram
    USER {
        int id PK
        string name "User Name"
        string email
    }
    POST {
        int id PK
        string title
        int user_id FK
    }
    USER ||--o{ POST : writes"""
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": mermaid_content,
                    "input_type": "mermaid",
                    "output_format": "django",
                    "app_label": "testapp"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) == 1
        assert response["result"]["content"][0]["type"] == "text"
        
        result_text = response["result"]["content"][0]["text"]
        assert "from django.db import models" in result_text
        assert "class USER" in result_text or "class User" in result_text
        assert "class POST" in result_text or "class Post" in result_text
        assert "testapp" in result_text
    
    def test_convert_er_diagram_plantuml_to_sqlalchemy(self):
        """Test convert_er_diagram tool with PlantUML input and SQLAlchemy output."""
        plantuml_content = """@startuml
entity User {
    * id : int
    username : string
    email : string
}
@enduml"""
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": plantuml_content,
                    "input_type": "plantuml",
                    "output_format": "sqlalchemy"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        assert "from sqlalchemy" in result_text
        assert "class User" in result_text
    
    def test_convert_er_diagram_file_path(self):
        """Test convert_er_diagram with file path."""
        mermaid_file = get_asset_path("simple", "input.mermaid")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": mermaid_file,
                    "input_type": "mermaid",
                    "output_format": "django"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "content" in response["result"]
    
    def test_parse_er_diagram(self):
        """Test parse_er_diagram tool."""
        mermaid_content = """erDiagram
    USER {
        int id PK
        string name
    }"""
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "parse_er_diagram",
                "arguments": {
                    "content": mermaid_content,
                    "input_type": "mermaid"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        model_dict = json.loads(result_text)
        
        assert "entities" in model_dict
        assert "USER" in model_dict["entities"]
        assert "columns" in model_dict["entities"]["USER"]
        assert len(model_dict["entities"]["USER"]["columns"]) == 2
    
    def test_render_er_model(self):
        """Test render_er_model tool."""
        model_json = json.dumps({
            "entities": {
                "USER": {
                    "name": "USER",
                    "columns": [
                        {"name": "id", "type": "int", "is_pk": True},
                        {"name": "name", "type": "string"}
                    ],
                    "comment": None,
                    "extends": [],
                    "export_path": None
                }
            },
            "relationships": []
        })
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "render_er_model",
                "arguments": {
                    "model_json": model_json,
                    "output_format": "django",
                    "app_label": "testapp"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        assert "from django.db import models" in result_text
        assert "class USER" in result_text or "class User" in result_text
    
    def test_validate_er_model_valid(self):
        """Test validate_er_model with valid model."""
        model_json = json.dumps({
            "entities": {
                "USER": {
                    "name": "USER",
                    "columns": [
                        {"name": "id", "type": "int", "is_pk": True}
                    ],
                    "comment": None,
                    "extends": [],
                    "export_path": None
                }
            },
            "relationships": []
        })
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "validate_er_model",
                "arguments": {
                    "model_json": model_json
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        validation_result = json.loads(result_text)
        
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_validate_er_model_invalid_relationship(self):
        """Test validate_er_model with invalid relationship."""
        model_json = json.dumps({
            "entities": {
                "USER": {
                    "name": "USER",
                    "columns": [],
                    "comment": None,
                    "extends": [],
                    "export_path": None
                }
            },
            "relationships": [
                {
                    "left_entity": "USER",
                    "right_entity": "POST",
                    "relation_type": "one-to-many"
                }
            ]
        })
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "validate_er_model",
                "arguments": {
                    "model_json": model_json
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        validation_result = json.loads(result_text)
        
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_invalid_method(self):
        """Test handling of invalid method."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invalid_method",
            "params": {}
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32601
    
    def test_invalid_tool(self):
        """Test handling of invalid tool name."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "invalid_tool",
                "arguments": {}
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        # ValueError returns -32602 (Invalid params), not -32603 (Internal error)
        assert response["error"]["code"] in (-32602, -32603)
    
    def test_convert_er_diagram_invalid_input_type(self):
        """Test convert_er_diagram with invalid input type."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": "test",
                    "input_type": "invalid_type"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
    
    def test_convert_er_diagram_empty_content(self):
        """Test convert_er_diagram with empty content."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": ""
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
    
    def test_parse_er_diagram_invalid_json(self):
        """Test parse_er_diagram with invalid JSON in model."""
        # This should not happen for parse_er_diagram, but test error handling
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "parse_er_diagram",
                "arguments": {
                    "content": "",
                    "input_type": "mermaid"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
    
    def test_validate_er_model_invalid_json(self):
        """Test validate_er_model with invalid JSON."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "validate_er_model",
                "arguments": {
                    "model_json": "invalid json"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        validation_result = json.loads(result_text)
        
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_ping(self):
        """Test ping method."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "ping",
            "params": {}
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"] == "pong"
    
    def test_convert_mermaid_to_plantuml(self):
        """Test format conversion from Mermaid to PlantUML."""
        mermaid_content = """erDiagram
    USER {
        int id PK
        string name
    }"""
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": mermaid_content,
                    "input_type": "mermaid",
                    "output_format": "plantuml"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        assert "@startuml" in result_text
        assert "entity USER" in result_text
    
    def test_convert_plantuml_to_mermaid(self):
        """Test format conversion from PlantUML to Mermaid."""
        plantuml_content = """@startuml
entity User {
    * id : int
    name : string
}
@enduml"""
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_er_diagram",
                "arguments": {
                    "content": plantuml_content,
                    "input_type": "plantuml",
                    "output_format": "mermaid"
                }
            }
        }
        
        response = self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        
        result_text = response["result"]["content"][0]["text"]
        assert "erDiagram" in result_text
        assert "USER" in result_text or "User" in result_text

