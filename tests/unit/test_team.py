import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

try:
    import pytest  # type: ignore

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    class MockMark:
        def asyncio(self, func=None):
            """Mock asyncio marker that can be used as decorator"""
            if func is None:
                # Called as @pytest.mark.asyncio()
                return lambda f: f
            else:
                # Called as @pytest.mark.asyncio
                return func

    class MockPytest:
        def __init__(self):
            self.mark = MockMark()
            self.fixture = lambda f: f

        def raises(self, *args, **kwargs):
            # Mock implementation
            class MockContext:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    return None

            return MockContext()

        def skip(self, reason):
            raise Exception(f"Skipped: {reason}")

        @staticmethod
        def main(args):
            pass

    pytest = MockPytest()

import yaml
from click.testing import CliRunner


# Mock classes for engine-core dependencies
class MockTeamBuilder:
    def __init__(self):
        self.id = None
        self.name = None
        self.coordination_strategy = None
        self.description = None
        self.members = []

    def with_id(self, id):
        self.id = id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_coordination_strategy(self, strategy):
        self.coordination_strategy = strategy
        return self

    def with_description(self, description):
        self.description = description
        return self

    def add_member(self, agent_id):
        self.members.append(agent_id)
        return self

    def build(self, agents=None):
        team = MagicMock()
        team.id = self.id
        team.name = self.name
        team.coordination_strategy = (
            self.coordination_strategy.value
            if self.coordination_strategy is not None
            and hasattr(self.coordination_strategy, "value")
            else self.coordination_strategy
        )
        team.description = self.description
        team.agents = agents or {}
        return team


class MockAgentBuilder:
    def __init__(self):
        self.id = None
        self.name = None
        self.model = None

    def with_id(self, id):
        self.id = id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_model(self, model):
        self.model = model
        return self

    def build(self):
        agent = MagicMock()
        agent.id = self.id
        agent.name = self.name
        agent.model = self.model
        return agent


class MockTeamCoordinationStrategy:
    HIERARCHICAL = MagicMock(value="hierarchical")
    COLLABORATIVE = MagicMock(value="collaborative")
    PARALLEL = MagicMock(value="parallel")
    SEQUENTIAL = MagicMock(value="sequential")


class MockTeamMemberRole:
    LEADER = MagicMock(value="leader")
    MEMBER = MagicMock(value="member")


# Mock the engine-core imports
@pytest.fixture
def mock_team_enums():
    # Import enums directly from engine_core instead of using _get_team_enums
    try:
        from engine_core import TeamCoordinationStrategy, TeamMemberRole  # type: ignore

        yield TeamCoordinationStrategy, TeamMemberRole
    except ImportError:
        # Fallback for when engine_core is not available
        yield None, None


@pytest.fixture
def mock_team_builder():
    with patch(
        "engine_cli.commands.team.TeamBuilder", return_value=MockTeamBuilder()
    ) as mock_builder:
        yield mock_builder


@pytest.fixture
def mock_agent_builder():
    with patch(
        "engine_cli.commands.team.AgentBuilder",
        return_value=MockAgentBuilder(),
        create=True,
    ) as mock_builder:
        yield mock_builder


@pytest.fixture
def mock_team_storage():
    """Mock TeamStorage class"""
    mock_storage = MagicMock()
    mock_storage.list_teams.return_value = [
        {
            "id": "test_team_1",
            "name": "Test Team 1",
            "coordination_strategy": "collaborative",
            "agents": ["agent1", "agent2"],
            "leader": "agent1",
            "description": "A test team",
            "created_at": "2024-01-01T00:00:00",
        },
        {
            "id": "test_team_2",
            "name": "Test Team 2",
            "coordination_strategy": "hierarchical",
            "agents": ["agent3"],
            "leader": "agent3",
            "description": "Another test team",
        },
    ]
    mock_storage.get_team.return_value = {
        "id": "test_team_1",
        "name": "Test Team 1",
        "coordination_strategy": "collaborative",
        "agents": ["agent1", "agent2"],
        "leader": "agent1",
        "description": "A test team",
        "created_at": "2024-01-01T00:00:00",
    }
    mock_storage.delete_team.return_value = True
    return mock_storage


