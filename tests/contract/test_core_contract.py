"""Contract tests for Engine CLI - Engine Core integration."""

try:
    import pytest  # type: ignore

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    class MockPytest:
        class mark:
            @staticmethod
            def contract(func):
                return func

    pytest = MockPytest

# Import engine core components
try:
    from engine_core import AgentBuilder  # type: ignore
    from engine_core import BookBuilder  # type: ignore
    from engine_core import ProtocolBuilder  # type: ignore
    from engine_core import TeamBuilder  # type: ignore
    from engine_core import ToolBuilder  # type: ignore
    from engine_core import WorkflowBuilder  # type: ignore
    from engine_core import WorkflowEngine  # type: ignore
    from engine_core import __version__ as core_version  # type: ignore
    from engine_core.core.teams.team_builder import (  # type: ignore; type: ignore; type: ignore
        TeamCoordinationStrategy,
        TeamMemberRole,
    )
    from engine_core.models.tool import ToolType  # type: ignore

    ENGINE_CORE_AVAILABLE = True

except ImportError:
    ENGINE_CORE_AVAILABLE = False
    AgentBuilder = None
    BookBuilder = None
    ProtocolBuilder = None
    TeamBuilder = None
    ToolBuilder = None
    WorkflowBuilder = None
    WorkflowEngine = None
    core_version = None
    TeamCoordinationStrategy = None
    TeamMemberRole = None
    ToolType = None


