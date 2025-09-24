import json
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml
from click.testing import CliRunner


# Mock classes for engine-core dependencies
class MockProtocolBuilder:
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.configuration = MagicMock()

    def with_id(self, id):
        self.id = id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_version(self, version):
        self.configuration.version = version
        return self

    def with_author(self, author):
        self.configuration.author = author
        return self

    def with_tags(self, tags):
        self.configuration.tags = tags
        return self

    def with_supported_intents(self, intents):
        self.configuration.supported_intents = intents
        return self

    def with_supported_command_types(self, cmd_types):
        self.configuration.supported_command_types = cmd_types
        return self

    def with_default_scope(self, scope):
        self.configuration.default_scope = scope
        return self

    def with_strict_validation(self, strict):
        self.configuration.strict_validation = strict
        return self

    def build(self):
        protocol = MagicMock()
        protocol.id = self.id
        protocol.name = self.name
        protocol.description = self.description
        protocol.configuration = self.configuration
        return protocol


class MockIntentCategory:
    ANALYSIS = MagicMock(value="analysis")
    DEVELOPMENT = MagicMock(value="development")
    DEBUGGING = MagicMock(value="debugging")


class MockCommandType:
    TASK_EXECUTION = MagicMock(value="task_execution")
    INFORMATION_REQUEST = MagicMock(value="information_request")


class MockContextScope:
    def __init__(self, scope):
        self.value = scope


class MockCommandContext:
    def __init__(self, user_id, session_id, project_id):
        self.user_id = user_id
        self.session_id = session_id
        self.project_id = project_id


# Mock the engine-core imports
@pytest.fixture
def mock_protocol_enums():
    # Import enums directly from engine_core instead of using _get_protocol_enums
    try:
        from engine_core import (
            CommandContext,
            CommandType,
            ContextScope,
            IntentCategory,
        )

        yield IntentCategory, CommandType, ContextScope, CommandContext
    except ImportError:
        # Fallback for when engine_core is not available
        yield None, None, None, None


@pytest.fixture
def mock_protocol_builder():
    with patch(
        "engine_cli.commands.protocol.ProtocolBuilder",
        return_value=MockProtocolBuilder(),
    ) as mock_builder:
        yield mock_builder


@pytest.fixture
def mock_protocol_storage():
    """Mock ProtocolStorage class"""
    mock_storage = MagicMock()
    mock_storage.list_protocols.return_value = [
        {
            "id": "test_protocol_1",
            "name": "Test Protocol 1",
            "version": "1.0.0",
            "author": "Test Author",
            "tags": ["test", "development"],
            "description": "A test protocol",
        },
        {
            "id": "test_protocol_2",
            "name": "Test Protocol 2",
            "version": "2.0.0",
            "author": "Another Author",
            "tags": ["production"],
            "description": "Another test protocol",
        },
    ]
    mock_storage.get_protocol.return_value = {
        "id": "test_protocol_1",
        "name": "Test Protocol 1",
        "version": "1.0.0",
        "author": "Test Author",
        "tags": ["test", "development"],
        "description": "A test protocol",
        "supported_intents": ["analysis", "development"],
        "supported_command_types": ["task_execution"],
        "default_scope": "global",
        "strict_validation": False,
        "created_at": "2024-01-01T00:00:00",
    }
    mock_storage.delete_protocol.return_value = True
    mock_storage.save_protocol.return_value = True
    return mock_storage


@pytest.fixture
def mock_imports():
    """Mock all external imports"""
    with patch.dict(
        "sys.modules",
        {
            "engine_core": MagicMock(),
            "engine_core.builders": MagicMock(),
            "engine_core.builders.protocol": MagicMock(),
            "engine_core.enums": MagicMock(),
            "engine_core.enums.protocol": MagicMock(),
        },
    ):
        yield


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)


