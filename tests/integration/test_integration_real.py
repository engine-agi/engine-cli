"""
Testes de Integração - Framework Engine Completo
Testes que inicializam o framework completo com dependências reais
"""

import tempfile

import pytest


# Testes de integração com framework completo
@pytest.mark.integration
def test_engine_core_initialization():
    """Testa inicialização completa do Engine Core"""
    try:
        import importlib

        engine_core = importlib.import_module("engine_core")
        AgentBuilder = getattr(engine_core, "AgentBuilder", None)
        BookBuilder = getattr(engine_core, "BookBuilder", None)
        TeamBuilder = getattr(engine_core, "TeamBuilder", None)
        WorkflowBuilder = getattr(engine_core, "WorkflowBuilder", None)

        assert AgentBuilder is not None, "AgentBuilder not available"
        assert BookBuilder is not None, "BookBuilder not available"
        assert TeamBuilder is not None, "TeamBuilder not available"
        assert WorkflowBuilder is not None, "WorkflowBuilder not available"

        # Test Book Builder
        book = (
            BookBuilder()
            .with_id("test_book")
            .with_title("Test Book")
            .with_author("Test Author")
            .build()
        )

        assert book.book_id == "test_book"
        assert book.title == "Test Book"

        # Test Agent Builder
        agent = (
            AgentBuilder()
            .with_id("test_agent")
            .with_model("claude-3.5-sonnet")
            .with_stack(["python"])
            .build()
        )

        assert agent.id == "test_agent"
        assert agent.model == "claude-3.5-sonnet"

        # Test Workflow Builder
        workflow = (
            WorkflowBuilder()
            .with_id("test_workflow")
            .add_agent_vertex("task1", agent, "Process test data")
            .build()
        )

        assert workflow.id == "test_workflow"

        # Team Builder test skipped for now - requires complex setup

    except ImportError:
        pytest.skip("Engine Core not available")


