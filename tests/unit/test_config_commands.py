"""Unit tests for CLI config commands."""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from engine_cli.commands.config import show, get, set, init, validate, paths


class TestConfigCommands:
    """Test suite for configuration commands."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    @pytest.fixture
    def mock_config_manager(self):
        """Mock config manager."""
        with patch('engine_cli.commands.config.config_manager') as mock_manager:
            yield mock_manager

    def test_show_command(self, runner, mock_config_manager):
        """Test config show command."""
        # Mock the show_config function
        with patch('engine_cli.commands.config.show_config') as mock_show:
            result = runner.invoke(show)
            assert result.exit_code == 0
            mock_show.assert_called_once()

    def test_get_command(self, runner, mock_config_manager):
        """Test config get command."""
        with patch('engine_cli.commands.config.get_config_value') as mock_get:
            mock_get.return_value = "test_value"

            result = runner.invoke(get, ['api.base_url'])
            assert result.exit_code == 0
            assert "api.base_url: test_value" in result.output
            mock_get.assert_called_once_with('api.base_url')

    def test_get_command_not_found(self, runner, mock_config_manager):
        """Test config get command when value not found."""
        with patch('engine_cli.commands.config.get_config_value') as mock_get:
            mock_get.return_value = None

            result = runner.invoke(get, ['nonexistent.key'])
            assert result.exit_code == 0
            assert "Configuration key 'nonexistent.key' not found" in result.output

    def test_set_command(self, runner, mock_config_manager):
        """Test config set command."""
        with patch('engine_cli.commands.config.set_config_value') as mock_set:
            with patch('engine_cli.commands.config.load_config') as mock_load:
                with patch('engine_cli.commands.config.save_config') as mock_save:
                    mock_config = MagicMock()
                    mock_load.return_value = mock_config

                    result = runner.invoke(set, ['api.base_url', 'http://test.com'])
                    assert result.exit_code == 0
                    assert "Configuration updated: api.base_url = http://test.com" in result.output
                    mock_set.assert_called_once_with('api.base_url', 'http://test.com')
                    mock_save.assert_called_once_with(mock_config, None)

    def test_init_command(self, runner, mock_config_manager):
        """Test config init command."""
        with patch('engine_cli.commands.config.create_default_config') as mock_create:
            with patch('engine_cli.commands.config.save_config') as mock_save:
                mock_config = MagicMock()
                mock_create.return_value = mock_config

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Default configuration created" in result.output
                mock_create.assert_called_once()
                mock_save.assert_called_once_with(mock_config, None)

    def test_validate_command(self, runner, mock_config_manager):
        """Test config validate command."""
        with patch('engine_cli.commands.config.load_config') as mock_load:
            mock_config = MagicMock()
            mock_load.return_value = mock_config

            result = runner.invoke(validate, ['test_config.yaml'])
            assert result.exit_code == 0
            assert "Configuration file is valid" in result.output

    def test_validate_command_file_not_found(self, runner, mock_config_manager):
        """Test config validate command with non-existent file."""
        result = runner.invoke(validate, ['nonexistent.yaml'])
        assert result.exit_code == 1
        assert "does not exist" in result.output

    def test_paths_command(self, runner, mock_config_manager):
        """Test config paths command."""
        # Mock the config manager attributes
        mock_config_manager.config_file = "/home/user/.engine/config.yaml"
        mock_config_manager.env_prefix = "ENGINE_"

        result = runner.invoke(paths)
        assert result.exit_code == 0
        assert "Configuration File Search Paths" in result.output
        assert "Environment Variables" in result.output
        assert "ENGINE_" in result.output