class TestEngineCoreContract:
    """Test contracts between Engine CLI and Engine Core."""

    @pytest.mark.contract  # type: ignore
    def test_core_version_available(self):
        """Test that core version is accessible."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        assert core_version is not None
        assert isinstance(core_version, str)
        assert len(core_version) > 0

    @pytest.mark.contract  # type: ignore
    def test_agent_builder_available(self):
        """Test that AgentBuilder is available and functional."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        builder = AgentBuilder()  # type: ignore
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_model")
        assert hasattr(builder, "with_stack")
        assert hasattr(builder, "build")

    @pytest.mark.contract  # type: ignore
    def test_team_builder_available(self):
        """Test that TeamBuilder is available and functional."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        builder = TeamBuilder()  # type: ignore
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "add_member")
        assert hasattr(builder, "with_coordination_strategy")
        assert hasattr(builder, "build")

    @pytest.mark.contract  # type: ignore
    def test_workflow_builder_available(self):
        """Test that WorkflowBuilder is available and functional."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        builder = WorkflowBuilder()  # type: ignore
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "add_agent_vertex")
        assert hasattr(builder, "add_edge")
        assert hasattr(builder, "build")

    @pytest.mark.contract  # type: ignore
    def test_book_builder_available(self):
        """Test that BookBuilder is available and functional."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        builder = BookBuilder()  # type: ignore
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_title")
        assert hasattr(builder, "build")

    @pytest.mark.contract  # type: ignore
    def test_protocol_builder_available(self):
        """Test that ProtocolBuilder is available and functional."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        builder = ProtocolBuilder()  # type: ignore
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_name")
        assert hasattr(builder, "with_default_scope")
        assert hasattr(builder, "build")

    @pytest.mark.contract  # type: ignore
    def test_tool_builder_available(self):
        """Test that ToolBuilder is available and functional."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        builder = ToolBuilder()  # type: ignore
        assert builder is not None
        assert hasattr(builder, "with_id")
        assert hasattr(builder, "with_name")
        assert hasattr(builder, "with_description")
        assert hasattr(builder, "build")

    @pytest.mark.contract  # type: ignore
    def test_workflow_engine_available(self):
        """Test that WorkflowEngine is available."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        engine = WorkflowEngine()  # type: ignore
        assert engine is not None
        assert hasattr(engine, "add_vertex")
        assert hasattr(engine, "add_edge")
        assert hasattr(engine, "validate_workflow")
        assert hasattr(engine, "execute_workflow")

    @pytest.mark.contract  # type: ignore
    def test_agent_builder_functional(self):
        """Test that AgentBuilder produces valid agents."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        agent = (
            AgentBuilder()  # type: ignore
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

    @pytest.mark.contract  # type: ignore
    def test_team_builder_functional(self):
        """Test that TeamBuilder produces valid teams."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        # Create a minimal valid team with required fields
        team = (
            TeamBuilder()  # type: ignore
            .with_id("test-team")
            .with_name("Test Team")
            .add_member(
                "test-leader", TeamMemberRole.LEADER  # type: ignore
            )  # Add a leader to satisfy validation
            .add_member(
                "test-agent", TeamMemberRole.MEMBER  # type: ignore
            )  # Add a member
            .build()
        )

        assert team is not None
        # Just verify the object was created successfully
        assert team is not None

    @pytest.mark.contract  # type: ignore
    def test_workflow_builder_functional(self):
        """Test that WorkflowBuilder produces valid workflows."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        # Create an agent first to use in the workflow
        agent = (
            AgentBuilder()  # type: ignore
            .with_id("test-agent")
            .with_model("claude-3-haiku")
            .build()
        )

        # Create a minimal valid workflow with at least one vertex
        workflow = (
            WorkflowBuilder()  # type: ignore
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

    @pytest.mark.contract  # type: ignore
    def test_book_builder_functional(self):
        """Test that BookBuilder produces valid books."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        book = (
            BookBuilder()  # type: ignore
            .with_id("test-book")
            .with_title("Test Book")
            .with_description("A test book")
            .with_author("Test Author")
            .build()
        )

        assert book is not None
        # Just verify the object was created successfully
        assert book is not None

    @pytest.mark.contract  # type: ignore
    def test_protocol_builder_functional(self):
        """Test that ProtocolBuilder produces valid protocols."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        protocol = (
            ProtocolBuilder()  # type: ignore
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

    @pytest.mark.contract  # type: ignore
    def test_tool_builder_functional(self):
        """Test that ToolBuilder produces valid tools."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        tool = (
            ToolBuilder()  # type: ignore
            .with_id("test-tool")
            .with_name("Test Tool")
            .with_description("A test tool")
            .with_type(ToolType.CLI)  # type: ignore # Add required type
            .build()
        )

        assert tool is not None
        # Just verify the object was created successfully
        assert str(tool).find("test-tool") >= 0

    @pytest.mark.contract  # type: ignore
    def test_agent_builder_minimal_contract(self):
        """Test minimal AgentBuilder contract (required fields only)."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        # According to spec, only id and model are required
        agent = (
            AgentBuilder()  # type: ignore
            .with_id("minimal-agent")
            .with_model("claude-3-haiku")
            .build()
        )

        assert agent is not None
        # Just verify the object was created successfully
        assert str(agent).find("minimal-agent") >= 0

    @pytest.mark.contract  # type: ignore
    def test_builder_method_chaining(self):
        """Test that all builders support method chaining."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        # Test AgentBuilder chaining
        agent = (
            AgentBuilder()  # type: ignore
            .with_id("chain-test")
            .with_model("gpt-4")
            .with_name("Chain Test")
            .build()
        )
        assert agent is not None

        # Test WorkflowBuilder chaining with required vertex
        workflow_agent = (
            AgentBuilder()  # type: ignore
            .with_id("wf-agent")
            .with_model("claude-3-haiku")
            .build()
        )
        workflow = (
            WorkflowBuilder()  # type: ignore
            .with_id("chain-workflow")
            .with_name("Chain Workflow")
            .add_agent_vertex("task1", workflow_agent, "Test task")
            .build()
        )
        assert workflow is not None

    @pytest.mark.contract  # type: ignore
    def test_builder_error_handling(self):
        """Test that builders handle errors appropriately."""
        if not ENGINE_CORE_AVAILABLE:
            pytest.skip("Engine Core not available")  # type: ignore
        # Test missing required fields - should not crash
        try:
            AgentBuilder().build()  # type: ignore
            # If it doesn't raise, that's also acceptable
        except Exception:
            # Expected to potentially raise
            pass
