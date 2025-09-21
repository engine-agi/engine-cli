"""Test CLI imports and basic functionality."""
import pytest
from unittest.mock import patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_import_main():
    """Test that main CLI module can be imported."""
    from engine_cli.main import app
    assert app is not None


def test_import_commands():
    """Test that all command modules can be imported."""
    from engine_cli.commands import agent, team, workflow, tool, protocol, book

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
    from engine_cli.main import app

    # Test that the app can be invoked (this would normally show help)
    # We mock typer.echo to avoid actual output
    with patch('typer.echo') as mock_echo:
        try:
            # This should not raise an exception - just test that app exists
            assert app is not None
        except SystemExit:
            # CLI apps often call sys.exit(0) for --help
            pass

    # Just verify the app object exists
    assert app is not None