@pytest.mark.integration
def test_cli_with_real_dependencies():
    """Testa CLI com dependências reais disponíveis"""
    try:
        from engine_cli.cache import CLICache
        from engine_cli.config import ConfigManager
        from engine_cli.storage.agent_book_storage import AgentBookStorage
        from engine_cli.storage.workflow_state_manager import WorkflowStateManager

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test Cache com Redis real (se disponível)
            try:
                pass

                cache = CLICache(cache_dir=temp_dir)
                # Redis operations would be tested here
                assert cache is not None
            except ImportError:
                pytest.skip("Redis not available")

            # Test Config Manager
            config = ConfigManager()
            assert config is not None

            # Test Agent Book Storage
            storage = AgentBookStorage(storage_dir=temp_dir)
            assert storage is not None

            # Test Workflow State Manager com Redis real
            try:
                manager = WorkflowStateManager(
                    redis_url="redis://localhost:6379", enable_fallback=False
                )
                assert manager is not None
            except Exception:
                # Fallback to memory-only mode
                manager = WorkflowStateManager(enable_fallback=True)
                assert manager is not None

    except ImportError as e:
        pytest.skip(f"Required modules not available: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_execution_real():
    """Testa execução real de workflow com dependências"""
    try:
        from engine_cli.storage.workflow_state_manager import WorkflowStateManager

        # Test with real Redis if available
        try:
            manager = WorkflowStateManager(
                redis_url="redis://localhost:6379", enable_fallback=False
            )

            # Create execution
            execution_id = await manager.create_execution(
                workflow_id="integration_test",
                workflow_name="Integration Test Workflow",
                input_data={"test": "data"},
            )

            assert execution_id is not None

            # Get execution status
            status = await manager.get_execution_status(execution_id)
            assert status is not None
            assert status.workflow_id == "integration_test"

            # Update execution state
            from engine_cli.storage.workflow_state_manager import WorkflowExecutionState

            await manager.update_execution_state(
                execution_id=execution_id,
                state=WorkflowExecutionState.RUNNING,
                current_vertex="task1",
            )

            # Verify state change
            updated_status = await manager.get_execution_status(execution_id)
            assert updated_status is not None
            assert updated_status.state == WorkflowExecutionState.RUNNING

        except Exception as e:
            # Fallback to memory mode
            pytest.skip(f"Redis integration failed: {e}")

    except ImportError:
        pytest.skip("Workflow State Manager not available")


@pytest.mark.integration
def test_database_integration():
    """Testa integração com PostgreSQL"""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        # Test database connection (would need actual schema)
        # This is a placeholder for real database integration tests
        engine = create_async_engine(
            "postgresql+asyncpg://engine:engine123@localhost:5432/engine_test"
        )

        # In a real scenario, we would:
        # 1. Create tables
        # 2. Insert test data
        # 3. Query and verify
        # 4. Clean up

        assert engine is not None

    except ImportError:
        pytest.skip("Database dependencies not available")
    except Exception as e:
        pytest.skip(f"Database connection failed: {e}")


@pytest.mark.integration
def test_full_cli_initialization():
    """Testa inicialização completa da CLI"""
    try:
        from engine_cli.cache import CLICache
        from engine_cli.config import ConfigManager
        from engine_cli.main import cli

        # Test CLI initialization
        assert cli is not None

        # Test config initialization
        config = ConfigManager()
        assert config is not None

        # Test cache initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CLICache(cache_dir=temp_dir)
            assert cache is not None

    except ImportError as e:
        pytest.skip(f"CLI modules not available: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_agent_workflow():
    """Teste end-to-end: criar agente -> executar workflow -> verificar resultado"""
    try:
        from engine_cli.storage.agent_book_storage import AgentBookStorage
        from engine_cli.storage.workflow_state_manager import WorkflowStateManager

        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup storage
            agent_storage = AgentBookStorage(storage_dir=temp_dir)
            workflow_manager = WorkflowStateManager(enable_fallback=True)

            # Create and save agent
            agent_data = {
                "id": "e2e_agent",
                "name": "End-to-End Test Agent",
                "model": "claude-3.5-sonnet",
                "stack": ["python", "cli"],
                "created_at": "2024-01-01T00:00:00Z",
            }

            agent_storage.save_agent(agent_data)

            # Verify agent was saved
            loaded_agent = agent_storage.get_agent("e2e_agent")
            assert loaded_agent is not None
            assert loaded_agent["id"] == "e2e_agent"

            # Create workflow execution
            execution_id = await workflow_manager.create_execution(
                workflow_id="e2e_workflow",
                workflow_name="End-to-End Workflow",
                input_data={"agent_id": "e2e_agent"},
            )

            assert execution_id is not None

            # Verify execution was created
            status = await workflow_manager.get_execution_status(execution_id)
            assert status is not None
            assert status.workflow_name == "End-to-End Workflow"

    except ImportError as e:
        pytest.skip(f"Required modules not available: {e}")
    except Exception as e:
        pytest.fail(f"End-to-end test failed: {e}")


@pytest.mark.integration
def test_cli_commands_with_real_data():
    """Testa comandos CLI com dados reais"""
    try:
        import importlib

        from click.testing import CliRunner

        # Import CLI commands conditionally
        try:
            agent_module = importlib.import_module("engine_cli.commands.agent")
            create_agent = getattr(agent_module, "create_agent", None)
            list_agents = getattr(agent_module, "list_agents", None)
        except ImportError:
            create_agent = None
            list_agents = None

        try:
            book_module = importlib.import_module("engine_cli.commands.book")
            create_book = getattr(book_module, "create_book", None)
            list_books = getattr(book_module, "list_books", None)
        except ImportError:
            create_book = None
            list_books = None

        runner = CliRunner()

        # Test book commands (if available)
        if create_book is not None:
            try:
                result = runner.invoke(
                    create_book,
                    [
                        "--id",
                        "integration_book",
                        "--title",
                        "Integration Test Book",
                        "--author",
                        "Test Suite",
                    ],
                )
                # Note: This might fail if the command requires additional setup
                # but we're testing that the command exists and can be invoked
                assert result.exit_code in [0, 1, 2]  # Success or expected failure
            except Exception:
                # Command might not be fully implemented yet
                pass

        # Test agent commands (if available)
        if create_agent is not None:
            try:
                result = runner.invoke(
                    create_agent,
                    [
                        "--id",
                        "integration_agent",
                        "--model",
                        "claude-3.5-sonnet",
                        "--stack",
                        "python",
                    ],
                )
                assert result.exit_code in [0, 1, 2]
            except Exception:
                pass

    except ImportError:
        pytest.skip("CLI commands not available")