class TestProtocolStorage:
    """Test ProtocolStorage class functionality"""

    def test_list_protocols(self, mock_protocol_storage):
        """Test listing protocols"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import protocol_storage

            protocols = protocol_storage.list_protocols()
            assert len(protocols) == 2
            assert protocols[0]["name"] == "Test Protocol 1"
            assert protocols[1]["name"] == "Test Protocol 2"

    def test_get_protocol(self, mock_protocol_storage):
        """Test getting a specific protocol"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import protocol_storage

            protocol = protocol_storage.get_protocol("test_protocol_1")
            assert protocol is not None
            assert protocol["id"] == "test_protocol_1"
            assert protocol["name"] == "Test Protocol 1"

    def test_get_protocol_not_found(self, mock_protocol_storage):
        """Test getting a non-existent protocol"""
        mock_protocol_storage.get_protocol.return_value = None
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import protocol_storage

            protocol = protocol_storage.get_protocol("nonexistent")
            assert protocol is None

    def test_delete_protocol(self, mock_protocol_storage):
        """Test deleting a protocol"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import protocol_storage

            result = protocol_storage.delete_protocol("test_protocol_1")
            assert result is True

    def test_delete_protocol_not_found(self, mock_protocol_storage):
        """Test deleting a non-existent protocol"""
        mock_protocol_storage.delete_protocol.return_value = False
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import protocol_storage

            result = protocol_storage.delete_protocol("nonexistent")
            assert result is False


class TestProtocolCLICommands:
    """Test CLI commands for protocol management"""

    def test_create_protocol_basic(
        self, cli_runner, mock_protocol_enums, mock_protocol_builder, mock_imports
    ):
        """Test creating a basic protocol"""
        with patch("engine_cli.commands.protocol.success"), patch(
            "engine_cli.commands.protocol.table"
        ), patch("engine_cli.commands.protocol.print_table"), patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "os.makedirs"
        ), patch(
            "yaml.safe_dump"
        ):

            from engine_cli.commands.protocol import create

            result = cli_runner.invoke(
                create, ["test_protocol", "--description", "A test protocol", "--save"]
            )

            assert result.exit_code == 0

    def test_create_protocol_full_options(
        self, cli_runner, mock_protocol_enums, mock_protocol_builder, mock_imports
    ):
        """Test creating a protocol with all options"""
        with patch("engine_cli.commands.protocol.success"), patch(
            "engine_cli.commands.protocol.table"
        ), patch("engine_cli.commands.protocol.print_table"), patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "os.makedirs"
        ), patch(
            "yaml.safe_dump"
        ):

            from engine_cli.commands.protocol import create

            result = cli_runner.invoke(
                create,
                [
                    "full_protocol",
                    "--description",
                    "Full featured protocol",
                    "--author",
                    "Test Author",
                    "--version",
                    "2.0.0",
                    "--tags",
                    "test,development,production",
                    "--intents",
                    "analysis,development",
                    "--command-types",
                    "task_execution",
                    "--scope",
                    "project",
                    "--strict-validation",
                    "--save",
                ],
            )

            assert result.exit_code == 0

    def test_create_protocol_import_error(self, cli_runner):
        """Test create protocol when engine-core is not available"""
        with patch(
            "engine_cli.commands.protocol.ProtocolBuilder",
            side_effect=ImportError("No module"),
        ):
            from engine_cli.commands.protocol import create

            result = cli_runner.invoke(create, ["test_protocol"])

            assert result.exit_code == 0
            assert "Engine Core not available" in result.output

    def test_list_protocols_table_format(self, cli_runner, mock_protocol_storage):
        """Test listing protocols in table format"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("engine_cli.commands.protocol.table"), patch(
            "engine_cli.commands.protocol.print_table"
        ), patch(
            "engine_cli.commands.protocol.success"
        ):

            from engine_cli.commands.protocol import list

            result = cli_runner.invoke(list, ["--format", "table"])

            assert result.exit_code == 0

    def test_list_protocols_json_format(self, cli_runner, mock_protocol_storage):
        """Test listing protocols in JSON format"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import list

            result = cli_runner.invoke(list, ["--format", "json"])

            assert result.exit_code == 0
            # Should contain JSON output
            assert "test_protocol_1" in result.output

    def test_list_protocols_yaml_format(self, cli_runner, mock_protocol_storage):
        """Test listing protocols in YAML format"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import list

            result = cli_runner.invoke(list, ["--format", "yaml"])

            assert result.exit_code == 0
            # Should contain YAML output
            assert "test_protocol_1" in result.output

    def test_list_protocols_with_filters(self, cli_runner, mock_protocol_storage):
        """Test listing protocols with tag and author filters"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("engine_cli.commands.protocol.table"), patch(
            "engine_cli.commands.protocol.print_table"
        ), patch(
            "engine_cli.commands.protocol.success"
        ):

            from engine_cli.commands.protocol import list

            result = cli_runner.invoke(
                list, ["--tag", "test", "--author", "Test Author"]
            )

            assert result.exit_code == 0

    def test_list_protocols_empty(self, cli_runner):
        """Test listing protocols when none exist"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.list_protocols.return_value = []

        with patch("engine_cli.commands.protocol.protocol_storage", mock_empty_storage):
            from engine_cli.commands.protocol import list

            result = cli_runner.invoke(list)

            assert result.exit_code == 0
            assert "No protocols found" in result.output

    def test_show_protocol_table_format(self, cli_runner, mock_protocol_storage):
        """Test showing protocol details in table format"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("engine_cli.commands.protocol.key_value"):

            from engine_cli.commands.protocol import show

            result = cli_runner.invoke(show, ["test_protocol_1", "--format", "table"])

            assert result.exit_code == 0

    def test_show_protocol_json_format(self, cli_runner, mock_protocol_storage):
        """Test showing protocol details in JSON format"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import show

            result = cli_runner.invoke(show, ["test_protocol_1", "--format", "json"])

            assert result.exit_code == 0
            assert "test_protocol_1" in result.output

    def test_show_protocol_yaml_format(self, cli_runner, mock_protocol_storage):
        """Test showing protocol details in YAML format"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):
            from engine_cli.commands.protocol import show

            result = cli_runner.invoke(show, ["test_protocol_1", "--format", "yaml"])

            assert result.exit_code == 0
            assert "test_protocol_1" in result.output

    def test_show_protocol_not_found(self, cli_runner):
        """Test showing a non-existent protocol"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.get_protocol.return_value = None

        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_empty_storage
        ), patch("engine_cli.commands.protocol.error"):

            from engine_cli.commands.protocol import show

            result = cli_runner.invoke(show, ["nonexistent"])

            assert result.exit_code == 0

    def test_delete_protocol_success(self, cli_runner, mock_protocol_storage):
        """Test deleting a protocol successfully"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("engine_cli.commands.protocol.success"):

            from engine_cli.commands.protocol import delete

            result = cli_runner.invoke(delete, ["test_protocol_1", "--force"])

            assert result.exit_code == 0

    def test_delete_protocol_not_found(self, cli_runner):
        """Test deleting a non-existent protocol"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.get_protocol.return_value = None

        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_empty_storage
        ), patch("engine_cli.commands.protocol.error"):

            from engine_cli.commands.protocol import delete

            result = cli_runner.invoke(delete, ["nonexistent", "--force"])

            assert result.exit_code == 0

    def test_delete_protocol_with_confirmation(self, cli_runner, mock_protocol_storage):
        """Test deleting a protocol with user confirmation"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("engine_cli.commands.protocol.success"), patch(
            "click.confirm", return_value=True
        ):

            from engine_cli.commands.protocol import delete

            result = cli_runner.invoke(delete, ["test_protocol_1"])

            assert result.exit_code == 0

    def test_delete_protocol_cancelled(self, cli_runner, mock_protocol_storage):
        """Test cancelling protocol deletion"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("click.confirm", return_value=False):

            from engine_cli.commands.protocol import delete

            result = cli_runner.invoke(delete, ["test_protocol_1"])

            assert result.exit_code == 0
            assert "Operation cancelled" in result.output

    def test_test_protocol_success(
        self, cli_runner, mock_protocol_storage, mock_protocol_enums
    ):
        """Test testing a protocol with command"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ), patch("engine_cli.commands.protocol.success"):

            from engine_cli.commands.protocol import test

            result = cli_runner.invoke(
                test,
                [
                    "test_protocol_1",
                    "--command",
                    "analyze codebase",
                    "--context",
                    '{"user_id": "test_user"}',
                ],
            )

            assert result.exit_code == 0

    def test_test_protocol_not_found(self, cli_runner):
        """Test testing a non-existent protocol"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.get_protocol.return_value = None

        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_empty_storage
        ), patch("engine_cli.commands.protocol.error"):

            from engine_cli.commands.protocol import test

            result = cli_runner.invoke(test, ["nonexistent", "--command", "test"])

            assert result.exit_code == 0

    def test_test_protocol_no_command(self, cli_runner, mock_protocol_storage):
        """Test testing a protocol without providing command"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):

            from engine_cli.commands.protocol import test

            result = cli_runner.invoke(test, ["test_protocol_1"])

            # Should exit with error code when no command provided
            assert (
                result.exit_code == 1
                or "Please provide a command to test" in result.output
            )

    def test_test_protocol_invalid_context(self, cli_runner, mock_protocol_storage):
        """Test testing a protocol with invalid JSON context"""
        with patch(
            "engine_cli.commands.protocol.protocol_storage", mock_protocol_storage
        ):

            from engine_cli.commands.protocol import test

            result = cli_runner.invoke(
                test,
                [
                    "test_protocol_1",
                    "--command",
                    "test command",
                    "--context",
                    "invalid json",
                ],
            )

            # Should exit with error code when invalid JSON provided
            assert result.exit_code == 1 or "Invalid JSON context" in result.output


class TestProtocolUtilityFunctions:
    """Test utility functions"""

    def test_protocol_enums_import(self):
        """Test that protocol enums can be imported from engine_core"""
        try:
            from engine_core import (
                CommandContext,
                CommandType,
                ContextScope,
                IntentCategory,
            )

            assert IntentCategory is not None
            assert CommandType is not None
            assert ContextScope is not None
            assert CommandContext is not None
        except ImportError:
            pytest.skip("engine_core not available")


if __name__ == "__main__":
    pytest.main([__file__])
