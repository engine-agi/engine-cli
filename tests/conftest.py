"""Shared pytest fixtures and configuration for engine-cli."""

import pytest
import sys
import os
from unittest.mock import MagicMock
from click.testing import CliRunner

# Add src to path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def mock_config(mocker) -> MagicMock:
    """Mock configuration loading."""
    mock_config = mocker.patch('engine_cli.config.load_config')
    mock_config.return_value = {
        "api_url": "http://localhost:8000",
        "api_key": "test-key",
        "timeout": 30
    }
    return mock_config


@pytest.fixture
def mock_api_client(mocker) -> MagicMock:
    """Mock API client for CLI tests."""
    mock_client = mocker.patch('engine_cli.api.EngineAPI')
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance
    return mock_instance


@pytest.fixture
def sample_cli_args() -> dict:
    """Sample CLI arguments for testing."""
    return {
        "agent_id": "test-agent",
        "team_id": "test-team",
        "workflow_id": "test-workflow",
        "config_file": "test-config.yaml",
        "output_format": "json",
        "verbose": True
    }


@pytest.fixture
def temp_config_file(tmp_path) -> str:
    """Create a temporary config file for testing."""
    config_path = tmp_path / "test-config.yaml"
    config_content = """
api_url: http://localhost:8000
api_key: test-key
timeout: 30
"""
    config_path.write_text(config_content)
    return str(config_path)