"""Test CLI imports and basic functionality."""

import os
import sys

import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_import_main():
    """Test that main CLI module can be imported."""
    from engine_cli.main import cli

    assert cli is not None


def test_import_commands():
    """Test that all command modules can be imported."""
    from engine_cli.commands import agent, book, protocol, team, tool, workflow

    # Verify modules are imported
    assert agent is not None
    assert team is not None
    assert workflow is not None
    assert tool is not None
    assert protocol is not None
    assert book is not None


@pytest.mark.asyncio
async def test_cli_basic_functionality():
    """Test basic CLI functionality without external dependencies."""
    from engine_cli.main import cli

    # Test that the app can be invoked (this would normally show help)
    # Just verify the cli object exists and is callable
    assert cli is not None
    assert callable(cli)
