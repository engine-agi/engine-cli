"""
Data Contract Validation Tests
Tests for validating JSON/YAML schemas and data contracts between CLI and core components.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml


class CLISchemaValidator:
    """Validator for CLI-specific schemas."""

    @staticmethod
    def validate_cli_config(data: Dict[str, Any]) -> bool:
        """Validate CLI configuration schema."""
        required_keys = [
            "cli",
            "commands",
            "formatting",
            "storage",
            "features",
        ]

        # Check required top-level keys
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        # Validate CLI section
        cli_section = data.get("cli", {})
        cli_required = [
            "colors",
            "interactive",
            "history_size",
            "table_style",
            "progress_bar",
        ]
        for key in cli_required:
            if key not in cli_section:
                raise ValueError(f"Missing CLI config key: {key}")

        # Validate commands section
        commands_section = data.get("commands", {})
        command_types = ["agent", "team", "workflow", "book"]
        for cmd_type in command_types:
            if cmd_type not in commands_section:
                raise ValueError(f"Missing command config: {cmd_type}")

        return True

    @staticmethod
    def validate_agent_schema(data: Dict[str, Any]) -> bool:
        """Validate agent YAML schema."""
        required_keys = ["id", "model", "name"]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required agent key: {key}")

        # Validate model format
        model = data.get("model", "")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Agent model must be a non-empty string")

        # Validate optional fields types
        if "stack" in data and not isinstance(data["stack"], list):
            raise ValueError("Agent stack must be a list")

        if "tools" in data and not isinstance(data["tools"], list):
            raise ValueError("Agent tools must be a list")

        return True

    @staticmethod
    def validate_workflow_schema(data: Dict[str, Any]) -> bool:
        """Validate workflow YAML schema."""
        required_keys = ["id", "name", "vertices"]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required workflow key: {key}")

        # Validate vertices is a list
        if not isinstance(data.get("vertices", []), list):
            raise ValueError("Workflow vertices must be a list")

        # Validate edges is a list if present
        if "edges" in data and not isinstance(data["edges"], list):
            raise ValueError("Workflow edges must be a list")

        return True

    @staticmethod
    def validate_team_schema(data: Dict[str, Any]) -> bool:
        """Validate team YAML schema."""
        required_keys = ["id", "name", "members"]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required team key: {key}")

        # Validate members is a list
        members = data.get("members", [])
        if not isinstance(members, list):
            raise ValueError("Team members must be a list")

        # Validate each member has required fields
        for i, member in enumerate(members):
            if not isinstance(member, dict):
                raise ValueError(f"Team member {i} must be a dictionary")

            member_required = ["id", "role", "name"]
            for key in member_required:
                if key not in member:
                    raise ValueError(f"Team member {i} missing required key: {key}")

        return True

    @staticmethod
    def validate_book_schema(data: Dict[str, Any]) -> bool:
        """Validate book YAML schema."""
        required_keys = ["id", "title", "author"]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required book key: {key}")

        # Validate chapters is a list if present
        if "chapters" in data and not isinstance(data["chapters"], list):
            raise ValueError("Book chapters must be a list")

        return True

    @staticmethod
    def validate_protocol_schema(data: Dict[str, Any]) -> bool:
        """Validate protocol YAML schema."""
        required_keys = ["id", "name"]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required protocol key: {key}")

        # Validate commands is a list if present
        if "commands" in data and not isinstance(data["commands"], list):
            raise ValueError("Protocol commands must be a list")

        return True

    @staticmethod
    def validate_tool_schema(data: Dict[str, Any]) -> bool:
        """Validate tool YAML schema."""
        required_keys = ["id", "name", "type"]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required tool key: {key}")

        # Validate type is valid
        valid_types = ["api", "cli", "mcp", "database", "filesystem", "custom"]
        tool_type = data.get("type", "")
        if tool_type not in valid_types:
            raise ValueError(
                f"Invalid tool type: {tool_type}. Must be one of {valid_types}"
            )

        return True


class TestDataContractValidation:
    """Test data contract validation for JSON/YAML schemas."""

    @pytest.mark.contract
    def test_cli_config_schema_validation(self):
        """Test CLI configuration schema validation."""
        # Load actual CLI config
        config_path = Path(__file__).parent.parent.parent / "config" / "cli-config.yaml"
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Validate schema
        assert CLISchemaValidator.validate_cli_config(config_data)

        # Test missing required key
        invalid_config = config_data.copy()
        del invalid_config["cli"]
        with pytest.raises(ValueError, match="Missing required key: cli"):
            CLISchemaValidator.validate_cli_config(invalid_config)

    @pytest.mark.contract
    def test_agent_schema_validation(self):
        """Test agent YAML schema validation."""
        # Test valid agent schema
        valid_agent = {
            "id": "test-agent",
            "model": "claude-3.5-sonnet",
            "name": "Test Agent",
            "stack": ["python", "javascript"],
            "tools": ["github", "vscode"],
            "speciality": "Development",
            "persona": "Experienced developer",
        }

        assert CLISchemaValidator.validate_agent_schema(valid_agent)

        # Test missing required field
        invalid_agent = valid_agent.copy()
        del invalid_agent["id"]
        with pytest.raises(ValueError, match="Missing required agent key: id"):
            CLISchemaValidator.validate_agent_schema(invalid_agent)

        # Test invalid model type
        invalid_agent2 = valid_agent.copy()
        invalid_agent2["model"] = ""
        with pytest.raises(ValueError, match="Agent model must be a non-empty string"):
            CLISchemaValidator.validate_agent_schema(invalid_agent2)

    @pytest.mark.contract
    def test_workflow_schema_validation(self):
        """Test workflow YAML schema validation."""
        # Test valid workflow schema
        valid_workflow = {
            "id": "test-workflow",
            "name": "Test Workflow",
            "description": "A test workflow",
            "vertices": [{"id": "task1", "agent": "agent1", "task": "Test task"}],
            "edges": [],
        }

        assert CLISchemaValidator.validate_workflow_schema(valid_workflow)

        # Test missing required field
        invalid_workflow = valid_workflow.copy()
        del invalid_workflow["vertices"]
        with pytest.raises(ValueError, match="Missing required workflow key: vertices"):
            CLISchemaValidator.validate_workflow_schema(invalid_workflow)

        # Test invalid vertices type
        invalid_workflow2 = valid_workflow.copy()
        invalid_workflow2["vertices"] = "not_a_list"
        with pytest.raises(ValueError, match="Workflow vertices must be a list"):
            CLISchemaValidator.validate_workflow_schema(invalid_workflow2)

    @pytest.mark.contract
    def test_team_schema_validation(self):
        """Test team YAML schema validation."""
        # Test valid team schema
        valid_team = {
            "id": "test-team",
            "name": "Test Team",
            "description": "A test team",
            "members": [
                {
                    "id": "member1",
                    "role": "member",
                    "name": "Team Member 1",
                    "speciality": "Development",
                },
                {
                    "id": "member2",
                    "role": "leader",
                    "name": "Team Leader",
                    "speciality": "Management",
                },
            ],
        }

        assert CLISchemaValidator.validate_team_schema(valid_team)

        # Test missing required field
        invalid_team = valid_team.copy()
        del invalid_team["members"]
        with pytest.raises(ValueError, match="Missing required team key: members"):
            CLISchemaValidator.validate_team_schema(invalid_team)

        # Test invalid members type
        invalid_team2 = valid_team.copy()
        invalid_team2["members"] = "not_a_list"
        with pytest.raises(ValueError, match="Team members must be a list"):
            CLISchemaValidator.validate_team_schema(invalid_team2)

        # Test member missing required field
        invalid_team3 = valid_team.copy()
        invalid_team3["members"][0].pop("id")
        with pytest.raises(ValueError, match="Team member 0 missing required key: id"):
            CLISchemaValidator.validate_team_schema(invalid_team3)

    @pytest.mark.contract
    def test_book_schema_validation(self):
        """Test book YAML schema validation."""
        # Test valid book schema
        valid_book = {
            "id": "test-book",
            "title": "Test Book",
            "author": "Test Author",
            "description": "A test book",
            "chapters": [{"id": "chap1", "title": "Chapter 1", "content": "Content"}],
        }

        assert CLISchemaValidator.validate_book_schema(valid_book)

        # Test missing required field
        invalid_book = valid_book.copy()
        del invalid_book["title"]
        with pytest.raises(ValueError, match="Missing required book key: title"):
            CLISchemaValidator.validate_book_schema(invalid_book)

        # Test invalid chapters type
        invalid_book2 = valid_book.copy()
        invalid_book2["chapters"] = "not_a_list"
        with pytest.raises(ValueError, match="Book chapters must be a list"):
            CLISchemaValidator.validate_book_schema(invalid_book2)

    @pytest.mark.contract
    def test_protocol_schema_validation(self):
        """Test protocol YAML schema validation."""
        # Test valid protocol schema
        valid_protocol = {
            "id": "test-protocol",
            "name": "Test Protocol",
            "description": "A test protocol",
            "commands": [
                {"name": "analyze", "description": "Analyze task"},
                {"name": "implement", "description": "Implement solution"},
            ],
        }

        assert CLISchemaValidator.validate_protocol_schema(valid_protocol)

        # Test missing required field
        invalid_protocol = valid_protocol.copy()
        del invalid_protocol["name"]
        with pytest.raises(ValueError, match="Missing required protocol key: name"):
            CLISchemaValidator.validate_protocol_schema(invalid_protocol)

        # Test invalid commands type
        invalid_protocol2 = valid_protocol.copy()
        invalid_protocol2["commands"] = "not_a_list"
        with pytest.raises(ValueError, match="Protocol commands must be a list"):
            CLISchemaValidator.validate_protocol_schema(invalid_protocol2)

    @pytest.mark.contract
    def test_tool_schema_validation(self):
        """Test tool YAML schema validation."""
        # Test valid tool schema
        valid_tool = {
            "id": "test-tool",
            "name": "Test Tool",
            "description": "A test tool",
            "type": "cli",
            "config": {"command": "echo hello"},
        }

        assert CLISchemaValidator.validate_tool_schema(valid_tool)

        # Test missing required field
        invalid_tool = valid_tool.copy()
        del invalid_tool["type"]
        with pytest.raises(ValueError, match="Missing required tool key: type"):
            CLISchemaValidator.validate_tool_schema(invalid_tool)

        # Test invalid type
        invalid_tool2 = valid_tool.copy()
        invalid_tool2["type"] = "invalid_type"
        with pytest.raises(ValueError, match="Invalid tool type: invalid_type"):
            CLISchemaValidator.validate_tool_schema(invalid_tool2)

    @pytest.mark.contract
    def test_yaml_file_parsing(self):
        """Test that YAML files can be parsed correctly."""
        # Test parsing CLI config
        config_path = Path(__file__).parent.parent.parent / "config" / "cli-config.yaml"
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        assert isinstance(data, dict)
        assert "cli" in data

        # Test parsing workflow file
        workflow_path = (
            Path(__file__).parent.parent.parent / "workflows" / "test-workflow-e2e.yaml"
        )
        with open(workflow_path, "r") as f:
            workflow_data = yaml.safe_load(f)

        assert isinstance(workflow_data, dict)
        assert "id" in workflow_data

    @pytest.mark.contract
    def test_json_serialization_compatibility(self):
        """Test that YAML data can be converted to JSON."""
        # Test CLI config JSON conversion
        config_path = Path(__file__).parent.parent.parent / "config" / "cli-config.yaml"
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        # Convert to JSON string and back
        json_str = json.dumps(yaml_data, indent=2)
        json_data = json.loads(json_str)

        # Verify structure is preserved
        assert json_data == yaml_data
        assert json_data["cli"]["colors"] == yaml_data["cli"]["colors"]

    @pytest.mark.contract
    def test_schema_backward_compatibility(self):
        """Test that schemas support backward compatibility."""
        # Test that optional fields don't break validation
        minimal_agent = {
            "id": "minimal-agent",
            "model": "gpt-4",
            "name": "Minimal Agent",
        }

        assert CLISchemaValidator.validate_agent_schema(minimal_agent)

        # Test workflow without edges
        workflow_no_edges = {
            "id": "workflow-no-edges",
            "name": "Workflow Without Edges",
            "vertices": [],
        }

        assert CLISchemaValidator.validate_workflow_schema(workflow_no_edges)

    @pytest.mark.contract
    def test_data_contract_edge_cases(self):
        """Test edge cases in data contract validation."""
        # Test empty lists are valid
        agent_empty_lists = {
            "id": "agent-empty",
            "model": "claude-3-haiku",
            "name": "Agent with Empty Lists",
            "stack": [],
            "tools": [],
        }

        assert CLISchemaValidator.validate_agent_schema(agent_empty_lists)

        # Test team with single member
        team_single_member = {
            "id": "single-member-team",
            "name": "Single Member Team",
            "members": [{"id": "only-member", "role": "leader", "name": "Only Member"}],
        }

        assert CLISchemaValidator.validate_team_schema(team_single_member)

        # Test tool with minimal config
        minimal_tool = {
            "id": "minimal-tool",
            "name": "Minimal Tool",
            "type": "api",
        }

        assert CLISchemaValidator.validate_tool_schema(minimal_tool)
