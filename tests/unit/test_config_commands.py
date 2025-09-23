"""Unit tests for CLI config commands."""
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
import subprocess
import os
from pathlib import Path

from engine_cli.commands.config import show, get, set, init, validate, paths, edit, reset


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
            with patch('pathlib.Path.exists', return_value=False):
                mock_config = MagicMock()
                mock_create.return_value = mock_config

                result = runner.invoke(init, ['--force'])
                assert result.exit_code == 0
                assert "Default configuration created" in result.output
                mock_create.assert_called_once()

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
        assert result.exit_code == 2  # Click error for missing file
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

    def test_edit_command(self, runner, mock_config_manager):
        """Test config edit command."""
        # Mock config paths
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_config_manager.config_paths = [mock_path]

        with patch('subprocess.run') as mock_subprocess:
            with patch.dict(os.environ, {'EDITOR': 'nano'}):
                result = runner.invoke(edit)
                assert result.exit_code == 0
                assert "Configuration edited" in result.output
                mock_subprocess.assert_called_once_with(['nano', str(mock_path)], check=True)

    def test_edit_command_with_file(self, runner, mock_config_manager):
        """Test config edit command with specific file."""
        config_path = "/custom/config.yaml"

        with patch('subprocess.run') as mock_subprocess:
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {'EDITOR': 'vim'}):
                    result = runner.invoke(edit, ['--file', config_path])
                    assert result.exit_code == 0
                    assert "Configuration edited" in result.output
                    mock_subprocess.assert_called_once_with(['vim', config_path], check=True)

    def test_edit_command_no_config_file(self, runner, mock_config_manager):
        """Test config edit command when no config file exists."""
        # Mock config paths - none exist
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_config_manager.config_paths = [mock_path]

        result = runner.invoke(edit)
        assert result.exit_code == 0
        assert "No configuration file found" in result.output

    def test_edit_command_file_not_found(self, runner, mock_config_manager):
        """Test config edit command with non-existent file."""
        config_path = "/nonexistent/config.yaml"

        with patch('pathlib.Path.exists', return_value=False):
            result = runner.invoke(edit, ['--file', config_path])
            assert result.exit_code == 0
            assert "Configuration file not found" in result.output

    def test_edit_command_editor_not_found(self, runner, mock_config_manager):
        """Test config edit command when editor fails."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_config_manager.config_paths = [mock_path]

        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'nano')):
            with patch.dict(os.environ, {'EDITOR': 'nano'}):
                result = runner.invoke(edit)
                assert result.exit_code == 0
                assert "Editor 'nano' not found or failed" in result.output

    def test_reset_command_full_reset(self, runner, mock_config_manager):
        """Test config reset command for full configuration."""
        with patch('engine_cli.commands.config.create_default_config') as mock_create:
            with patch('engine_cli.commands.config.save_config') as mock_save:
                mock_default_config = MagicMock()
                mock_create.return_value = mock_default_config

                result = runner.invoke(reset)
                assert result.exit_code == 0
                assert "Entire configuration reset to defaults" in result.output
                mock_save.assert_called_once_with(mock_default_config)

    def test_reset_command_section_reset(self, runner, mock_config_manager):
        """Test config reset command for specific section."""
        with patch('engine_cli.commands.config.create_default_config') as mock_create:
            with patch('engine_cli.commands.config.load_config') as mock_load:
                with patch('engine_cli.commands.config.save_config') as mock_save:
                    mock_default_config = MagicMock()
                    mock_current_config = MagicMock()
                    mock_default_config.api = "default_api"
                    mock_create.return_value = mock_default_config
                    mock_load.return_value = mock_current_config

                    result = runner.invoke(reset, ['api'])
                    assert result.exit_code == 0
                    assert "Section 'api' reset to defaults" in result.output
                    mock_save.assert_called_once_with(mock_current_config)

    def test_reset_command_unknown_section(self, runner, mock_config_manager):
        """Test config reset command with unknown section."""
        with patch('engine_cli.commands.config.create_default_config') as mock_create:
            with patch('engine_cli.commands.config.load_config') as mock_load:
                mock_default_config = MagicMock()
                # Remove the hasattr behavior by not setting the attribute
                del mock_default_config.unknown_section  # Ensure hasattr returns False
                mock_create.return_value = mock_default_config
                mock_load.return_value = MagicMock()

                result = runner.invoke(reset, ['unknown_section'])
                assert result.exit_code == 0
                assert "Unknown configuration section: unknown_section" in result.output

    def test_show_command_with_file(self, runner, mock_config_manager):
        """Test config show command with specific file."""
        with patch('engine_cli.commands.config.show_config') as mock_show:
            result = runner.invoke(show, ['--file', 'custom_config.yaml'])
            assert result.exit_code == 0
            mock_config_manager.load_config.assert_called_once_with('custom_config.yaml')
            mock_show.assert_called_once()

    def test_show_command_error(self, runner, mock_config_manager):
        """Test config show command with error."""
        mock_config_manager.load_config.side_effect = Exception("Load error")

        result = runner.invoke(show, ['--file', 'bad_config.yaml'])
        assert result.exit_code == 0
        assert "Failed to show configuration: Load error" in result.output

    def test_set_command_with_file(self, runner, mock_config_manager):
        """Test config set command with specific file."""
        with patch('engine_cli.commands.config.set_config_value') as mock_set:
            with patch('engine_cli.commands.config.load_config') as mock_load:
                with patch('engine_cli.commands.config.save_config') as mock_save:
                    mock_config = MagicMock()
                    mock_load.return_value = mock_config

                    result = runner.invoke(set, ['api.base_url', 'http://test.com', '--file', 'custom_config.yaml'])
                    assert result.exit_code == 0
                    mock_load.assert_called_with('custom_config.yaml')
                    mock_save.assert_called_with(mock_config, 'custom_config.yaml')

    def test_set_command_error(self, runner, mock_config_manager):
        """Test config set command with error."""
        with patch('engine_cli.commands.config.load_config', side_effect=Exception("Load error")):
            result = runner.invoke(set, ['api.base_url', 'http://test.com'])
            assert result.exit_code == 0
            assert "Failed to set configuration: Load error" in result.output

    def test_get_command_error(self, runner, mock_config_manager):
        """Test config get command with error."""
        with patch('engine_cli.commands.config.get_config_value', side_effect=Exception("Get error")):
            result = runner.invoke(get, ['api.base_url'])
            assert result.exit_code == 0
            assert "Failed to get configuration: Get error" in result.output

    def test_init_command_with_custom_path(self, runner, mock_config_manager):
        """Test config init command with custom path."""
        with patch('engine_cli.commands.config.create_default_config') as mock_create:
            with patch('pathlib.Path.exists', return_value=False):
                with patch('pathlib.Path.home') as mock_home:
                    mock_config = MagicMock()
                    mock_create.return_value = mock_config

                    result = runner.invoke(init, ['--file', '/custom/path/config.yaml'])
                    assert result.exit_code == 0
                    # Should not call Path.home() when custom path is provided
                    mock_home.assert_not_called()

    def test_init_command_error(self, runner, mock_config_manager):
        """Test config init command with error."""
        with patch('engine_cli.commands.config.create_default_config', side_effect=Exception("Create error")):
            with patch('pathlib.Path.exists', return_value=False):
                result = runner.invoke(init, ['--force'])
                assert result.exit_code == 0
                assert "Failed to create configuration: Create error" in result.output

    def test_reset_command_error(self, runner, mock_config_manager):
        """Test config reset command with error."""
        with patch('engine_cli.commands.config.create_default_config', side_effect=Exception("Reset error")):
            result = runner.invoke(reset)
            assert result.exit_code == 0
            assert "Failed to reset configuration: Reset error" in result.output