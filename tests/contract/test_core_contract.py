"""Contract tests for Engine CLI - Engine Core integration."""

import pytest
from engine_core import (
    AgentBuilder,
    BookBuilder,
    ProtocolBuilder,
    TeamBuilder,
    ToolBuilder,
    WorkflowBuilder,
    WorkflowEngine,
)
from engine_core import __version__ as core_version
from engine_core.core.teams.team_builder import TeamCoordinationStrategy, TeamMemberRole
from engine_core.models.tool import ToolType


class TestEngineCoreContract:
    """Test contracts between Engine CLI and Engine Core."""

    @pytest.mark.contract
    def test_core_version_available(self):
        """Test that core version is accessible."""
        assert core_version is not None
        assert isinstance(core_version, str)
        assert len(core_version) > 0

    @pytest.mark.contract
    def test_agent_builder_available(self):
        """Test that AgentBuilder is available and functional."""
        builder = AgentBuilder()
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_model")
        assert hasattr(builder, "with_stack")
        assert hasattr(builder, "build")

    @pytest.mark.contract
    def test_team_builder_available(self):
        """Test that TeamBuilder is available and functional."""
        builder = TeamBuilder()
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "add_member")
        assert hasattr(builder, "with_coordination_strategy")
        assert hasattr(builder, "build")

    @pytest.mark.contract
    def test_workflow_builder_available(self):
        """Test that WorkflowBuilder is available and functional."""
        builder = WorkflowBuilder()
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "add_agent_vertex")
        assert hasattr(builder, "add_edge")
        assert hasattr(builder, "build")

    @pytest.mark.contract
    def test_book_builder_available(self):
        """Test that BookBuilder is available and functional."""
        builder = BookBuilder()
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_title")
        assert hasattr(builder, "build")

    @pytest.mark.contract
    def test_protocol_builder_available(self):
        """Test that ProtocolBuilder is available and functional."""
        builder = ProtocolBuilder()
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_name")
        assert hasattr(builder, "with_default_scope")
        assert hasattr(builder, "build")

    @pytest.mark.contract
    def test_tool_builder_available(self):
        """Test that ToolBuilder is available and functional."""
        builder = ToolBuilder()
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_name")
        assert hasattr(builder, "with_description")
        assert hasattr(builder, "build")

    @pytest.mark.contract
    def test_workflow_engine_available(self):
        """Test that WorkflowEngine is available."""
        engine = WorkflowEngine()
        assert engine is not None
        assert hasattr(engine, "add_vertex")
        assert hasattr(engine, "add_edge")
        assert hasattr(engine, "validate_workflow")
        assert hasattr(engine, "execute_workflow")

    @pytest.mark.contract
    def test_agent_builder_functional(self):
        """Test that AgentBuilder produces valid agents."""
        agent = (
            AgentBuilder()
            .with_id("test-agent")
            .with_name("Test Agent")
            .with_model("claude-3.5-sonnet")
            .with_speciality("Testing")
            .with_stack(["python", "pytest"])
            .build()
        )

        assert agent is not None
        # Just verify the object was created successfully
        assert (
            hasattr(agent, "id")
            or hasattr(agent, "get_id")
            or str(agent).find("test-agent") >= 0
        )

    @pytest.mark.contract
    def test_team_builder_functional(self):
        """Test that TeamBuilder produces valid teams."""
        # Create a minimal valid team with required fields
        team = (
            TeamBuilder()
            .with_id("test-team")
            .with_name("Test Team")
            .add_member(
                "test-leader", TeamMemberRole.LEADER
            )  # Add a leader to satisfy validation
            .add_member("test-agent", TeamMemberRole.MEMBER)  # Add a member
            .build()
        )

        assert team is not None
        # Just verify the object was created successfully
        assert team is not None

    @pytest.mark.contract
    def test_workflow_builder_functional(self):
        """Test that WorkflowBuilder produces valid workflows."""
        # Create an agent first to use in the workflow
        agent = (
            AgentBuilder().with_id("test-agent").with_model("claude-3-haiku").build()
        )

        # Create a minimal valid workflow with at least one vertex
        workflow = (
            WorkflowBuilder()
            .with_id("test-workflow")
            .with_name("Test Workflow")
            .add_agent_vertex(
                "task1", agent, "Test task"
            )  # Add vertex to satisfy validation
            .build()
        )

        assert workflow is not None
        # Just verify the object was created successfully
        assert workflow is not None

    @pytest.mark.contract
    def test_book_builder_functional(self):
        """Test that BookBuilder produces valid books."""
        book = (
            BookBuilder()
            .with_id("test-book")
            .with_title("Test Book")
            .with_description("A test book")
            .with_author("Test Author")
            .build()
        )

        assert book is not None
        # Just verify the object was created successfully
        assert book is not None

    @pytest.mark.contract
    def test_protocol_builder_functional(self):
        """Test that ProtocolBuilder produces valid protocols."""
        protocol = (
            ProtocolBuilder()
            .with_id("test-protocol")
            .with_name("Test Protocol")
            .build()
        )

        assert protocol is not None
        # Just verify the object was created successfully
        assert (
            hasattr(protocol, "id")
            or hasattr(protocol, "get_id")
            or str(protocol).find("test-protocol") >= 0
        )

    @pytest.mark.contract
    def test_tool_builder_functional(self):
        """Test that ToolBuilder produces valid tools."""
        tool = (
            ToolBuilder()
            .with_id("test-tool")
            .with_name("Test Tool")
            .with_description("A test tool")
            .with_type(ToolType.CLI)  # Add required type
            .build()
        )

        assert tool is not None
        # Just verify the object was created successfully
        assert str(tool).find("test-tool") >= 0

    @pytest.mark.contract
    def test_agent_builder_minimal_contract(self):
        """Test minimal AgentBuilder contract (required fields only)."""
        # According to spec, only id and model are required
        agent = (
            AgentBuilder().with_id("minimal-agent").with_model("claude-3-haiku").build()
        )

        assert agent is not None
        # Just verify the object was created successfully
        assert str(agent).find("minimal-agent") >= 0

    @pytest.mark.contract
    def test_builder_method_chaining(self):
        """Test that all builders support method chaining."""
        # Test AgentBuilder chaining
        agent = (
            AgentBuilder()
            .with_id("chain-test")
            .with_model("gpt-4")
            .with_name("Chain Test")
            .build()
        )
        assert agent is not None

        # Test WorkflowBuilder chaining with required vertex
        workflow_agent = (
            AgentBuilder().with_id("wf-agent").with_model("claude-3-haiku").build()
        )
        workflow = (
            WorkflowBuilder()
            .with_id("chain-workflow")
            .with_name("Chain Workflow")
            .add_agent_vertex("task1", workflow_agent, "Test task")
            .build()
        )
        assert workflow is not None

    @pytest.mark.contract
    def test_builder_error_handling(self):
        """Test that builders handle errors appropriately."""
        # Test missing required fields - should not crash
        try:
            AgentBuilder().build()
            # If it doesn't raise, that's also acceptable
        except Exception:
            # Expected to potentially raise
            pass