@pytest.fixture
def mock_imports():
    """Mock all external imports"""
    with patch.dict(
        "sys.modules",
        {
            "engine_core": MagicMock(),
            "engine_core.core": MagicMock(),
            "engine_core.core.teams": MagicMock(),
            "engine_core.core.teams.team_builder": MagicMock(),
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


class TestTeamStorage:
    """Test TeamStorage class functionality"""

    def test_list_teams(self, mock_team_storage):
        """Test listing teams"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import team_storage

            teams = team_storage.list_teams()
            assert len(teams) == 2
            assert teams[0]["name"] == "Test Team 1"
            assert teams[1]["name"] == "Test Team 2"

    def test_get_team(self, mock_team_storage):
        """Test getting a specific team"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import team_storage

            team = team_storage.get_team("test_team_1")
            assert team is not None
            assert team["id"] == "test_team_1"
            assert team["name"] == "Test Team 1"

    def test_get_team_not_found(self, mock_team_storage):
        """Test getting a non-existent team"""
        mock_team_storage.get_team.return_value = None
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import team_storage

            team = team_storage.get_team("nonexistent")
            assert team is None

    def test_delete_team(self, mock_team_storage):
        """Test deleting a team"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import team_storage

            result = team_storage.delete_team("test_team_1")
            assert result is True

    def test_delete_team_not_found(self, mock_team_storage):
        """Test deleting a non-existent team"""
        mock_team_storage.delete_team.return_value = False
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import team_storage

            result = team_storage.delete_team("nonexistent")
            assert result is False

    def test_team_storage_initialization(self, temp_dir):
        """Test TeamStorage initialization creates directory"""
        from engine_cli.commands.team import TeamStorage

        storage = TeamStorage()
        assert os.path.exists(storage.teams_dir)
        assert storage.teams_dir.endswith("teams")

    def test_list_teams_with_corrupt_file(self, temp_dir):
        """Test listing teams when a file is corrupted"""
        from engine_cli.commands.team import TeamStorage

        # Create a corrupted YAML file
        teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(teams_dir, exist_ok=True)

        with open(os.path.join(teams_dir, "corrupt.yaml"), "w") as f:
            f.write("invalid: yaml: content: [\n")

        # Create a valid team file
        with open(os.path.join(teams_dir, "valid.yaml"), "w") as f:
            yaml.safe_dump({"id": "valid_team", "name": "Valid Team"}, f)

        storage = TeamStorage()
        teams = storage.list_teams()

        # Should only return the valid team, corrupt file should be skipped
        assert len(teams) == 1
        assert teams[0]["id"] == "valid_team"

    def test_get_team_file_handling(self, temp_dir):
        """Test get_team with file operations"""
        from engine_cli.commands.team import TeamStorage

        teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(teams_dir, exist_ok=True)

        # Create a team file
        team_data = {"id": "test_team", "name": "Test Team"}
        with open(os.path.join(teams_dir, "test_team.yaml"), "w") as f:
            yaml.safe_dump(team_data, f)

        storage = TeamStorage()
        team = storage.get_team("test_team")

        assert team is not None
        assert team["id"] == "test_team"
        assert team["name"] == "Test Team"

    def test_get_team_corrupt_file(self, temp_dir):
        """Test get_team with corrupted file"""
        from engine_cli.commands.team import TeamStorage

        teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(teams_dir, exist_ok=True)

        # Create a corrupted file
        with open(os.path.join(teams_dir, "corrupt.yaml"), "w") as f:
            f.write("invalid: yaml: content: [\n")  # Truly invalid YAML

        storage = TeamStorage()
        team = storage.get_team("corrupt")

        assert team is None

    def test_delete_team_file_operation(self, temp_dir):
        """Test delete_team file operations"""
        from engine_cli.commands.team import TeamStorage

        teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(teams_dir, exist_ok=True)

        # Create a team file
        team_file = os.path.join(teams_dir, "test_team.yaml")
        with open(team_file, "w") as f:
            f.write("id: test_team\n")

        storage = TeamStorage()
        result = storage.delete_team("test_team")

        assert result is True
        assert not os.path.exists(team_file)

    def test_get_team_file_read_error(self, temp_dir):
        """Test get_team when file read fails"""
        from engine_cli.commands.team import TeamStorage

        teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(teams_dir, exist_ok=True)

        # Create a file that will cause read error (simulate permission issue)
        team_file = os.path.join(teams_dir, "error_team.yaml")
        with open(team_file, "w") as f:
            f.write("id: error_team\n")

        storage = TeamStorage()

        # Mock open to raise exception
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            team = storage.get_team("error_team")
            assert team is None

    def test_delete_team_file_remove_error(self, temp_dir):
        """Test delete_team when file removal fails"""
        from engine_cli.commands.team import TeamStorage

        teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(teams_dir, exist_ok=True)

        # Create a team file
        team_file = os.path.join(teams_dir, "fail_delete.yaml")
        with open(team_file, "w") as f:
            f.write("id: fail_delete\n")

        storage = TeamStorage()

        # Mock os.remove to raise exception
        with patch("os.remove", side_effect=OSError("Permission denied")):
            result = storage.delete_team("fail_delete")
            assert result is False


class TestTeamCLICommands:
    """Test CLI commands for team management"""

    def test_create_team_basic(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test creating a basic team"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"), patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "os.makedirs"
        ), patch(
            "yaml.safe_dump"
        ):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "test_team",
                    "--agents",
                    "agent1,agent2",
                    "--strategy",
                    "collaborative",
                    "--description",
                    "A test team",
                    "--save",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_hierarchical(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test creating a hierarchical team with leader"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"), patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "os.makedirs"
        ), patch(
            "yaml.safe_dump"
        ):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "hierarchical_team",
                    "--agents",
                    "agent1,agent2,agent3",
                    "--leader",
                    "agent1",
                    "--strategy",
                    "hierarchical",
                    "--description",
                    "Hierarchical team",
                    "--save",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_different_strategies(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test creating teams with different coordination strategies"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"):

            from engine_cli.commands.team import create

            # Test parallel strategy
            result = cli_runner.invoke(
                create,
                [
                    "parallel_team",
                    "--agents",
                    "agent1,agent2",
                    "--strategy",
                    "parallel",
                ],
            )
            assert result.exit_code == 0

            # Test sequential strategy
            result = cli_runner.invoke(
                create,
                [
                    "sequential_team",
                    "--agents",
                    "agent1,agent2",
                    "--strategy",
                    "sequential",
                ],
            )
            assert result.exit_code == 0

    def test_create_team_no_agents(
        self, cli_runner, mock_team_enums, mock_team_builder, mock_imports
    ):
        """Test creating a team without agents"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "empty_team",
                    "--strategy",
                    "collaborative",
                    "--description",
                    "Team without agents",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_with_output_file(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
        temp_dir,
    ):
        """Test creating a team with output file"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"), patch(
            "builtins.open", mock_open()
        ) as mock_file, patch(
            "os.makedirs"
        ), patch(
            "yaml.safe_dump"
        ):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "output_team",
                    "--agents",
                    "agent1,agent2",
                    "--output",
                    "custom_output.yaml",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_save_error(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test create team when save fails"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"), patch(
            "builtins.open", side_effect=OSError("Permission denied")
        ), patch(
            "os.makedirs"
        ):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create, ["failing_team", "--agents", "agent1", "--save"]
            )

            assert result.exit_code == 0
            # Should still succeed in creating team, just fail to save

    def test_create_team_agent_creation_logic(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test the agent creation logic in create command"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "agent_test_team",
                    "--agents",
                    "agent1, agent2 , agent3",  # Test whitespace handling
                    "--strategy",
                    "parallel",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_empty_agent_list(
        self, cli_runner, mock_team_enums, mock_team_builder, mock_imports
    ):
        """Test creating team with empty agent string"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "empty_agents_team",
                    "--agents",
                    "",  # Empty agent list
                    "--strategy",
                    "collaborative",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_with_leader(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test creating team with leader specified"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "leader_team",
                    "--agents",
                    "agent1,agent2,agent3",
                    "--leader",
                    "agent1",
                    "--strategy",
                    "hierarchical",
                ],
            )

            assert result.exit_code == 0

    def test_create_team_with_whitespace_in_agents(
        self,
        cli_runner,
        mock_team_enums,
        mock_team_builder,
        mock_agent_builder,
        mock_imports,
    ):
        """Test create team with whitespace around agent names"""
        with patch("engine_cli.commands.team.success"), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"):

            from engine_cli.commands.team import create

            result = cli_runner.invoke(
                create,
                [
                    "whitespace_team",
                    "--agents",
                    "  agent1  ,  agent2  , agent3 ",
                    "--strategy",
                    "parallel",
                ],
            )

            assert result.exit_code == 0

    def test_list_teams_table_format(self, cli_runner, mock_team_storage):
        """Test listing teams in table format"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"), patch(
            "engine_cli.commands.team.success"
        ):

            from engine_cli.commands.team import list

            result = cli_runner.invoke(list, ["--format", "table"])

            assert result.exit_code == 0

    def test_list_teams_json_format(self, cli_runner, mock_team_storage):
        """Test listing teams in JSON format"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import list

            result = cli_runner.invoke(list, ["--format", "json"])

            assert result.exit_code == 0
            # Should contain JSON output
            assert "test_team_1" in result.output

    def test_list_teams_yaml_format(self, cli_runner, mock_team_storage):
        """Test listing teams in YAML format"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import list

            result = cli_runner.invoke(list, ["--format", "yaml"])

            assert result.exit_code == 0
            # Should contain YAML output
            assert "test_team_1" in result.output

    def test_list_teams_empty(self, cli_runner):
        """Test listing teams when none exist"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.list_teams.return_value = []

        with patch("engine_cli.commands.team.team_storage", mock_empty_storage):
            from engine_cli.commands.team import list

            result = cli_runner.invoke(list)

            assert result.exit_code == 0
            assert "No teams found" in result.output

    def test_show_team_table_format(self, cli_runner, mock_team_storage):
        """Test showing team details in table format"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.key_value"
        ):

            from engine_cli.commands.team import show

            result = cli_runner.invoke(show, ["test_team_1", "--format", "table"])

            assert result.exit_code == 0

    def test_show_team_json_format(self, cli_runner, mock_team_storage):
        """Test showing team details in JSON format"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import show

            result = cli_runner.invoke(show, ["test_team_1", "--format", "json"])

            assert result.exit_code == 0
            assert "test_team_1" in result.output

    def test_show_team_yaml_format(self, cli_runner, mock_team_storage):
        """Test showing team details in YAML format"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage):
            from engine_cli.commands.team import show

            result = cli_runner.invoke(show, ["test_team_1", "--format", "yaml"])

            assert result.exit_code == 0
            assert "test_team_1" in result.output

    def test_show_team_not_found(self, cli_runner):
        """Test showing a non-existent team"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.get_team.return_value = None

        with patch("engine_cli.commands.team.team_storage", mock_empty_storage), patch(
            "engine_cli.commands.team.error"
        ):

            from engine_cli.commands.team import show

            result = cli_runner.invoke(show, ["nonexistent"])

            assert result.exit_code == 0

    def test_delete_team_success(self, cli_runner, mock_team_storage):
        """Test deleting a team successfully"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.success"
        ):

            from engine_cli.commands.team import delete

            result = cli_runner.invoke(delete, ["test_team_1", "--force"])

            assert result.exit_code == 0

    def test_delete_team_not_found(self, cli_runner):
        """Test deleting a non-existent team"""
        mock_empty_storage = MagicMock()
        mock_empty_storage.get_team.return_value = None

        with patch("engine_cli.commands.team.team_storage", mock_empty_storage), patch(
            "engine_cli.commands.team.error"
        ):

            from engine_cli.commands.team import delete

            result = cli_runner.invoke(delete, ["nonexistent", "--force"])

            assert result.exit_code == 0

    def test_delete_team_with_confirmation(self, cli_runner, mock_team_storage):
        """Test deleting a team with user confirmation"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.success"
        ), patch("click.confirm", return_value=True):

            from engine_cli.commands.team import delete

            result = cli_runner.invoke(delete, ["test_team_1"])

            assert result.exit_code == 0

    def test_list_teams_error_handling(self, cli_runner):
        """Test list teams with error handling"""
        mock_error_storage = MagicMock()
        mock_error_storage.list_teams.side_effect = Exception("Storage error")

        with patch("engine_cli.commands.team.team_storage", mock_error_storage), patch(
            "engine_cli.commands.team.error"
        ):

            from engine_cli.commands.team import list

            result = cli_runner.invoke(list)

            assert result.exit_code == 0

    def test_list_teams_with_long_description(self, cli_runner, mock_team_storage):
        """Test list teams with long description truncation"""
        mock_team_storage.list_teams.return_value = [
            {
                "id": "long_desc_team",
                "name": "Long Desc Team",
                "coordination_strategy": "collaborative",
                "agents": ["agent1"],
                "description": (
                    "This is a very long description that should be truncated "
                    "in table display to show only first 30 chars followed by ellipsis"
                ),
            }
        ]

        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.table"
        ), patch("engine_cli.commands.team.print_table"), patch(
            "engine_cli.commands.team.success"
        ):

            from engine_cli.commands.team import list

            result = cli_runner.invoke(list)

            assert result.exit_code == 0

    def test_show_team_error_handling(self, cli_runner):
        """Test show team with error handling"""
        mock_error_storage = MagicMock()
        mock_error_storage.get_team.side_effect = Exception("Storage error")

        with patch("engine_cli.commands.team.team_storage", mock_error_storage), patch(
            "engine_cli.commands.team.error"
        ):

            from engine_cli.commands.team import show

            result = cli_runner.invoke(show, ["error_team"])

            assert result.exit_code == 0

    def test_show_team_with_all_fields(self, cli_runner, mock_team_storage):
        """Test show team with all optional fields present"""
        mock_team_storage.get_team.return_value = {
            "id": "complete_team",
            "name": "Complete Team",
            "coordination_strategy": "hierarchical",
            "agents": ["agent1", "agent2", "agent3"],
            "leader": "agent1",
            "description": "A complete team with all fields",
            "created_at": "2024-01-01T12:00:00",
        }

        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.key_value"
        ):

            from engine_cli.commands.team import show

            result = cli_runner.invoke(show, ["complete_team"])

            assert result.exit_code == 0

    def test_delete_team_error_handling(self, cli_runner, mock_team_storage):
        """Test delete team with error handling"""
        mock_team_storage.get_team.return_value = {"id": "error_team"}
        mock_team_storage.delete_team.side_effect = Exception("Delete error")

        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "engine_cli.commands.team.error"
        ):

            from engine_cli.commands.team import delete

            result = cli_runner.invoke(delete, ["error_team", "--force"])

            assert result.exit_code == 0

    def test_delete_team_confirmation_prompt(self, cli_runner, mock_team_storage):
        """Test delete team confirmation prompt behavior"""
        with patch("engine_cli.commands.team.team_storage", mock_team_storage), patch(
            "click.confirm", return_value=True
        ), patch("engine_cli.commands.team.success"):

            from engine_cli.commands.team import delete

            result = cli_runner.invoke(delete, ["test_team_1"])

            assert result.exit_code == 0
            # Should prompt for confirmation when --force is not used


class TestTeamUtilityFunctions:
    """Test utility functions"""

    def test_team_enums_import(self):
        """Test that team enums can be imported from engine_core"""
        try:
            from engine_core import TeamCoordinationStrategy  # type: ignore
            from engine_core import TeamMemberRole  # type: ignore; type: ignore

            assert TeamCoordinationStrategy is not None
            assert TeamMemberRole is not None
        except ImportError:
            pytest.skip("engine_core not available")

    def test_get_team_storage(self):
        """Test getting team storage instance"""
        from engine_cli.commands.team import get_team_storage

        storage = get_team_storage()
        assert storage is not None


if __name__ == "__main__":
    pytest.main([__file__])
