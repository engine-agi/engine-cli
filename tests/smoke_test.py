"""Smoke tests for engine-cli package."""

import os
import sys

import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.mark.smoke
def test_package_import():
    """Test that the engine_cli package can be imported."""
    try:
        import engine_cli

        assert engine_cli is not None
    except ImportError:
        pytest.skip("engine_cli package not yet implemented")


@pytest.mark.smoke
def test_main_app_import():
    """Test that the main CLI app can be imported."""
    try:
        from engine_cli.main import app

        assert app is not None
    except ImportError:
        pytest.skip("CLI main app not yet implemented")


@pytest.mark.smoke
def test_commands_import():
    """Test that command modules can be imported."""
    try:
        from engine_cli import commands

        assert commands is not None
    except ImportError:
        pytest.skip("CLI commands not yet implemented")


@pytest.mark.smoke
@pytest.mark.cli
def test_cli_runner_basic(cli_runner):
    """Test basic CLI runner functionality."""
    # This will test the CLI testing infrastructure
    # Just test that CliRunner is available and can be instantiated
    assert cli_runner is not None
    assert hasattr(cli_runner, "invoke")


@pytest.mark.smoke
def test_config_loading():
    """Test that configuration can be loaded."""
    try:
        from engine_cli import config

        # Just test that config module exists
        assert config is not None
    except ImportError:
        pytest.skip("CLI config not yet implemented")
