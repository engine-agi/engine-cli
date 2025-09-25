"""
Testes de cobertura para módulos CLI disponíveis - Testes unitários diretos
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Testes para módulos que estão disponíveis
def test_cache_module_import():
    """Testa se o módulo cache pode ser importado"""
    from engine_cli.cache import CLICache

    assert CLICache is not None


def test_config_module_import():
    """Testa se o módulo config pode ser importado"""
    from engine_cli.config import ConfigManager, EngineConfig

    assert EngineConfig is not None
    assert ConfigManager is not None


def test_formatting_module_import():
    """Testa se o módulo formatting pode ser importado"""
    from engine_cli.formatting import (
        error,
        header,
        info,
        success,
        table,
        warning,
    )

    assert success is not None
    assert error is not None
    assert warning is not None
    assert info is not None
    assert header is not None
    assert table is not None


def test_interactive_module_import():
    """Testa se o módulo interactive pode ser importado"""
    from engine_cli.interactive import InteractiveCLI

    assert InteractiveCLI is not None


def test_main_module_import():
    """Testa se o módulo main pode ser importado"""
    from engine_cli.main import cli, interactive, status, version

    assert cli is not None
    assert version is not None
    assert status is not None
    assert interactive is not None


# Testes para storage
def test_storage_modules_import():
    """Testa se os módulos de storage podem ser importados"""
    from engine_cli.storage.agent_book_storage import AgentBookStorage
    from engine_cli.storage.workflow_state_manager import WorkflowStateManager

    assert AgentBookStorage is not None
    assert WorkflowStateManager is not None


# Testes funcionais para cache
def test_cache_initialization():
    """Testa inicialização do cache"""
    from engine_cli.cache import CLICache

    with tempfile.TemporaryDirectory() as temp_dir:
        cache = CLICache(cache_dir=temp_dir)
        assert cache.cache_dir == Path(temp_dir)
        assert cache.commands_cache_file is not None
        assert cache.modules_cache_file is not None


def test_cache_operations():
    """Testa operações básicas do cache"""
    from engine_cli.cache import CLICache

    with tempfile.TemporaryDirectory() as temp_dir:
        cache = CLICache(cache_dir=temp_dir)

        # Test set/get command info
        test_info = {"description": "test command", "usage": "test usage"}
        cache.set_command_info("test_cmd", test_info)

        retrieved = cache.get_command_info("test_cmd")
        assert retrieved == test_info

        # Test module hash operations
        cache.set_module_hash("test_module", "abc123")
        hash_value = cache.get_module_hash("test_module")
        assert hash_value == "abc123"

        # Test clear cache
        cache.clear_cache()
        assert not cache.commands_cache_file.exists()
        assert not cache.modules_cache_file.exists()


# Testes funcionais para config
def test_config_initialization():
    """Testa inicialização do config"""
    from engine_cli.config import ConfigManager

    config = ConfigManager()
    assert config.config_paths is not None
    assert isinstance(config.config_paths, list)
    assert len(config.config_paths) > 0


def test_config_operations():
    """Testa operações básicas do config"""
    from engine_cli.config import ConfigManager

    config = ConfigManager()

    # Test set/get
    config.set("test.section.key", "test_value")
    assert config.get("test.section.key") == "test_value"

    # Test get com default
    assert config.get("nonexistent", "default") == "default"


# Testes funcionais para formatting
def test_formatting_functions():
    """Testa funções de formatação"""
    from engine_cli.formatting import (
        error,
        header,
        info,
        success,
        table,
        warning,
    )

    # Test that functions exist and can be called (without actually printing)
    # We'll mock console.print to avoid actual output
    with patch("engine_cli.formatting.console.print"):
        success("Test message")
        error("Test error")
        warning("Test warning")
        info("Test info")
        header("Test Header")
        table("Test Table", ["col1", "col2"])


# Testes funcionais para storage
def test_agent_book_storage():
    """Testa operações do AgentBookStorage"""
    from engine_cli.storage.agent_book_storage import AgentBookStorage

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = AgentBookStorage(storage_dir=temp_dir)

        # Test save/load agent
        test_data = {
            "id": "test_agent",
            "name": "Test Agent",
            "model": "claude-3.5-sonnet",
            "created_at": "2024-01-01T00:00:00Z",
        }
        storage.save_agent(test_data)

        loaded = storage.get_agent("test_agent")
        assert loaded is not None
        assert loaded["id"] == "test_agent"
        assert loaded["name"] == "Test Agent"

        # Test list agents
        agents = storage.list_agents()
        assert len(agents) >= 1

        # Test agent exists
        assert storage.agent_exists("test_agent")
        assert not storage.agent_exists("nonexistent")


def test_workflow_state_manager():
    """Testa operações do WorkflowStateManager"""
    import asyncio

    from engine_cli.storage.workflow_state_manager import WorkflowStateManager

    async def test_async():
        # Test with fallback (no Redis)
        manager = WorkflowStateManager(enable_fallback=True)

        # Test create execution
        execution_id = await manager.create_execution(
            workflow_id="test_workflow",
            workflow_name="Test Workflow",
            input_data={"test": "data"},
        )
        assert execution_id is not None

        # Test get execution status
        status = await manager.get_execution_status(execution_id)
        assert status is not None

    asyncio.run(test_async())


# Testes para comandos individuais (se disponíveis)
def test_book_command_import():
    """Testa se o módulo book command pode ser importado"""
    try:
        from engine_cli.commands.book import create_book, get_book, list_books

        assert create_book is not None
        assert list_books is not None
        assert get_book is not None
    except ImportError:
        pytest.skip("Book commands not available")


def test_examples_command_import():
    """Testa se o módulo examples command pode ser importado"""
    try:
        from engine_cli.commands.examples import show_examples

        assert show_examples is not None
    except ImportError:
        pytest.skip("Examples commands not available")


def test_monitoring_command_import():
    """Testa se o módulo monitoring command pode ser importado"""
    try:
        from engine_cli.commands.monitoring import show_status

        assert show_status is not None
    except ImportError:
        pytest.skip("Monitoring commands not available")


def test_project_command_import():
    """Testa se o módulo project command pode ser importado"""
    try:
        from engine_cli.commands.project import init_project

        assert init_project is not None
    except ImportError:
        pytest.skip("Project commands not available")
